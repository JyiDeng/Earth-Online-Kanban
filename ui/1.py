from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import time
from datetime import datetime, timedelta
import random
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import pandas as pd
import traceback
import threading
import tempfile
import atexit
import signal
import speech_recognition as sr
import base64
import sys
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain_core.messages import HumanMessage

# Agent imports
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.utilities import TextRequestsWrapper
from langchain_openai import ChatOpenAI

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
ATTRIBUTE_CHANGE_FILE = os.path.join(DATA_DIR, 'attribute_changes.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 添加langchain目录到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'langchain'))

# 初始化OpenAI代理
try:
    # 设置OpenAI API密钥和代理
    os.environ["GOOGLE_CSE_ID"] = "e74736660ea16424e"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDi8Ri0JE93Sdk6RM-pgXgxhLbROjHCL2U"
    os.environ["OPENAI_API_KEY"] = "sk-q21325baf11b4aaf3bdef5ecdb338313a5bf68e80aez8d6w"
    os.environ["http_proxy"] = "http://localhost:7890"
    os.environ["https_proxy"] = "http://localhost:7890"
    
    # 初始化LLM模型
    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo', base_url="https://api.gptsapi.net/v1")
    
    # 初始化工具
    search = GoogleSearchAPIWrapper()
    requests = TextRequestsWrapper()
    
    toolkit = [
        Tool(
            name = "Search",
            func=search.run,
            description="useful for when you need to search google to answer questions about current events"
        ),
        Tool(
            name = "Requests",
            func=requests.get,
            description="Useful for when you to make a request to a URL"
        ),
    ]
    
    # 初始化代理
    agent = initialize_agent(toolkit, llm, agent="zero-shot-react-description", verbose=True, return_intermediate_steps=True)
    OPENAI_AVAILABLE = True
    print("OpenAI代理已加载")
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI代理导入失败，将使用模拟响应")

# 导入千帆大模型
try:
    from langchain_community.chat_models import QianfanChatEndpoint
    from langchain_core.messages import HumanMessage
    QIANFAN_AVAILABLE = True
    # 设置千帆API密钥
    os.environ["QIANFAN_AK"] = "g6MdHGaXwbPy3Stt55UYIAoP"
    os.environ["QIANFAN_SK"] = "FUf5sz1x6SJ8lEnYsbB6M5fPY2vjYVfe"
    print("千帆大模型API已加载")
except ImportError:
    QIANFAN_AVAILABLE = False
    print("千帆大模型API导入失败，将使用模拟响应")

# 禁用语音识别功能，使用模拟响应
@app.route('/api/speech/record', methods=['POST'])
def record_speech():
    try:
        print("接收到语音识别请求 - 调用讯飞语音识别")
        
        # 导入讯飞语音识别模块
        import sys
        import os
        
        # 确保当前目录在搜索路径中
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
            
        # 现在导入讯飞模块
        try:
            import qianfan_xunfei
            print("成功导入讯飞模块")
        except ImportError as e:
            print(f"导入讯飞模块失败: {e}")
            print(f"Python路径: {sys.path}")
            raise
            
        import threading
        import time
        import base64
        import _thread as thread
        
        # 清空结果文本，确保每次录音都是新的开始
        result_text = ""
        
        # 存储语音识别结果的回调
        def on_message_callback(ws, message):
            nonlocal result_text
            try:
                data = json.loads(message)
                code = data.get("code")
                if code == 0:
                    data = data["data"]["result"]["ws"]
                    recognized_text = ""
                    for i in data:
                        for w in i["cw"]:
                            recognized_text += w["w"]
                    # 累积所有识别结果，而不是替换
                    if recognized_text:
                        result_text += recognized_text
                        print(f"累积识别结果: {result_text}")
            except Exception as e:
                print(f"处理讯飞回调消息出错: {e}")
                print(f"原始消息: {message}")

        # 创建讯飞语音识别的实例
        audio_input = qianfan_xunfei.AudioInput()
        audio_filename = audio_input.audio_record()
        
        # 设置讯飞语音识别参数
        wsParam = qianfan_xunfei.Ws_Param(
            APPID='704ffc5f', 
            APISecret='MDBmNmQyMzM4YzhmZTJjNDUwNGRmZWUw',
            APIKey='221ada6e9100f9f98ff5b1b901b6802d',
            AudioFile=audio_filename
        )
        
        # 配置WebSocket
        websocket = qianfan_xunfei.websocket
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        
        # 重写on_open函数以解决变量作用域问题
        def custom_on_open(ws):
            def run(*args):
                frameSize = 8000  # 每一帧的音频大小
                intervel = 0.04  # 发送音频间隔(单位:s)
                status = qianfan_xunfei.STATUS_FIRST_FRAME  # 音频的状态信息

                try:
                    with open(audio_filename, "rb") as fp:
                        while True:
                            buf = fp.read(frameSize)
                            # 文件结束
                            if not buf:
                                status = qianfan_xunfei.STATUS_LAST_FRAME
                            # 第一帧处理
                            if status == qianfan_xunfei.STATUS_FIRST_FRAME:
                                d = {"common": wsParam.CommonArgs,
                                    "business": wsParam.BusinessArgs,
                                    "data": {"status": 0, "format": "audio/L16;rate=16000",
                                            "audio": str(base64.b64encode(buf), 'utf-8'),
                                            "encoding": "raw"}}
                                d = json.dumps(d)
                                ws.send(d)
                                status = qianfan_xunfei.STATUS_CONTINUE_FRAME
                            # 中间帧处理
                            elif status == qianfan_xunfei.STATUS_CONTINUE_FRAME:
                                d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                            "audio": str(base64.b64encode(buf), 'utf-8'),
                                            "encoding": "raw"}}
                                ws.send(json.dumps(d))
                            # 最后一帧处理
                            elif status == qianfan_xunfei.STATUS_LAST_FRAME:
                                d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                            "audio": str(base64.b64encode(buf), 'utf-8'),
                                            "encoding": "raw"}}
                                ws.send(json.dumps(d))
                                time.sleep(1)
                                break
                            # 模拟音频采样间隔
                            time.sleep(intervel)
                except Exception as e:
                    print(f"语音处理错误: {e}")
                finally:
                    ws.close()
                    print("WebSocket连接已关闭")

            thread.start_new_thread(run, ())
        
        # 创建WebSocket连接
        ws = websocket.WebSocketApp(
            wsUrl, 
            on_message=on_message_callback, 
            on_error=qianfan_xunfei.on_error, 
            on_close=qianfan_xunfei.on_close
        )
        ws.on_open = custom_on_open
        
        # 在单独的线程中运行WebSocket客户端
        def run_ws():
            ws.run_forever(sslopt={"cert_reqs": qianfan_xunfei.ssl.CERT_NONE})
            
        ws_thread = threading.Thread(target=run_ws)
        ws_thread.daemon = True
        ws_thread.start()
        
        # 等待识别完成，最多等待8秒
        max_wait = 8
        while max_wait > 0 and not result_text:
            time.sleep(0.5)
            max_wait -= 0.5
            
        # 打印并返回最终识别结果
        if result_text:
            print(f"讯飞语音识别结果: {result_text}")
            return jsonify({
                "status": "success", 
                "text": result_text
            })
        else:
            print("讯飞语音识别未返回结果或超时")
            return jsonify({
                "status": "success", 
                "text": "未能识别语音内容，请直接输入文字"
            })
    except Exception as e:
        error_msg = f"语音识别处理错误: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        # 即使出错，也返回一个友好的响应，让用户可以继续操作
        return jsonify({
            "status": "partial_success", 
            "text": "语音识别发生了一些问题，请直接输入事件描述",
            "error": str(e)
        })

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
            with open(file_path, 'r', encoding='utf-8') as f:
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
                with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"已备份损坏的文件到: {backup_path}")
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
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"数据已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"保存数据错误 {file_path}: {e}")
        return False

# 模拟数据变化
def simulate_data_change(data):
    """模拟数据变化"""
    if not isinstance(data, dict):
        print(f"错误：输入数据不是字典类型: {type(data)}")
        return data
        
    try:
        print("开始模拟数据变化...")
        # 创建数据的深拷贝以避免修改原始数据
        modified_data = {}
        
        for category in data:
            if not isinstance(data[category], dict):
                print(f"警告：类别 {category} 的数据不是字典类型，跳过")
                modified_data[category] = data[category]
                continue
                
            modified_data[category] = {}
            for key, value in data[category].items():
                try:
                    # 确保当前值是数值类型
                    current_value = float(value)
                    # 生成一个较小的随机变化值，范围在-0.5到0.5之间
                    change = random.uniform(-0.5, 0.5)
                    # 应用变化并确保值在0-100之间
                    new_value = max(0, min(100, current_value + change))
                    modified_data[category][key] = new_value
                    # print(f"属性 {category}.{key} 从 {current_value:.2f} 变化 {change:+.2f}, 新值: {new_value:.2f}")
                except (ValueError, TypeError) as e:
                    print(f"警告：无法处理属性 {category}.{key} 的值 {value}: {str(e)}")
                    modified_data[category][key] = value
        
        return modified_data
    except Exception as e:
        print(f"模拟数据变化时出错: {str(e)}\n{traceback.format_exc()}")
        return data  # 如果出错，返回原始数据

# 属性变化追踪函数
def track_attribute_changes(health_data):
    """追踪属性变化，检测累计下降超过50%的属性"""
    try:
        # 加载历史变化数据
        attribute_changes = load_data(ATTRIBUTE_CHANGE_FILE) or {}
        
        # 初始化变化数据结构
        if not attribute_changes:
            attribute_changes = {
                "physiological": {},
                "mental": {},
                "ability": {}
            }
        
        alerts = []
        
        # 检查每个类别的属性变化
        for category in ["physiological", "mental", "ability"]:
            if category not in health_data:
                continue
                
            # 确保类别存在于变化记录中
            if category not in attribute_changes:
                attribute_changes[category] = {}
                
            for key, value in health_data[category].items():
                # 初始化属性记录
                if key not in attribute_changes[category]:
                    attribute_changes[category][key] = {
                        "baseline": value,
                        "current": value,
                        "cumulative_decrease": 0
                    }
                    continue
                
                # 获取当前记录
                record = attribute_changes[category][key]
                current_value = float(value)
                previous_value = float(record["current"])
                
                # 更新当前值
                record["current"] = current_value
                
                # 检查是否有下降
                if current_value < previous_value:
                    decrease = previous_value - current_value
                    percentage_decrease = (decrease / previous_value) * 100
                    record["cumulative_decrease"] += percentage_decrease
                    
                    # 检查累计下降是否超过50%
                    if record["cumulative_decrease"] >= 50:
                        label = get_metric_label(key)
                        alerts.append({
                            "category": category,
                            "key": key,
                            "label": label,
                            "cumulative_decrease": record["cumulative_decrease"],
                            "message": f"{label}属性累计下降了{record['cumulative_decrease']:.1f}%，建议关注"
                        })
                        # 重置累计下降计数器
                        record["cumulative_decrease"] = 0
                elif current_value > previous_value:
                    # 数值上升，减少累计下降值（但不低于0）
                    record["cumulative_decrease"] = max(0, record["cumulative_decrease"] - 10)
        
        # 保存更新后的变化记录
        save_data(ATTRIBUTE_CHANGE_FILE, attribute_changes)
        
        return alerts
    except Exception as e:
        print(f"追踪属性变化错误: {str(e)}")
        traceback.print_exc()
        return []

# 健康数据同步
@app.route('/api/health/sync', methods=['POST'])
def sync_health_data():
    try:
        print("收到健康数据同步请求")
        data = request.json
        if not data:
            print("错误：未提供同步数据")
            return jsonify({"status": "error", "message": "未提供同步数据"}), 400
        
        # 检查是否是从example.data同步的请求
        if 'action' in data and data['action'] == 'sync_from_example':
            print("收到从示例数据同步请求")
            return sync_from_example_data_handler()
            
        # print(f"接收到的同步数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 验证数据格式
        required_categories = ["physiological", "mental", "ability"]
        if not all(category in data for category in required_categories):
            error_msg = f"数据格式错误：缺少必要的类别 {required_categories}"
            print(error_msg)
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # 保存数据到文件
        data_file = os.path.join('data', 'health_data.json')
        print(f"准备保存数据到文件: {data_file}")
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        try:
            # 保存主数据文件
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("主数据保存成功")
            
            # 保存到历史记录
            history_file = os.path.join('data', 'health_history.json')
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = []
            
            # 添加新的历史记录
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            history.append(history_entry)
            
            # 只保留最近50条记录
            if len(history) > 50:
                history = history[-50:]
            
            # 保存历史记录
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print("历史数据保存成功")
            
            # 追踪属性变化
            attribute_alerts = track_attribute_changes(data)
            
            # 模拟数据小变化
            updated_data = simulate_data_change(data.copy())
            
            # 返回包含更新后数据的响应
            return jsonify({
                "status": "success",
                "message": "数据同步成功",
                "data": updated_data,
                "alerts": attribute_alerts
            })
            
        except Exception as save_error:
            error_msg = f"保存数据失败: {str(save_error)}\n{traceback.format_exc()}"
            print(error_msg)
            return jsonify({"status": "error", "message": f"保存数据失败: {str(save_error)}"}), 500
        
    except Exception as e:
        error_msg = f"同步健康数据错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"status": "error", "message": str(e)}), 500

# 处理从示例数据同步的请求
def sync_from_example_data_handler():
    try:
        print("准备从示例数据同步")
        example_file = os.path.join('data', 'example.data')
        if not os.path.exists(example_file):
            print(f"示例数据文件不存在: {example_file}")
            
            # 尝试在ui/data目录下查找
            alt_example_file = os.path.join('ui', 'data', 'example.data')
            if os.path.exists(alt_example_file):
                example_file = alt_example_file
                print(f"在替代位置找到示例数据文件: {example_file}")
            else:
                return jsonify({"status": "error", "message": "示例数据文件不存在"}), 404
            
        # 读取示例数据
        with open(example_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"已从{example_file}读取示例数据")
        
        # 验证数据格式
        required_categories = ["physiological", "mental", "ability"]
        if not all(category in data for category in required_categories):
            error_msg = f"示例数据格式错误：缺少必要的类别 {required_categories}"
            print(error_msg)
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # 保存数据到文件
        data_file = os.path.join('data', 'health_data.json')
        print(f"准备保存数据到文件: {data_file}")
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        try:
            # 保存主数据文件
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("主数据保存成功")
            
            # 保存到历史记录
            history_file = os.path.join('data', 'health_history.json')
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = []
            
            # 添加新的历史记录
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            history.append(history_entry)
            
            # 只保留最近50条记录
            if len(history) > 50:
                history = history[-50:]
            
            # 保存历史记录
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print("历史数据保存成功")
            
            # 追踪属性变化
            attribute_alerts = track_attribute_changes(data)
            
            # 模拟数据小变化
            updated_data = simulate_data_change(data.copy())
            
            # 返回包含更新后数据的响应
            return jsonify({
                "status": "success",
                "message": "健康数据同步成功！",
                "data": updated_data,
                "alerts": attribute_alerts
            })
            
        except Exception as save_error:
            error_msg = f"保存示例数据失败: {str(save_error)}\n{traceback.format_exc()}"
            print(error_msg)
            return jsonify({"status": "error", "message": f"保存示例数据失败: {str(save_error)}"}), 500
        
    except Exception as e:
        error_msg = f"同步示例数据错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
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

# 阈值设置页面
@app.route('/thresholds')
def thresholds_page():
    return send_file('thresholds.html')

# 趋势图页面
@app.route('/trends')
def trends_page():
    return send_file('trends.html')

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

# AI分析API
@app.route('/api/analyze', methods=['POST'])
def analyze_with_ai():
    try:
        print("收到AI分析请求")
        data = request.json
        if not data or 'healthData' not in data:
            print("错误：未提供健康数据")
            return jsonify({"status": "error", "message": "未提供健康数据"}), 400
        
        health_data = data['healthData']
        # print(f"接收到的健康数据: {json.dumps(health_data, ensure_ascii=False)}")
        
        # 格式化健康数据
        formatted_data = format_health_data_for_ai(health_data)
        print(f"格式化后的健康数据: {formatted_data}")
        # 检测异常模式
        abnormal_patterns = detect_abnormal_patterns(health_data)
        print(f"检测到的异常模式: {abnormal_patterns}")
        # 构建提示词
        prompt = f"""作为一位专业的健康顾问，请用中文分析以下用户的健康数据并给出建议。

当前健康数据:
{formatted_data}

识别到的异常模式:
{abnormal_patterns}

请从以下几个方面进行分析，输出为json：
1. 跨维度异常模式分析（例如卫生属性下降+成就感属性下降可能预示需要心理干预）
2. 需要重点关注的指标（数值低于50%的指标），对于每一条给出具体的改善建议

请全程用中文回答！
"""

        print("开始调用AI进行分析...")
        print("发送的提示词:", prompt)
        
        # 优先使用OpenAI代理进行分析
        if OPENAI_AVAILABLE:
            try:
                print("使用OpenAI代理进行分析...")
                response = agent({"input": prompt})
                content = response['output']
                print("OpenAI代理返回结果:", content)
                
                recommendations = extract_recommendations(content)
                
                return jsonify({
                    "status": "success",
                    "content": content,
                    "recommendations": recommendations
                })
            except Exception as api_error:
                print(f"调用OpenAI代理失败: {str(api_error)}")
                print("尝试使用千帆API作为备用...")
        
        # 如果OpenAI不可用或失败，尝试使用千帆API
        if QIANFAN_AVAILABLE:
            try:
                print("使用千帆API进行分析...")
                chat = QianfanChatEndpoint(streaming=False)
                response = chat([HumanMessage(content=prompt)])
                content = response.content
                print("千帆API返回结果:", content)
                
                recommendations = extract_recommendations(content)
                
                return jsonify({
                    "status": "success",
                    "content": content,
                    "recommendations": recommendations
                })
            except Exception as api_error:
                print(f"调用千帆API失败: {str(api_error)}")
                print("使用模拟数据作为备用")
        
        # 如果所有API都失败，使用模拟数据
        content = generate_mock_analysis(health_data)
        recommendations = extract_recommendations(content)
        
        return jsonify({
            "status": "success",
            "content": content,
            "recommendations": recommendations,
            "note": "使用模拟数据（API调用失败）"
        })
            
    except Exception as e:
        error_msg = f"AI分析错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            "status": "error", 
            "message": str(e),
            "content": "分析过程中出现错误，请稍后重试",
            "recommendations": ["系统暂时无法提供分析建议，请稍后再试"]
        }), 500

def detect_abnormal_patterns(health_data):
    """检测跨维度异常模式"""
    patterns = []
    
    # 定义异常模式规则
    pattern_rules = [
        # 身心健康异常模式
        {
            "indicators": [("physiological", "hygiene", 40), ("mental", "achievement", 40)],
            "description": "卫生状况与成就感同时偏低，可能预示心理健康问题"
        },
        {
            "indicators": [("physiological", "fatigue", 30), ("mental", "eyeFatigue", 30)],
            "description": "身体疲惫与眼部疲劳同时偏高，可能预示过度用眼与工作压力"
        },
        {
            "indicators": [("mental", "happiness", 40), ("mental", "sleepQuality", 40)],
            "description": "幸福感与睡眠质量同时偏低，可能预示情绪与睡眠问题"
        },
        {
            "indicators": [("physiological", "social", 30), ("mental", "happiness", 40)],
            "description": "社交需求与幸福感同时偏低，可能预示社交孤独问题"
        },
        {
            "indicators": [("physiological", "hunger", 30), ("mental", "fitness", 40)],
            "description": "饱腹度与健身指数同时偏低，可能预示饮食不规律问题"
        }
    ]
    
    # 检查每个规则
    for rule in pattern_rules:
        match = True
        for category, key, threshold in rule["indicators"]:
            if category not in health_data or key not in health_data[category]:
                match = False
                break
            value = health_data[category][key]
            if threshold < 50 and value > threshold:  # 低于阈值的指标
                match = False
                break
        
        if match:
            patterns.append(rule["description"])
    
    # 检查基于用户设置的阈值的异常
    try:
        # 加载用户设置的阈值
        thresholds = load_data(THRESHOLDS_FILE) or {}
        
        # 检查每个类别的属性是否低于阈值
        for category in ["physiological", "mental", "ability"]:
            if category not in health_data:
                continue
                
            for key, value in health_data[category].items():
                if key not in thresholds:
                    continue
                
                threshold_value = thresholds[key]
                label = get_metric_label(key)
                
                # 针对需要保持高值的属性（低阈值检查）
                if key in ["hunger", "thirst", "social", "hygiene", "fitness", "happiness", 
                          "achievement", "sleepQuality", "heartHealth", "muscle", "agility", 
                          "resistance", "timeControl", "creativity", "security"]:
                    if value <= threshold_value:
                        patterns.append(f"{label}低于设定阈值({threshold_value})，当前值: {value:.1f}")
                
                # 针对需要保持低值的属性（高阈值检查）
                elif key in ["toilet", "fatigue", "eyeFatigue"]:
                    if value >= threshold_value:
                        patterns.append(f"{label}高于设定阈值({threshold_value})，当前值: {value:.1f}")
    except Exception as e:
        print(f"基于阈值检测异常时出错: {str(e)}")
        traceback.print_exc()
    
    if patterns:
        return "\n".join(patterns)
    else:
        return "未检测到明显的跨维度异常模式。"

def format_health_data_for_ai(health_data):
    """格式化健康数据用于AI分析"""
    formatted = []
    
    # 生理需求
    if "physiological" in health_data:
        formatted.append("\n生理需求:")
        for key, value in health_data["physiological"].items():
            label = get_metric_label(key)
            formatted.append(f"- {label}: {value:.1f}%")
    
    # 身心状况
    if "mental" in health_data:
        formatted.append("\n身心状况:")
        for key, value in health_data["mental"].items():
            label = get_metric_label(key)
            formatted.append(f"- {label}: {value:.1f}%")
    
    # 能力属性
    if "ability" in health_data:
        formatted.append("\n能力属性:")
        for key, value in health_data["ability"].items():
            label = get_metric_label(key)
            formatted.append(f"- {label}: {value:.1f}%")
    
    return "\n".join(formatted)

def get_metric_label(key):
    """获取指标的中文标签"""
    labels = {
        "hunger": "饱腹度",
        "thirst": "口渴度",
        "toilet": "如厕需求",
        "social": "社交需求",
        "fatigue": "疲惫度",
        "hygiene": "卫生状况",
        "fitness": "瘦身指数",
        "happiness": "幸福感",
        "achievement": "成就感",
        "eyeFatigue": "视疲劳",
        "sleepQuality": "睡眠质量",
        "heartHealth": "心脏健康度",
        "muscle": "肌肉强度",
        "agility": "敏捷度",
        "resistance": "抗击打能力",
        "timeControl": "时间掌控度",
        "creativity": "创造力",
        "security": "安全感"
    }
    return labels.get(key, key)

# 从AI分析结果中提取建议
def extract_recommendations(content):
    """从AI分析结果中提取建议"""
    try:
        if not content:
            print("警告：输入内容为空")
            return ["系统暂时无法提供具体建议，请保持健康的生活方式"]
            
        print("开始提取建议...")
        print(f"输入内容: {content}")
        
        # 如果内容是JSON字符串，尝试解析
        if isinstance(content, str) and content.strip().startswith('{'):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # 尝试从不同可能的键中获取建议
                    recommendations = []
                    if '建议' in data:
                        recs = data['建议']
                        if isinstance(recs, list):
                            recommendations.extend(recs)
                        elif isinstance(recs, str):
                            recommendations.append(recs)
                    
                    if '分析结果' in data and isinstance(data['分析结果'], dict):
                        if '建议' in data['分析结果']:
                            recs = data['分析结果']['建议']
                            if isinstance(recs, list):
                                recommendations.extend(recs)
                            elif isinstance(recs, str):
                                recommendations.append(recs)
                    
                    if recommendations:
                        print(f"从JSON中提取的建议: {recommendations}")
                        return recommendations
            except json.JSONDecodeError:
                print("JSON解析失败，尝试其他方式提取建议")
        
        # 如果不是JSON或解析失败，尝试从文本中提取建议
        recommendations = []
        lines = content.split('\n') if isinstance(content, str) else []
        in_recommendations = False
        
        for line in lines:
            if not isinstance(line, str):
                continue
                
            line = line.strip()
            if not line:
                continue
                
            if '建议' in line or '推荐' in line:
                in_recommendations = True
                continue
                
            if in_recommendations and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                recommendation = line.lstrip('-•* ').strip()
                if recommendation:
                    recommendations.append(recommendation)
        
        # 如果没有找到建议，生成一些通用建议
        if not recommendations:
            recommendations = [
                "建议适当休息，保持作息规律",
                "注意营养均衡，定时就餐",
                "保持适度运动，增强体质"
            ]
        
        print(f"提取的建议: {recommendations}")
        return recommendations
        
    except Exception as e:
        print(f"提取建议时出错: {str(e)}\n{traceback.format_exc()}")
        return ["系统暂时无法提供具体建议，请保持健康的生活方式"]

# 生成模拟AI分析响应（当无法使用千帆API时）
def generate_mock_analysis(health_data):
    # 找出最低的3个指标
    all_metrics = []
    
    for category, metrics in health_data.items():
        for key, value in metrics.items():
            all_metrics.append({
                "category": category,
                "key": key,
                "value": value,
                "label": get_metric_label(key)
            })
    
    # 按值排序
    all_metrics.sort(key=lambda x: x['value'])
    lowest_metrics = all_metrics[:3]
    
    # 生成分析结果
    result = "## 健康状况分析\n\n"
    
    # 总体评估
    avg_value = sum(metric['value'] for metric in all_metrics) / len(all_metrics)
    if avg_value > 70:
        result += "您的整体健康状况良好。大多数指标处于理想范围内，继续保持良好的生活习惯。\n\n"
    elif avg_value > 50:
        result += "您的整体健康状况一般。部分指标需要关注，建议适当调整生活习惯。\n\n"
    else:
        result += "您的整体健康状况需要关注。多项指标处于较低水平，建议积极调整生活方式。\n\n"
    
    # 重点关注项
    result += "### 需要关注的指标:\n\n"
    
    for metric in lowest_metrics:
        result += f"- **{metric['label']}**: {metric['value']}%\n"
    
    result += "\n### 改善建议:\n\n"
    
    # 针对低指标的具体建议
    for metric in lowest_metrics:
        if metric['key'] == 'hunger':
            result += "1. 饱腹度偏低，建议及时补充营养，保持规律三餐\n"
        elif metric['key'] == 'thirst':
            result += "1. 口渴度偏低，建议增加日常饮水量，保持充分水分摄入\n"
        elif metric['key'] == 'social':
            result += "1. 社交需求偏低，建议增加社交活动，保持与朋友家人的联系\n"
        elif metric['key'] == 'fatigue':
            result += "1. 疲惫度较高，建议保证充足睡眠，适当休息\n"
        elif metric['key'] == 'hygiene':
            result += "1. 卫生状况偏低，建议注意个人卫生，保持环境整洁\n"
        elif metric['key'] == 'fitness':
            result += "1. 瘦身指数偏低，建议加强有氧运动，控制饮食\n"
        elif metric['key'] == 'sleepQuality':
            result += "1. 睡眠质量偏低，建议调整作息时间，创造良好睡眠环境\n"
        else:
            result += f"1. {metric['label']}偏低，建议关注并采取相应措施改善\n"
    
    # 一般性建议
    result += "\n### 一般健康建议:\n\n"
    result += "1. 保持均衡饮食，多摄入蔬果，减少高糖高脂食物\n"
    result += "2. 每天保持30分钟以上中等强度运动\n"
    result += "3. 建立规律作息，保证7-8小时高质量睡眠\n"
    result += "4. 保持积极心态，学会缓解压力\n"
    result += "5. 定期体检，关注身体变化\n"
    
    return result

# 读取example.data文件
@app.route('/api/example-data', methods=['GET'])
def read_example_data():
    try:
        example_file = os.path.join('data', 'example.data')
        if not os.path.exists(example_file):
            return jsonify({"status": "error", "message": "示例数据文件不存在"}), 404
            
        with open(example_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return jsonify({
            "status": "success", 
            "message": "示例数据读取成功",
            "data": data
        })
    except Exception as e:
        print(f"读取示例数据错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 生成周报
@app.route('/api/reports/weekly', methods=['GET'])
def generate_weekly_report():
    try:
        # 创建报告目录
        reports_dir = os.path.join('data', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # 加载健康历史数据
        history_file = os.path.join('data', 'health_history.json')
        if not os.path.exists(history_file):
            return jsonify({"status": "error", "message": "没有足够的历史数据生成周报"}), 400
            
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 获取最近7天的数据
        now = datetime.now()
        one_week_ago = now - timedelta(days=7)
        
        # 筛选过去7天的数据
        week_data = []
        for entry in history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= one_week_ago:
                    week_data.append(entry)
            except (ValueError, KeyError):
                continue
        
        if not week_data:
            return jsonify({"status": "error", "message": "过去7天没有足够的数据生成周报"}), 400
            
        # 分析数据
        report_data = analyze_report_data(week_data, "周报")
        
        # 生成报告文件
        report_filename = f"earth_online_weekly_{now.strftime('%Y%m%d')}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_data["report_text"])
        
        return jsonify({
            "status": "success",
            "message": "周报生成成功",
            "report_file": report_path,
            "report_data": report_data
        })
        
    except Exception as e:
        print(f"生成周报错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 生成月报
@app.route('/api/reports/monthly', methods=['GET'])
def generate_monthly_report():
    try:
        # 创建报告目录
        reports_dir = os.path.join('data', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # 加载健康历史数据
        history_file = os.path.join('data', 'health_history.json')
        if not os.path.exists(history_file):
            return jsonify({"status": "error", "message": "没有足够的历史数据生成月报"}), 400
            
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 获取最近30天的数据
        now = datetime.now()
        one_month_ago = now - timedelta(days=30)
        
        # 筛选过去30天的数据
        month_data = []
        for entry in history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= one_month_ago:
                    month_data.append(entry)
            except (ValueError, KeyError):
                continue
        
        if not month_data:
            return jsonify({"status": "error", "message": "过去30天没有足够的数据生成月报"}), 400
            
        # 分析数据
        report_data = analyze_report_data(month_data, "月报")
        
        # 生成报告文件
        report_filename = f"earth_online_monthly_{now.strftime('%Y%m%d')}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_data["report_text"])
        
        return jsonify({
            "status": "success",
            "message": "月报生成成功",
            "report_file": report_path,
            "report_data": report_data
        })
        
    except Exception as e:
        print(f"生成月报错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 分析报告数据
def analyze_report_data(data_entries, report_type):
    # 提取开始和结束时间
    start_time = datetime.fromisoformat(data_entries[0]["timestamp"])
    end_time = datetime.fromisoformat(data_entries[-1]["timestamp"])
    
    period_start = start_time.strftime("%Y-%m-%d")
    period_end = end_time.strftime("%Y-%m-%d")
    
    # 初始化类别和属性统计
    categories = ["physiological", "mental", "ability"]
    attributes = {}
    
    # 初始化报告数据结构
    for entry in data_entries:
        for category in categories:
            if category in entry["data"]:
                for attr, value in entry["data"][category].items():
                    if attr not in attributes:
                        attributes[attr] = {
                            "values": [],
                            "category": category,
                            "label": get_metric_label(attr)
                        }
                    try:
                        attributes[attr]["values"].append(float(value))
                    except (ValueError, TypeError):
                        continue
    
    # 统计每个属性的趋势和变化
    attr_stats = {}
    improved_attrs = []
    high_attrs = []
    
    for attr, data in attributes.items():
        if not data["values"]:
            continue
            
        # 计算统计值
        avg = sum(data["values"]) / len(data["values"])
        max_val = max(data["values"])
        min_val = min(data["values"])
        start_val = data["values"][0]
        end_val = data["values"][-1]
        
        # 计算趋势（简单线性回归）
        x = list(range(len(data["values"])))
        if len(x) > 1:
            # 使用简单的线性回归计算趋势
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(data["values"])
            sum_xy = sum(x[i] * data["values"][i] for i in range(n))
            sum_xx = sum(x[i] ** 2 for i in range(n))
            
            # 计算斜率
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x ** 2)
            except ZeroDivisionError:
                slope = 0
        else:
            slope = 0
            
        # 确定趋势符号
        if slope > 0.1:
            trend_symbol = "↑"
        elif slope < -0.1:
            trend_symbol = "↓"
        else:
            trend_symbol = "→"
            
        # 计算变化百分比
        if start_val > 0:
            change_percent = ((end_val - start_val) / start_val) * 100
        else:
            change_percent = 0
            
        # 保存统计结果
        attr_stats[attr] = {
            "label": data["label"],
            "category": data["category"],
            "average": avg,
            "max": max_val,
            "min": min_val,
            "start": start_val,
            "end": end_val,
            "trend": slope,
            "trend_symbol": trend_symbol,
            "change_percent": change_percent
        }
        
        # 识别改善最大的属性
        if change_percent > 10 and attr not in ["toilet", "fatigue", "eyeFatigue"]:
            improved_attrs.append((attr, change_percent))
        elif change_percent < -10 and attr in ["toilet", "fatigue", "eyeFatigue"]:
            improved_attrs.append((attr, -change_percent))
            
        # 识别保持较高的属性
        if avg > 70 and attr not in ["toilet", "fatigue", "eyeFatigue"]:
            high_attrs.append((attr, avg))
        elif avg < 30 and attr in ["toilet", "fatigue", "eyeFatigue"]:
            high_attrs.append((attr, 100 - avg))
    
    # 排序改善和高值属性
    improved_attrs.sort(key=lambda x: x[1], reverse=True)
    high_attrs.sort(key=lambda x: x[1], reverse=True)
    
    # 构建文本报告
    report = f"地球Online {report_type}\n"
    report += f"报告期间: {period_start} 至 {period_end}\n\n"
    
    # 添加改善最大的属性
    report += "===== 改善最显著的属性 =====\n"
    if improved_attrs:
        for i, (attr, change) in enumerate(improved_attrs[:3], 1):
            stats = attr_stats[attr]
            report += f"{i}. {stats['label']}:\n"
            report += f"   起始值: {stats['start']:.1f} → 当前值: {stats['end']:.1f}\n"
            report += f"   改善幅度: {abs(change):.1f}%\n\n"
    else:
        report += "暂无显著改善的属性\n\n"
    
    # 添加保持较高的属性
    report += "===== 保持较高水平的属性 =====\n"
    if high_attrs:
        for i, (attr, avg) in enumerate(high_attrs[:3], 1):
            stats = attr_stats[attr]
            report += f"{i}. {stats['label']}:\n"
            report += f"   平均值: {stats['average']:.1f}\n"
            report += f"   最大值: {stats['max']:.1f}\n\n"
    else:
        report += "暂无保持较高水平的属性\n\n"
    
    # 按类别组织的详细数据
    report += "===== 详细数据 =====\n"
    for category in categories:
        category_attrs = {k: v for k, v in attr_stats.items() if v["category"] == category}
        if not category_attrs:
            continue
            
        if category == "physiological":
            category_name = "生理需求"
        elif category == "mental":
            category_name = "身心状况"
        elif category == "ability":
            category_name = "能力属性"
        else:
            category_name = category
            
        report += f"\n{category_name}:\n"
        report += "-" * 50 + "\n"
        
        for attr, stats in category_attrs.items():
            report += f"{stats['label']}:\n"
            report += f"  当前值: {stats['end']:.1f} {stats['trend_symbol']}\n"
            report += f"  平均值: {stats['average']:.1f}\n"
            report += f"  最大值: {stats['max']:.1f}\n"
            report += f"  最小值: {stats['min']:.1f}\n"
            report += f"  变化趋势: {stats['trend']:.4f}/天\n"
            report += "\n"
    
    # 生成个性化鼓励语
    encouragement = generate_encouragement(improved_attrs, high_attrs, attr_stats)
    report += "\n===== 个性化鼓励 =====\n"
    report += encouragement
    
    # 返回结果
    return {
        "report_text": report,
        "period_start": period_start,
        "period_end": period_end,
        "attributes": attr_stats,
        "improved_attrs": improved_attrs,
        "high_attrs": high_attrs,
        "encouragement": encouragement
    }

# 生成个性化鼓励语
def generate_encouragement(improved_attrs, high_attrs, attr_stats):
    try:
        # 准备鼓励语句
        if QIANFAN_AVAILABLE:
            # 使用千帆大模型生成鼓励语
            chat = QianfanChatEndpoint(streaming=False)
            
            # 构建提示词
            prompt = "作为一位温柔的健康顾问，请根据以下数据给用户一段温馨的鼓励语，长度在100-150字之间。语气要温暖亲切。全程使用中文。\n\n"
            
            # 添加改善的属性信息
            if improved_attrs:
                prompt += "用户改善最显著的属性：\n"
                for attr, change in improved_attrs[:3]:
                    stats = attr_stats[attr]
                    prompt += f"- {stats['label']}：从 {stats['start']:.1f} 提升到 {stats['end']:.1f}，改善了 {abs(change):.1f}%\n"
            
            # 添加保持较高的属性信息
            if high_attrs:
                prompt += "\n用户保持较高水平的属性：\n"
                for attr, avg in high_attrs[:3]:
                    stats = attr_stats[attr]
                    prompt += f"- {stats['label']}：平均值 {stats['average']:.1f}，最高达到 {stats['max']:.1f}\n"
            
            try:
                response = chat([HumanMessage(content=prompt)])
                encouragement = response.content.strip()
                print("千帆API生成的鼓励语:", encouragement)
                return encouragement
            except Exception as e:
                print(f"调用千帆API失败: {e}")
        
        # 如果千帆API不可用或失败，使用预设鼓励语
        if improved_attrs:
            # 有改善的属性
            most_improved = attr_stats[improved_attrs[0][0]]['label']
            encouragement = f"亲爱的用户，我注意到你的{most_improved}有了显著的提升，这真的很棒！这表明你在自我管理方面正在取得进步。"
            encouragement += f"健康是一场持久的马拉松，而不是短跑，每一个小进步都是值得庆祝的。继续保持这样的节奏，相信未来会有更多惊喜等着你。记住，温和而持续的努力往往比激进的改变更有效。期待在下次报告中看到你的更多进步！"
        elif high_attrs:
            # 有保持较高的属性
            best_attr = attr_stats[high_attrs[0][0]]['label']
            encouragement = f"亲爱的用户，你的{best_attr}一直保持在很高的水平，这是非常值得肯定的成就！"
            encouragement += f"保持良好状态需要持续的努力和坚持，而你做到了这一点。这份坚持不仅体现了你的自律，也为你的整体健康打下了坚实基础。希望你能将这种良好的习惯延续下去，同时也可以尝试在其他方面有所突破。健康的旅程上，你已经走在了正确的道路上！"
        else:
            # 通用鼓励语
            encouragement = "亲爱的用户，健康是一场持久的旅程，每一个小小的进步都值得被肯定。"
            encouragement += "即使现在可能没有看到显著的变化，但你的坚持和努力正在为未来打下基础。健康的变化往往是渐进的，需要时间来展现。"
            encouragement += "请继续保持你的节奏，关注自己的感受，相信随着时间的推移，这些细微的改变会累积成显著的进步。期待在下一次报告中看到你的成长！"
        
        return encouragement
    except Exception as e:
        print(f"生成鼓励语错误: {e}")
        return "亲爱的用户，感谢你持续关注自己的健康状况。健康是一场马拉松，而不是短跑，每一个小进步都值得庆祝。相信通过你的坚持和努力，一定会看到更多积极的变化！"

# 添加周报页面
@app.route('/weekly-report')
def weekly_report_page():
    return send_file('weekly_report.html')

# 添加月报页面
@app.route('/monthly-report')
def monthly_report_page():
    return send_file('monthly_report.html')

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

# 从example.data同步健康数据
@app.route('/api/sync-from-example', methods=['POST'])
def sync_from_example_data():
    try:
        print("收到从示例数据同步请求")
        example_file = os.path.join('data', 'example.data')
        if not os.path.exists(example_file):
            return jsonify({"status": "error", "message": "示例数据文件不存在"}), 404
            
        # 读取示例数据
        with open(example_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证数据格式
        required_categories = ["physiological", "mental", "ability"]
        if not all(category in data for category in required_categories):
            error_msg = f"数据格式错误：缺少必要的类别 {required_categories}"
            print(error_msg)
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # 保存数据到文件
        data_file = os.path.join('data', 'health_data.json')
        print(f"准备保存数据到文件: {data_file}")
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        try:
            # 保存主数据文件
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("主数据保存成功")
            
            # 保存到历史记录
            history_file = os.path.join('data', 'health_history.json')
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = []
            
            # 添加新的历史记录
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            history.append(history_entry)
            
            # 只保留最近50条记录
            if len(history) > 50:
                history = history[-50:]
            
            # 保存历史记录
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print("历史数据保存成功")
            
            # 追踪属性变化
            attribute_alerts = track_attribute_changes(data)
            
            # 模拟数据小变化
            updated_data = simulate_data_change(data.copy())
            
            # 返回包含更新后数据的响应
            return jsonify({
                "status": "success",
                "message": "示例数据同步成功",
                "data": updated_data,
                "alerts": attribute_alerts
            })
            
        except Exception as save_error:
            error_msg = f"保存示例数据失败: {str(save_error)}\n{traceback.format_exc()}"
            print(error_msg)
            return jsonify({"status": "error", "message": f"保存示例数据失败: {str(save_error)}"}), 500
        
    except Exception as e:
        error_msg = f"同步示例数据错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"status": "error", "message": str(e)}), 500