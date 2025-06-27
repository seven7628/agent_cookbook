// pages/profile/profile.js
Page({
  data: {
    userInfo: {},
    bodyData: {
      height: 0,
      weight: 0,
      bmi: 0,
      targetCalories: 0
    },
    menuItems: [
      {
        icon: '/images/icon-settings.png',
        text: '设置',
        path: '/pages/settings/settings'
      },
      {
        icon: '/images/icon-preferences.png',
        text: '饮食偏好',
        path: '/pages/preferences/preferences'
      },
      {
        icon: '/images/icon-favorite.png',
        text: '常用食物',
        path: '/pages/favorite-foods/favorite-foods'
      },
      {
        icon: '/images/icon-history.png',
        text: '历史报告',
        path: '/pages/history-reports/history-reports'
      },
      {
        icon: '/images/icon-help.png',
        text: '帮助中心',
        path: '/pages/help/help'
      },
      {
        icon: '/images/icon-about.png',
        text: '关于我们',
        path: '/pages/about/about'
      }
    ]
  },

  onLoad: function() {
    // 获取应用实例
    this.app = getApp();
    // 加载用户信息
    this.loadUserInfo();
  },

  onShow: function() {
    // 页面显示时重新加载用户信息
    this.loadUserInfo();
  },

  // 加载用户信息
  loadUserInfo: function() {
    // 从本地存储获取用户信息
    const userInfo = wx.getStorageSync('userInfo') || {};
    // 计算BMI
    const bmi = this.app.calculateBMI(userInfo.height, userInfo.weight);
    // 计算目标热量
    const targetCalories = this.app.calculateTargetCalories(userInfo);
    // 更新数据
    this.setData({
      userInfo: userInfo,
      bodyData: {
        height: userInfo.height || 0,
        weight: userInfo.weight || 0,
        bmi: bmi,
        targetCalories: targetCalories
      }
    });
  },

  // 跳转到编辑个人信息页面
  goToEditProfile: function() {
    wx.navigateTo({
      url: '/pages/profile/edit/edit'
    });
  },

  // 跳转到身体数据页面
  goToBodyData: function() {
    wx.navigateTo({
      url: '/pages/profile/body-data/body-data'
    });
  },

  // 菜单点击事件
  onMenuItemTap: function(e) {
    const path = e.currentTarget.dataset.path;
    if (path) {
      wx.navigateTo({
        url: path
      });
    }
  },

  // 退出登录
  logout: function() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出当前账号吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除用户信息（保留基础设置）
          const userInfo = wx.getStorageSync('userInfo') || {};
          const basicInfo = {
            height: userInfo.height || 0,
            weight: userInfo.weight || 0,
            age: userInfo.age || 0,
            gender: userInfo.gender || 0,
            activityLevel: userInfo.activityLevel || 'medium',
            target: userInfo.target || 'maintain'
          };
          wx.setStorageSync('userInfo', {
            ...basicInfo,
            nickname: '健康饮食用户',
            avatarUrl: '/images/avatar-default.png'
          });
          // 更新页面数据
          this.loadUserInfo();
          // 显示提示
          wx.showToast({
            title: '已退出',
            icon: 'success'
          });
        }
      }
    });
  }
})