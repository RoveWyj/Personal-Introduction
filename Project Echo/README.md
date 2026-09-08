# Project Echo

为脑卒中后失语症患者提供实时语音补全与图片转述功能的 AI 辅助沟通工具。

## 项目简介

脑卒中后失语症患者在日常交流中常面临表达困难。Project Echo 通过 AI 技术，在患者说话或展示图片时提供实时补全与转述支持，帮助他们更自然、更流畅地完成沟通。

## 核心功能

- **实时语音补全**：捕获患者语音输入，基于上下文预测并补全完整表达。
- **图片转述**：对图片内容进行描述与解释，辅助患者理解或表达。
- **语音合成反馈**：将补全或转述结果通过语音播报，降低阅读负担。

## 技术栈

| 模块 | 技术 |
|------|------|
| 语音识别 | Whisper |
| 语言模型 | GPT-4o-mini |
| 语音合成 | Edge TTS |
| 后端框架 | FastAPI |
| 前端应用 | Flutter |
| 模型部署 | Hugging Face Spaces |

## 项目结构

```
Project Echo/
├── backend/              # FastAPI 后端服务
│   ├── main.py           # 核心接口：语音补全、图片转述
│   ├── requirements.txt
│   ├── Dockerfile        # Hugging Face Spaces 部署镜像
│   └── README.md
├── frontend/echo_app/    # Flutter 移动端应用
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/      # 页面
│   │   ├── services/     # API 请求
│   │   └── widgets/      # 可复用组件
│   ├── pubspec.yaml
│   └── README.md
├── .gitignore
└── README.md
```

## 快速开始

### 1. 启动后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端

```bash
cd frontend/echo_app
flutter pub get
# 修改 lib/services/api_service.dart 中的 baseUrl
flutter run
```

### 3. 部署到 Hugging Face Spaces

将 `backend/` 目录内容上传至 Hugging Face Docker Space，并在 Space Settings 中配置 `OPENAI_API_KEY`。

## 我的角色

项目发起人及核心后端开发，负责整体技术方案设计、后端服务搭建及模型接口集成。
