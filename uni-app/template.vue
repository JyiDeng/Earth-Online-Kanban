
<template>
    <view class="page">
      <!-- 顶部标题栏 -->
      <view class="header">
        <text class="title">状态监测</text>
        <text class="user-id">玩家名称: {{ playerId }}</text>
      </view>
  
      <!-- 三大状态模块 -->
      <scroll-view class="content" scroll-y>
        <!-- 生理需求模块 -->
        <view class="status-card">
          <view class="card-title">生理需求</view>
          <view class="indicators">
            <view class="indicator-item" v-for="(item, index) in physiological" :key="index">
              <view class="indicator-header">
                <uni-icons :type="item.icon" size="20" :color="getIconColor(item.value)"/>
                <text class="indicator-name">{{ item.name }}</text>
              </view>
              <view class="progress-container">
                <view class="progress-bar">
                  <view 
                    class="progress-inner" 
                    :style="{ width: item.value + '%', backgroundColor: getProgressColor(item.value) }"
                  ></view>
                </view>
                <text class="progress-value">{{ item.value }}%</text>
              </view>
            </view>
          </view>
        </view>
  
        <!-- 社会需求模块 -->
        <view class="status-card">
          <view class="card-title">社会需求</view>
          <view class="indicators">
            <view class="indicator-item" v-for="(item, index) in social" :key="index">
              <view class="indicator-header">
                <uni-icons :type="item.icon" size="20" :color="getIconColor(item.value)"/>
                <text class="indicator-name">{{ item.name }}</text>
              </view>
              <view class="progress-container">
                <view class="progress-bar">
                  <view 
                    class="progress-inner" 
                    :style="{ width: item.value + '%', backgroundColor: getProgressColor(item.value) }"
                  ></view>
                </view>
                <text class="progress-value">{{ item.value }}%</text>
              </view>
            </view>
          </view>
        </view>
  
        <!-- 能力属性模块 -->
        <view class="status-card">
          <view class="card-title">能力属性</view>
          <view class="indicators">
            <view class="indicator-item" v-for="(item, index) in ability" :key="index">
              <view class="indicator-header">
                <uni-icons :type="item.icon" size="20" :color="getIconColor(item.value)"/>
                <text class="indicator-name">{{ item.name }}</text>
              </view>
              <view class="progress-container">
                <view class="progress-bar">
                  <view 
                    class="progress-inner" 
                    :style="{ width: item.value + '%', backgroundColor: getProgressColor(item.value) }"
                  ></view>
                </view>
                <text class="progress-value">{{ item.value }}%</text>
              </view>
            </view>
          </view>
        </view>
  
        <!-- 系统日志 -->
        <view class="log-section">
          <view class="log-title" @click="toggleLog">
            系统日志
            <uni-icons :type="showLog ? 'top' : 'bottom'" size="16"/>
          </view>
          <view class="log-content" v-if="showLog">
            <view class="log-item" v-for="(log, index) in systemLogs" :key="index">
              {{ log }}
            </view>
          </view>
        </view>
      </scroll-view>
  
      <!-- 底部功能按钮 -->
      <view class="footer">
        <view class="button-group">
          <uni-button class="action-button" @click="handleAction('设置')">设置</uni-button>
          <uni-button class="action-button" @click="handleAction('保存数据')">保存数据</uni-button>
          <uni-button class="action-button" @click="handleAction('事件')">事件</uni-button>
          <uni-button class="action-button" @click="handleAction('训练模型')">训练模型</uni-button>
          <uni-button class="action-button" @click="handleAction('分析趋势')">分析趋势</uni-button>
        </view>
        <uni-button class="reset-button" @click="handleReset">重置</uni-button>
      </view>
    </view>
  </template>
  
  <script lang="ts" setup>
  import { ref } from 'vue'
  
  const playerId = ref('地球玩家001')
  const showLog = ref(false)
  
  const physiological = ref([
    { name: '饱腹', value: 60, icon: 'star' },
    { name: '口渴', value: 57, icon: 'hand-down' },
    { name: '如厕', value: 47, icon: 'info' },
    { name: '肥胖指数', value: 51, icon: 'staff' },
    { name: '心脏健康度', value: 84, icon: 'heart' }
  ])
  
  const social = ref([
    { name: '社交', value: 57, icon: 'chat' },
    { name: '情绪', value: 71, icon: 'emotion' },
    { name: '成就感', value: 59, icon: 'medal' },
    { name: '情商', value: 73, icon: 'heart-filled' },
    { name: '安全感', value: 79, icon: 'shield' }
  ])
  
  const ability = ref([
    { name: '肌肉强度', value: 48, icon: 'staff' },
    { name: '敏捷', value: 54, icon: 'arrow-right' },
    { name: '抗击打能力', value: 59, icon: 'shield' },
    { name: '魅力', value: 64, icon: 'star' },
    { name: '道德', value: 73, icon: 'info' }
  ])
  
  const systemLogs = ref([
    '自动调整 口渴 变化率: -0.0331 (趋势: -0.3294)',
    '历史数据已保存 - 2025-03-20 10:15:02',
    '自动调整 社交 变化率: 0.0053 (趋势: 0.0836)',
    '自动调整 情绪 变化率: -0.0098 (趋势: -0.095ε)'
  ])
  
  const getProgressColor = (value: number) => {
    return value >= 70 ? '#4CD964' : '#FF9500'
  }
  
  const getIconColor = (value: number) => {
    return value >= 70 ? '#4CD964' : '#FF9500'
  }
  
  const toggleLog = () => {
    showLog.value = !showLog.value
  }
  
  const handleAction = (action: string) => {
    // 处理按钮点击事件
    console.log(`点击了${action}按钮`)
  }
  
  const handleReset = () => {
    // 处理重置事件
    console.log('点击了重置按钮')
  }
  </script>
  
  <style>
  page {
    height: 100%;
  }
  
  .page {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: #F5F5F5;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 30rpx;
    background-color: #FFFFFF;
    border-bottom: 1px solid #EEEEEE;
    flex-shrink: 0;
  }
  
  .title {
    font-size: 16px;
    font-weight: bold;
    color: #333333;
  }
  
  .user-id {
    font-size: 14px;
    color: #666666;
  }
  
  .content {
    flex: 1;
    overflow: auto;
    padding: 20rpx;
  }
  
  .status-card {
    background-color: #FFFFFF;
    border-radius: 16rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .card-title {
    font-size: 16px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 30rpx;
  }
  
  .indicators {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .indicator-item {
    display: flex;
    flex-direction: column;
    gap: 10rpx;
  }
  
  .indicator-header {
    display: flex;
    align-items: center;
    gap: 10rpx;
  }
  
  .indicator-name {
    font-size: 14px;
    color: #666666;
  }
  
  .progress-container {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }
  
  .progress-bar {
    flex: 1;
    height: 20rpx;
    background-color: #F5F5F5;
    border-radius: 10rpx;
    overflow: hidden;
  }
  
  .progress-inner {
    height: 100%;
    transition: width 0.3s ease;
  }
  
  .progress-value {
    font-size: 14px;
    color: #999999;
    width: 60rpx;
    text-align: right;
  }
  
  .log-section {
    background-color: #FFFFFF;
    border-radius: 16rpx;
    margin-bottom: 120rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .log-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20rpx 30rpx;
    font-size: 14px;
    color: #333333;
    border-bottom: 1px solid #EEEEEE;
  }
  
  .log-content {
    padding: 20rpx 30rpx;
  }
  
  .log-item {
    font-size: 12px;
    color: #666666;
    font-family: monospace;
    margin-bottom: 10rpx;
  }
  
  .footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20rpx;
    background-color: #FFFFFF;
    border-top: 1px solid #EEEEEE;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .button-group {
    display: flex;
    gap: 20rpx;
  }
  
  .action-button {
    font-size: 14px;
    padding: 0 20rpx;
    background-color: #007AFF;
    color: #FFFFFF;
  }
  
  .reset-button {
    font-size: 14px;
    padding: 0 30rpx;
    background-color: #FF3B30;
    color: #FFFFFF;
  }
  
  .cursor-pointer {
    cursor: pointer;
  }
  </style>
  
  