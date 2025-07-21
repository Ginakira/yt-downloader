#!/bin/bash

echo "正在下载依赖文件..."

# 检测系统架构
ARCH=$(uname -m)
echo "检测到系统架构: $ARCH"

# 下载 yt-dlp
if [ ! -f "yt-dlp" ]; then
    echo "下载 yt-dlp..."
    if [ "$ARCH" = "x86_64" ]; then
        echo "Intel Mac 检测到，下载 legacy 版本..."
        curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos_legacy -o yt-dlp
    else
        echo "Apple Silicon Mac 检测到，下载标准版本..."
        curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos -o yt-dlp
    fi
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