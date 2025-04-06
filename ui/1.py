from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import time
from datetime import datetime, timedelta
import random
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import traceback
import threading
import tempfile
import atexit
import signal
import speech_recognition as sr
import base64
import sys

app = Flask(__name__, static_folder='.', static_url_path='')
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

# 禁用语音识别功能，使用模拟响应
@app.route('/api/speech/record', methods=['POST'])
def record_speech():
    try:
        print("接收到语音识别请求 - 使用模拟响应")
        return jsonify({
            "status": "success", 
            "text": "模拟语音识别结果：有氧运动30分钟"
        })
    except Exception as e:
        print(f"语音识别处理错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# 释放语音识别资源
@app.route('/api/speech/cleanup', methods=['POST'])
def cleanup_speech():
    return jsonify({"status": "success", "message": "模拟释放资源成功"})

# 初始化默认数据
def init_default_data():
    print("初始化默认数据...")
    default_health_data = {
        "physiological": {
            "hunger": 70,
            "thirst": 70,
            "toilet": 50,
            "social": 60,
            "fatigue": 40,
            "hygiene": 80
        },
        "mental": {
            "fitness": 65,
            "happiness": 75,
            "achievement": 60,
            "eyeFatigue": 30,
            "sleepQuality": 70,
            "heartHealth": 80
        },
        "ability": {
            "muscle": 55,
            "agility": 60,
            "resistance": 65,
            "timeControl": 50,
            "creativity": 70,
            "security": 75
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
        print(f"健康数据文件不存在，创建新文件: {HEALTH_DATA_FILE}")
        with open(HEALTH_DATA_FILE, 'w') as f:
            json.dump(default_health_data, f)
    else:
        print(f"健康数据文件已存在: {HEALTH_DATA_FILE}")
        # 检查文件内容
        try:
            with open(HEALTH_DATA_FILE, 'r') as f:
                existing_data = json.load(f)
            print(f"现有健康数据: {existing_data}")
            
            # 检查数据是否完整
            if (not existing_data or 
                not all(key in existing_data for key in ['physiological', 'mental', 'ability']) or
                not existing_data['physiological'] or not existing_data['mental'] or not existing_data['ability']):
                
                print("现有健康数据结构不完整，使用默认值覆盖")
                with open(HEALTH_DATA_FILE, 'w') as f:
                    json.dump(default_health_data, f)
                print(f"已保存默认健康数据")
        except Exception as e:
            print(f"读取健康数据文件出错: {e}，使用默认值覆盖")
            with open(HEALTH_DATA_FILE, 'w') as f:
                json.dump(default_health_data, f)

    if not os.path.exists(SETTINGS_FILE):
        print(f"设置文件不存在，创建新文件: {SETTINGS_FILE}")
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f)

    if not os.path.exists(THRESHOLDS_FILE):
        print(f"阈值文件不存在，创建新文件: {THRESHOLDS_FILE}")
        with open(THRESHOLDS_FILE, 'w') as f:
            json.dump(default_thresholds, f)

    if not os.path.exists(EVENTS_FILE):
        print(f"事件文件不存在，创建新文件: {EVENTS_FILE}")
        with open(EVENTS_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(HISTORY_FILE):
        print(f"历史文件不存在，创建新文件: {HISTORY_FILE}")
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(MODEL_FILE):
        print(f"模型文件不存在，创建新文件: {MODEL_FILE}")
        with open(MODEL_FILE, 'w') as f:
            json.dump({}, f)
            
    print("初始化默认数据完成")

# 加载数据
def load_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"从 {file_path} 加载数据成功")
            return data
        else:
            print(f"文件不存在: {file_path}")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 {file_path}: {e}")
        # 备份损坏的文件
        if os.path.exists(file_path):
            backup_path = f"{file_path}.bak.{int(time.time())}"
            try:
                os.rename(file_path, backup_path)
                print(f"已备份损坏的文件到 {backup_path}")
            except Exception as backup_error:
                print(f"备份文件失败: {backup_error}")
        return None
    except Exception as e:
        print(f"加载数据错误 {file_path}: {e}")
        return None

# 保存数据
def save_data(file_path, data):
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"数据已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"保存数据错误 {file_path}: {e}")
        return False

# 模拟数据变化
def simulate_data_change(data):
    for category in data:
        for key in data[category]:
            # 随机变化范围在-2到2之间，但大部分情况下不变
            if random.random() < 0.3:  # 只有30%的概率改变
                change = random.uniform(-1, 1)
                new_value = data[category][key] + change
                # 确保值在0-100之间
                data[category][key] = max(0, min(100, new_value))
    return data

# 健康数据同步
@app.route('/api/health/sync', methods=['POST'])
def sync_health_data():
    try:
        health_data = request.json
        if not health_data:
            return jsonify({"status": "error", "message": "未提供健康数据"}), 400
            
        # 验证数据格式
        if not all(key in health_data for key in ["physiological", "mental", "ability"]):
            return jsonify({"status": "error", "message": "健康数据格式错误"}), 400
        
        # 保存数据
        save_data(HEALTH_DATA_FILE, health_data)
        
        # 添加到历史记录
        history = load_data(HISTORY_FILE) or []
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": health_data
        }
        history.append(history_entry)
        
        # 只保留最近50条记录
        if len(history) > 50:
            history = history[-50:]
            
        save_data(HISTORY_FILE, history)
        
        # 模拟数据小变化
        health_data = simulate_data_change(health_data)
        
        # 分析健康数据
        analysis = analyze_data(health_data)
        
        return jsonify({
            "status": "success",
            "message": "数据同步成功",
            "data": health_data,
            "analysis": analysis
        })
    except Exception as e:
        print(f"同步健康数据错误: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 分析健康数据
def analyze_data(health_data):
    # 简单分析，找出最低和最高的指标
    lowest = {"category": "", "name": "", "value": 100}
    highest = {"category": "", "name": "", "value": 0}
    
    for category, metrics in health_data.items():
        for name, value in metrics.items():
            if value < lowest["value"]:
                lowest = {"category": category, "name": name, "value": value}
            if value > highest["value"]:
                highest = {"category": category, "name": name, "value": value}
    
    # 生成分析结果
    analysis = {
        "summary": f"当前状态: {'良好' if lowest['value'] > 30 else '需要注意'}",
        "lowest": lowest,
        "highest": highest,
        "recommendations": []
    }
    
    # 根据最低值给出建议
    if lowest["name"] == "hunger":
        analysis["recommendations"].append("建议: 适当进食，补充能量")
    elif lowest["name"] == "thirst":
        analysis["recommendations"].append("建议: 及时补充水分")
    elif lowest["name"] == "social":
        analysis["recommendations"].append("建议: 增加社交活动")
    elif lowest["name"] == "hygiene":
        analysis["recommendations"].append("建议: 注意个人卫生")
    elif lowest["name"] == "fitness":
        analysis["recommendations"].append("建议: 增加锻炼活动")
    elif lowest["name"] == "happiness":
        analysis["recommendations"].append("建议: 做些让自己开心的事")
    
    return analysis

# 获取健康数据
@app.route('/api/health-data', methods=['GET'])
def get_health_data():
    try:
        health_data = load_data(HEALTH_DATA_FILE)
        if not health_data:
            # 初始化默认数据
            init_default_data()
            health_data = load_data(HEALTH_DATA_FILE)
            
        return jsonify(health_data)
    except Exception as e:
        print(f"获取健康数据错误: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 获取阈值设置
@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    try:
        thresholds = load_data(THRESHOLDS_FILE)
        if not thresholds:
            # 初始化默认数据
            init_default_data()
            thresholds = load_data(THRESHOLDS_FILE)
            
        return jsonify(thresholds)
    except Exception as e:
        print(f"获取阈值设置错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 更新阈值设置
@app.route('/api/thresholds', methods=['POST'])
def update_thresholds():
    try:
        thresholds = request.json
        save_data(THRESHOLDS_FILE, thresholds)
        return jsonify({"status": "success", "message": "阈值设置已更新"})
    except Exception as e:
        print(f"更新阈值设置错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 获取事件列表
@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = load_data(EVENTS_FILE) or []
        return jsonify(events)
    except Exception as e:
        print(f"获取事件列表错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 创建事件
@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        event_data = request.json
        if not event_data:
            return jsonify({"status": "error", "message": "未提供事件数据"}), 400
            
        # 验证事件数据
        if not all(key in event_data for key in ["type", "name", "duration"]):
            return jsonify({"status": "error", "message": "事件数据格式错误"}), 400
        
        # 添加事件ID和时间戳
        event_data["id"] = str(int(time.time()))
        event_data["timestamp"] = datetime.now().isoformat()
        
        # 保存事件
        events = load_data(EVENTS_FILE) or []
        events.append(event_data)
        save_data(EVENTS_FILE, events)
        
        return jsonify({"status": "success", "message": "事件已创建", "event": event_data})
    except Exception as e:
        print(f"创建事件错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 删除事件
@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        events = load_data(EVENTS_FILE) or []
        events = [event for event in events if event.get("id") != event_id]
        save_data(EVENTS_FILE, events)
        return jsonify({"status": "success", "message": "事件已删除"})
    except Exception as e:
        print(f"删除事件错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 获取事件建议
@app.route('/api/event-suggestions', methods=['GET'])
def get_event_suggestions():
    suggestions = {
        "学习": ["阅读专业书籍", "学习编程", "看视频课程", "做习题"],
        "运动": ["慢跑30分钟", "健身房锻炼", "打篮球", "游泳"],
        "睡觉": ["午休20分钟", "晚上早睡", "提前半小时上床"],
        "社交": ["与朋友聚餐", "参加社区活动", "打电话给家人"],
        "饮食": ["健康早餐", "按时吃午餐", "晚餐少食", "多喝水"],
        "娱乐": ["看电影", "玩游戏", "听音乐", "看书"],
        "工作": ["专注工作", "处理邮件", "开会", "写文档"],
        "休息": ["冥想", "放松", "闭目养神"],
        "如厕": ["定时如厕"],
        "展览/讲座": ["参观艺术展", "听讲座", "看展览"],
        "复盘/冥想": ["每日复盘", "冥想15分钟", "反思"],
        "洗漱/沐浴": ["洗澡", "护肤", "刷牙"]
    }
    return jsonify(suggestions)

# 计算事件影响
@app.route('/api/event-impact', methods=['POST'])
def calculate_event_impact():
    try:
        event_data = request.json
        if not event_data:
            return jsonify({"status": "error", "message": "未提供事件数据"}), 400
            
        # 验证事件数据
        if not all(key in event_data for key in ["type", "name", "duration"]):
            return jsonify({"status": "error", "message": "事件数据格式错误"}), 400
        
        # 获取当前健康数据
        health_data = load_data(HEALTH_DATA_FILE)
        if not health_data:
            init_default_data()
            health_data = load_data(HEALTH_DATA_FILE)
        
        # 根据事件类型计算影响
        impact = {}
        event_type = event_data["type"]
        duration = float(event_data["duration"])
        
        if event_type == "学习":
            impact["achievement"] = {"current": health_data["mental"]["achievement"], "change": min(10, duration * 2), "new": min(100, health_data["mental"]["achievement"] + min(10, duration * 2))}
            impact["eyeFatigue"] = {"current": health_data["mental"]["eyeFatigue"], "change": min(15, duration * 3), "new": min(100, health_data["mental"]["eyeFatigue"] + min(15, duration * 3))}
            impact["fatigue"] = {"current": health_data["physiological"]["fatigue"], "change": min(5, duration), "new": min(100, health_data["physiological"]["fatigue"] + min(5, duration))}
            
        elif event_type == "运动":
            impact["fitness"] = {"current": health_data["mental"]["fitness"], "change": min(15, duration * 3), "new": min(100, health_data["mental"]["fitness"] + min(15, duration * 3))}
            impact["muscle"] = {"current": health_data["ability"]["muscle"], "change": min(10, duration * 2), "new": min(100, health_data["ability"]["muscle"] + min(10, duration * 2))}
            impact["agility"] = {"current": health_data["ability"]["agility"], "change": min(8, duration * 1.5), "new": min(100, health_data["ability"]["agility"] + min(8, duration * 1.5))}
            impact["fatigue"] = {"current": health_data["physiological"]["fatigue"], "change": min(20, duration * 4), "new": min(100, health_data["physiological"]["fatigue"] + min(20, duration * 4))}
            impact["thirst"] = {"current": health_data["physiological"]["thirst"], "change": -min(15, duration * 3), "new": max(0, health_data["physiological"]["thirst"] - min(15, duration * 3))}
            impact["hunger"] = {"current": health_data["physiological"]["hunger"], "change": -min(10, duration * 2), "new": max(0, health_data["physiological"]["hunger"] - min(10, duration * 2))}
            
        elif event_type == "睡觉":
            impact["fatigue"] = {"current": health_data["physiological"]["fatigue"], "change": -min(50, duration * 7), "new": max(0, health_data["physiological"]["fatigue"] - min(50, duration * 7))}
            impact["sleepQuality"] = {"current": health_data["mental"]["sleepQuality"], "change": min(30, duration * 4), "new": min(100, health_data["mental"]["sleepQuality"] + min(30, duration * 4))}
            impact["eyeFatigue"] = {"current": health_data["mental"]["eyeFatigue"], "change": -min(40, duration * 5), "new": max(0, health_data["mental"]["eyeFatigue"] - min(40, duration * 5))}
            
        elif event_type == "社交":
            impact["social"] = {"current": health_data["physiological"]["social"], "change": min(25, duration * 5), "new": min(100, health_data["physiological"]["social"] + min(25, duration * 5))}
            impact["happiness"] = {"current": health_data["mental"]["happiness"], "change": min(15, duration * 3), "new": min(100, health_data["mental"]["happiness"] + min(15, duration * 3))}
            impact["fatigue"] = {"current": health_data["physiological"]["fatigue"], "change": min(5, duration), "new": min(100, health_data["physiological"]["fatigue"] + min(5, duration))}
            
        elif event_type == "饮食":
            impact["hunger"] = {"current": health_data["physiological"]["hunger"], "change": min(40, duration * 40), "new": min(100, health_data["physiological"]["hunger"] + min(40, duration * 40))}
            impact["thirst"] = {"current": health_data["physiological"]["thirst"], "change": min(20, duration * 20), "new": min(100, health_data["physiological"]["thirst"] + min(20, duration * 20))}
            impact["toilet"] = {"current": health_data["physiological"]["toilet"], "change": min(10, duration * 10), "new": min(100, health_data["physiological"]["toilet"] + min(10, duration * 10))}
            
        elif event_type == "如厕":
            impact["toilet"] = {"current": health_data["physiological"]["toilet"], "change": -min(80, duration * 80), "new": max(0, health_data["physiological"]["toilet"] - min(80, duration * 80))}
            
        elif event_type == "洗漱/沐浴":
            impact["hygiene"] = {"current": health_data["physiological"]["hygiene"], "change": min(50, duration * 50), "new": min(100, health_data["physiological"]["hygiene"] + min(50, duration * 50))}
            
        else:
            # 默认影响，针对其他类型
            impact["happiness"] = {"current": health_data["mental"]["happiness"], "change": min(5, duration), "new": min(100, health_data["mental"]["happiness"] + min(5, duration))}
            impact["fatigue"] = {"current": health_data["physiological"]["fatigue"], "change": min(2, duration * 0.5), "new": min(100, health_data["physiological"]["fatigue"] + min(2, duration * 0.5))}
        
        # 应用默认变化
        # 如厕需求随时间增长
        if "toilet" not in impact:
            impact["toilet"] = {"current": health_data["physiological"]["toilet"], "change": min(2, duration * 0.4), "new": min(100, health_data["physiological"]["toilet"] + min(2, duration * 0.4))}
        
        # 饥饿感随时间增长
        if "hunger" not in impact:
            impact["hunger"] = {"current": health_data["physiological"]["hunger"], "change": -min(3, duration * 0.5), "new": max(0, health_data["physiological"]["hunger"] - min(3, duration * 0.5))}
        
        # 口渴感随时间增长
        if "thirst" not in impact:
            impact["thirst"] = {"current": health_data["physiological"]["thirst"], "change": -min(4, duration * 0.6), "new": max(0, health_data["physiological"]["thirst"] - min(4, duration * 0.6))}
        
        return jsonify({
            "status": "success",
            "event": event_data,
            "impact": impact
        })
        
    except Exception as e:
        print(f"计算事件影响错误: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 服务根目录
@app.route('/')
def index():
    return send_file('1.html')

# 事件页面
@app.route('/event')
def event():
    return send_file('event.html')

# 静态文件
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# 全局错误处理
@app.errorhandler(Exception)
def handle_error(e):
    print(f"全局错误处理: {str(e)}")
    traceback.print_exc()
    return jsonify({"status": "error", "message": "服务器内部错误"}), 500

# 清理函数，用于释放资源
def cleanup_resources():
    print("清理资源...")
    
    # 释放语音识别器资源
    if hasattr(app, 'active_recognizer') and app.active_recognizer is not None:
        try:
            # 确保麦克风资源被释放
            if hasattr(app.active_recognizer, 'audio'):
                app.active_recognizer.audio = None
            
            if hasattr(app.active_recognizer, 'microphone'):
                app.active_recognizer.microphone = None
                
            app.active_recognizer = None
            print("语音识别器资源已释放")
        except Exception as e:
            print(f"释放语音识别器资源时出错: {e}")
    
    print("所有资源清理完成")

# 注册信号处理器
def register_signal_handlers():
    # 注册清理函数在程序退出时执行
    atexit.register(cleanup_resources)
    
    # 处理各种信号
    signal.signal(signal.SIGINT, lambda sig, frame: handle_exit_signal('SIGINT'))
    signal.signal(signal.SIGTERM, lambda sig, frame: handle_exit_signal('SIGTERM'))
    
    if hasattr(signal, 'SIGBREAK'):  # Windows特有
        signal.signal(signal.SIGBREAK, lambda sig, frame: handle_exit_signal('SIGBREAK'))
        
    print("已注册信号处理器和退出清理函数")

def handle_exit_signal(sig_name):
    print(f"收到信号 {sig_name}，正在清理资源并退出...")
    cleanup_resources()
    sys.exit(0)

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    
    # 创建临时文件保存上传的音频
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        audio_file.save(temp_file.name)
        temp_filename = temp_file.name
    
    try:
        # 创建新的识别器实例
        recognizer = sr.Recognizer()
        app.active_recognizer = recognizer
        
        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)
            
            try:
                # 使用Google API进行语音识别
                text = recognizer.recognize_google(audio_data, language='zh-CN')
                print(f"语音识别结果: {text}")
                return jsonify({'text': text})
            except sr.UnknownValueError:
                print("Google Speech Recognition 无法理解音频")
                return jsonify({'error': 'Could not understand audio'}), 400
            except sr.RequestError as e:
                print(f"无法从Google Speech Recognition服务请求结果; {e}")
                return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        print(f"语音识别过程中出错: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # 无论如何都要删除临时文件
        try:
            os.unlink(temp_filename)
        except:
            pass
        
        # 释放资源
        app.active_recognizer = None

# 启动服务器
if __name__ == '__main__':
    # 注册信号处理器
    register_signal_handlers()
    
    # 初始化默认数据
    init_default_data()
    # 启动应用
    print("启动应用服务器...")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("键盘中断，正在关闭服务器...")
        cleanup_resources()
    except Exception as e:
        print(f"服务器异常: {e}")
        traceback.print_exc()
        cleanup_resources()
    finally:
        print("服务器已关闭")