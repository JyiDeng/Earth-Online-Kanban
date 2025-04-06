// API基础配置
const API_BASE_URL = 'http://localhost:5000/api';

// API请求工具函数
async function apiRequest(endpoint, options = {}) {
    console.log(`开始API请求: ${endpoint}`, options);
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        console.log(`API响应状态: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            console.error('API响应错误:', {
                status: response.status,
                statusText: response.statusText,
                endpoint,
                options
            });
            throw new Error(`API请求失败: ${response.status}`);
        }

        const result = await response.json();
        console.log(`API响应数据:`, result);
        return result;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// API服务对象
export async function getHealthData(cacheParam = '') {
    try {
        console.log('开始获取健康数据...');
        // 添加时间戳参数避免浏览器缓存
        const timestamp = `${cacheParam || ''}${cacheParam ? '&' : '?'}t=${Date.now()}`;
        const data = await apiRequest(`/health-data${timestamp}`);
        console.log('获取到的健康数据:', data);
        return data;
    } catch (error) {
        console.error('获取健康数据失败:', error);
        throw error;
    }
}

export async function syncHealthData(data) {
    try {
        console.log('开始同步健康数据...', data);
        const result = await apiRequest('/health/sync', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        console.log('同步健康数据结果:', result);
        return result;
    } catch (error) {
        console.error('同步健康数据失败:', error);
        throw error;
    }
}

export const getEvents = async function() {
    try {
        const response = await apiRequest('/events');
        return response;
    } catch (error) {
        console.error('获取事件列表失败:', error);
        return [];
    }
};

export const createEvent = async function(eventData) {
    try {
        const response = await apiRequest('/events', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
        return response;
    } catch (error) {
        console.error('创建事件失败:', error);
        throw error;
    }
};

export const updateEvent = async function(eventId, eventData) {
    try {
        const response = await apiRequest(`/events/${eventId}`, {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
        return response;
    } catch (error) {
        console.error('更新事件失败:', error);
        throw error;
    }
};

export const deleteEvent = async function(eventId) {
    try {
        const response = await apiRequest(`/events/${eventId}`, {
            method: 'DELETE'
        });
        return response;
    } catch (error) {
        console.error('删除事件失败:', error);
        throw error;
    }
};

export const getEventSuggestions = async function() {
    try {
        const response = await apiRequest('/event-suggestions');
        return response;
    } catch (error) {
        console.error('获取事件建议失败:', error);
        return {};
    }
};

export const calculateEventImpact = async function(eventData) {
    try {
        const response = await apiRequest('/event-impact', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
        return response;
    } catch (error) {
        console.error('计算事件影响失败:', error);
        // 返回默认影响
        return {
            status: 'error',
            event: {
                name: eventData.name,
                type: eventData.type,
                duration: eventData.duration
            },
            impact: {}
        };
    }
};

export const trainModel = async function(trainingData) {
    try {
        const response = await apiRequest('/model/train', {
            method: 'POST',
            body: JSON.stringify(trainingData)
        });
        return response;
    } catch (error) {
        console.error('训练模型失败:', error);
        throw error;
    }
};

export const getModelStatus = async function() {
    try {
        const response = await apiRequest('/model/status');
        return response;
    } catch (error) {
        console.error('获取模型状态失败:', error);
        return { status: 'error' };
    }
};

export const analyzeWithAI = async function(data) {
    try {
        console.log('开始AI分析...', data);
        const response = await apiRequest('/analyze', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        console.log('AI分析结果:', response);
        return response;
    } catch (error) {
        console.error('AI分析失败:', error);
        return { 
            status: 'error', 
            analysis: [],
            message: error.message || '分析失败，请稍后重试'
        };
    }
};

export const getTrends = async function() {
    try {
        const response = await apiRequest('/history');
        return response;
    } catch (error) {
        console.error('获取趋势数据失败:', error);
        return [];
    }
};

export const generateReport = async function(reportType, dateRange) {
    try {
        const response = await apiRequest('/reports/generate', {
            method: 'POST',
            body: JSON.stringify({ reportType, dateRange })
        });
        return response;
    } catch (error) {
        console.error('生成报告失败:', error);
        return { status: 'error', content: '' };
    }
};

export const getSettings = async function() {
    try {
        const response = await apiRequest('/settings');
        return response;
    } catch (error) {
        console.error('获取设置失败:', error);
        return { syncInterval: 5, alertThreshold: 30 };
    }
};

export const updateSettings = async function(settings) {
    try {
        const response = await apiRequest('/settings', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
        return response;
    } catch (error) {
        console.error('更新设置失败:', error);
        throw error;
    }
};

export async function getThresholds() {
    try {
        const thresholds = await apiRequest('/thresholds');
        return thresholds;
    } catch (error) {
        console.error('获取阈值设置失败:', error);
        // 返回默认阈值而不是抛出错误
        return {
            hunger: 20,
            thirst: 20,
            toilet: 80,
            social: 30,
            fatigue: 80,
            hygiene: 30,
            fitness: 30,
            happiness: 30,
            achievement: 30,
            eyeFatigue: 80,
            sleepQuality: 30,
            heartHealth: 30,
            muscle: 30,
            agility: 30,
            resistance: 30,
            timeControl: 30,
            creativity: 30,
            security: 30
        };
    }
}

export const updateThresholds = async function(thresholds) {
    try {
        const response = await apiRequest('/thresholds', {
            method: 'POST',
            body: JSON.stringify(thresholds)
        });
        return response;
    } catch (error) {
        console.error('更新阈值设置失败:', error);
        throw error;
    }
};

export const recordSpeech = async function(audioData) {
    try {
        const formData = new FormData();
        formData.append('audio', audioData);
        const response = await fetch(`${API_BASE_URL}/speech/record`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error(`语音识别失败: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('语音识别失败:', error);
        return { status: 'error', text: '' };
    }
}; 