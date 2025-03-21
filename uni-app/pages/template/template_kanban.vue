<template>
    <view class="container">
      <!-- 顶部状态栏 -->
      <view class="header">
        <view class="title">地球 Online</view>
        <view class="user-info">玩家名称: 地球玩家001</view>
      </view>
  
      <!-- 主要内容区域 -->
      <scroll-view class="content" scroll-y>
        <!-- 三个状态卡片 -->
        <view class="status-cards">
          <view class="status-card">
            <view class="card-title">生理需求</view>
            <view class="status-items">
              <view class="status-item">
                <uni-icons type="shop" size="24" color="#666"></uni-icons>
                <text>饱腹</text>
                <view class="progress-bar">
                  <view class="progress" :style="{ width: '22%', backgroundColor: '#ff4d4f' }"></view>
                </view>
                <text>22%</text>
              </view>
              <!-- 其他生理状态项 -->
              <view v-for="(item, index) in physiologicalStatus" :key="index" class="status-item">
                <uni-icons :type="item.icon" size="24" color="#666"></uni-icons>
                <text>{{ item.name }}</text>
                <view class="progress-bar">
                  <view class="progress" :style="{ width: item.value + '%', backgroundColor: item.color }"></view>
                </view>
                <text>{{ item.value }}%</text>
              </view>
            </view>
          </view>
  
          <view class="status-card">
            <view class="card-title">社会需求</view>
            <view class="status-items">
              <view v-for="(item, index) in socialStatus" :key="index" class="status-item">
                <uni-icons :type="item.icon" size="24" color="#666"></uni-icons>
                <text>{{ item.name }}</text>
                <view class="progress-bar">
                  <view class="progress" :style="{ width: item.value + '%', backgroundColor: item.color }"></view>
                </view>
                <text>{{ item.value }}%</text>
              </view>
            </view>
          </view>
  
          <view class="status-card">
            <view class="card-title">能力属性</view>
            <view class="status-items">
              <view v-for="(item, index) in abilityStatus" :key="index" class="status-item">
                <uni-icons :type="item.icon" size="24" color="#666"></uni-icons>
                <text>{{ item.name }}</text>
                <view class="progress-bar">
                  <view class="progress" :style="{ width: item.value + '%', backgroundColor: item.color }"></view>
                </view>
                <text>{{ item.value }}%</text>
              </view>
            </view>
          </view>
        </view>
  
        <!-- AI分析区域 -->
        <view class="analysis-section">
          <view class="section-title">AI状态分析</view>
          <view class="analysis-content">
            <view class="analysis-item">
              <view class="item-title">### 1. 需要注意的问题</view>
              <view class="item-content">
                <text>**饱腹**：当前饱腹值为24.2%，非常低，说明玩家可能长时间没有进食，可能导致体力下降和健康问题。</text>
              </view>
            </view>
          </view>
          <button class="analysis-btn cursor-pointer" @click="handleAnalysis">AI分析当前状态</button>
        </view>
  
        <!-- 阈值设置区域 -->
        <view class="threshold-section">
          <view class="section-title">阈值预警设置</view>
          <view class="threshold-content">
            <view v-for="(item, index) in thresholdSettings" :key="index" class="threshold-item">
              <text>{{ item.name }}: {{ item.value }} (预定时间: {{ item.time }})</text>
            </view>
          </view>
          <button class="threshold-btn cursor-pointer" @click="handleThreshold">设置阈值处理</button>
        </view>
      </scroll-view>
  
      <!-- 底部导航栏 -->
      <view class="tab-bar">
        <view v-for="(tab, index) in tabs" :key="index" class="tab-item cursor-pointer" @click="handleTabClick(index)">
          <view class="tab-icon">
            <uni-icons :type="tab.icon" :size="28" :color="currentTab === index ? '#00BCD4' : '#999999'"></uni-icons>
          </view>
          <text :class="['tab-text', currentTab === index ? 'active' : '']">{{ tab.name }}</text>
        </view>
      </view>
    </view>
  </template>
  
  <script lang="ts" setup>
  import { ref } from 'vue';
  
  interface StatusItem {
    name: string;
    value: number;
    icon: string;
    color: string;
  }
  
  interface TabItem {
    name: string;
    icon: string;
  }
  
  interface ThresholdItem {
    name: string;
    value: number;
    time: string;
  }
  
  const currentTab = ref(0);
  
  const tabs: TabItem[] = [
    { name: '看板', icon: 'chart' },
    { name: '事件', icon: 'calendar' },
    { name: '训练', icon: 'staff' },
    { name: '趋势', icon: 'chart-box' },
    { name: '同步', icon: 'refresh' }
  ];
  
  const physiologicalStatus: StatusItem[] = [
    { name: '口渴', value: 66, icon: 'cup', color: '#ffa940' },
    { name: '如厕', value: 55, icon: 'info', color: '#ffa940' },
    { name: '肥胖指数', value: 33, icon: 'person', color: '#ffa940' },
    { name: '心脏健康度', value: 45, icon: 'heart', color: '#ffa940' }
  ];
  
  const socialStatus: StatusItem[] = [
    { name: '社交', value: 70, icon: 'staff', color: '#ffa940' },
    { name: '情绪', value: 73, icon: 'emotion', color: '#52c41a' },
    { name: '成就感', value: 67, icon: 'medal', color: '#ffa940' },
    { name: '情商', value: 48, icon: 'star', color: '#ffa940' },
    { name: '安全感', value: 57, icon: 'shield', color: '#ffa940' }
  ];
  
  const abilityStatus: StatusItem[] = [
    { name: '肌肉强度', value: 57, icon: 'hand-up', color: '#ffa940' },
    { name: '敏捷', value: 24, icon: 'run', color: '#ff4d4f' },
    { name: '抗击打能力', value: 45, icon: 'shield', color: '#ffa940' },
    { name: '魅力', value: 30, icon: 'star', color: '#ff4d4f' },
    { name: '道德', value: 48, icon: 'heart-filled', color: '#ffa940' }
  ];
  
  const thresholdSettings: ThresholdItem[] = [
    { name: '饱腹', value: 30.0, time: '' },
    { name: '口渴', value: 30.0, time: '11:14' },
    { name: '如厕', value: 30.0, time: '' },
    { name: '肥胖指数', value: 30.0, time: '' },
    { name: '心脏健康度', value: 30.0, time: '' }
  ];
  
  const handleTabClick = (index: number) => {
    currentTab.value = index;
  };
  
  const handleAnalysis = () => {
    // AI分析处理逻辑
    console.log('AI分析当前状态');
  };
  
  const handleThreshold = () => {
    // 阈值设置处理逻辑
    console.log('设置阈值处理');
  };
  </script>
  
  <style>
  page {
    height: 100%;
  }
  
  .container {
    height: 100%;
    display: flex;
    flex-direction: column;
    background-color: #f5f5f5;
  }
  
  .header {
    padding: 20rpx 30rpx;
    background-color: #ffffff;
    border-bottom: 1px solid #eee;
    flex-shrink: 0;
  }
  
  .title {
    font-size: 36rpx;
    color: #00BCD4;
    font-weight: bold;
  }
  
  .user-info {
    font-size: 24rpx;
    color: #666;
    margin-top: 10rpx;
  }
  
  .content {
    flex: 1;
    overflow: auto;
    padding: 20rpx;
  }
  
  .status-cards {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .status-card {
    background-color: #ffffff;
    border-radius: 16rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
  }
  
  .card-title {
    font-size: 28rpx;
    color: #333;
    margin-bottom: 20rpx;
    font-weight: bold;
  }
  
  .status-items {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
  }
  
  .status-item {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }
  
  .status-item text {
    font-size: 24rpx;
    color: #666;
    width: 120rpx;
  }
  
  .progress-bar {
    flex: 1;
    height: 16rpx;
    background-color: #f0f0f0;
    border-radius: 8rpx;
    overflow: hidden;
  }
  
  .progress {
    height: 100%;
    border-radius: 8rpx;
    transition: width 0.3s ease;
  }
  
  .analysis-section,
  .threshold-section {
    margin-top: 20rpx;
    background-color: #ffffff;
    border-radius: 16rpx;
    padding: 20rpx;
  }
  
  .section-title {
    font-size: 28rpx;
    color: #333;
    margin-bottom: 20rpx;
    font-weight: bold;
  }
  
  .analysis-content,
  .threshold-content {
    font-size: 24rpx;
    color: #666;
    line-height: 1.6;
  }
  
  .analysis-btn,
  .threshold-btn {
    margin-top: 20rpx;
    background-color: #00BCD4;
    color: #ffffff;
    font-size: 28rpx;
  }
  
  .tab-bar {
    height: 100rpx;
    background-color: #ffffff;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border-top: 1px solid #eee;
    flex-shrink: 0;
  }
  
  .tab-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
  }
  
  .tab-text {
    font-size: 24rpx;
    color: #999999;
  }
  
  .tab-text.active {
    color: #00BCD4;
  }
  
  .cursor-pointer {
    cursor: pointer;
  }
  
  .item-title {
    font-weight: bold;
    margin-bottom: 10rpx;
  }
  
  .item-content {
    color: #666;
    line-height: 1.6;
  }
  
  .threshold-item {
    margin-bottom: 10rpx;
  }
  </style>
  
  