from flask import Flask, request, jsonify, send_file, send_from_directory
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
import traceback

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

# 初始化语音识别
recognizer = sr.Recognizer()

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
        data = request.json
        print(f"收到健康数据同步请求: {data}")
        
        # 验证数据结构
        if (not data or 
            not all(key in data for key in ['physiological', 'mental', 'ability']) or
            not data['physiological'] or not data['mental'] or not data['ability']):
            
            print("同步请求中的健康数据结构不完整，使用默认值")
            
            # 使用默认值
            data = {
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
        
        # 保存当前数据到历史记录
        history = load_data(HISTORY_FILE) or []
        history.append({
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        save_data(HISTORY_FILE, history)
        
        # 更新当前数据
        save_data(HEALTH_DATA_FILE, data)
        print(f"健康数据同步成功: {data}")
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"健康数据同步错误: {e}")
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
        print(f"获取健康数据: {health_data}")
        
        # 检查健康数据是否为None或空对象或结构不完整
        if (not health_data or 
            not all(key in health_data for key in ['physiological', 'mental', 'ability']) or
            not health_data['physiological'] or not health_data['mental'] or not health_data['ability']):
            
            print("健康数据为空或结构不完整，使用默认值")
            
            # 使用默认值
            health_data = {
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
            
            # 保存默认数据
            save_data(HEALTH_DATA_FILE, health_data)
            print(f"保存了默认健康数据: {health_data}")
        
        return jsonify(health_data)
    except Exception as e:
        print(f"获取健康数据错误: {e}")
        return jsonify({"error": str(e)}), 500

# 获取阈值设置
@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    try:
        thresholds = load_data(THRESHOLDS_FILE) or {
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

# 事件相关API
@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = load_data(EVENTS_FILE) or []
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        event_data = request.json
        events = load_data(EVENTS_FILE) or []
        event_data['id'] = str(len(events) + 1)
        event_data['timestamp'] = datetime.now().isoformat()
        events.append(event_data)
        save_data(EVENTS_FILE, events)
        return jsonify({"status": "success", "event": event_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<event_id>', methods=['POST'])
def update_event(event_id):
    try:
        event_data = request.json
        events = load_data(EVENTS_FILE) or []
        for i, event in enumerate(events):
            if event['id'] == event_id:
                events[i] = {**event, **event_data}
                save_data(EVENTS_FILE, events)
                return jsonify({"status": "success", "event": events[i]})
        return jsonify({"error": "Event not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        events = load_data(EVENTS_FILE) or []
        events = [event for event in events if event['id'] != event_id]
        save_data(EVENTS_FILE, events)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/event-suggestions', methods=['GET'])
def get_event_suggestions():
    try:
        suggestions = {
            "学习": ["阅读专业书籍", "在线课程学习", "编程练习", "写作训练"],
            "运动": ["跑步", "力量训练", "游泳", "瑜伽"],
            "睡觉": ["午休", "夜间睡眠", "小憩", "深度睡眠"],
            "社交": ["朋友聚会", "团队会议", "社交活动", "网络社交"],
            "饮食": ["健康饮食", "适量饮水", "定时进食", "均衡营养"],
            "娱乐": ["看电影", "听音乐", "玩游戏", "户外活动"],
            "工作": ["制定计划", "时间管理", "任务分解", "团队协作"],
            "休息": ["午休", "夜间睡眠", "小憩", "深度睡眠"],
            "如厕": ["如厕"],
            "展览/讲座": ["参观展览", "听讲座", "参加研讨会", "学术交流"],
            "复盘/冥想": ["每日复盘", "冥想练习", "自我反思", "情绪管理"],
            "洗漱/沐浴": ["洗漱", "沐浴", "个人卫生", "整理仪容"]
        }
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/event-impact', methods=['POST'])
def calculate_event_impact():
    try:
        data = request.json
        print(f"收到事件影响计算请求: {data}")
        
        event_type = data.get('type')
        duration = float(data.get('duration', 1.0))
        event_name = data.get('name', '')
        
        # 获取当前健康数据
        health_data = load_data(HEALTH_DATA_FILE) or {}
        print(f"事件影响计算中获取的健康数据: {health_data}")
        
        # 检查健康数据是否为None或空对象或结构不完整
        if (not health_data or 
            not all(key in health_data for key in ['physiological', 'mental', 'ability']) or
            not health_data['physiological'] or not health_data['mental'] or not health_data['ability']):
            
            print("事件计算中：健康数据为空或结构不完整，使用默认值")
            
            # 使用默认值
            health_data = {
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
            
            # 保存默认数据
            save_data(HEALTH_DATA_FILE, health_data)
            print(f"事件计算中：保存了默认健康数据")
        
        # 定义事件类型和指标的关系映射
        relationships = {
            "学习": ["成就感", "创造力", "视疲劳", "疲惫度", "时间掌控度"],
            "运动": ["饱腹度", "瘦身指数", "肌肉强度", "抗击打能力", "敏捷度", "疲惫度", "睡眠质量"],
            "睡觉": ["疲惫度", "视疲劳", "睡眠质量", "心脏健康度"],
            "社交": ["社交需求", "幸福感", "安全感", "疲惫度"],
            "饮食": ["饱腹度", "口渴度", "如厕需求"],
            "娱乐": ["幸福感", "社交需求", "视疲劳", "疲惫度"],
            "工作": ["成就感", "疲惫度", "视疲劳", "时间掌控度", "创造力"],
            "休息": ["疲惫度", "视疲劳", "睡眠质量"],
            "如厕": ["如厕需求"],
            "展览/讲座": ["成就感", "创造力", "社交需求"],
            "复盘/冥想": ["时间掌控度", "创造力", "幸福感", "安全感"],
            "洗漱/沐浴": ["卫生状况", "幸福感"]
        }
        
        # 定义影响系数（正值为增加，负值为减少）
        impact_coefficients = {
            "学习": {
                "成就感": 10.0,
                "创造力": 5.0,
                "视疲劳": 8.0,
                "疲惫度": 7.0,
                "时间掌控度": 5.0
            },
            "运动": {
                "饱腹度": -5.0,
                "瘦身指数": 8.0,
                "肌肉强度": 10.0,
                "抗击打能力": 6.0,
                "敏捷度": 7.0,
                "疲惫度": 15.0,
                "睡眠质量": 5.0
            },
            "睡觉": {
                "疲惫度": -20.0,
                "视疲劳": -15.0,
                "睡眠质量": 20.0,
                "心脏健康度": 5.0
            },
            "社交": {
                "社交需求": -15.0,
                "幸福感": 10.0,
                "安全感": 5.0,
                "疲惫度": 5.0
            },
            "饮食": {
                "饱腹度": 20.0,
                "口渴度": 10.0,
                "如厕需求": 10.0
            },
            "娱乐": {
                "幸福感": 15.0,
                "社交需求": -5.0,
                "视疲劳": 10.0,
                "疲惫度": 5.0
            },
            "工作": {
                "成就感": 12.0,
                "疲惫度": 10.0,
                "视疲劳": 8.0,
                "时间掌控度": 7.0,
                "创造力": 6.0
            },
            "休息": {
                "疲惫度": -15.0,
                "视疲劳": -10.0,
                "睡眠质量": 10.0
            },
            "如厕": {
                "如厕需求": -30.0
            },
            "展览/讲座": {
                "成就感": 8.0,
                "创造力": 9.0,
                "社交需求": -7.0
            },
            "复盘/冥想": {
                "时间掌控度": 9.0,
                "创造力": 8.0,
                "幸福感": 7.0,
                "安全感": 6.0
            },
            "洗漱/沐浴": {
                "卫生状况": 20.0,
                "幸福感": 8.0
            }
        }
        
        # 定义中文指标名称到英文名称的映射
        zh_en_map = {
            "饱腹度": "hunger",
            "口渴度": "thirst",
            "如厕需求": "toilet",
            "社交需求": "social",
            "疲惫度": "fatigue",
            "卫生状况": "hygiene",
            "瘦身指数": "fitness",
            "幸福感": "happiness",
            "成就感": "achievement",
            "视疲劳": "eyeFatigue",
            "睡眠质量": "sleepQuality",
            "心脏健康度": "heartHealth",
            "肌肉强度": "muscle",
            "敏捷度": "agility",
            "抗击打能力": "resistance",
            "时间掌控度": "timeControl",
            "创造力": "creativity",
            "安全感": "security"
        }
        
        # 计算影响
        impact = {}
        
        # 根据事件类型和影响系数计算
        for chinese_metric in relationships.get(event_type, []):
            if chinese_metric in impact_coefficients.get(event_type, {}):
                # 找到对应的英文键名
                english_key = zh_en_map.get(chinese_metric)
                if not english_key:
                    continue
                    
                # 添加一些随机波动，使相同类型的不同具体事件有略微不同的影响
                random_factor = random.uniform(0.9, 1.1)
                base_impact = impact_coefficients[event_type][chinese_metric] * duration * random_factor
                
                # 找到键对应的类别
                category = None
                if english_key in health_data.get('physiological', {}):
                    category = 'physiological'
                elif english_key in health_data.get('mental', {}):
                    category = 'mental'
                elif english_key in health_data.get('ability', {}):
                    category = 'ability'
                
                if category:
                    current_value = health_data[category][english_key]
                    new_value = max(0, min(100, current_value + base_impact))
                    impact[english_key] = {
                        "current": current_value,
                        "new": new_value,
                        "change": new_value - current_value
                    }
        
        # 确保有预测结果
        if not impact:
            print(f"未能生成有效的影响预测: 事件类型={event_type}")
            # 为不同类型的事件添加默认影响
            if event_type in ['学习', '工作']:
                impact['achievement'] = {
                    "current": health_data['mental']['achievement'],
                    "new": min(100, health_data['mental']['achievement'] + 10),
                    "change": 10
                }
            elif event_type in ['睡觉', '休息']:
                impact['fatigue'] = {
                    "current": health_data['physiological']['fatigue'],
                    "new": max(0, health_data['physiological']['fatigue'] - 20),
                    "change": -20
                }
            elif event_type in ['社交', '娱乐']:
                impact['happiness'] = {
                    "current": health_data['mental']['happiness'],
                    "new": min(100, health_data['mental']['happiness'] + 15),
                    "change": 15
                }
            else:
                # 通用默认影响
                impact['happiness'] = {
                    "current": health_data['mental']['happiness'],
                    "new": min(100, health_data['mental']['happiness'] + 5),
                    "change": 5
                }
        
        response_data = {
            "status": "success",
            "event": {
                "name": event_name,
                "type": event_type,
                "duration": duration
            },
            "impact": impact
        }
        print(f"事件影响计算结果: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        print(f"事件影响计算错误: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# 静态文件路由
@app.route('/')
def index():
    return send_file('1.html')

@app.route('/event')
def event():
    return send_file('event.html')

@app.route('/health')
def health():
    return send_file('health.html')

@app.route('/settings')
def settings():
    return send_file('settings.html')

# 静态资源路由
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# 启动服务器
if __name__ == '__main__':
    init_default_data()
    app.run(debug=True, port=5000)