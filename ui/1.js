import apiService from './api.js';

// 全局变量
let healthData = {
    physiological: {
        hunger: 96,
        thirst: 86,
        toilet: 30,
        social: 49,
        fatigue: 92,
        hygiene: 50
    },
    mental: {
        fitness: 40,
        happiness: 99,
        achievement: 49,
        eyeFatigue: 89,
        sleepQuality: 75,
        heartHealth: 76
    },
    ability: {
        muscle: 44,
        agility: 49,
        resistance: 48,
        timeControl: 50,
        creativity: 51,
        security: 49
    }
};

let settings = {
    syncInterval: 5,
    alertThreshold: 30
};

let thresholds = {};

// 工具函数
function showLoading(button) {
    const originalText = button.textContent;
    button.disabled = true;
    button.innerHTML = `<span class="loading"></span> 处理中...`;
    return () => {
        button.disabled = false;
        button.textContent = originalText;
    };
}

function showModal(content, title = '') {
    const modalContainer = document.getElementById('modalContainer');
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-header">
            <h3>${title}</h3>
            <span class="modal-close">&times;</span>
        </div>
        <div class="modal-content">${content}</div>
    `;
    modalContainer.appendChild(modal);
    modalContainer.classList.add('show');

    modal.querySelector('.modal-close').addEventListener('click', () => {
        modalContainer.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    });
}

// 健康数据管理
async function loadHealthData() {
    try {
        const data = await apiService.getHealthData();
        healthData = data;
        updateUI();
        checkThresholds();
    } catch (error) {
        console.error('加载健康数据失败:', error);
        showAnalysisResult({ message: '加载健康数据失败，请检查网络连接' });
    }
}

function updateUI() {
    // 更新生理需求
    Object.entries(healthData.physiological).forEach(([key, value]) => {
        const element = document.querySelector(`.physiological .metric[data-type="${key}"]`);
        if (element) {
            element.querySelector('.value').textContent = `${Math.round(value)}%`;
            element.querySelector('progress').value = value;
        }
    });

    // 更新身心状况
    Object.entries(healthData.mental).forEach(([key, value]) => {
        const element = document.querySelector(`.mental .metric[data-type="${key}"]`);
        if (element) {
            element.querySelector('.value').textContent = `${Math.round(value)}%`;
            element.querySelector('progress').value = value;
        }
    });

    // 更新能力属性
    Object.entries(healthData.ability).forEach(([key, value]) => {
        const element = document.querySelector(`.ability .metric[data-type="${key}"]`);
        if (element) {
            element.querySelector('.value').textContent = `${Math.round(value)}%`;
            element.querySelector('progress').value = value;
        }
    });

    updateProgressColors();
}

// 阈值检查
async function checkThresholds() {
    try {
        const currentThresholds = await apiService.getThresholds();
        thresholds = currentThresholds;

        // 检查每个指标是否低于阈值
        Object.entries(healthData.physiological).forEach(([key, value]) => {
            if (value < (thresholds[key] || 30)) {
                showAnalysisResult({
                    message: `警告：${getMetricLabel(key)}低于阈值！当前值：${Math.round(value)}%`
                });
            }
        });

        Object.entries(healthData.mental).forEach(([key, value]) => {
            if (value < (thresholds[key] || 30)) {
                showAnalysisResult({
                    message: `警告：${getMetricLabel(key)}低于阈值！当前值：${Math.round(value)}%`
                });
            }
        });

        Object.entries(healthData.ability).forEach(([key, value]) => {
            if (value < (thresholds[key] || 30)) {
                showAnalysisResult({
                    message: `警告：${getMetricLabel(key)}低于阈值！当前值：${Math.round(value)}%`
                });
            }
        });
    } catch (error) {
        console.error('检查阈值失败:', error);
    }
}

function getMetricLabel(key) {
    const labels = {
        hunger: '饱腹度',
        thirst: '口渴度',
        toilet: '如厕需求',
        social: '社交需求',
        fatigue: '疲惫度',
        hygiene: '卫生状况',
        fitness: '瘦身指数',
        happiness: '幸福感',
        achievement: '成就感',
        eyeFatigue: '视疲劳',
        sleepQuality: '睡眠质量',
        heartHealth: '心脏健康度',
        muscle: '肌肉强度',
        agility: '敏捷度',
        resistance: '抗击打能力',
        timeControl: '时间掌控度',
        creativity: '创造力',
        security: '安全感'
    };
    return labels[key] || key;
}

// 事件管理
async function showEventWindow() {
    try {
        const events = await apiService.getEvents();
        const content = `
            <div class="event-form">
                <h4>添加新事件</h4>
                <form id="eventForm">
                    <div class="form-group">
                        <label>事件名称</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>事件类型</label>
                        <select name="type" required>
                            <option value="work">工作</option>
                            <option value="exercise">运动</option>
                            <option value="rest">休息</option>
                            <option value="social">社交</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>持续时间(分钟)</label>
                        <input type="number" name="duration" required>
                    </div>
                    <button type="submit">保存</button>
                </form>
            </div>
            <div class="event-list">
                <h4>历史事件</h4>
                <ul>
                    ${events.map(event => `
                        <li>
                            <span>${event.name}</span>
                            <span>${event.type}</span>
                            <span>${event.duration}分钟</span>
                            <button onclick="deleteEvent('${event.id}')">删除</button>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
        showModal(content, '事件管理');

        // 添加事件表单提交处理
        document.getElementById('eventForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const eventData = {
                name: formData.get('name'),
                type: formData.get('type'),
                duration: parseInt(formData.get('duration'))
            };
            try {
                await apiService.createEvent(eventData);
                showEventWindow(); // 刷新事件列表
            } catch (error) {
                console.error('创建事件失败:', error);
                showAnalysisResult({ message: '创建事件失败，请检查网络连接' });
            }
        });
    } catch (error) {
        console.error('加载事件失败:', error);
        showAnalysisResult({ message: '加载事件失败，请检查网络连接' });
    }
}

// 模型训练
async function trainModel() {
    const button = document.querySelector('.footer button:nth-child(3)');
    const resetButton = showLoading(button);
    
    try {
        const result = await apiService.trainModel(healthData);
        showAnalysisResult({ message: '模型训练成功完成' });
    } catch (error) {
        console.error('模型训练失败:', error);
        showAnalysisResult({ message: '模型训练失败，请检查网络连接' });
    } finally {
        resetButton();
    }
}

// 趋势分析
async function analyzeTrends() {
    try {
        const trends = await apiService.getTrends();
        const content = `
            <div class="trend-analysis">
                <h4>趋势分析结果</h4>
                <div class="trend-chart">
                    <!-- 这里可以添加图表 -->
                </div>
                <div class="trend-summary">
                    ${trends.summary}
                </div>
            </div>
        `;
        showModal(content, '趋势分析');
    } catch (error) {
        console.error('趋势分析失败:', error);
        showAnalysisResult({ message: '趋势分析失败，请检查网络连接' });
    }
}

// 报告生成
async function generateWeeklyReport() {
    try {
        const report = await apiService.generateReport('weekly', {
            start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            end: new Date()
        });
        showModal(report.content, '周报');
    } catch (error) {
        console.error('生成周报失败:', error);
        showAnalysisResult({ message: '生成周报失败，请检查网络连接' });
    }
}

async function generateMonthlyReport() {
    try {
        const report = await apiService.generateReport('monthly', {
            start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
            end: new Date()
        });
        showModal(report.content, '月报');
    } catch (error) {
        console.error('生成月报失败:', error);
        showAnalysisResult({ message: '生成月报失败，请检查网络连接' });
    }
}

// 设置管理
async function showSettings() {
    try {
        const currentSettings = await apiService.getSettings();
        settings = currentSettings;
        const content = `
            <div class="settings-form">
                <h4>系统设置</h4>
                <form id="settingsForm">
                    <div class="form-group">
                        <label>数据同步频率(分钟)</label>
                        <input type="number" name="syncInterval" value="${settings.syncInterval}">
                    </div>
                    <div class="form-group">
                        <label>提醒阈值</label>
                        <input type="number" name="alertThreshold" value="${settings.alertThreshold}">
                    </div>
                    <button type="submit">保存设置</button>
                </form>
            </div>
        `;
        showModal(content, '系统设置');

        // 添加设置表单提交处理
        document.getElementById('settingsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const newSettings = {
                syncInterval: parseInt(formData.get('syncInterval')),
                alertThreshold: parseInt(formData.get('alertThreshold'))
            };
            try {
                await apiService.updateSettings(newSettings);
                settings = newSettings;
                // 更新同步间隔
                clearInterval(syncInterval);
                syncInterval = setInterval(loadHealthData, settings.syncInterval * 60 * 1000);
                showAnalysisResult({ message: '设置已保存' });
            } catch (error) {
                console.error('保存设置失败:', error);
                showAnalysisResult({ message: '保存设置失败，请检查网络连接' });
            }
        });
    } catch (error) {
        console.error('加载设置失败:', error);
        showAnalysisResult({ message: '加载设置失败，请检查网络连接' });
    }
}

// 阈值设置
async function showThresholdSettings() {
    try {
        const currentThresholds = await apiService.getThresholds();
        thresholds = currentThresholds;
        const content = `
            <div class="threshold-form">
                <h4>阈值设置</h4>
                <form id="thresholdForm">
                    ${Object.entries(thresholds).map(([key, value]) => `
                        <div class="form-group">
                            <label>${getMetricLabel(key)}</label>
                            <input type="number" name="${key}" value="${value}">
                        </div>
                    `).join('')}
                    <button type="submit">保存阈值</button>
                </form>
            </div>
        `;
        showModal(content, '阈值设置');

        // 添加阈值表单提交处理
        document.getElementById('thresholdForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const newThresholds = {};
            for (const [key, value] of formData.entries()) {
                newThresholds[key] = parseInt(value);
            }
            try {
                await apiService.updateThresholds(newThresholds);
                thresholds = newThresholds;
                showAnalysisResult({ message: '阈值设置已保存' });
            } catch (error) {
                console.error('保存阈值设置失败:', error);
                showAnalysisResult({ message: '保存阈值设置失败，请检查网络连接' });
            }
        });
    } catch (error) {
        console.error('加载阈值设置失败:', error);
        showAnalysisResult({ message: '加载阈值设置失败，请检查网络连接' });
    }
}

// 更新进度条颜色
function updateProgressColors() {
    document.querySelectorAll('.metric').forEach(metric => {
        const progress = metric.querySelector('progress');
        const value = parseInt(progress.value);
        
        // 移除所有颜色类
        progress.classList.remove('progress-green', 'progress-yellow', 'progress-red');
        
        // 根据值添加相应的颜色类
        if (value >= 80) {
            progress.classList.add('progress-green');
        } else if (value >= 50) {
            progress.classList.add('progress-yellow');
        } else {
            progress.classList.add('progress-red');
        }
    });
}

// 更新当前时间
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    document.querySelector('.time').textContent = `当前时间: ${timeString}`;
}

// 显示分析结果
function showAnalysisResult(result) {
    const logElement = document.querySelector('.log pre');
    const timestamp = new Date().toLocaleString();
    logElement.innerHTML += `\n[${timestamp}] ${result.message}`;
    logElement.scrollTop = logElement.scrollHeight;
}

// 处理底部按钮点击
function handleFooterButtonClick(buttonText) {
    switch(buttonText) {
        case '设置':
            showSettings();
            break;
        case '事件':
            showEventWindow();
            break;
        case '训练模型(事件对应属性增减)':
            trainModel();
            break;
        case '分析趋势':
            analyzeTrends();
            break;
        case '同步健康数据':
            loadHealthData();
            break;
        case '趋势图':
            showTrendCharts();
            break;
        case '周报':
            generateWeeklyReport();
            break;
        case '月报':
            generateMonthlyReport();
            break;
        case '重置(下次打开生效)':
            resetData();
            break;
    }
}

// 初始化函数
let syncInterval;


// ... 保持现有代码不变 ...

// 语音识别功能
class SpeechRecognitionManager {
    constructor() {
        this.recorder = null;
        this.mediaStream = null;
        this.isRecording = false;
    }

    async initialize() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.recorder = new MediaRecorder(this.mediaStream);
            
            this.recorder.ondataavailable = async (event) => {
                if (event.data.size > 0) {
                    const formData = new FormData();
                    formData.append('audio', new Blob([event.data], { type: 'audio/wav' }));
                    
                    try {
                        const response = await fetch('/api/speech/record', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        if (result.text) {
                            showAnalysisResult({ message: `语音识别结果: ${result.text}` });
                            // 处理语音命令
                            handleVoiceCommand(result.text);
                        }
                    } catch (error) {
                        console.error('语音识别失败:', error);
                        showAnalysisResult({ message: '语音识别失败，请重试' });
                    }
                }
            };
        } catch (error) {
            console.error('初始化语音识别失败:', error);
            showAnalysisResult({ message: '初始化语音识别失败，请检查麦克风权限' });
        }
    }

    startRecording(duration = 5) {
        if (!this.recorder || this.isRecording) return;
        
        this.isRecording = true;
        this.recorder.start();
        showAnalysisResult({ message: '开始录音...' });
        
        setTimeout(() => {
            this.stopRecording();
        }, duration * 1000);
    }

    stopRecording() {
        if (!this.recorder || !this.isRecording) return;
        
        this.recorder.stop();
        this.isRecording = false;
        showAnalysisResult({ message: '录音结束，正在识别...' });
    }
}

// 语音命令处理
function handleVoiceCommand(text) {
    const commands = {
        '分析': () => analyzeWithAI(),
        '趋势': () => analyzeTrends(),
        '周报': () => generateWeeklyReport(),
        '月报': () => generateMonthlyReport(),
        '设置': () => showSettings(),
        '事件': () => showEventWindow(),
        '训练': () => trainModel(),
        '同步': () => loadHealthData()
    };

    for (const [command, action] of Object.entries(commands)) {
        if (text.includes(command)) {
            action();
            break;
        }
    }
}

// 初始化语音识别
const speechManager = new SpeechRecognitionManager();

// 更新初始化函数
async function initialize() {
    await loadHealthData();
    await checkThresholds();
    await speechManager.initialize();
    updateCurrentTime();
    initializeEventListeners();
    
    // 每秒更新时间
    setInterval(updateCurrentTime, 1000);
    
    // 定期同步数据
    syncInterval = setInterval(loadHealthData, settings.syncInterval * 60 * 1000);
}

// 添加语音按钮事件
function initializeEventListeners() {
    // ... 保持现有事件监听器不变 ...

    // 添加语音按钮
    const voiceButton = document.createElement('button');
    voiceButton.className = 'gradient-button';
    voiceButton.textContent = '语音输入';
    voiceButton.style.position = 'fixed';
    voiceButton.style.bottom = '20px';
    voiceButton.style.right = '20px';
    voiceButton.style.zIndex = '1000';
    
    voiceButton.addEventListener('mousedown', () => {
        speechManager.startRecording();
    });
    
    voiceButton.addEventListener('mouseup', () => {
        speechManager.stopRecording();
    });
    
    voiceButton.addEventListener('mouseleave', () => {
        if (speechManager.isRecording) {
            speechManager.stopRecording();
        }
    });
    
    document.body.appendChild(voiceButton);
}



// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initialize);