import json
import os

class ConfigManager:
    def __init__(self):
        # 确保必要的目录存在
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保所需的目录都存在"""
        directories = ['data', 'model', 'outputs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_api_config(self):
        """加载API配置"""
        try:
            if os.path.exists("data/api_config.json"):
                with open("data/api_config.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return {
                "api_key": "",
                "model": "",
                "available_models": [],
                "prompts": {}
            }
        except Exception as e:
            print(f"加载API配置出错: {e}")
            return {
                "api_key": "",
                "model": "",
                "available_models": [],
                "prompts": {}
            }
    
    def save_api_config(self, config):
        """保存API配置"""
        try:
            with open("data/api_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print("API配置已保存")
            return True
        except Exception as e:
            print(f"保存API配置出错: {e}")
            return False
    
    def load_thresholds(self):
        """加载阈值设置"""
        try:
            if os.path.exists("data/thresholds.json"):
                with open("data/thresholds.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"thresholds": {}, "scheduled_times": {}}
        except Exception as e:
            print(f"加载阈值设置时出错: {e}")
            return {"thresholds": {}, "scheduled_times": {}}
    
    def save_thresholds(self, thresholds, scheduled_times):
        """保存阈值设置"""
        data = {
            "thresholds": thresholds,
            "scheduled_times": scheduled_times
        }
        try:
            with open("data/thresholds.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("阈值设置已保存")
            return True
        except Exception as e:
            print(f"保存阈值设置时出错: {e}")
            return False
    
    def load_player_data(self):
        """加载玩家数据"""
        try:
            if os.path.exists("data/player_data.json"):
                with open("data/player_data.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载数据出错: {e}")
            return None
    
    def save_player_data(self, data):
        """保存玩家数据"""
        try:
            with open("data/player_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存 - {data.get('last_update', '')}")
            return True
        except Exception as e:
            print(f"保存数据出错: {e}")
            return False 