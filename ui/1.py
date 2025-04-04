from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
from datetime import datetime, timedelta
import random
import speech_recognition as sr
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd

app = Flask(__name__)
CORS(app)

# 数据存储路径
DATA_DIR = 'data'
HEALTH_DATA_FILE = os.path.join(DATA_DIR, 'health_data.json')
EVENTS_FILE = os.path.join(DATA_DIR, 'events.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
THRESHOLDS_FILE = os.path.join(DATA_DIR, 'thresholds.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
MODEL_FILE = os.path.join(DATA_DIR, 'model.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化语音识别
recognizer = sr.Recognizer()

# 初始化默认数据
def init_default_data():
    default_health_data = {
        "physiological": {
            "hunger": 96,
            "thirst": 86,
            "toilet": 30,
            "social": 49,
            "fatigue": 92,
            "hygiene": 50
        },
        "mental": {
            "fitness": 40,
            "happiness": 99,
            "achievement": 49,
            "eyeFatigue": 89,
            "sleepQuality": 75,
            "heartHealth": 76
        },
        "ability": {
            "muscle": 44,
            "agility": 49,
            "resistance": 48,
            "timeControl": 50,
            "creativity": 51,
            "security": 49
        }
    }

    default_settings = {
        "syncInterval": 5,
        "alertThreshold": 30
    }

    default_thresholds = {
        "hunger": 20,
        "thirst": 20,
        "toilet": 80,
        "social": 30,
        "fatigue": 80,
        "hygiene": 30,
        "fitness": 30,
        "happiness": 30,
        "achievement": 30,
        "eyeFatigue": 80,
        "sleepQuality": 30,
        "heartHealth": 30,
        "muscle": 30,
        "agility": 30,
        "resistance": 30,
        "timeControl": 30,
        "creativity": 30,
        "security": 30
    }

    # 保存默认数据
    if not os.path.exists(HEALTH_DATA_FILE):
        with open(HEALTH_DATA_FILE, 'w') as f:
            json.dump(default_health_data, f)

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f)

    if not os.path.exists(THRESHOLDS_FILE):
        with open(THRESHOLDS_FILE, 'w') as f:
            json.dump(default_thresholds, f)

    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'w') as f:
            json.dump({}, f)

# 加载数据
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# 保存数据
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# 模拟数据变化
def simulate_data_change(data):
    for category in data:
        for key in data[category]:
            # 随机变化范围在-2到2之间
            change = random.uniform(-2, 2)
            new_value = data[category][key] + change
            # 确保值在0-100之间
            data[category][key] = max(0, min(100, new_value))
    return data

# 语音识别
@app.route('/api/speech/record', methods=['POST'])
def record_speech():
    try:
        audio_file = request.files['audio']
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language='zh-CN')
            return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 健康数据同步
@app.route('/api/health/sync', methods=['POST'])
def sync_health_data():
    try:
        health_data = request.json
        # 保存当前数据到历史记录
        history = load_data(HISTORY_FILE) or []
        history.append({
            "timestamp": datetime.now().isoformat(),
            "data": health_data
        })
        save_data(HISTORY_FILE, history)
        
        # 更新当前数据
        save_data(HEALTH_DATA_FILE, health_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# AI分析
@app.route('/api/analysis/ai', methods=['POST'])
def analyze_with_ai():
    try:
        data = request.json
        history = load_data(HISTORY_FILE) or []
        
        # 分析趋势
        trends = analyze_trends(history)
        
        # 生成分析报告
        analysis = generate_ai_analysis(data, trends)
        
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "trends": trends
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 趋势分析
def analyze_trends(history):
    if not history:
        return {}
    
    # 转换为DataFrame
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    trends = {}
    for category in ['physiological', 'mental', 'ability']:
        for key in df['data'].iloc[0][category].keys():
            values = [d[category][key] for d in df['data']]
            # 计算趋势
            x = np.arange(len(values)).reshape(-1, 1)
            y = np.array(values)
            model = LinearRegression().fit(x, y)
            trend = model.coef_[0]
            
            trends[f"{category}_{key}"] = {
                "current": values[-1],
                "trend": trend,
                "change": values[-1] - values[0] if len(values) > 1 else 0
            }
    
    return trends

# 生成AI分析
def generate_ai_analysis(data, trends):
    analysis = []
    
    # 分析生理需求
    physiological = data['physiological']
    if physiological['fatigue'] > 80:
        analysis.append("疲劳度较高，建议适当休息")
    if physiological['hunger'] < 30:
        analysis.append("饱腹度较低，建议及时进食")
    
    # 分析身心状况
    mental = data['mental']
    if mental['eyeFatigue'] > 80:
        analysis.append("视疲劳严重，建议进行眼部放松")
    if mental['sleepQuality'] < 50:
        analysis.append("睡眠质量不佳，建议调整作息")
    
    # 分析能力属性
    ability = data['ability']
    if ability['muscle'] < 40:
        analysis.append("肌肉强度较低，建议增加运动")
    if ability['timeControl'] < 50:
        analysis.append("时间掌控度不足，建议优化时间管理")
    
    # 分析趋势
    for key, trend in trends.items():
        if abs(trend['trend']) > 1:
            category, metric = key.split('_')
            if trend['trend'] > 0:
                analysis.append(f"{metric}呈上升趋势，继续保持")
            else:
                analysis.append(f"{metric}呈下降趋势，需要注意")
    
    return analysis

# 报告生成
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    try:
        report_type = request.json.get('reportType')
        history = load_data(HISTORY_FILE) or []
        
        if report_type == 'weekly':
            # 获取最近7天的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            filtered_data = [d for d in history if 
                           start_date <= datetime.fromisoformat(d['timestamp']) <= end_date]
        else:
            # 获取最近30天的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            filtered_data = [d for d in history if 
                           start_date <= datetime.fromisoformat(d['timestamp']) <= end_date]
        
        # 生成报告
        report = {
            "period": report_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": generate_report_summary(filtered_data),
            "trends": analyze_trends(filtered_data)
        }
        
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_report_summary(data):
    if not data:
        return "无数据"
    
    # 计算平均值
    summary = {}
    for category in ['physiological', 'mental', 'ability']:
        summary[category] = {}
        for key in data[0]['data'][category].keys():
            values = [d['data'][category][key] for d in data]
            summary[category][key] = sum(values) / len(values)
    
    # 生成总结
    report = []
    for category, metrics in summary.items():
        report.append(f"{category}总结：")
        for metric, value in metrics.items():
            report.append(f"- {metric}: {value:.1f}%")
    
    return "\n".join(report)

# 获取健康数据
@app.route('/api/health-data', methods=['GET'])
def get_health_data():
    try:
        health_data = load_data(HEALTH_DATA_FILE)
        if not health_data:
            init_default_data()
            health_data = load_data(HEALTH_DATA_FILE)
        return jsonify(health_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取阈值设置
@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    try:
        thresholds = load_data(THRESHOLDS_FILE)
        if not thresholds:
            init_default_data()
            thresholds = load_data(THRESHOLDS_FILE)
        return jsonify(thresholds)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新阈值设置
@app.route('/api/thresholds', methods=['POST'])
def update_thresholds():
    try:
        thresholds = request.json
        save_data(THRESHOLDS_FILE, thresholds)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取历史数据
@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history = load_data(HISTORY_FILE) or []
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取设置
@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        settings = load_data(SETTINGS_FILE)
        if not settings:
            init_default_data()
            settings = load_data(SETTINGS_FILE)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新设置
@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        settings = request.json
        save_data(SETTINGS_FILE, settings)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 启动服务器
if __name__ == '__main__':
    init_default_data()
    app.run(debug=True, port=5000)