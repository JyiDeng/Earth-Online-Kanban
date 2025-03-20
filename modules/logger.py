import os
from datetime import datetime
import tkinter as tk

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
        # 确保data目录存在
        os.makedirs("data", exist_ok=True)
        
        # 创建或打开日志文件
        self.log_file_path = os.path.join("data", "system_log.txt")
        self.log_file = open(self.log_file_path, "a", encoding="utf-8")
        
        # 写入启动分隔符
        start_message = f"\n{'-'*50}\n系统启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'-'*50}\n"
        self.log_file.write(start_message)
        self.log_file.flush()

    def write(self, string):
        self.buffer += string
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        
        # 同时写入日志文件
        self.log_file.write(string)
        self.log_file.flush()

    def flush(self):
        self.log_file.flush()
        
    def close(self):
        """关闭日志文件"""
        if self.log_file:
            self.log_file.close() 