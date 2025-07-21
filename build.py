import PyInstaller.__main__
import os
import platform

# 确保必要文件存在
if not os.path.exists('yt-dlp'):
    print("错误: 请先下载 yt-dlp 二进制文件")
    exit(1)

if not os.path.exists('ffmpeg'):
    print("错误: 请先下载 ffmpeg 二进制文件")
    exit(1)

# 检查当前架构
current_arch = platform.machine()
print(f"当前架构: {current_arch}")

# 打包参数
build_args = [
    'youtube_downloader.py',
    '--onefile',
    '--windowed',
    '--add-binary=yt-dlp:.',
    '--add-binary=ffmpeg:.',
    '--name=yt-downloader',
    '--clean',
    '--noupx',
    # 添加通用二进制支持
    # '--target-architecture=universal2',
    # 兼容性设置
    # '--osx-bundle-identifier=com.pmrfansub.youtubedownloader',
]

# 如果有图标文件
if os.path.exists('app.icns'):
    build_args.append('--icon=app.icns')

PyInstaller.__main__.run(build_args)