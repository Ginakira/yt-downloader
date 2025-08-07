#!/usr/bin/env python3
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Youtube Downloader")
        self.root.geometry("800x600")

        # 创建界面
        self.create_widgets()

        # 消息队列用于线程通信
        self.queue = queue.Queue()

    def create_widgets(self):
        # URL 输入
        tk.Label(self.root, text="YouTube 视频链接:").pack(pady=10)
        self.url_entry = tk.Entry(self.root, width=60)
        self.url_entry.pack(pady=5)

        # 下载目录选择
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10)

        tk.Label(frame1, text="下载目录:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.path_label = tk.Label(frame1, textvariable=self.path_var, width=40, relief="sunken")
        self.path_label.pack(side=tk.LEFT, padx=5)

        tk.Button(frame1, text="选择目录", command=self.select_directory).pack(side=tk.LEFT)

        # 下载选项
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10)

        self.download_option = tk.StringVar(value="video")
        tk.Radiobutton(frame2, text="下载视频", variable=self.download_option, value="video",
                       command=self.on_option_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame2, text="下载封面", variable=self.download_option, value="thumbnail",
                       command=self.on_option_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame2, text="下载字幕", variable=self.download_option, value="subtitle",
                       command=self.on_option_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame2, text="下载全部", variable=self.download_option, value="all",
                       command=self.on_option_change).pack(side=tk.LEFT, padx=10)

        # 字幕语言选择框（默认隐藏）
        self.subtitle_frame = tk.Frame(self.root)

        tk.Label(self.subtitle_frame, text="字幕语言（用逗号分隔，如: zh,en,ko）:").pack(side=tk.LEFT)
        self.subtitle_langs = tk.Entry(self.subtitle_frame, width=30)
        self.subtitle_langs.insert(0, "ko")  # 默认韩文
        self.subtitle_langs.pack(side=tk.LEFT, padx=5)

        # 字幕选项
        self.auto_subtitle_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.subtitle_frame, text="包含自动生成字幕", variable=self.auto_subtitle_var).pack(side=tk.LEFT,
                                                                                                           padx=5)

        # 初始化显示状态
        self.on_option_change()

        # 下载按钮
        self.download_btn = tk.Button(self.root, text="开始下载", command=self.start_download)
        self.download_btn.pack(pady=20)

        # 进度显示
        self.progress_text = tk.Text(self.root, height=10, width=70)
        self.progress_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(self.progress_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.progress_text.yview)

    def on_option_change(self):
        """当下载选项改变时，显示或隐藏字幕语言输入框"""
        option = self.download_option.get()
        if option in ["subtitle", "all"]:
            self.subtitle_frame.pack(pady=10, after=self.root.winfo_children()[2])
        else:
            self.subtitle_frame.pack_forget()

    def get_binary_paths(self):
        """获取 yt-dlp 和 ffmpeg 的路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            bundle_dir = sys._MEIPASS
            ytdlp_path = os.path.join(bundle_dir, 'yt-dlp')
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
        else:
            # 开发环境
            ytdlp_path = 'yt-dlp'
            ffmpeg_path = 'ffmpeg'

        return ytdlp_path, ffmpeg_path

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)

    def append_text(self, text):
        self.progress_text.insert(tk.END, text + "\n")
        self.progress_text.see(tk.END)
        self.root.update()

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入 YouTube 视频链接")
            return

        self.download_btn.config(state="disabled", text="下载中...")
        self.progress_text.delete(1.0, tk.END)

        # 在新线程中执行下载
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def download_video(self, url):
        try:
            ytdlp_path, ffmpeg_path = self.get_binary_paths()

            download_path = self.path_var.get()
            option = self.download_option.get()

            self.append_text(f"开始下载: {url}")
            self.append_text(f"保存路径: {download_path}")
            self.append_text(f"下载选项: {option}")
            self.append_text("-" * 50)

            success = True

            if option == "video":
                success &= self.download_video_file(ytdlp_path, ffmpeg_path, url, download_path)
            elif option == "thumbnail":
                success &= self.download_thumbnail_file(ytdlp_path, ffmpeg_path, url, download_path)
            elif option == "subtitle":
                success &= self.download_subtitle_file(ytdlp_path, ffmpeg_path, url, download_path)
            elif option == "all":
                success &= self.download_video_file(ytdlp_path, ffmpeg_path, url, download_path)
                success &= self.download_thumbnail_file(ytdlp_path, ffmpeg_path, url, download_path)
                success &= self.download_subtitle_file(ytdlp_path, ffmpeg_path, url, download_path)

            if success:
                self.append_text("-" * 50)
                self.append_text("✅ 下载完成！")
                messagebox.showinfo("成功", "下载完成！")
            else:
                self.append_text("❌ 下载失败")
                messagebox.showerror("错误", "下载过程中出现错误")

        except Exception as e:
            self.append_text(f"错误: {str(e)}")
            messagebox.showerror("错误", f"发生错误: {str(e)}")

        finally:
            self.download_btn.config(state="normal", text="开始下载")

    def download_video_file(self, ytdlp_path, ffmpeg_path, url, download_path):
        try:
            self.append_text("正在下载视频...")

            cmd = [
                ytdlp_path,
                "-f", "mp4",
                "--ffmpeg-location", ffmpeg_path,
                "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                url
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 实时显示输出
            for line in process.stdout:
                self.append_text(line.strip())

            process.wait()

            if process.returncode == 0:
                self.append_text("✅ 视频下载完成")
                return True
            else:
                self.append_text("❌ 视频下载失败")
                return False

        except Exception as e:
            self.append_text(f"视频下载错误: {str(e)}")
            return False

    def download_thumbnail_file(self, ytdlp_path, ffmpeg_path, url, download_path):
        try:
            self.append_text("正在下载封面...")

            cmd = [
                ytdlp_path,
                "--write-thumbnail",
                "--convert-thumbnails",
                "jpg",
                "--skip-download",
                "--ffmpeg-location", ffmpeg_path,
                "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                url
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 实时显示输出
            for line in process.stdout:
                self.append_text(line.strip())

            process.wait()

            if process.returncode == 0:
                self.append_text("✅ 封面下载完成")
                return True
            else:
                self.append_text("❌ 封面下载失败")
                return False

        except Exception as e:
            self.append_text(f"封面下载错误: {str(e)}")
            return False

    def download_subtitle_file(self, ytdlp_path, ffmpeg_path, url, download_path):
        try:
            self.append_text("正在下载字幕...")

            # 获取字幕语言设置
            langs = self.subtitle_langs.get().strip()
            if not langs:
                langs = "all"  # 如果没有指定，下载所有语言

            # 构建命令
            cmd = [
                ytdlp_path,
                "--sub-langs", langs,
                "--sub-format", "srt",
                "--write-subs",
                "--skip-download",
                "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                url
            ]

            # 如果选择了包含自动生成字幕
            if self.auto_subtitle_var.get():
                cmd.insert(5, "--write-auto-subs")  # 在 --skip-download 之前插入

            self.append_text(f"字幕语言: {langs}")
            self.append_text(f"包含自动生成字幕: {'是' if self.auto_subtitle_var.get() else '否'}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 实时显示输出
            for line in process.stdout:
                self.append_text(line.strip())

            process.wait()

            if process.returncode == 0:
                self.append_text("✅ 字幕下载完成")
                return True
            else:
                self.append_text("❌ 字幕下载失败（可能没有可用字幕）")
                return False

        except Exception as e:
            self.append_text(f"字幕下载错误: {str(e)}")
            return False


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()