import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

class HomePage:
    def __init__(self, root, on_enter_callback=None):
        self.root = root
        self.root.title("地球Online看板 - 欢迎")
        self.on_enter_callback = on_enter_callback
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="🌍 地球Online看板",
            font=("Microsoft YaHei", 28, "bold"),
            bootstyle="info"
        )
        title_label.pack()
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        enter_btn = ttk.Button(
            button_frame,
            text="进入看板",
            bootstyle="info",
            width=20,
            command=self.enter_kanban
        )
        enter_btn.pack(pady=10)
        
        manual_btn = ttk.Button(
            button_frame,
            text="用户手册",
            bootstyle="warning",
            width=20,
            command=self.show_manual
        )
        manual_btn.pack(pady=10)
        
        # 用户手册内容区域
        self.manual_frame = ttk.LabelFrame(
            self.main_frame,
            text="用户手册",
            padding="20",
            bootstyle="info"
        )
        
        self.manual_text = tk.Text(
            self.manual_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10),
            height=15,
            width=50
        )
        self.manual_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加手册内容
        self.manual_content = """
【基本功能】
• 属性监控：实时显示15种生理、情感和能力属性的状态
• 数据同步：支持与Apple Watch等智能设备同步健康数据
• 智能分析：AI分析当前状态并提供改善建议

【按钮功能说明】
• 保存数据：点击保存按钮将当前所有属性状态保存
• 设置：可以自定义玩家名称、初始属性值和变化速率
• 事件输入：记录生活事件，系统会预测对属性的影响
• 数据分析：查看属性变化趋势和预测
• 阈值提醒：当属性达到设定阈值时自动提醒
• 定时任务：支持设置定时提醒和检查点

【数据安全】
• 所有数据本地存储，确保隐私安全
• 定期自动备份，防止数据丢失
"""
        self.manual_text.insert("1.0", self.manual_content)
        self.manual_text.configure(state="disabled")
        
        # 初始隐藏手册
        # self.manual_frame.pack_forget()
        self.show_manual()
        
        # 设置窗口大小和位置
        self.center_window(800, 700)
        
    def center_window(self, width, height):
        """将窗口居中显示"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def enter_kanban(self):
        """进入看板页面"""
        self.main_frame.destroy()  # 只销毁主框架
        if self.on_enter_callback:
            self.on_enter_callback()
        
    def show_manual(self):
        """显示/隐藏用户手册"""
        if self.manual_frame.winfo_ismapped():
            self.manual_frame.pack_forget()
        else:
            self.manual_frame.pack(fill=tk.BOTH, expand=True, pady=20)
            
    def hide(self):
        """隐藏主页"""
        self.main_frame.pack_forget()
        
    def show(self):
        """显示主页"""
        self.main_frame.pack(fill=tk.BOTH, expand=True) 