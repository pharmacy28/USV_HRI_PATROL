# Whisper model cache

Whisper 权重不提交到 Git：`base.pt` 约 145 MB，超过 GitHub 的单文件限制。使用 `./run_vrx.sh --voice` 时，Whisper 会把所选模型自动下载到本目录；也可通过 `--voice-model-dir PATH` 指定已有缓存。
