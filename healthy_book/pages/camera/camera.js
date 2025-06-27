// pages/camera/camera.js
Page({
  data: {
    previewVisible: false,
    previewImage: '',
    cameraContext: null,
    mealType: ''
  },

  onLoad: function(options) {
    // 初始化相机上下文
    this.setData({
      cameraContext: wx.createCameraContext(),
      mealType: options.mealType || '' // 接收从记录页传递的餐次类型
    });

    // 请求相机权限
    this.requestCameraPermission();
  },

  // 请求相机权限
  requestCameraPermission: function() {
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.camera']) {
          wx.authorize({
            scope: 'scope.camera',
            success: () => {},
            fail: () => {
              wx.showModal({
                title: '权限申请',
                content: '需要相机权限才能使用拍照功能',
                success: (res) => {
                  if (res.confirm) {
                    wx.openSetting();
                  } else {
                    wx.navigateBack();
                  }
                }
              });
            }
          });
        }
      }
    });
  },

  // 拍照
  takePhoto: function() {
    const ctx = this.data.cameraContext;
    ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        this.setData({
          previewVisible: true,
          previewImage: res.tempImagePath
        });
      },
      fail: (err) => {
        wx.showToast({
          title: '拍照失败',
          icon: 'none'
        });
        console.error('拍照失败:', err);
      }
    });
  },

  // 从相册选择图片
  chooseImage: function() {
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album'],
      success: (res) => {
        this.setData({
          previewVisible: true,
          previewImage: res.tempFilePaths[0]
        });
      },
      fail: (err) => {
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
        console.error('选择图片失败:', err);
      }
    });
  },

  // 重拍
  retakePhoto: function() {
    this.setData({
      previewVisible: false,
      previewImage: ''
    });
  },

  // 确认照片（跳转到识别结果页）
  confirmPhoto: function() {
    if (!this.data.previewImage) return;

    // 显示加载中提示
    wx.showLoading({
      title: '识别中...',
      mask: true
    });

    // 模拟AI识别过程（实际项目中这里会调用后端API）
    setTimeout(() => {
      wx.hideLoading();
      // 跳转到识别结果页，并传递图片路径和餐次类型
      wx.navigateTo({
        url: `/pages/recognition/result?imagePath=${encodeURIComponent(this.data.previewImage)}&mealType=${this.data.mealType}`
      });
    }, 1500);
  },

  // 返回上一页
  navigateBack: function() {
    wx.navigateBack();
  },

  // 相机错误处理
  cameraError: function(e) {
    console.error('相机错误:', e.detail);
    wx.showToast({
      title: '相机初始化失败',
      icon: 'none'
    });
    wx.navigateBack();
  }
})