// app.js
App({
  onLaunch: function() {
    // 初始化本地存储
    this.initLocalStorage();
    // 检查用户登录状态
    this.checkLoginStatus();
    // 获取系统信息
    this.getSystemInfo();
  },

  // 初始化本地存储
  initLocalStorage: function() {
    // 检查是否有饮食记录数据
    if (!wx.getStorageSync('mealRecords')) {
      wx.setStorageSync('mealRecords', {});
    }
    // 检查是否有用户信息
    if (!wx.getStorageSync('userInfo')) {
      wx.setStorageSync('userInfo', {
        nickname: '健康饮食用户',
        avatarUrl: '/images/avatar-default.png',
        gender: 0,
        age: 0,
        height: 0,
        weight: 0,
        activityLevel: 'medium',
        target: 'maintain'
      });
    }
  },

  // 检查用户登录状态
  checkLoginStatus: function() {
    // 实际项目中这里会调用微信登录接口
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          // 已授权，可以直接调用 getUserInfo 获取头像昵称
          wx.getUserInfo({
            success: (res) => {
              this.globalData.userInfo = res.userInfo;
              // 更新本地存储
              const storedUserInfo = wx.getStorageSync('userInfo') || {};
              wx.setStorageSync('userInfo', {
                ...storedUserInfo,
                nickname: res.userInfo.nickname,
                avatarUrl: res.userInfo.avatarUrl,
                gender: res.userInfo.gender
              });
            }
          });
        }
      }
    });
  },

  // 获取系统信息
  getSystemInfo: function() {
    const systemInfo = wx.getWindowInfo();
    this.globalData.systemInfo = systemInfo;
    this.globalData.screenWidth = systemInfo.screenWidth;
    this.globalData.screenHeight = systemInfo.screenHeight;
    this.globalData.pixelRatio = systemInfo.pixelRatio;
  },

  // 计算BMI
  calculateBMI: function(height, weight) {
    if (!height || !weight) return 0;
    // 身高单位转换为米
    const heightInMeter = height / 100;
    // 计算BMI
    const bmi = weight / (heightInMeter * heightInMeter);
    // 保留一位小数
    return Math.round(bmi * 10) / 10;
  },

  // 计算每日目标热量
  calculateTargetCalories: function(userInfo) {
    if (!userInfo || !userInfo.gender || !userInfo.age || !userInfo.height || !userInfo.weight) {
      return 2000; // 默认值
    }

    let bmr = 0;
    // 使用Mifflin-St Jeor公式计算基础代谢率(BMR)
    if (userInfo.gender === 1) { // 男性
      bmr = 10 * userInfo.weight + 6.25 * userInfo.height - 5 * userInfo.age + 5;
    } else { // 女性
      bmr = 10 * userInfo.weight + 6.25 * userInfo.height - 5 * userInfo.age - 161;
    }

    // 根据活动水平调整
    let activityFactor = 1.2; // 久坐不动
    switch(userInfo.activityLevel) {
      case 'light':
        activityFactor = 1.375; // 轻度活动
        break;
      case 'medium':
        activityFactor = 1.55; // 中度活动
        break;
      case 'high':
        activityFactor = 1.725; // 高度活动
        break;
      case 'extreme':
        activityFactor = 1.9; // 极高活动
        break;
    }

    // 根据目标调整
    let targetFactor = 1; // 维持体重
    switch(userInfo.target) {
      case 'lose':
        targetFactor = 0.85; // 减重
        break;
      case 'gain':
        targetFactor = 1.15; // 增重
        break;
    }

    // 计算目标热量
    const targetCalories = Math.round(bmr * activityFactor * targetFactor);
    return targetCalories;
  },

  globalData: {
    userInfo: null,
    systemInfo: null,
    screenWidth: 0,
    screenHeight: 0,
    pixelRatio: 1
  }
})