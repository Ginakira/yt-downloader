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
        self.root.geometry("600x400")
        
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
        tk.Radiobutton(frame2, text="下载视频", variable=self.download_option, value="video").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame2, text="下载封面", variable=self.download_option, value="thumbnail").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame2, text="下载视频和封面", variable=self.download_option, value="both").pack(side=tk.LEFT, padx=10)
        
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
            
            if option == "video" or option == "both":
                success &= self.download_video_file(ytdlp_path, ffmpeg_path, url, download_path)
            
            if option == "thumbnail" or option == "both":
                success &= self.download_thumbnail_file(ytdlp_path, ffmpeg_path, url, download_path)
            
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
                "-t", "mp4",
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

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()