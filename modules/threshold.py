import time
from datetime import datetime

class ThresholdManager:
    def __init__(self, panel):
        self.panel = panel
        self.check_interval = 60  # 每分钟检查一次
        self.last_check_time = {}  # 记录每个属性的上次检查时间
        self.operator_text = {
            "<": "低于",
            ">": "高于",
            "<=": "不高于",
            ">=": "不低于",
            "==": "等于"
        }
    
    def check_thresholds(self):
        """检查阈值并发送提醒"""
        try:
            now = time.time()
            current_time = datetime.now().strftime("%H:%M")
            
            # 检查定时提醒
            self._check_scheduled_times(current_time)
            
            # 检查属性阈值
            self._check_attribute_thresholds(now)
            
        except Exception as e:
            print(f"检查阈值时出错: {e}")
        finally:
            # 安排下一次检查
            self.panel.root.after(self.check_interval * 1000, self.check_thresholds)
    
    def _check_scheduled_times(self, current_time):
        """检查定时提醒"""
        try:
            for time_str in self.panel.scheduled_times.get("times", []):
                if time_str and time_str == current_time:
                    self.panel.alert_manager.show_alert(
                        "定时提醒",
                        f"现在是 {time_str}，请检查您的状态。"
                    )
        except Exception as e:
            print(f"检查定时提醒时出错: {e}")
    
    def _check_attribute_thresholds(self, now):
        """检查属性阈值"""
        try:
            for attr, info in self.panel.attributes.items():
                # 获取阈值设置
                threshold_info = self.panel.thresholds.get(attr, {})
                if not threshold_info:
                    continue
                
                try:
                    # 获取阈值参数
                    threshold_value = float(threshold_info.get("value", 0))
                    interval = int(threshold_info.get("interval", 30)) * 60  # 转换为秒
                    operator = threshold_info.get("operator", ">")
                    
                    # 获取当前值
                    current_value = info["current_value"]
                    
                    # 检查是否需要提醒
                    if self._should_alert(attr, current_value, threshold_value, operator, interval, now):
                        self._show_threshold_alert(attr, current_value, threshold_value, operator)
                        self.last_check_time[attr] = now
                    
                except (ValueError, TypeError) as e:
                    print(f"检查属性 {attr} 的阈值时出错: {e}")
                    continue
                
        except Exception as e:
            print(f"检查属性阈值时出错: {e}")
    
    def _should_alert(self, attr, current_value, threshold_value, operator, interval, now):
        """检查是否应该发送提醒"""
        try:
            # 检查时间间隔
            last_time = self.last_check_time.get(attr, 0)
            if now - last_time < interval:
                return False
            
            # 检查阈值条件
            return self._check_threshold_condition(current_value, threshold_value, operator)
            
        except Exception as e:
            print(f"检查是否应该提醒时出错: {e}")
            return False
    
    def _check_threshold_condition(self, current_value, threshold_value, operator):
        """检查是否满足阈值条件"""
        try:
            if operator == "<":
                return current_value < threshold_value
            elif operator == ">":
                return current_value > threshold_value
            elif operator == "<=":
                return current_value <= threshold_value
            elif operator == ">=":
                return current_value >= threshold_value
            elif operator == "==":
                return abs(current_value - threshold_value) < 0.01
            return False
        except Exception as e:
            print(f"检查阈值条件时出错: {e}")
            return False
    
    def _show_threshold_alert(self, attr, current_value, threshold_value, operator):
        """显示阈值提醒"""
        try:
            operator_text = self.operator_text.get(operator, "")
            message = (
                f"{self.panel.icons.get(attr, '')} {attr} 当前值为 {current_value:.1f}，"
                f"{operator_text}阈值 {threshold_value:.1f}"
            )
            self.panel.alert_manager.show_alert("阈值提醒", message)
        except Exception as e:
            print(f"显示阈值提醒时出错: {e}")
    
    def update_threshold_text(self):
        """更新阈值提醒文本显示"""
        try:
            if not hasattr(self.panel, 'threshold_text'):
                return
            
            self.panel.threshold_text.delete(1.0, "end")
            
            # 添加阈值信息
            for attr, info in self.panel.thresholds.items():
                if "value" not in info:
                    continue
                
                value = info["value"]
                interval = info.get("interval", 30)
                operator = info.get("operator", ">")
                
                text = f"{self.panel.icons.get(attr, '')} {attr}: {operator} {value:.1f} (间隔: {interval}分钟)\n"
                self.panel.threshold_text.insert("end", text)
            
            # 添加定时提醒信息
            self.panel.threshold_text.insert("end", "\n定时提醒:\n")
            for time_str in self.panel.scheduled_times.get("times", []):
                if time_str:
                    self.panel.threshold_text.insert("end", f"⏰ {time_str}\n")
            
        except Exception as e:
            print(f"更新阈值提醒文本时出错: {e}")
    
    def add_scheduled_time(self, time_str):
        """添加定时提醒时间"""
        try:
            if time_str and time_str not in self.panel.scheduled_times.get("times", []):
                self.panel.scheduled_times.setdefault("times", []).append(time_str)
                self.update_threshold_text()
                return True
            return False
        except Exception as e:
            print(f"添加定时提醒时间时出错: {e}")
            return False
    
    def remove_scheduled_time(self, time_str):
        """删除定时提醒时间"""
        try:
            times = self.panel.scheduled_times.get("times", [])
            if time_str in times:
                times.remove(time_str)
                self.update_threshold_text()
                return True
            return False
        except Exception as e:
            print(f"删除定时提醒时间时出错: {e}")
            return False
    
    def set_threshold(self, attr, value, interval=30, operator=">"):
        """设置属性阈值"""
        try:
            self.panel.thresholds[attr] = {
                "value": float(value),
                "interval": int(interval),
                "operator": operator
            }
            self.update_threshold_text()
            return True
        except (ValueError, TypeError) as e:
            print(f"设置属性 {attr} 的阈值时出错: {e}")
            return False
    
    def remove_threshold(self, attr):
        """删除属性阈值"""
        try:
            if attr in self.panel.thresholds:
                del self.panel.thresholds[attr]
                self.update_threshold_text()
                return True
            return False
        except Exception as e:
            print(f"删除属性 {attr} 的阈值时出错: {e}")
            return False 