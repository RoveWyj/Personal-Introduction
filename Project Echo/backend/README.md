# Project Echo - Backend

基于 FastAPI 的后端服务，提供实时语音补全与图片转述能力。

## 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/voice-completion` | 语音补全：语音 → 文本 → GPT 补全 → 语音 |
| POST | `/image-description` | 图片转述：图片 → GPT 描述 → 语音 |
| GET | `/audio/{filename}` | 获取 TTS 生成的音频文件 |

## 快速开始

1. 复制环境变量文件并填写 OpenAI API Key：

   ```bash
   cp .env.example .env
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 启动服务：

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. 访问文档：

   ```
   http://localhost:8000/docs
   ```

## Hugging Face Spaces 部署

1. 在 [Hugging Face Spaces](https://huggingface.co/spaces) 创建新 Space，选择 **Docker** 模板。
2. 将 `backend/` 目录下的内容上传至 Space 仓库。
3. 在 Space 的 **Settings > Secrets** 中添加：
   - `OPENAI_API_KEY`：你的 OpenAI API Key
   - 可选：`WHISPER_MODEL_SIZE`（默认 base）
4. Space 构建完成后即可通过 `/docs` 访问接口文档。

## 依赖说明

- **Whisper**：本地加载，首次运行会自动下载模型。
- **GPT-4o-mini**：通过 OpenAI API 调用。
- **Edge TTS**：免费在线语音合成，无需 Azure 订阅。
