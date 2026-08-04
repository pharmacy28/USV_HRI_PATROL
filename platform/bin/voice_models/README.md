# 本地 Whisper 模型

本目录是本地语音识别模型缓存：

- `base.pt`：Whisper `base`，当前默认模型，识别质量较好；
- `tiny.pt`：Whisper `tiny`，启动和推理更快，但中文识别质量较低。

程序通过 `run_vrx.sh --voice` 将本目录传给 `whisper.load_model(..., download_root=...)`。如果文件缺失，Whisper 会自动下载；模型权重不应提交到 Git，首次部署时单独准备即可。
