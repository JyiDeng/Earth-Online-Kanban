<template>
  <view class="home-container">
    <view class="title">
      <text>🌍 地球Online看板</text>
    </view>
    
    <view class="buttons">
      <button class="enter-btn" @click="enterKanban">进入看板</button>
      <button class="manual-btn" @click="showManual">用户手册</button>
    </view>

    <view class="manual" v-if="showManualContent">
      <view class="manual-title">用户手册</view>
      <view class="manual-content">
        <view class="section">
          <view class="section-title">基本功能</view>
          <view class="section-item">• 属性监控：实时显示15种生理、情感和能力属性的状态</view>
          <view class="section-item">• 数据同步：支持与Apple Watch等智能设备同步健康数据</view>
          <view class="section-item">• 智能分析：AI分析当前状态并提供改善建议</view>
        </view>
        
        <view class="section">
          <view class="section-title">按钮功能说明</view>
          <view class="section-item">• 保存数据：点击保存按钮将当前所有属性状态保存</view>
          <view class="section-item">• 设置：可以自定义玩家名称、初始属性值和变化速率</view>
          <view class="section-item">• 事件输入：记录生活事件，系统会预测对属性的影响</view>
          <view class="section-item">• 数据分析：查看属性变化趋势和预测</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      showManualContent: false
    }
  },
  methods: {
    enterKanban() {
      uni.navigateTo({
        url: '/pages/kanban/index'
      })
    },
    showManual() {
      this.showManualContent = !this.showManualContent
    }
  }
}
</script>

<style>
.home-container {
  padding: 30px;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

.title {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 40px;
}

.title text {
  font-size: 28px;
  color: #ffffff;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0,255,255,0.5);
}

.buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.enter-btn, .manual-btn {
  width: 200px;
  height: 50px;
  border: none;
  border-radius: 25px;
  font-size: 18px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.enter-btn {
  background: linear-gradient(45deg, #00b4db, #0083b0);
  box-shadow: 0 4px 15px rgba(0,180,219,0.3);
}

.manual-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5253);
  box-shadow: 0 4px 15px rgba(255,107,107,0.3);
}

.enter-btn:hover, .manual-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,180,219,0.4);
}

.manual {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255,255,255,0.1);
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.manual-title {
  font-size: 24px;
  color: #ffffff;
  text-align: center;
  margin-bottom: 20px;
}

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  color: #00b4db;
  margin-bottom: 10px;
}

.section-item {
  color: #ffffff;
  margin-bottom: 8px;
  font-size: 16px;
  line-height: 1.5;
}
</style> 