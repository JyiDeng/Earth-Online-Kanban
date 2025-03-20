import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import os

class ModelManager:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载已训练的模型"""
        model_path = "model/event_model.pkl"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print("已成功加载训练模型")
                return True
            except Exception as e:
                print(f"加载模型时出错: {e}")
                return False
        return False
    
    def save_model(self):
        """保存训练好的模型"""
        if not self.model:
            return False
            
        model_path = "model/event_model.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print("模型已成功保存")
            return True
        except Exception as e:
            print(f"保存模型时出错: {e}")
            return False
    
    def train_model(self):
        """训练机器学习模型以预测事件影响值"""
        try:
            # 加载数据
            data = pd.read_csv('model/event_data.csv')
            
            # 特征和目标
            X = pd.get_dummies(data[['event_name', 'attribute']])
            y = data['impact_value']
            
            # 拆分数据集
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 训练模型
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            
            print(f"模型训练完成，特征数量: {len(self.model.feature_names_in_)}")
            return True
        except Exception as e:
            print(f"训练模型时出错: {e}")
            return False
    
    def predict_impact(self, event_name, attribute):
        """预测事件对属性的影响值"""
        if self.model is None:
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
            return 0 