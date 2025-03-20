import time
import numpy as np
from datetime import datetime
from scipy.stats import linregress
import random

class UpdateManager:
    def __init__(self, panel):
        self.panel = panel
        self.update_interval = 300  # 5分钟更新一次
        self.history_save_interval = 300  # 5分钟保存一次历史数据
        self.last_update_time = time.time()
        self.last_save_time = time.time()
        self.trend_window_size = 20  # 趋势分析窗口大小
        
    def update_panel(self):
        """更新面板状态"""
        try:
            current_time = time.time()
            elapsed = current_time - self.last_update_time
            
            # 更新属性值
            self._update_attributes(elapsed)
            
            # 检查是否需要保存历史数据
            if current_time - self.last_save_time >= self.history_save_interval:
                self._save_history_data()
                self.last_save_time = current_time
            
            # 更新最后更新时间
            self.last_update_time = current_time
            
            # 安排下一次更新
            self.panel.root.after(1000, self.update_panel)  # 每秒更新一次
            
        except Exception as e:
            print(f"更新面板时出错: {e}")
            # 即使出错也继续更新
            self.panel.root.after(1000, self.update_panel)
    
    def _update_attributes(self, elapsed):
        """更新所有属性值"""
        try:
            for attr, info in self.panel.attributes.items():
                self._update_attribute_value(attr, info, elapsed)
                self._update_attribute_trend(attr)
                self._update_progress_bar(attr, info)
        except Exception as e:
            print(f"更新属性时出错: {e}")
    
    def _update_attribute_value(self, attr, info, elapsed):
        """更新单个属性值"""
        try:
            # 获取当前值和变化率
            current_value = info["current_value"]
            change_rate = info["change_rate"]
            
            # 计算新值
            new_value = current_value + change_rate * (elapsed / 60)  # 每分钟的变化
            
            # 添加随机波动
            random_factor = random.uniform(-0.1, 0.1)
            new_value += random_factor
            
            # 确保值在0-100之间
            new_value = max(0, min(100, new_value))
            
            # 更新值
            info["current_value"] = new_value
            
        except Exception as e:
            print(f"更新属性 {attr} 值时出错: {e}")
    
    def _update_attribute_trend(self, attr):
        """更新属性趋势"""
        try:
            # 获取历史数据
            values = self.panel.history_data.get("attributes", {}).get(attr, [])
            if len(values) < 2:  # 需要至少两个数据点
                return
            
            # 只使用最近的数据点进行趋势分析
            recent_values = values[-self.trend_window_size:]
            if len(recent_values) < 2:
                return
            
            # 使用简单线性回归分析趋势
            x = np.arange(len(recent_values))
            slope, _, r_value, _, _ = linregress(x, recent_values)
            
            # 保存趋势斜率
            self.panel.attributes[attr]["trend"] = slope
            
            # 根据趋势自动调整变化率
            self._adjust_change_rate(attr, slope, r_value)
            
        except Exception as e:
            print(f"更新属性 {attr} 趋势时出错: {e}")
    
    def _adjust_change_rate(self, attr, slope, r_value):
        """根据趋势调整变化率"""
        try:
            # 只在趋势明显且相关性较高时调整
            if abs(slope) > 0.05 and abs(r_value) > 0.7 and random.random() < 0.3:
                # 计算调整量
                adjustment = slope * 0.01 * abs(r_value)  # 相关性越高，调整越大
                
                # 获取当前变化率
                current_rate = self.panel.attributes[attr]["change_rate"]
                
                # 应用调整，但限制变化率在合理范围内
                new_rate = current_rate + adjustment
                new_rate = max(-0.05, min(0.05, new_rate))  # 限制在 -5% 到 5% 之间
                
                # 更新变化率
                self.panel.attributes[attr]["change_rate"] = new_rate
                
                print(f"自动调整 {attr} 变化率: {new_rate:.4f} (趋势: {slope:.4f}, 相关性: {r_value:.4f})")
            
        except Exception as e:
            print(f"调整属性 {attr} 变化率时出错: {e}")
    
    def _update_progress_bar(self, attr, info):
        """更新进度条显示"""
        try:
            # 更新进度条
            value = info["current_value"]
            info["progress_bar"]["value"] = value
            
            # 更新标签
            info["value_label"]["text"] = f"{value:.1f}%"
            
            # 根据值更新进度条样式
            style = self._get_progress_style(value)
            info["progress_bar"]["bootstyle"] = style
            
        except Exception as e:
            print(f"更新属性 {attr} 进度条时出错: {e}")
    
    def _get_progress_style(self, value):
        """根据值返回进度条样式"""
        if value > 70:
            return "success-striped"
        elif value > 30:
            return "warning-striped"
        else:
            return "danger-striped"
    
    def _save_history_data(self):
        """保存历史数据"""
        try:
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加时间戳
            self.panel.history_data.setdefault("timestamps", []).append(timestamp)
            
            # 添加属性值
            for attr, info in self.panel.attributes.items():
                self.panel.history_data.setdefault("attributes", {}).setdefault(attr, []).append(info["current_value"])
            
            # 限制历史数据长度
            max_history = 100  # 保留最近100个数据点
            if len(self.panel.history_data["timestamps"]) > max_history:
                self.panel.history_data["timestamps"] = self.panel.history_data["timestamps"][-max_history:]
                for attr in self.panel.history_data["attributes"]:
                    self.panel.history_data["attributes"][attr] = self.panel.history_data["attributes"][attr][-max_history:]
            
            # 保存到文件
            self.panel.save_history_data()
            print(f"历史数据已保存 - {timestamp}")
            
        except Exception as e:
            print(f"保存历史数据时出错: {e}") 