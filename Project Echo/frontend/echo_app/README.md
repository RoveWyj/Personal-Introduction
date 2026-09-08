# Project Echo - Flutter 客户端

为脑卒中后失语症患者设计的移动端界面，提供语音补全与图片转述入口。

## 前置要求

- 已安装 [Flutter](https://docs.flutter.dev/get-started/install) SDK
- 已配置 Android / iOS / Web 模拟器或真机

## 首次运行

1. 进入项目目录：

   ```bash
   cd frontend/echo_app
   ```

2. 获取依赖：

   ```bash
   flutter pub get
   ```

3. 修改后端地址：

   打开 `lib/services/api_service.dart`，将 `baseUrl` 替换为你的后端地址：

   ```dart
   const String baseUrl = 'https://your-hf-space-url.hf.space';
   ```

   本地开发使用 Android 模拟器时，可设置为 `http://10.0.2.2:8000`。

4. 运行应用：

   ```bash
   flutter run
   ```

## 功能说明

- **语音补全**：按住录音按钮说话，松开后自动上传并返回补全后的句子及语音播报。
- **图片转述**：从相册选择或拍照上传，自动获取图片描述及语音播报。

## 依赖

- `record`：录音
- `image_picker`：相册 / 相机选图
- `audioplayers`：播放后端返回的语音
- `http`：与后端 API 通信
