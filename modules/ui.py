import tkinter as tk
from tkinter import ttk, font

class UIManager:
    def __init__(self):
        # 定义颜色方案
        self.colors = {
            "bg": "#f0f0f0",
            "highlight": "#3498db", 
            "text": "#2c3e50",
            "good": "#2ecc71",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "panel_bg": "#ffffff",
            "button": "#3498db",
            "button_text": "#ffffff",
        }
        
        # 创建字体
        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_font = font.Font(family="Arial", size=10)
        
        # 图标映射
        self.icons = {
            "饱腹": "🍔", "口渴": "💧", "如厕": "🚽",
            "肥胖指数": "⚖️", "心脏健康度": "🩷",
            "社交": "👥", "情绪": "😊", "成就感": "🏆",
            "情商": "🧠", "安全感": "💖",
            "肌肉强度": "💪", "敏捷": "🏃",
            "抗击打能力": "🏠", "魅力": "✨", "道德": "⚖️"
        }
    
    def setup_styles(self, style):
        """设置UI样式"""
        style.theme_use('clam')
        
        # 应用颜色样式
        style.configure('TFrame', background=self.colors["bg"])
        style.configure('TLabelframe', background=self.colors["bg"], foreground=self.colors["text"])
        style.configure('TLabelframe.Label', background=self.colors["bg"], 
                       foreground=self.colors["text"], font=('Arial', 11, 'bold'))
        style.configure('TLabel', background=self.colors["bg"], foreground=self.colors["text"])
        
        # 自定义按钮样式
        style.configure('TButton', background=self.colors["button"], 
                       foreground=self.colors["button_text"], font=('Arial', 10))
        style.map('TButton', 
                 background=[('active', '#2980b9'), ('pressed', '#1f618d')],
                 foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # 自定义进度条样式
        style.configure("health.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                       background=self.colors["good"], borderwidth=0, thickness=20)
        style.configure("warning.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                       background=self.colors["warning"], borderwidth=0, thickness=20)
        style.configure("danger.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                       background=self.colors["danger"], borderwidth=0, thickness=20)
    
    def get_progress_style(self, value):
        """根据值返回对应的进度条样式"""
        if value > 70:
            return "health.Horizontal.TProgressbar"
        elif value > 30:
            return "warning.Horizontal.TProgressbar"
        else:
            return "danger.Horizontal.TProgressbar" 