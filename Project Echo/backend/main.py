"""
Project Echo - Backend API
提供实时语音补全与图片转述功能。

技术栈：
- 语音识别：OpenAI Whisper
- 语言模型：GPT-4o-mini
- 语音合成：Edge TTS
"""

import os
import base64
import tempfile
import traceback
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import edge_tts
import whisper
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

# 配置
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")
TTS_OUTPUT_DIR = os.getenv("TTS_OUTPUT_DIR", "./tts_outputs")

os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

# 全局模型实例
whisper_model = None
openai_client: Optional[OpenAI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global whisper_model, openai_client

    if not OPENAI_API_KEY:
        raise RuntimeError("请设置环境变量 OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    print(f"正在加载 Whisper 模型: {WHISPER_MODEL_SIZE} ...")
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    print("Whisper 模型加载完成")
    yield
    print("服务关闭")


app = FastAPI(
    title="Project Echo API",
    description="脑卒中后失语症患者的实时语音补全与图片转述服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoiceCompletionResponse(BaseModel):
    original_text: str = Field(..., description="Whisper 识别的原始文本")
    completed_text: str = Field(..., description="GPT 补全后的完整表达")
    audio_url: Optional[str] = Field(None, description="合成语音文件路径")


class ImageDescriptionResponse(BaseModel):
    description: str = Field(..., description="图片内容描述")
    audio_url: Optional[str] = Field(None, description="合成语音文件路径")


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def guess_mime_type(filename: str, fallback: str = "image/jpeg") -> str:
    """根据文件名后缀推断 MIME 类型。"""
    ext = os.path.splitext(filename.lower())[-1]
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    return mapping.get(ext, fallback)


async def text_to_speech(text: str, filename_prefix: str) -> str:
    """使用 Edge TTS 将文本转为语音，返回生成的音频文件路径。"""
    output_path = os.path.join(TTS_OUTPUT_DIR, f"{filename_prefix}.mp3")
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(output_path)
    return output_path


@app.get("/")
async def root():
    return {
        "name": "Project Echo API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "whisper_loaded": whisper_model is not None}


@app.post("/voice-completion", response_model=VoiceCompletionResponse)
async def voice_completion(
    audio: UploadFile = File(..., description="用户语音文件（支持 mp3/wav/m4a 等格式）"),
    context: Optional[str] = Form(None, description="可选上下文，帮助模型更准确地补全"),
    return_audio: bool = Form(True, description="是否返回合成后的语音文件"),
):
    """
    语音补全接口：
    1. 使用 Whisper 将语音转为文本；
    2. 使用 GPT-4o-mini 根据上下文补全为完整、自然的表达；
    3. 使用 Edge TTS 将补全结果转为语音返回。
    """
    try:
        audio_bytes = await audio.read()

        # Whisper 转录
        suffix = os.path.splitext(audio.filename or ".wav")[-1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        result = whisper_model.transcribe(tmp_path, language="zh")
        original_text = result.get("text", "").strip()
        os.remove(tmp_path)

        if not original_text:
            raise HTTPException(status_code=400, detail="未能识别到语音内容")

        # GPT 补全
        system_prompt = (
            "你是一位耐心的语言辅助助手，正在帮助脑卒中后失语症患者完成表达。\n"
            "请根据用户断断续续的语音内容，补全为一句完整、自然、礼貌的中文表达。\n"
            "不要添加解释，只输出补全后的句子。"
        )
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "user", "content": f"上下文：{context}\n用户说：{original_text}"})
        else:
            messages.append({"role": "user", "content": f"用户说：{original_text}"})

        chat = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
            max_tokens=120,
        )
        completed_text = chat.choices[0].message.content.strip()

        # Edge TTS 合成
        audio_url = None
        if return_audio and completed_text:
            audio_path = await text_to_speech(completed_text, f"vc_{uuid.uuid4().hex[:12]}")
            audio_url = os.path.basename(audio_path)

        return VoiceCompletionResponse(
            original_text=original_text,
            completed_text=completed_text,
            audio_url=audio_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"语音补全失败: {str(e)}")


@app.post("/image-description", response_model=ImageDescriptionResponse)
async def image_description(
    image: UploadFile = File(..., description="用户上传的图片文件"),
    scene_hint: Optional[str] = Form(None, description="可选场景提示，例如‘这是今天的午餐’"),
    return_audio: bool = Form(True, description="是否返回合成后的语音文件"),
):
    """
    图片转述接口：
    1. 使用 GPT-4o-mini 视觉能力描述图片内容；
    2. 将描述转为简洁、适合失语症患者理解的表达；
    3. 使用 Edge TTS 将结果转为语音返回。
    """
    try:
        image_bytes = await image.read()
        base64_image = encode_image_to_base64(image_bytes)
        mime_type = image.content_type or guess_mime_type(image.filename or "")

        user_content = [
            {
                "type": "text",
                "text": (
                    "请用简洁、温和的中文描述这张图片，适合帮助失语症患者理解或表达。"
                    f"场景提示：{scene_hint or '无'}"
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
            },
        ]

        chat = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_content}],
            temperature=0.4,
            max_tokens=200,
        )
        description = chat.choices[0].message.content.strip()

        audio_url = None
        if return_audio and description:
            audio_path = await text_to_speech(description, f"img_{uuid.uuid4().hex[:12]}")
            audio_url = os.path.basename(audio_path)

        return ImageDescriptionResponse(description=description, audio_url=audio_url)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片转述失败: {str(e)}")


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """获取 Edge TTS 生成的音频文件。"""
    file_path = os.path.join(TTS_OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")
    return FileResponse(file_path, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
