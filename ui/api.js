// API基础配置
const API_BASE_URL = 'http://localhost:5000/api';

// API请求工具函数
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`API请求失败: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// API服务对象
const apiService = {
    // 健康数据相关
    async getHealthData() {
        return await apiRequest('/health-data');
    },

    async updateHealthData(data) {
        return await apiRequest('/health-data', 'POST', data);
    },

    // 事件相关
    async getEvents() {
        return await apiRequest('/events');
    },

    async createEvent(eventData) {
        return await apiRequest('/events', 'POST', eventData);
    },

    async updateEvent(eventId, eventData) {
        return await apiRequest(`/events/${eventId}`, 'PUT', eventData);
    },

    async deleteEvent(eventId) {
        return await apiRequest(`/events/${eventId}`, 'DELETE');
    },

    // 模型训练相关
    async trainModel(trainingData) {
        return await apiRequest('/model/train', 'POST', trainingData);
    },

    async getModelStatus() {
        return await apiRequest('/model/status');
    },

    // 分析相关
    async analyzeWithAI(data) {
        return await apiRequest('/analysis/ai', 'POST', data);
    },

    async getTrends() {
        return await apiRequest('/analysis/trends');
    },

    // 报告相关
    async generateReport(reportType, dateRange) {
        return await apiRequest('/reports/generate', 'POST', { reportType, dateRange });
    },

    // 设置相关
    async getSettings() {
        return await apiRequest('/settings');
    },

    async updateSettings(settings) {
        return await apiRequest('/settings', 'PUT', settings);
    },

    // 阈值相关
    async getThresholds() {
        return await apiRequest('/thresholds');
    },

    async updateThresholds(thresholds) {
        return await apiRequest('/thresholds', 'PUT', thresholds);
    }
};

export default apiService; 