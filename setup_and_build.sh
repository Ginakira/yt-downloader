#!/bin/bash

echo "正在下载依赖文件..."

# 下载 yt-dlp
if [ ! -f "yt-dlp" ]; then
    echo "下载 yt-dlp..."
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos -o yt-dlp
    chmod +x yt-dlp
fi

# 下载 ffmpeg
if [ ! -f "ffmpeg" ]; then
    echo "下载 ffmpeg..."
    curl -L https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip -o ffmpeg.zip
    unzip ffmpeg.zip
    chmod +x ffmpeg
    rm ffmpeg.zip
fi

# 验证架构
echo "验证文件架构:"
echo "yt-dlp:"
file yt-dlp
echo "ffmpeg:"
file ffmpeg

# 安装 PyInstaller (如果没有)
pip install pyinstaller

# 开始打包
echo "开始打包..."
python build.py

echo "打包完成! 生成的应用位于 dist/ 目录"