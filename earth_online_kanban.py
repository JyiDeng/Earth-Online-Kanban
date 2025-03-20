import tkinter as tk
from tkinter import ttk, font, messagebox
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

# 重定向stdout到窗口显示
class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class EarthOnlinePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("地球Online看板")
        self.root.geometry("1000x600")
        
        # 设置应用程序图标和主题
        self.root.minsize(800, 500)
        
        # 应用主题风格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
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
        
        # 应用颜色样式
        self.style.configure('TFrame', background=self.colors["bg"])
        self.style.configure('TLabelframe', background=self.colors["bg"], foreground=self.colors["text"])
        self.style.configure('TLabelframe.Label', background=self.colors["bg"], foreground=self.colors["text"], font=('Arial', 11, 'bold'))
        self.style.configure('TLabel', background=self.colors["bg"], foreground=self.colors["text"])
        
        # 自定义按钮样式
        self.style.configure('TButton', background=self.colors["button"], foreground=self.colors["button_text"], font=('Arial', 10))
        self.style.map('TButton', 
                       background=[('active', '#2980b9'), ('pressed', '#1f618d')],
                       foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # 自定义进度条样式
        self.style.configure("health.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                            background=self.colors["good"], borderwidth=0, thickness=20)
        self.style.configure("warning.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                            background=self.colors["warning"], borderwidth=0, thickness=20)
        self.style.configure("danger.Horizontal.TProgressbar", troughcolor=self.colors["bg"], 
                            background=self.colors["danger"], borderwidth=0, thickness=20)
        
        # 创建字体
        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_font = font.Font(family="Arial", size=10)
        
        # 设置背景色
        self.root.configure(background=self.colors["bg"])
        
        # 初始化数据
        self.attributes = {}
        self.last_update_time = time.time()
        self.model = None
        
        # 创建UI元素
        self.create_ui()
        
        # 加载模拟数据
        self.load_mock_data()
        
        # 启动定时更新
        self.update_panel()
        
        # 加载模型（如果存在）
        self.load_model()
    
    def load_model(self):
        """加载已训练的模型"""
        model_path = "model/event_model.pkl"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                messagebox.showinfo("模型加载", "已成功加载训练模型")
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
            return "health.Horizontal.TProgressbar"
        elif value > 30:
            return "warning.Horizontal.TProgressbar"
        else:
            return "danger.Horizontal.TProgressbar"
    
    def create_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部信息栏
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题
        title_label = ttk.Label(self.top_frame, text="地球 Online", font=('Arial', 18, 'bold'), foreground=self.colors["highlight"])
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
            "生理需求": ["饱腹", "口渴", "如厕", "肥胖指数", "心脏健康度"],
            "社会需求": ["社交", "情绪", "成就感", "情商", "安全感"],
            "能力属性": ["肌肉强度", "敏捷", "抗击打能力", "魅力", "道德"]
        }
        
        # 图标映射
        self.icons = {
            "饱腹": "🍔",
            "口渴": "💧",
            "如厕": "🚽",
            "肥胖指数": "⚖️",
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
            category_frame = ttk.LabelFrame(self.categories_frame, text=category, padding=15)
            category_frame.grid(row=0, column=column_index, padx=8, pady=5, sticky="nsew")
            
            # 为每个属性创建进度条和标签
            for i, attr in enumerate(attrs):
                icon = self.icons.get(attr, "")
                ttk.Label(category_frame, text=f"{icon} {attr}", font=self.text_font).grid(row=i, column=0, sticky=tk.W, pady=6)
                
                # 创建进度条框架
                progress_frame = ttk.Frame(category_frame)
                progress_frame.grid(row=i, column=1, sticky=tk.EW, pady=6, padx=(10, 0))
                
                # 创建进度条
                progress_bar = ttk.Progressbar(progress_frame, length=100, mode="determinate", style="health.Horizontal.TProgressbar")
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
                    "change_rate": random.uniform(-0.01, 0.01)  # 随机变化率
                }
            
            # 设置列权重
            category_frame.columnconfigure(1, weight=1)
            column_index += 1
        
        # 设置列权重
        self.categories_frame.columnconfigure(0, weight=1)
        self.categories_frame.columnconfigure(1, weight=1)
        self.categories_frame.columnconfigure(2, weight=1)
        
        # 创建底部控制栏
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 添加分隔线
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        self.setup_button = ttk.Button(self.control_frame, text="设置", command=self.setup)
        self.setup_button.pack(side=tk.LEFT)
        
        self.save_button = ttk.Button(self.control_frame, text="保存数据", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=(10, 0))
        
        self.reset_button = ttk.Button(self.control_frame, text="重置", command=self.reset_data)
        self.reset_button.pack(side=tk.RIGHT)
        
        # 添加事件按钮
        self.event_button = ttk.Button(self.control_frame, text="事件", command=self.open_event_window)
        self.event_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加训练模型按钮
        self.train_button = ttk.Button(self.control_frame, text="训练模型", command=self.train_and_save_model)
        self.train_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加日志窗口
        self.log_frame = ttk.LabelFrame(self.main_frame, text="系统日志")
        self.log_frame.pack(fill=tk.X, pady=(15, 0), after=separator)
        
        self.log_text = tk.Text(self.log_frame, height=5, width=50, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.X, expand=True, pady=5, padx=5)
        
        # 重定向标准输出到日志窗口
        self.stdout_redirector = StdoutRedirector(self.log_text)
        sys.stdout = self.stdout_redirector
    
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
            if os.path.exists("player_data.json"):
                with open("player_data.json", "r", encoding="utf-8") as f:
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
            self.attributes[attr]["current_value"] = random.randint(30, 70)
            self.attributes[attr]["change_rate"] = random.uniform(-0.02, 0.02)
    
    def save_data(self):
        """保存当前数据"""
        data = {
            "player_name": self.player_name,
            "attributes": {}
        }
        
        for attr, info in self.attributes.items():
            data["attributes"][attr] = {
                "value": info["current_value"],
                "change_rate": info["change_rate"]
            }
        
        try:
            with open("player_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("数据已保存")
        except Exception as e:
            print(f"保存数据出错: {e}")
    
    def reset_data(self):
        """重置所有属性"""
        for attr in self.attributes:
            self.attributes[attr]["current_value"] = 50
            self.attributes[attr]["change_rate"] = random.uniform(-0.01, 0.01)
    
    def setup(self):
        """打开设置窗口"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("设置")
        setup_window.geometry("450x600")
        setup_window.grab_set()  # 模态窗口
        
        # 创建设置界面
        setup_frame = ttk.Frame(setup_window, padding=15)
        setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置标题
        title_label = ttk.Label(setup_frame, text="玩家设置", font=('Arial', 16, 'bold'), foreground=self.colors["highlight"])
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # 玩家名称设置
        ttk.Label(setup_frame, text="玩家名称:", font=self.subtitle_font).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        name_entry = ttk.Entry(setup_frame, width=30, font=self.text_font)
        name_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        name_entry.insert(0, self.player_name)
        
        # 添加分隔线
        separator = ttk.Separator(setup_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # 属性设置
        ttk.Label(setup_frame, text="属性设置:", font=self.subtitle_font).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # 创建滚动框架
        canvas = tk.Canvas(setup_frame, background=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(setup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=4, column=0, columnspan=2, sticky="nsew")
        scrollbar.grid(row=4, column=2, sticky="ns")
        setup_frame.grid_rowconfigure(4, weight=1)
        setup_frame.grid_columnconfigure(0, weight=0)
        setup_frame.grid_columnconfigure(1, weight=1)
        
        # 为每个属性创建滑块
        row = 0
        attr_entries = {}
        rate_entries = {}
        
        # 按类别组织设置项
        for category, attrs in self.categories.items():
            # 添加类别标题
            category_label = ttk.Label(scrollable_frame, text=category, font=self.subtitle_font, foreground=self.colors["highlight"])
            category_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
            row += 1
            
            for attr in attrs:
                icon = self.icons.get(attr, "")
                ttk.Label(scrollable_frame, text=f"{icon} {attr}", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
                
                # 创建属性值输入框
                attr_frame = ttk.Frame(scrollable_frame)
                attr_frame.grid(row=row, column=1, sticky=tk.EW, pady=2)
                
                # 当前值滑块
                info = self.attributes[attr]
                value_var = tk.DoubleVar(value=info["current_value"])
                slider = ttk.Scale(attr_frame, from_=0, to=100, variable=value_var, orient=tk.HORIZONTAL)
                slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # 当前值输入框
                value_entry = ttk.Entry(attr_frame, width=5, textvariable=value_var)
                value_entry.pack(side=tk.RIGHT, padx=(5, 0))
                
                attr_entries[attr] = value_var
                
                # 变化率
                row += 1
                ttk.Label(scrollable_frame, text=f"{attr}变化率", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2, padx=(20, 0))
                
                rate_var = tk.DoubleVar(value=info["change_rate"])
                rate_entry = ttk.Entry(scrollable_frame, width=10, textvariable=rate_var)
                rate_entry.grid(row=row, column=1, sticky=tk.W, pady=2)
                
                rate_entries[attr] = rate_var
                
                row += 1
        
        # 添加分隔线
        separator2 = ttk.Separator(setup_frame, orient='horizontal')
        separator2.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # 确认按钮
        def apply_settings():
            # 更新玩家名称
            self.player_name = name_entry.get()
            self.name_label.config(text=f"玩家名称: {self.player_name}")
            
            # 更新属性值
            for attr, var in attr_entries.items():
                try:
                    value = float(var.get())
                    self.attributes[attr]["current_value"] = max(0, min(100, value))
                except ValueError:
                    pass
            
            # 更新变化率
            for attr, var in rate_entries.items():
                try:
                    rate = float(var.get())
                    self.attributes[attr]["change_rate"] = rate
                except ValueError:
                    pass
            
            # 保存数据
            self.save_data()
            
            # 关闭窗口
            setup_window.destroy()
        
        button_frame = ttk.Frame(setup_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="确认", command=apply_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=setup_window.destroy).pack(side=tk.LEFT)
    
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
            print(input_data)
            
            # 预测
            impact_value = self.model.predict(input_data)[0]
            print(f"预测 '{event_name}' 对 '{attribute}' 的影响值: {impact_value:.2f}")
            return impact_value
        except Exception as e:
            print(f"预测过程中出错: {e}")
            messagebox.showerror("预测错误", f"预测过程中出错: {e}")
            return 0

    def open_event_window(self):
        """打开事件输入窗口"""
        event_window = tk.Toplevel(self.root)
        event_window.title("事件输入")
        event_window.geometry("400x350")
        event_window.grab_set()  # 模态窗口
        
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
        
        ttk.Button(event_frame, text="预测影响", command=predict_event_impact).grid(row=4, column=0, pady=(10, 0))
        
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
            except Exception as e:
                print(f"应用事件时出错: {e}")
                messagebox.showerror("应用事件错误", f"应用事件时出错: {e}")
            
            event_window.destroy()
        
        button_frame = ttk.Frame(event_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="应用事件", command=apply_event).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=event_window.destroy).pack(side=tk.LEFT)
    
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
            info["progress_bar"].configure(style=self.get_progress_style(percentage))
        
        # 安排下一次更新
        self.root.after(1000, self.update_panel)

def main():
    root = tk.Tk()
    app = EarthOnlinePanel(root)
    root.mainloop()

if __name__ == "__main__":
    main() 