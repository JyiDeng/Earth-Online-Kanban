import csv
import tkinter as tk
from tkinter import font, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import time
import math
import random
from datetime import datetime
import os
import pandas as pd
import pickle
import sys
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.stats import linregress
import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from modules.analytics import AnalyticsManager
from modules.home_page import HomePage

# 重定向stdout到窗口显示和文件
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

class BackgroundMixin:
    """背景图片混入类"""
    def set_background(self, window):
        try:
            # 加载背景图片
            image = Image.open("pic/bg.jpg")
            # 获取窗口大小
            window.update()
            window_width = window.winfo_width()
            window_height = window.winfo_height()
            # 调整图片大小以适应窗口
            image = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(image)
            
            # 创建背景标签
            bg_label = ttk.Label(window, image=bg_image)
            bg_label.image = bg_image  # 保持引用
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # 将背景标签放到最底层
            bg_label.lower()
            
            # 设置所有框架的透明度
            def set_frame_transparency(widget):
                if isinstance(widget, (ttk.Frame, ttk.Labelframe)):
                    widget.configure(style='Transparent.TFrame')
                for child in widget.winfo_children():
                    set_frame_transparency(child)
            
            # 创建透明样式
            style = ttk.Style()
            style.configure('Transparent.TFrame', background='#ffffff', opacity=0.85)
            style.configure('Transparent.TLabelframe', background='#ffffff', opacity=0.85)
            
            # 应用透明样式到所有框架
            set_frame_transparency(window)
            
            # 绑定窗口大小变化事件
            def on_resize(event):
                if event.widget == window:
                    # 重新调整背景图片大小
                    new_width = event.width
                    new_height = event.height
                    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    new_bg_image = ImageTk.PhotoImage(resized_image)
                    bg_label.configure(image=new_bg_image)
                    bg_label.image = new_bg_image
            
            window.bind("<Configure>", on_resize)
            
        except Exception as e:
            print(f"设置背景图片时出错: {e}")

    def center_window(self, window, width=None, height=None):
        """将窗口居中显示"""
        # 如果没有指定宽高，获取当前窗口的宽高
        if width is None or height is None:
            window.update()
            width = window.winfo_width()
            height = window.winfo_height()
        
        # 获取屏幕宽高
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")

class AlertManager(BackgroundMixin):
    def __init__(self):
        self.pending_alerts = []
        self.alert_window = None
        self.alert_text = None
    
    def show_alert(self, title, message):
        if self.alert_window and self.alert_window.winfo_exists():
            # 如果已有警告窗口，则追加消息
            self.alert_text.insert(tk.END, "\n\n" + message)
            self.alert_window.lift()  # 将窗口提到前面
        else:
            # 创建新的警告窗口
            self.alert_window = ttk.Toplevel()
            self.alert_window.title(title)
            
            # 设置背景图片
            self.set_background(self.alert_window)
            
            # 居中显示窗口
            self.center_window(self.alert_window, 400, 500)
            
            # 创建可滚动的文本框
            frame = ttk.Frame(self.alert_window, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            self.alert_text = tk.Text(frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
            self.alert_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            self.alert_text.insert(tk.END, message)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.alert_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.alert_text.configure(yscrollcommand=scrollbar.set)
            
            # 确定按钮
            ttk.Button(frame, text="确定", command=self.alert_window.destroy).pack(pady=(0, 5))
            
            # 居中显示窗口
            self.center_window(self.alert_window, 400, 500)

class EarthOnlinePanel(BackgroundMixin):
    def __init__(self, root):
        # 确保outputs目录存在
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("data", exist_ok=True)  # 确保data目录存在
        
        self.root = root
        
        # 设置背景图片
        self.set_background(self.root)
        
        # 创建字体
        self.title_font = font.Font(family="Microsoft YaHei", size=14, weight="bold")
        self.subtitle_font = font.Font(family="Microsoft YaHei", size=12, weight="bold")
        self.text_font = font.Font(family="Microsoft YaHei", size=10)
        
        # 初始化数据
        self.attributes = {}
        self.last_update_time = time.time()
        self.model = None
        
        # 历史数据记录
        self.history_data = {}
        self.last_save_time = time.time()
        
        # 更新间隔设置（秒）
        self.update_interval = 30
        self.history_save_interval = 300  # 每5分钟保存历史数据
        
        # 初始化阈值设置
        self.thresholds = {}
        self.scheduled_times = {}
        self.load_thresholds()
        
        # 添加API配置
        self.api_key = ""
        self.api_model = ""
        self.available_models = []
        self.prompts = {}
        self.load_api_config()
        
        # 添加阈值提醒状态记录
        self.threshold_alerts = {}  # 用于记录阈值提醒状态
        self.last_alert_time = {}  # 用于记录上次提醒时间
        
        # 添加健康数据相关属性
        self.health_data = {}
        self.last_health_sync = None
        self.health_sync_interval = 300  # 5分钟同步一次
        
        # 添加警告管理器
        self.alert_manager = AlertManager()
        
        # 添加分析管理器
        self.analytics_manager = None
        
        # 创建UI元素
        self.create_ui()
        
        # 加载模拟数据
        self.load_mock_data()
        
        # 加载历史数据
        self.load_history_data()
        
        # 初始化分析管理器
        self.analytics_manager = AnalyticsManager(self.history_data)
        
        # 更新阈值提醒文本
        self.update_threshold_text()
        
        # 启动定时更新
        self.update_panel()
        
        # 加载模型（如果存在）
        self.load_model()
        
        # 在关闭窗口时保存数据
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_model(self):
        """加载已训练的模型"""
        model_path = "model/event_model.pkl"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                # messagebox.showinfo("模型加载", "已成功加载训练模型")
            except Exception as e:
                messagebox.showerror("模型加载错误", f"加载模型时出错: {e}")
        else:
            messagebox.showinfo("模型加载", "未找到已训练的模型，请点击'训练模型'按钮")
    
    def save_model(self, model):
        """保存训练好的模型"""
        model_path = "model/event_model.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            messagebox.showinfo("模型保存", "模型已成功保存")
        except Exception as e:
            messagebox.showerror("模型保存错误", f"保存模型时出错: {e}")
    
    def get_progress_style(self, value):
        """根据值返回对应的样式"""
        if value > 70:
            return "success-striped"
        elif value > 30:
            return "warning-striped"
        else:
            return "danger-striped"
    
    def create_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部信息栏
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题
        title_label = ttk.Label(self.top_frame, text="地球 Online", font=('Microsoft YaHei', 18, 'bold'), bootstyle="info")
        title_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(self.top_frame, text="当前时间: ", font=self.text_font)
        self.time_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.name_label = ttk.Label(self.top_frame, text="玩家名称: ", font=self.text_font)
        self.name_label.pack(side=tk.RIGHT)
        
        # 创建类别框架
        self.categories_frame = ttk.Frame(self.main_frame)
        self.categories_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个类别的列
        self.categories = {
            "生理需求": ["饱腹", "口渴", "如厕", "瘦身指数", "心脏健康度"],
            "社会需求": ["社交", "情绪", "成就感", "情商", "安全感"],
            "能力属性": ["肌肉强度", "敏捷", "抗击打能力", "魅力", "道德"]
        }
        
        # 图标映射
        self.icons = {
            "饱腹": "🍔",
            "口渴": "💧",
            "如厕": "🚽",
            "瘦身指数": "⚖️",
            "心脏健康度": "🩷",
            "社交": "👥",
            "情绪": "😊",
            "成就感": "🏆",
            "情商": "🧠",
            "安全感": "💖",
            "肌肉强度": "💪",
            "敏捷": "🏃",
            "抗击打能力": "🏠",
            "魅力": "✨",
            "道德": "⚖️"
        }
        
        # 创建三列布局
        column_index = 0
        for category, attrs in self.categories.items():
            # 创建类别框架
            category_frame = ttk.Labelframe(self.categories_frame, text=category, padding=15, bootstyle="default")
            category_frame.grid(row=0, column=column_index, padx=8, pady=5, sticky="nsew")
            
            # 为每个属性创建进度条和标签
            for i, attr in enumerate(attrs):
                icon = self.icons.get(attr, "")
                ttk.Label(category_frame, text=f"{icon} {attr}", font=self.text_font).grid(row=i, column=0, sticky=tk.W, pady=6)
                
                # 创建进度条框架
                progress_frame = ttk.Frame(category_frame)
                progress_frame.grid(row=i, column=1, sticky=tk.EW, pady=6, padx=(10, 0))
                
                # 创建进度条
                progress_bar = ttk.Progressbar(progress_frame, length=100, mode="determinate", bootstyle="success-striped")
                progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # 创建数值标签
                value_label = ttk.Label(progress_frame, text="0%", font=self.text_font, width=5)
                value_label.pack(side=tk.RIGHT, padx=(8, 0))
                
                # 存储引用
                self.attributes[attr] = {
                    "progress_bar": progress_bar,
                    "value_label": value_label,
                    "current_value": 0,
                    "max_value": 100,
                    "change_rate": random.uniform(-0.01, 0.01),  # 随机变化率
                    "trend": 0.0  # 趋势斜率
                }
            
            # 设置列权重
            category_frame.columnconfigure(1, weight=1)
            column_index += 1
        
        # 设置列权重
        self.categories_frame.columnconfigure(0, weight=1)
        self.categories_frame.columnconfigure(1, weight=1)
        self.categories_frame.columnconfigure(2, weight=1)
        
        # 创建AI分析和阈值提醒窗口
        self.analysis_frame = ttk.Frame(self.main_frame)
        self.analysis_frame.pack(fill=tk.X, pady=(0, 0))
        
        # AI分析窗口
        self.ai_frame = ttk.Labelframe(self.analysis_frame, text="AI状态分析", bootstyle="info")
        self.ai_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
        
        # 创建按钮框架
        ai_button_frame = ttk.Frame(self.ai_frame)
        ai_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.analyze_ai_button = ttk.Button(ai_button_frame, text="AI分析当前状态", 
                                          command=self.analyze_with_ai, bootstyle="info-outline")
        self.analyze_ai_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 添加放大按钮
        ttk.Button(ai_button_frame, text="放大查看", 
                  command=lambda: self.show_enlarged_window("AI状态分析", self.ai_text.get(1.0, tk.END)),
                  bootstyle="secondary-outline").pack(side=tk.LEFT)
        
        self.ai_text = tk.Text(self.ai_frame, height=8, width=40, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.ai_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # 阈值提醒窗口
        self.threshold_frame = ttk.Labelframe(self.analysis_frame, text="阈值提醒设置", bootstyle="info")
        self.threshold_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建按钮框架
        threshold_button_frame = ttk.Frame(self.threshold_frame)
        threshold_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.threshold_button = ttk.Button(threshold_button_frame, text="设置阈值提醒", 
                                         command=self.setup_thresholds, bootstyle="info-outline")
        self.threshold_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 添加放大按钮
        ttk.Button(threshold_button_frame, text="放大查看", 
                  command=lambda: self.show_enlarged_window("阈值提醒设置", self.threshold_text.get(1.0, tk.END)),
                  bootstyle="secondary-outline").pack(side=tk.LEFT)
        
        self.threshold_text = tk.Text(self.threshold_frame, height=8, width=40, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.threshold_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # 创建底部控制栏
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 添加分隔线
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        self.setup_button = ttk.Button(self.control_frame, text="设置", command=self.setup, bootstyle="primary")
        self.setup_button.pack(side=tk.LEFT)
        
        self.reset_button = ttk.Button(self.control_frame, text="重置(下次打开生效)", command=self.reset_data, bootstyle="danger")
        self.reset_button.pack(side=tk.RIGHT)
        
        # 添加事件按钮
        self.event_button = ttk.Button(self.control_frame, text="事件", command=self.open_event_window, bootstyle="success")
        self.event_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加训练模型按钮
        self.train_button = ttk.Button(self.control_frame, text="训练模型(事件对应属性增减)", command=self.train_and_save_model, bootstyle="info")
        self.train_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加分析趋势按钮
        self.analyze_button = ttk.Button(self.control_frame, text="分析趋势", command=self.analyze_trends, bootstyle="warning")
        self.analyze_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加健康数据同步按钮
        self.sync_health_button = ttk.Button(self.control_frame, text="同步健康数据", command=self.sync_health_data, bootstyle="secondary")
        self.sync_health_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加日志窗口
        self.log_frame = ttk.Labelframe(self.main_frame, text="系统日志", bootstyle="default")
        self.log_frame.pack(fill=tk.X, pady=(15, 0), after=separator)
        
        self.log_text = tk.Text(self.log_frame, height=5, width=50, wrap=tk.WORD, font=('Microsoft YaHei', 9))
        self.log_text.pack(fill=tk.X, expand=True, pady=5, padx=5)
        
        # 重定向标准输出到日志窗口
        self.stdout_redirector = StdoutRedirector(self.log_text)
        sys.stdout = self.stdout_redirector
        
        # 添加分析按钮
        self.analyze_frame = ttk.Frame(self.control_frame)
        self.analyze_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        self.trend_button = ttk.Button(self.analyze_frame, text="趋势图", command=self.show_trend_charts, bootstyle="info")
        self.trend_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.weekly_report_button = ttk.Button(self.analyze_frame, text="周报", command=self.generate_weekly_report, bootstyle="success")
        self.weekly_report_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.monthly_report_button = ttk.Button(self.analyze_frame, text="月报", command=self.generate_monthly_report, bootstyle="warning")
        self.monthly_report_button.pack(side=tk.LEFT)
    
    def train_and_save_model(self):
        """训练模型并保存"""
        try:
            model = self.train_model()
            self.model = model
            self.save_model(model)
            print("模型训练和保存成功")
        except Exception as e:
            messagebox.showerror("训练错误", f"训练模型时出错: {e}")
            print(f"训练模型时出错: {e}")
    
    def load_mock_data(self):
        """加载模拟数据或创建默认数据"""
        try:
            if os.path.exists("data/player_data.json"):
                with open("data/player_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                self.player_name = data.get("player_name", "未命名玩家")
                for attr, values in data.get("attributes", {}).items():
                    if attr in self.attributes:
                        self.attributes[attr]["current_value"] = values.get("value", 50)
                        self.attributes[attr]["change_rate"] = values.get("change_rate", random.uniform(-0.01, 0.01))
            else:
                self.create_mock_data()
        except Exception as e:
            print(f"加载数据出错: {e}")
            self.create_mock_data()
        
        self.name_label.config(text=f"玩家名称: {self.player_name}")
    
    def create_mock_data(self):
        """创建默认的模拟数据"""
        self.player_name = "测试玩家"
        
        for attr in self.attributes:
            # if attr == "瘦身指数":
            #     self.attributes[attr]["current_value"] = random.randint(30, 70)
            #     self.attributes[attr]["change_rate"] = random.uniform(0.01, 0.02)  # 确保为正值
            # else:
            self.attributes[attr]["current_value"] = random.randint(30, 70)
            self.attributes[attr]["change_rate"] = random.uniform(-0.02, 0.02)
    
    def save_data(self):
        """保存当前数据"""
        data = {
            "player_name": self.player_name,
            "attributes": {},
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for attr, info in self.attributes.items():
            data["attributes"][attr] = {
                "value": info["current_value"],
                "change_rate": info["change_rate"],
                "trend": info.get("trend", 0.0)
            }
        
        try:
            with open("data/player_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"保存数据出错: {e}")
    
    def reset_data(self):
        """重置所有属性"""
        for attr in self.attributes:
            self.attributes[attr]["current_value"] = 50
            self.attributes[attr]["change_rate"] = random.uniform(-0.01, 0.01)
    
    def setup(self):
        """打开设置窗口"""
        setup_window = ttk.Toplevel(self.root)
        setup_window.title("设置")
        
        # 设置背景图片
        self.set_background(setup_window)
        
        # 居中显示窗口，增加高度到1000
        self.center_window(setup_window, 600, 900)
        
        setup_window.grab_set()
        
        # 创建主滚动框架
        main_canvas = tk.Canvas(setup_window)
        main_scrollbar = ttk.Scrollbar(setup_window, orient="vertical", command=main_canvas.yview)
        
        # 创建设置界面
        setup_frame = ttk.Frame(main_canvas, padding=15)
        
        # 配置滚动区域
        main_canvas.create_window((0, 0), window=setup_frame, anchor="nw", width=580)  # 设置固定宽度
        setup_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # 布局主滚动框架
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 主题设置
        theme_frame = ttk.Labelframe(setup_frame, text="主题设置", padding=10, bootstyle="info")
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 主题选择
        theme_var = tk.StringVar(value=self.root.style.theme.name)
        available_themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 
                          'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly', 'superhero', 
                          'solar', 'cyborg', 'vapor']
        
        ttk.Label(theme_frame, text="界面主题:", font=self.text_font).pack(side=tk.LEFT)
        theme_combobox = ttk.Combobox(theme_frame, textvariable=theme_var, values=available_themes, 
                                    font=self.text_font, width=20, state="readonly")
        theme_combobox.pack(side=tk.LEFT, padx=5)
        
        # API设置
        api_frame = ttk.Labelframe(setup_frame, text="API设置", padding=10, bootstyle="info")
        api_frame.pack(fill=tk.X, pady=(0, 15))
        
        # API来源选择
        source_frame = ttk.Frame(api_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="API来源:", font=self.text_font).pack(side=tk.LEFT)
        source_var = tk.StringVar(value="siliconflow")
        sources = ["siliconflow", "huggingface"]
        source_combobox = ttk.Combobox(source_frame, textvariable=source_var, values=sources, 
                                      font=self.text_font, width=30, state="readonly")
        source_combobox.pack(side=tk.LEFT, padx=5)
        
        # 模型选择
        model_frame = ttk.Frame(api_frame)
        model_frame.pack(fill=tk.X, pady=5)
        ttk.Label(model_frame, text="模型:", font=self.text_font).pack(side=tk.LEFT)
        model_var = tk.StringVar(value=self.api_model)
        model_combobox = ttk.Combobox(model_frame, textvariable=model_var, values=self.available_models, 
                                     font=self.text_font, width=30)
        model_combobox.pack(side=tk.LEFT, padx=5)
        
        # API Key输入
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API Key:", font=self.text_font).pack(side=tk.LEFT)
        api_key_entry = ttk.Entry(key_frame, width=40, font=self.text_font)
        api_key_entry.pack(side=tk.LEFT, padx=5)
        api_key_entry.insert(0, self.api_key)
        
        # 原有的设置内容
        title_label = ttk.Label(setup_frame, text="玩家设置", font=('Microsoft YaHei', 16, 'bold'), bootstyle="info")
        title_label.pack(fill=tk.X, pady=(0, 15))
        
        # 玩家名称设置
        name_frame = ttk.Frame(setup_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(name_frame, text="玩家名称:", font=self.subtitle_font).pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, width=30, font=self.text_font)
        name_entry.pack(side=tk.LEFT, padx=5)
        name_entry.insert(0, self.player_name)
        
        # 添加分隔线
        ttk.Separator(setup_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 属性设置
        ttk.Label(setup_frame, text="属性设置:", font=self.subtitle_font).pack(anchor=tk.W, pady=(5, 10))
        
        # 创建滚动框架
        scroll_frame = ttk.Frame(setup_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加属性设置
        for category, attrs in self.categories.items():
            # 添加类别标题
            ttk.Label(scrollable_frame, text=category, font=self.subtitle_font, bootstyle="info").pack(
                anchor=tk.W, pady=(10, 5))
            
            for attr in attrs:
                attr_frame = ttk.Frame(scrollable_frame)
                attr_frame.pack(fill=tk.X, pady=2)
                
                icon = self.icons.get(attr, "")
                ttk.Label(attr_frame, text=f"{icon} {attr}", font=self.text_font).pack(side=tk.LEFT)
                
                # 变化率设置
                ttk.Label(attr_frame, text="变化率:", font=self.text_font).pack(side=tk.LEFT, padx=(10, 0))
                rate_entry = ttk.Entry(attr_frame, width=8)
                rate_entry.pack(side=tk.LEFT, padx=5)
                rate_entry.insert(0, f"{self.attributes[attr]['change_rate']:.4f}")
        
        # 布局滚动框架
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 保存按钮
        def save_settings():
            # 保存主题设置
            new_theme = theme_var.get()
            if new_theme != self.root.style.theme.name:
                self.root.style.theme_use(new_theme)
                # 保存主题设置到配置文件
                try:
                    with open("data/theme_config.json", "w", encoding="utf-8") as f:
                        json.dump({"theme": new_theme}, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"保存主题设置时出错: {e}")
            
            # 保存API设置
            self.api_key = api_key_entry.get().strip()
            self.api_model = model_var.get()
            self.save_api_config()
            
            # 更新玩家名称
            self.player_name = name_entry.get()
            self.name_label.config(text=f"玩家名称: {self.player_name}")
            
            # 保存数据
            self.save_data()
            
            # 关闭窗口
            setup_window.destroy()
        
        button_frame = ttk.Frame(setup_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="确认", command=save_settings, bootstyle="success").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=setup_window.destroy, bootstyle="danger").pack(side=tk.LEFT)
        
        # 解绑鼠标滚轮事件（窗口关闭时）
        def on_window_close():
            main_canvas.unbind_all("<MouseWheel>")
            setup_window.destroy()
        
        setup_window.protocol("WM_DELETE_WINDOW", on_window_close)
    
    def train_model(self):
        """训练机器学习模型以预测事件影响值"""
        # 加载数据
        data = pd.read_csv('model/event_data.csv')
        
        # 特征和目标
        X = pd.get_dummies(data[['event_name', 'attribute']])
        y = data['impact_value']
        
        # 拆分数据集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        print(f"模型训练完成，特征数量: {len(model.feature_names_in_)}")
        return model

    def predict_impact(self, event_name, attribute):
        """预测事件对属性的影响值"""
        if self.model is None:
            messagebox.showwarning("模型未加载", "请先训练模型")
            print("模型未加载，无法预测")
            return 0
        
        try:
            # 创建输入数据
            input_data = pd.DataFrame([[event_name, attribute]], columns=['event_name', 'attribute'])
            input_data = pd.get_dummies(input_data)
            
            # 确保输入数据与训练数据的特征一致
            for col in self.model.feature_names_in_:
                if col not in input_data:
                    input_data[col] = 0
            
            # 重新排序列，确保与训练数据一致
            input_data = input_data.reindex(columns=self.model.feature_names_in_, fill_value=0)
            
            # 预测
            impact_value = self.model.predict(input_data)[0]
            print(f"预测 '{event_name}' 对 '{attribute}' 的影响值: {impact_value:.2f}")
            return impact_value
        except Exception as e:
            print(f"预测过程中出错: {e}")
            messagebox.showerror("预测错误", f"预测过程中出错: {e}")
            return 0

    def record_event_data(self, event_name, attribute, impact_value):
        """记录事件数据到CSV文件"""
        try:
            file_path = 'model/event_data.csv'
            file_exists = os.path.exists(file_path)
            
            # 确保model目录存在
            os.makedirs("model", exist_ok=True)
            
            # 如果文件不存在，创建新文件并写入表头
            if not file_exists:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['event_name', 'attribute', 'impact_value'])
            
            # 追加新数据
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([event_name, attribute, impact_value])
            
            print(f"事件数据已记录: {event_name}, {attribute}, {impact_value}")
            
            # 立即重新训练模型
            self.train_and_save_model()
            
        except Exception as e:
            print(f"记录事件数据时出错: {e}")

    def open_event_window(self):
        """打开事件输入窗口"""
        event_window = ttk.Toplevel(self.root)
        event_window.title("事件输入")
        
        # 设置背景图片
        self.set_background(event_window)
        
        # 居中显示窗口
        self.center_window(event_window, 500, 400)
        
        event_window.grab_set()
        
        # 创建事件输入界面
        event_frame = ttk.Frame(event_window, padding=15)
        event_frame.pack(fill=tk.BOTH, expand=True)
        
        # 事件类型标签
        ttk.Label(event_frame, text="事件类型:", font=self.subtitle_font).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 使用下拉菜单选择事件类型
        event_types = ["吃饭", "喝水", "锻炼", "休息", "社交", "学习", "冥想", "工作", 
                      "看电影", "购物", "跑步", "阅读", "音乐会", "演讲", "绘画", "其他"]
        event_type_var = tk.StringVar()
        event_type_combobox = ttk.Combobox(event_frame, textvariable=event_type_var, values=event_types, font=self.text_font, width=28)
        event_type_combobox.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        event_type_combobox.current(0)
        
        # 自定义事件输入框 - 必填
        ttk.Label(event_frame, text="具体事件描述:", font=self.subtitle_font).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        event_name_entry = ttk.Entry(event_frame, width=30, font=self.text_font)
        event_name_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # 事件影响
        ttk.Label(event_frame, text="影响属性:", font=self.subtitle_font).grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        attr_combobox = ttk.Combobox(event_frame, values=list(self.attributes.keys()), font=self.text_font)
        attr_combobox.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        if len(self.attributes) > 0:
            attr_combobox.current(0)
        
        # 预测结果显示
        ttk.Label(event_frame, text="预测影响值:", font=self.subtitle_font).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        impact_label = ttk.Label(event_frame, text="点击预测按钮", font=self.text_font)
        impact_label.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # 检查输入有效性
        def validate_input():
            event_name = event_name_entry.get().strip()
            attr = attr_combobox.get()
            
            if not event_name:
                messagebox.showerror("输入错误", "请输入具体事件描述")
                return False
            
            if not attr:
                messagebox.showerror("输入错误", "请选择一个属性")
                return False
            
            return True
        
        # 预测按钮
        def predict_event_impact():
            if not validate_input():
                return
            
            # 获取事件名称和属性
            event_name = event_name_entry.get().strip()
            attr = attr_combobox.get()
            
            # 预测影响值
            impact_value = self.predict_impact(event_name, attr)
            impact_label.config(text=f"{impact_value:.2f}")
        
        # 创建按钮框架
        button_frame = ttk.Frame(event_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # 预测按钮
        ttk.Button(button_frame, text="预测影响", command=predict_event_impact, bootstyle="info-outline").pack(side=tk.LEFT, padx=5)
        
        # 确认按钮
        def apply_event():
            if not validate_input():
                return
            
            # 获取事件名称和属性
            event_name = event_name_entry.get().strip()
            attr = attr_combobox.get()
            
            try:
                # 使用模型预测影响值
                impact_value = self.predict_impact(event_name, attr)
                
                if attr in self.attributes:
                    self.attributes[attr]["current_value"] += impact_value
                    self.attributes[attr]["current_value"] = max(0, min(100, self.attributes[attr]["current_value"]))
                    print(f"事件 '{event_name}' 已应用，{attr} 预测影响值: {impact_value:.2f}")
                    messagebox.showinfo("事件应用", f"事件 '{event_name}' 已应用，{attr} 变化: {impact_value:.2f}")
                    self.record_event_data(event_name, attr, impact_value)
                    
            except Exception as e:
                print(f"应用事件时出错: {e}")
                messagebox.showerror("应用事件错误", f"应用事件时出错: {e}")
            
            event_window.destroy()
        
        ttk.Button(button_frame, text="应用事件", command=apply_event, bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=event_window.destroy, bootstyle="danger").pack(side=tk.LEFT, padx=5)
    
    def load_history_data(self):
        """加载历史数据"""
        try:
            if os.path.exists("data/history_data.json"):
                with open("data/history_data.json", "r", encoding="utf-8") as f:
                    self.history_data = json.load(f)
                print(f"已加载历史数据记录，共{len(self.history_data.get('timestamps', []))}个时间点")
            else:
                # 初始化历史数据结构
                self.history_data = {
                    "timestamps": [],
                    "attributes": {}
                }
                for attr in self.attributes:
                    self.history_data["attributes"][attr] = []
                print("创建新的历史数据记录")
        except Exception as e:
            print(f"加载历史数据出错: {e}")
            # 初始化历史数据结构
            self.history_data = {
                "timestamps": [],
                "attributes": {}
            }
            for attr in self.attributes:
                self.history_data["attributes"][attr] = []
    
    def save_history_data(self):
        """保存历史数据"""
        # 添加当前时间戳
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_data["timestamps"].append(current_time)
        
        # 添加当前属性值
        for attr, info in self.attributes.items():
            if attr not in self.history_data["attributes"]:
                self.history_data["attributes"][attr] = []
            self.history_data["attributes"][attr].append(info["current_value"])
        
        # 保持历史记录不超过1000个点（防止文件过大）
        max_history = 1000
        if len(self.history_data["timestamps"]) > max_history:
            self.history_data["timestamps"] = self.history_data["timestamps"][-max_history:]
            for attr in self.history_data["attributes"]:
                self.history_data["attributes"][attr] = self.history_data["attributes"][attr][-max_history:]
        
        try:
            with open("data/history_data.json", "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
            print(f"历史数据已保存 - {current_time}")
        except Exception as e:
            print(f"保存历史数据出错: {e}")
    
    def calculate_trend(self, history):
        """计算趋势值"""
        if len(history) < 2:
            return 0
        
        # 使用最近的10个数据点计算趋势
        recent_history = history[-10:]
        x = np.arange(len(recent_history))
        y = np.array(recent_history)
        
        try:
            slope, _, _, _, _ = linregress(x, y)
            return slope
        except:
            return 0

    def analyze_trends(self):
        """分析属性趋势并显示结果"""
        window = ttk.Toplevel(self.root)
        window.title("属性趋势分析")
        
        # 设置背景图片
        self.set_background(window)
        
        # 居中显示窗口
        self.center_window(window, 1000, 600)
        
        main_frame = ttk.Frame(window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右两列的框架
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 左侧：当前趋势
        ttk.Label(left_frame, text="当前趋势分析", font=self.subtitle_font, bootstyle="info").pack(pady=(0, 10))
        
        trend_frame = ttk.Frame(left_frame)
        trend_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        trend_canvas = tk.Canvas(trend_frame)
        trend_scrollbar = ttk.Scrollbar(trend_frame, orient="vertical", command=trend_canvas.yview)
        trend_scrollable_frame = ttk.Frame(trend_canvas)
        
        trend_scrollable_frame.bind(
            "<Configure>",
            lambda e: trend_canvas.configure(scrollregion=trend_canvas.bbox("all"))
        )
        
        trend_canvas.create_window((0, 0), window=trend_scrollable_frame, anchor="nw")
        trend_canvas.configure(yscrollcommand=trend_scrollbar.set)
        
        trend_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧：未来预测
        ttk.Label(right_frame, text="未来预测", font=self.subtitle_font, bootstyle="info").pack(pady=(0, 10))
        
        prediction_frame = ttk.Frame(right_frame)
        prediction_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        prediction_canvas = tk.Canvas(prediction_frame)
        prediction_scrollbar = ttk.Scrollbar(prediction_frame, orient="vertical", command=prediction_canvas.yview)
        prediction_scrollable_frame = ttk.Frame(prediction_canvas)
        
        prediction_scrollable_frame.bind(
            "<Configure>",
            lambda e: prediction_canvas.configure(scrollregion=prediction_canvas.bbox("all"))
        )
        
        prediction_canvas.create_window((0, 0), window=prediction_scrollable_frame, anchor="nw")
        prediction_canvas.configure(yscrollcommand=prediction_scrollbar.set)
        
        prediction_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prediction_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 分析每个属性的趋势
        for attr, info in self.attributes.items():
            # 从历史数据中获取该属性的历史记录
            if attr in self.history_data["attributes"]:
                history = self.history_data["attributes"][attr]
                if len(history) < 2:
                    continue
                
                # 计算趋势
                trend = self.calculate_trend(history)
                trend_text = f"{self.icons.get(attr, '')} {attr}: "
                
                if abs(trend) < 0.01:
                    bootstyle = "default"
                    trend_text += "保持稳定"
                elif trend > 0:
                    bootstyle = "success"
                    trend_text += f"上升趋势 (+{trend:.2f}/h)"
                else:
                    bootstyle = "danger"
                    trend_text += f"下降趋势 ({trend:.2f}/h)"
                
                # 显示趋势
                ttk.Label(trend_scrollable_frame, text=trend_text, bootstyle=bootstyle).pack(pady=5, anchor="w")
                
                # 预测未来值
                current_value = info["current_value"]
                future_value = current_value + (trend * 0.5)  # 预测30分钟后的值
                future_value = max(0, min(100, future_value))  # 确保值在0-100之间
                prediction_text = f"{self.icons.get(attr, '')} {attr}: {future_value:.1f} (30分钟后)"
                ttk.Label(prediction_scrollable_frame, text=prediction_text, bootstyle="info").pack(pady=5, anchor="w")
        
        # 底部按钮
        ttk.Button(window, text="关闭", command=window.destroy, bootstyle="secondary").pack(pady=10)
    
    def analyze_with_ai(self):
        """使用AI分析当前状态并给出建议"""
        # 收集当前状态数据
        current_state = {
            "player_name": self.player_name,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attributes": {}
        }
        
        for attr, info in self.attributes.items():
            current_state["attributes"][attr] = {
                "value": info["current_value"],
                "trend": info.get("trend", 0.0)
            }
        
        # 分析状态
        analysis = self.generate_ai_analysis(current_state)
        
        # 更新AI分析文本框
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, analysis)
    
    def generate_ai_analysis(self, state):
        """使用AI生成分析结果"""
        try:
            # 构建属性状态文本
            attributes_text = ""
            for category, attrs in self.categories.items():
                attributes_text += f"\n{category}:\n"
                for attr in attrs:
                    if attr in state["attributes"]:
                        value = state["attributes"][attr]["value"]
                        trend = state["attributes"][attr].get("trend", 0.0)
                        attributes_text += f"  {attr}: {value:.1f} (趋势: {trend:.4f})\n"
            
            # 构建完整的提示词
            prompt = f"""请作为一位专业的健康顾问，分析以下玩家状态数据，并直接输出JSON格式文件作为分析结果：

玩家：{state["player_name"]}
时间：{state["current_time"]}

当前状态：{attributes_text}

请从以下几个方面进行分析：
1. 总体健康状况评估
2. 需要注意的指标
3. 改善建议
4. 今日重点关注项

请按照上述JSON格式输出分析结果，用通俗易懂的语言给出分析和建议。"""
            
            # 创建等待提示窗口
            wait_window = tk.Toplevel(self.root)
            wait_window.title("请稍候")
            
            # 居中显示窗口
            self.center_window(wait_window, 300, 100)
            
            wait_window.transient(self.root)
            wait_window.grab_set()
            
            # 添加等待消息
            ttk.Label(wait_window, text="正在生成分析结果，请耐心等待...", 
                     font=self.text_font, wraplength=250).pack(pady=20)
            
            # 添加进度条
            progress = ttk.Progressbar(wait_window, mode='indeterminate')
            progress.pack(fill=tk.X, padx=20)
            progress.start()
            
            # 更新UI
            self.root.update()
            
            try:
                # 调用API
                response = self.call_deepseek_api(prompt)
                
                # 关闭等待窗口
                wait_window.destroy()
                
                if response:
                    # 保存AI回复到文件
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = os.path.join("outputs", f"ai_analysis_{timestamp}.txt")
                    try:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(f"时间: {state['current_time']}\n")
                            f.write(f"玩家: {state['player_name']}\n\n")
                            f.write("属性状态:\n")
                            f.write(attributes_text)
                            f.write("\nAI分析结果:\n")
                            f.write(response)
                        print(f"AI分析结果已保存到: {output_file}")
                    except Exception as e:
                        print(f"保存AI分析结果时出错: {e}")
                    
                    return response
                else:
                    return "API调用失败，请检查配置和网络连接"
            except Exception as e:
                wait_window.destroy()
                return f"生成分析时出错: {str(e)}"
                
        except Exception as e:
            print(f"生成AI分析时出错: {e}")
            return f"生成分析时出错: {str(e)}"
    
    def setup_thresholds(self):
        """设置阈值提醒"""
        threshold_window = ttk.Toplevel(self.root)
        threshold_window.title("阈值提醒设置")
        
        # 设置背景图片
        self.set_background(threshold_window)
        
        # 居中显示窗口
        self.center_window(threshold_window, 500, 600)
        
        threshold_window.grab_set()
        
        # 创建设置界面
        setup_frame = ttk.Frame(threshold_window, padding=15)
        setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置标题
        title_label = ttk.Label(setup_frame, text="阈值提醒设置", font=('Microsoft YaHei', 16, 'bold'), bootstyle="info")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # 创建滚动框架
        canvas = tk.Canvas(setup_frame)
        scrollbar = ttk.Scrollbar(setup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 阈值设置
        row = 0
        self.threshold_vars = {}
        self.time_vars = {}
        
        for category, attrs in self.categories.items():
            # 添加类别标题
            ttk.Label(scrollable_frame, text=category, font=self.subtitle_font, bootstyle="info").grid(
                row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
            row += 1
            
            for attr in attrs:
                icon = self.icons.get(attr, "")
                ttk.Label(scrollable_frame, text=f"{icon} {attr}", font=self.text_font).grid(
                    row=row, column=0, sticky=tk.W, pady=2)
                
                # 阈值输入
                threshold_var = tk.StringVar(value=str(self.thresholds.get(attr, 30)))
                threshold_entry = ttk.Entry(scrollable_frame, width=8, textvariable=threshold_var)
                threshold_entry.grid(row=row, column=1, padx=5)
                self.threshold_vars[attr] = threshold_var
                
                # 时间输入
                time_var = tk.StringVar(value=self.scheduled_times.get(attr, ""))
                time_entry = ttk.Entry(scrollable_frame, width=10, textvariable=time_var)
                time_entry.grid(row=row, column=2, padx=5)
                self.time_vars[attr] = time_var
                
                ttk.Label(scrollable_frame, text="(时间格式: HH:MM)", font=('Microsoft YaHei', 8)).grid(
                    row=row, column=3, sticky=tk.W, padx=5)
                
                row += 1
        
        # 布局滚动框架
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        setup_frame.grid_rowconfigure(1, weight=1)
        setup_frame.grid_columnconfigure(0, weight=1)
        
        # 保存按钮
        def save_settings():
            # 保存阈值设置
            for attr, var in self.threshold_vars.items():
                try:
                    value = float(var.get())
                    if 0 <= value <= 100:
                        self.thresholds[attr] = value
                    else:
                        messagebox.showwarning("警告", f"{attr}的阈值必须在0-100之间")
                        return
                except ValueError:
                    messagebox.showwarning("警告", f"{attr}的阈值必须是数字")
                    return
            
            # 保存时间设置
            for attr, var in self.time_vars.items():
                time_str = var.get().strip()
                if time_str:
                    try:
                        datetime.strptime(time_str, "%H:%M")
                        self.scheduled_times[attr] = time_str
                    except ValueError:
                        messagebox.showwarning("警告", f"{attr}的时间格式必须是HH:MM")
                        return
                else:
                    self.scheduled_times[attr] = ""
            
            # 保存到文件
            try:
                data = {
                    "thresholds": self.thresholds,
                    "scheduled_times": self.scheduled_times
                }
                with open("data/thresholds.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                # 更新阈值提醒文本框
                self.update_threshold_text()
                messagebox.showinfo("成功", "设置已保存")
                threshold_window.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存设置失败: {e}")
        
        save_button = ttk.Button(setup_frame, text="保存设置", command=save_settings, bootstyle="success")
        save_button.grid(row=2, column=0, columnspan=2, pady=(15, 0))
    
    def load_thresholds(self):
        """加载阈值设置"""
        try:
            if os.path.exists("data/thresholds.json"):
                with open("data/thresholds.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.thresholds = data.get("thresholds", {})
                self.scheduled_times = data.get("scheduled_times", {})
            else:
                self.thresholds = {attr: 30 for attr in self.attributes}
                self.scheduled_times = {}
        except Exception as e:
            print(f"加载阈值设置时出错: {e}")
            self.thresholds = {attr: 30 for attr in self.attributes}
            self.scheduled_times = {}
    
    def update_threshold_text(self):
        """更新阈值提醒文本框"""
        self.threshold_text.delete(1.0, tk.END)
        text = "当前阈值设置：\n"
        
        for attr, threshold in self.thresholds.items():
            text += f"{attr}: {threshold}"
            if attr in self.scheduled_times:
                text += f" (预定时间: {self.scheduled_times[attr]})"
            text += "\n"
        
        self.threshold_text.insert(tk.END, text)
    
    def check_thresholds(self):
        """检查阈值和预定时间"""
        current_time = datetime.now()
        current_minute = current_time.strftime("%H:%M")
        
        alerts = []  # 收集所有需要显示的警告
        
        for attr, info in self.attributes.items():
            if attr not in self.threshold_alerts:
                self.threshold_alerts[attr] = {"first_alert": False, "half_alert": False}
                self.last_alert_time[attr] = {"first": None, "half": None}
            
            current_value = info["current_value"]
            threshold = self.thresholds.get(attr, 30)
            
            # 检查是否需要第一次提醒（刚刚低于阈值）
            if not self.threshold_alerts[attr]["first_alert"] and current_value <= threshold:
                last_alert = self.last_alert_time[attr]["first"]
                if last_alert is None or (current_time - last_alert).total_seconds() >= 60:
                    alerts.append(f"{attr}已达到阈值({threshold})，当前值: {current_value:.1f}")
                    self.threshold_alerts[attr]["first_alert"] = True
                    self.last_alert_time[attr]["first"] = current_time
            
            # 检查是否需要第二次提醒（降至阈值的一半）
            if not self.threshold_alerts[attr]["half_alert"] and current_value <= threshold/2:
                last_alert = self.last_alert_time[attr]["half"]
                if last_alert is None or (current_time - last_alert).total_seconds() >= 60:
                    alerts.append(f"{attr}已降至危险水平({threshold/2})，当前值: {current_value:.1f}")
                    self.threshold_alerts[attr]["half_alert"] = True
                    self.last_alert_time[attr]["half"] = current_time
            
            # 重置提醒状态（当值回升超过阈值时）
            if current_value > threshold:
                self.threshold_alerts[attr]["first_alert"] = False
                self.threshold_alerts[attr]["half_alert"] = False
                self.last_alert_time[attr]["first"] = None
                self.last_alert_time[attr]["half"] = None
            
            # 检查是否到达预定时间
            if attr in self.scheduled_times and self.scheduled_times[attr] == current_minute:
                last_alert = self.last_alert_time[attr].get("schedule")
                if last_alert is None or (current_time - last_alert).total_seconds() >= 60:
                    alerts.append(f"现在是{current_minute}，是时候关注{attr}了")
                    self.last_alert_time[attr]["schedule"] = current_time
        
        # 如果有警告，统一显示
        if alerts:
            self.alert_manager.show_alert("属性提醒", "\n".join(alerts))
    
    def update_panel(self):
        """更新面板数据"""
        # 更新时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"当前时间: {current_time}")
        
        # 计算经过的时间
        now = time.time()
        elapsed = now - self.last_update_time
        self.last_update_time = now
        
        # 更新每个属性的值
        for attr, info in self.attributes.items():
            # 根据变化率更新属性值
            delta = info["change_rate"] * elapsed * 10  # 乘以10使变化更加明显
            
            # 添加一些随机波动
            delta += random.uniform(-0.1, 0.1)
            
            # 更新属性值
            new_value = info["current_value"] + delta
            new_value = max(0, min(100, new_value))  # 限制在0-100范围内
            info["current_value"] = new_value
            
            # 更新进度条
            percentage = int(new_value)
            info["progress_bar"]["value"] = percentage
            info["value_label"].config(text=f"{percentage}%")
            
            # 根据值更新进度条样式
            bootstyle = self.get_progress_style(percentage)
            info["progress_bar"].configure(bootstyle=bootstyle)
        
        # 每隔一段时间保存历史数据
        if now - self.last_save_time > self.history_save_interval:
            self.save_history_data()
            self.last_save_time = now
            
            # 自动分析趋势
            self.update_trends()
        
        # 检查阈值和预定时间
        self.check_thresholds()
        
        # 更新时间显示
        self.time_label.config(text=f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 安排下一次更新
        self.root.after(1000, self.update_panel)  # 每秒更新一次
    
    def update_trends(self):
        """更新所有属性的趋势分析"""
        if len(self.history_data.get("timestamps", [])) < 5:
            return
        
        for attr in self.attributes:
            if attr in self.history_data["attributes"] and len(self.history_data["attributes"][attr]) >= 5:
                # 获取历史数据
                values = self.history_data["attributes"][attr]
                
                # 使用简单线性回归分析趋势
                x = np.arange(len(values))
                try:
                    slope, intercept, r_value, p_value, std_err = linregress(x, values)
                    
                    # 保存趋势斜率
                    self.attributes[attr]["trend"] = slope
                    
                    # 根据趋势自动调整变化率
                    # 如果趋势明显，微调变化率以使其更接近期望趋势
                    if abs(slope) > 0.05 and random.random() < 0.3:  # 30%的概率进行自动调整
                        # 轻微调整当前变化率
                        adjustment = slope * 0.01
                        self.attributes[attr]["change_rate"] += adjustment
                        print(f"自动调整 {attr} 变化率: {self.attributes[attr]['change_rate']:.4f} (趋势: {slope:.4f})")
                
                except Exception as e:
                    print(f"更新 {attr} 趋势时出错: {e}")

    def load_api_config(self):
        """加载API配置"""
        try:
            if os.path.exists("data/api_config.json"):
                with open("data/api_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.api_key = config.get("api_key", "")
                self.api_model = config.get("model", "")
                self.available_models = config.get("available_models", [])
                self.prompts = config.get("prompts", {})
        except Exception as e:
            print(f"加载API配置出错: {e}")
            self.available_models = []
            self.prompts = {}
    
    def save_api_config(self):
        """保存API配置"""
        try:
            with open("data/api_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            
            config["api_key"] = self.api_key
            config["model"] = self.api_model
            
            with open("data/api_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print("API配置已保存")
        except Exception as e:
            print(f"保存API配置出错: {e}")
    
    def call_deepseek_api(self, prompt):
        """调用SiliconFlow API进行分析"""
        if not self.api_key:
            messagebox.showwarning("API未配置", "请先在设置中配置SiliconFlow API Key")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.api_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"调用SiliconFlow API时出错: {e}")
            return None

    def load_health_data(self):
        """加载并解析Apple健康数据"""
        try:
            export_path = "health_data/example_data.xml"
            if os.path.exists(export_path):
                tree = ET.parse(export_path)
                root = tree.getroot()
                
                # 获取今天的日期
                today = datetime.now().strftime("%Y-%m-%d")
                
                # 初始化健康数据字典
                self.health_data = {
                    "steps": [],
                    "distance": [],
                    "heart_rate": [],
                    "active_energy": [],
                    "body_mass": []
                }
                
                # 定义需要的数据类型
                type_mapping = {
                    "HKQuantityTypeIdentifierStepCount": "steps",
                    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance",
                    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
                    "HKQuantityTypeIdentifierActiveEnergyBurned": "active_energy",
                    "HKQuantityTypeIdentifierBodyMass": "body_mass"
                }
                
                # 解析数据
                for record in root.findall(".//Record"):
                    try:
                        type = record.get("type")
                        # 只处理我们需要的数据类型
                        if type not in type_mapping:
                            continue
                            
                        date = record.get("startDate", "").split()[0]  # 只取日期部分
                        # 只处理今天的数据
                        if date != today:
                            continue
                            
                        # 尝试转换值为浮点数
                        try:
                            value = float(record.get("value", 0))
                        except (ValueError, TypeError):
                            continue
                            
                        # 将数据添加到对应类型的列表中
                        data_type = type_mapping[type]
                        self.health_data[data_type].append({"date": date, "value": value})
                        
                    except Exception as e:
                        print(f"跳过一条无效记录: {e}")
                        continue
                
                print(f"今日({today})健康数据加载成功，共处理：")
                for data_type, data_list in self.health_data.items():
                    print(f"- {data_type}: {len(data_list)}条记录")
                    
                self.update_attributes_from_health_data()
            else:
                print("未找到健康数据文件")
        except Exception as e:
            print(f"加载健康数据时出错: {e}")
    
    def update_attributes_from_health_data(self):
        """根据健康数据更新属性值"""
        try:
            # 更新步数相关属性
            today_steps = sum(item["value"] for item in self.health_data["steps"])
            if today_steps > 0:
                # 根据步数更新敏捷属性
                agility_value = min(100, today_steps / 100)  # 10000步对应100分
                self.attributes["敏捷"]["current_value"] = agility_value
            
            # 更新心率相关属性
            today_heart_rates = [item["value"] for item in self.health_data["heart_rate"]]
            if today_heart_rates:
                avg_heart_rate = sum(today_heart_rates) / len(today_heart_rates)
                # 根据心率更新心脏健康度
                heart_health = 100 - abs(75 - avg_heart_rate)  # 假设75是最佳心率
                self.attributes["心脏健康度"]["current_value"] = max(0, min(100, heart_health))
            
            # 更新体重相关属性
            if self.health_data["body_mass"]:
                recent_weight = self.health_data["body_mass"][-1]["value"]
                # 根据体重计算BMI并更新瘦身指数
                height = 1.7  # 默认身高，可以从设置中读取
                bmi = recent_weight / (height * height)
                # 瘦身指数计算逻辑：BMI越接近正常范围（18.5-24）分数越高
                if bmi < 18.5:
                    fitness_index = 100 - (18.5 - bmi) * 10
                elif bmi > 24:
                    fitness_index = 100 - (bmi - 24) * 10
                else:
                    fitness_index = 100
                self.attributes["瘦身指数"]["current_value"] = max(0, min(100, fitness_index))
            
            # 更新运动消耗相关属性
            today_energy = sum(item["value"] for item in self.health_data["active_energy"])
            if today_energy > 0:
                # 根据消耗的卡路里更新肌肉强度
                strength_value = min(100, today_energy / 30)  # 3000卡路里对应100分
                self.attributes["肌肉强度"]["current_value"] = strength_value
            
            print("属性值已根据今日健康数据更新")
            
        except Exception as e:
            print(f"更新属性值时出错: {e}")

    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            self.save_data()
            print("应用关闭前数据已保存")
        except Exception as e:
            print(f"保存数据时出错: {e}")
        
        if hasattr(sys.stdout, 'close'):
            sys.stdout.close()
        self.root.destroy()

    def sync_health_data(self):
        """同步健康数据的处理函数"""
        # 创建等待窗口
        wait_window = tk.Toplevel(self.root)
        wait_window.title("请稍候")
        
        # 居中显示窗口
        self.center_window(wait_window, 300, 100)
        
        wait_window.transient(self.root)
        wait_window.grab_set()
        
        # 添加等待消息
        ttk.Label(wait_window, text="正在读取健康数据，文件较大，请耐心等待...", 
                 font=self.text_font, wraplength=250).pack(pady=20)
        
        # 添加进度条
        progress = ttk.Progressbar(wait_window, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20)
        progress.start()
        
        # 更新UI
        self.root.update()
        
        try:
            # 加载健康数据
            self.load_health_data()
            messagebox.showinfo("成功", "健康数据同步完成")
        except Exception as e:
            messagebox.showerror("错误", f"同步健康数据时出错: {e}")
        finally:
            wait_window.destroy()

    def show_trend_charts(self):
        """显示趋势图窗口"""
        window = ttk.Toplevel(self.root)
        window.title("属性趋势分析")
        
        # 设置背景图片
        self.set_background(window)
        
        # 居中显示窗口
        self.center_window(window, 900, 600)
        
        # 创建主框架
        main_frame = ttk.Frame(window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 总览标签页
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="总览")
        
        # 创建总览页的滚动区域
        overview_canvas = tk.Canvas(overview_frame)
        overview_scrollbar_y = ttk.Scrollbar(overview_frame, orient="vertical", command=overview_canvas.yview)
        overview_scrollbar_x = ttk.Scrollbar(overview_frame, orient="horizontal", command=overview_canvas.xview)
        overview_scrollable_frame = ttk.Frame(overview_canvas)
        
        overview_scrollable_frame.bind(
            "<Configure>",
            lambda e: overview_canvas.configure(scrollregion=overview_canvas.bbox("all"))
        )
        
        overview_canvas.create_window((0, 0), window=overview_scrollable_frame, anchor="nw")
        overview_canvas.configure(yscrollcommand=overview_scrollbar_y.set, xscrollcommand=overview_scrollbar_x.set)
        
        # 生成并显示总览图
        overview_file = self.analytics_manager.generate_overview_chart()
        overview_img = tk.PhotoImage(file=overview_file)
        overview_label = ttk.Label(overview_scrollable_frame, image=overview_img)
        overview_label.image = overview_img
        overview_label.pack(pady=10, padx=10)
        
        # 布局总览页的滚动条
        overview_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        overview_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        overview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 分类标签页
        for category, attrs in self.categories.items():
            category_frame = ttk.Frame(notebook)
            notebook.add(category_frame, text=category)
            
            # 创建双向滚动画布
            canvas = tk.Canvas(category_frame)
            scrollbar_y = ttk.Scrollbar(category_frame, orient="vertical", command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(category_frame, orient="horizontal", command=canvas.xview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # 为每个属性生成趋势图
            for attr in attrs:
                # 创建属性框架
                attr_frame = ttk.Labelframe(scrollable_frame, text=f"{self.icons.get(attr, '')} {attr}", padding=10)
                attr_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # 生成趋势图
                chart_file = self.analytics_manager.generate_trend_chart(attr)
                img = tk.PhotoImage(file=chart_file)
                label = ttk.Label(attr_frame, image=img)
                label.image = img
                label.pack()
            
            # 布局滚动条和画布
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 绑定鼠标滚轮事件
            def on_mousewheel(event, canvas):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", lambda e, c=canvas: on_mousewheel(e, c))
        
        # 底部按钮
        ttk.Button(main_frame, text="关闭", command=window.destroy, bootstyle="secondary").pack(pady=10)
    
    def generate_weekly_report(self):
        """生成并显示周报"""
        try:
            report_file = self.analytics_manager.generate_weekly_report()
            self.show_report(report_file, "周报")
        except Exception as e:
            messagebox.showerror("错误", f"生成周报时出错：{e}")
    
    def generate_monthly_report(self):
        """生成并显示月报"""
        try:
            report_file = self.analytics_manager.generate_monthly_report()
            self.show_report(report_file, "月报")
        except Exception as e:
            messagebox.showerror("错误", f"生成月报时出错：{e}")
    
    def show_report(self, report_file: str, report_type: str):
        """显示报告窗口"""
        window = ttk.Toplevel(self.root)
        window.title(f"地球Online {report_type}")
        
        # 设置背景图片
        self.set_background(window)
        
        # 居中显示窗口
        self.center_window(window, 800, 600)
        
        # 创建主框架
        main_frame = ttk.Frame(window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本框
        text = tk.Text(main_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)
        
        # 读取并显示报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            text.insert(tk.END, content)
        
        text.config(state=tk.DISABLED)  # 设置为只读
        
        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="导出PDF", command=lambda: self.export_pdf(report_file), 
                  bootstyle="primary").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=window.destroy, 
                  bootstyle="secondary").pack(side=tk.RIGHT, padx=5)
    
    def export_pdf(self, report_file: str):
        """导出报告为PDF"""
        return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 注册中文字体
            pdfmetrics.registerFont(TTFont('Microsoft YaHei', 'msyh.ttc'))
            
            # 创建PDF文件
            pdf_file = report_file.replace('.txt', '.pdf')
            c = canvas.Canvas(pdf_file, pagesize=A4)
            c.setFont('Microsoft YaHei', 12)
            
            # 读取报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 写入内容
            y = 800  # 起始y坐标
            for line in content.split('\n'):
                if y < 50:  # 如果页面空间不足，创建新页面
                    c.showPage()
                    c.setFont('Microsoft YaHei', 12)
                    y = 800
                
                c.drawString(50, y, line)
                y -= 20  # 行间距
            
            c.save()
            messagebox.showinfo("成功", f"报告已导出为PDF：{pdf_file}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出PDF时出错：{e}")

    def show_enlarged_window(self, title, content):
        """显示放大窗口"""
        window = ttk.Toplevel(self.root)
        window.title(title)
        
        # 设置背景图片
        self.set_background(window)
        
        # 设置窗口大小为屏幕的80%
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 居中显示窗口
        self.center_window(window, window_width, window_height)
        
        # 创建主框架
        main_frame = ttk.Frame(window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本框
        text = tk.Text(main_frame, wrap=tk.WORD, font=('Microsoft YaHei', 12))
        text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)
        
        # 插入内容
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)  # 设置为只读
        
        # 底部按钮
        ttk.Button(main_frame, text="关闭", command=window.destroy, 
                  bootstyle="secondary").pack(pady=(0, 5))
        
        # 将窗口提到前面
        window.lift()
        window.focus_force()
        
        # 绑定Esc键关闭窗口
        window.bind('<Escape>', lambda e: window.destroy())

def main():
    # 加载主题设置
    theme = "darkly"  # 默认主题
    try:
        if os.path.exists("data/theme_config.json"):
            with open("data/theme_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                theme = config.get("theme", "darkly")
    except Exception as e:
        print(f"加载主题设置时出错: {e}")

    root = ttk.Window(
        title="地球Online看板",
        themename=theme,
        size=(800, 600),
        position=(100, 50),
        minsize=(800, 600),
    )
    
    # 创建主页和看板实例
    app = None
    
    def switch_to_kanban():
        nonlocal app
        root.geometry("1024x768")  # 调整窗口大小以适应看板
        app = EarthOnlinePanel(root)
    
    # 创建主页，传入切换回调函数
    home = HomePage(root, on_enter_callback=switch_to_kanban)
    
    root.mainloop()

if __name__ == "__main__":
    main() 