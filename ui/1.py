import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 创建主窗口
root = ttk.Window(themename="litera")
root.title("地球Online看板 - 欢迎")
root.geometry("800x600")
root.configure(bg="#F8F9FA")

# 顶部导航区
nav_frame = ttk.Frame(root, bootstyle="primary", width=800, height=50)
nav_frame.pack(fill=X)
nav_frame.propagate(0)
nav_frame.configure(style="Nav.TFrame")
nav_frame.attributes("-alpha", 0.9)  # 模拟磨砂玻璃效果

# 左侧品牌标识
logo_label = ttk.Label(nav_frame, text="地球Online", font=("Arial", 18, "bold"), bootstyle="primary")
logo_label.pack(side=LEFT, padx=10)

# 右侧时间和用户名
time_label = ttk.Label(nav_frame, text="当前时间: 2025-04-04 11:19:08", font=("Roboto", 12), bootstyle="secondary")
time_label.pack(side=RIGHT, padx=10)
user_label = ttk.Label(nav_frame, text="玩家名称: 地球玩家001", font=("Roboto", 12), bootstyle="secondary")
user_label.pack(side=RIGHT, padx=10)

# 数据展示卡片
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=BOTH, expand=True)

# 生理需求卡片
physiological_card = ttk.Frame(main_frame, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
physiological_card.pack(side=LEFT, padx=10, pady=10)
physiological_card.columnconfigure(0, weight=1)

physiological_labels = [
    "饱腹", "口渴", "如厕", "社交需求", "疲惫", "卫生"
]
physiological_values = [96, 86, 30, 49, 92, 50]
physiological_colors = ["#34C759" if v > 70 else "#FFCC00" if v > 30 else "#FF3B30" for v in physiological_values]

for i, (label_text, value, color) in enumerate(zip(physiological_labels, physiological_values, physiological_colors)):
    icon_label = ttk.Label(physiological_card, text="📈", bootstyle="secondary")
    icon_label.grid(row=i, column=0, padx=5, pady=5, sticky=W)
    label = ttk.Label(physiological_card, text=label_text, font=("Arial", 12))
    label.grid(row=i, column=1, padx=5, pady=5, sticky=W)
    value_label = ttk.Label(physiological_card, text=f"{value}%", font=("Arial", 12, "bold"), bootstyle="secondary")
    value_label.grid(row=i, column=2, padx=5, pady=5, sticky=E)
    progress_bar = ttk.Progressbar(physiological_card, bootstyle=color, variable=tk.DoubleVar(value=value), maximum=100, length=150, borderradius=12)
    progress_bar.grid(row=i, column=3, padx=5, pady=5, sticky=E)

# 身心状况卡片
mental_card = ttk.Frame(main_frame, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
mental_card.pack(side=LEFT, padx=10, pady=10)
mental_card.columnconfigure(0, weight=1)

mental_labels = [
    "瘦身指数", "幸福感", "成就感", "视疲劳", "睡眠质量", "心脏健康度"
]
mental_values = [40, 99, 49, 89, 75, 76]
mental_colors = ["#34C759" if v > 70 else "#FFCC00" if v > 30 else "#FF3B30" for v in mental_values]

for i, (label_text, value, color) in enumerate(zip(mental_labels, mental_values, mental_colors)):
    icon_label = ttk.Label(mental_card, text="😀", bootstyle="secondary")
    icon_label.grid(row=i, column=0, padx=5, pady=5, sticky=W)
    label = ttk.Label(mental_card, text=label_text, font=("Arial", 12))
    label.grid(row=i, column=1, padx=5, pady=5, sticky=W)
    value_label = ttk.Label(mental_card, text=f"{value}%", font=("Arial", 12, "bold"), bootstyle="secondary")
    value_label.grid(row=i, column=2, padx=5, pady=5, sticky=E)
    progress_bar = ttk.Progressbar(mental_card, bootstyle=color, variable=tk.DoubleVar(value=value), maximum=100, length=150, borderradius=12)
    progress_bar.grid(row=i, column=3, padx=5, pady=5, sticky=E)

# 能力属性卡片
ability_card = ttk.Frame(main_frame, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
ability_card.pack(side=LEFT, padx=10, pady=10)
ability_card.columnconfigure(0, weight=1)

ability_labels = [
    "肌肉强度", "敏捷", "抗击打能力", "时间掌控度", "创造力", "安全感"
]
ability_values = [44, 49, 48, 50, 51, 49]
ability_colors = ["#34C759" if v > 70 else "#FFCC00" if v > 30 else "#FF3B30" for v in ability_values]

for i, (label_text, value, color) in enumerate(zip(ability_labels, ability_values, ability_colors)):
    icon_label = ttk.Label(ability_card, text="💪", bootstyle="secondary")
    icon_label.grid(row=i, column=0, padx=5, pady=5, sticky=W)
    label = ttk.Label(ability_card, text=label_text, font=("Arial", 12))
    label.grid(row=i, column=1, padx=5, pady=5, sticky=W)
    value_label = ttk.Label(ability_card, text=f"{value}%", font=("Arial", 12, "bold"), bootstyle="secondary")
    value_label.grid(row=i, column=2, padx=5, pady=5, sticky=E)
    progress_bar = ttk.Progressbar(ability_card, bootstyle=color, variable=tk.DoubleVar(value=value), maximum=100, length=150, borderradius=12)
    progress_bar.grid(row=i, column=3, padx=5, pady=5, sticky=E)

# 分析与设置区域
analysis_settings_frame = ttk.Frame(main_frame, padding=10)
analysis_settings_frame.pack(fill=BOTH, expand=True)

# AI状态分析面板
ai_analysis_panel = ttk.Frame(analysis_settings_frame, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
ai_analysis_panel.pack(side=LEFT, padx=10, pady=10)
ai_analysis_panel.columnconfigure(0, weight=1)

ai_label = ttk.Label(ai_analysis_panel, text="AI状态分析", font=("Arial", 14, "bold"))
ai_label.pack()
ai_button = ttk.Button(ai_analysis_panel, text="AI分析当前状态", bootstyle="primary", style="Gradient.TButton")
ai_button.pack(pady=5)
ai_view_button = ttk.Button(ai_analysis_panel, text="放大查看", bootstyle="secondary")
ai_view_button.pack()

# 阈值提醒设置面板
threshold_settings_panel = ttk.Frame(analysis_settings_frame, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
threshold_settings_panel.pack(side=LEFT, padx=10, pady=10)
threshold_settings_panel.columnconfigure(0, weight=1)

threshold_label = ttk.Label(threshold_settings_panel, text="阈值提醒设置", font=("Arial", 14, "bold"))
threshold_label.pack()
threshold_button = ttk.Button(threshold_settings_panel, text="设置阈值提醒", bootstyle="primary", style="Gradient.TButton")
threshold_button.pack(pady=5)
threshold_view_button = ttk.Button(threshold_settings_panel, text="放大查看", bootstyle="secondary")
threshold_view_button.pack()

# 底部功能区
bottom_frame = ttk.Frame(root, padding=10)
bottom_frame.pack(fill=X)

buttons = [
    "设置", "事件", "训练模型(事件对应属性增减)", "分析趋势", "同步健康数据", "趋势图", "周报", "月报", "重置(下次打开生效)"
]
for i, button_text in enumerate(buttons):
    button = ttk.Button(bottom_frame, text=button_text, bootstyle="outline-secondary" if button_text != "重置(下次打开生效)" else "danger", style="Button.TButton")
    button.grid(row=0, column=i, padx=5, pady=5)

# 系统日志区域
log_frame = ttk.Frame(root, bootstyle="light", padding=10, borderradius=12, style="Card.TFrame")
log_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

log_label = ttk.Label(log_frame, text="系统日志", font=("Arial", 14, "bold"))
log_label.pack()
log_text = tk.Text(log_frame, height=5)
log_text.insert(tk.END, "已加载历史数据记录，共164个时间点")
log_text.pack(fill=BOTH, expand=True)
log_text.configure(state=tk.DISABLED)

# 定义样式
style = ttk.Style()
style.configure("Nav.TFrame", background="#F8F9FA", borderradius=12, boxshadow="0 2px 12px rgba(0,0,0, 0.08)")
style.configure("Card.TFrame", background="#F8F9FA", borderradius=12, boxshadow="0 2px 12px rgba(0,0,0, 0.08)")
style.configure("Gradient.TButton", bootstyle="primary", background="#18A0FB", backgroundactive="#0D47A1", borderradius=12)
style.configure("Button.TButton", borderradius=12)

root.mainloop()
