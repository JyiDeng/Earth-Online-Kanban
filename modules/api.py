import requests
from datetime import datetime
import os

class APIManager:
    def __init__(self, api_key="", api_model=""):
        self.api_key = api_key
        self.api_model = api_model
    
    def call_siliconflow_api(self, prompt):
        """调用SiliconFlow API进行分析"""
        if not self.api_key:
            print("API未配置")
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
    
    def save_analysis_result(self, state, response, attributes_text):
        """保存AI分析结果到文件"""
        if not response:
            return False
            
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
            return True
        except Exception as e:
            print(f"保存AI分析结果时出错: {e}")
            return False 