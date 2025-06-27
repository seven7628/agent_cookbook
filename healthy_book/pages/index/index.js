// pages/index/index.js
const app = getApp();
const echarts = require('../../ec-canvas/echarts');

Page({
  data: {
    userInfo: {},
    date: '',
    calorieData: {
      current: 0,
      target: 0,
      percent: 0
    },
    nutritionData: {
      protein: 25,
      carb: 55,
      fat: 20
    },
    mealRecords: {
      breakfast: [],
      lunch: [],
      dinner: [],
      snack: []
    },
    ec: {
      onInit: function(canvas, width, height) {
        const chart = echarts.init(canvas, null, {
          width: width,
          height: height
        });
        canvas.setChart(chart);
        return chart;
      }
    }
  },

  onLoad: function() {
    // 初始化日期
    this.initDate();
    // 获取用户信息
    this.getUserInfo();
    // 加载饮食记录
    this.loadMealRecords();
    // 初始化营养图表
    this.initNutritionChart();
  },

  // 初始化日期
  initDate: function() {
    const date = new Date();
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
    const weekDay = weekDays[date.getDay()];
    this.setData({
      date: `${year}年${month}月${day}日 周${weekDay}`
    });
  },

  // 获取用户信息
  getUserInfo: function() {
    const userInfo = wx.getStorageSync('userInfo') || {};
    // 计算目标热量
    const targetCalories = app.calculateTargetCalories(userInfo);
    // 获取今日已摄入热量
    const today = this.formatDate(new Date());
    const mealRecords = wx.getStorageSync('mealRecords') || {};
    const todayRecords = mealRecords[today] || {};
    let currentCalories = 0;

    // 计算总热量
    for (const meal in todayRecords) {
      if (todayRecords[meal] && todayRecords[meal].length) {
        todayRecords[meal].forEach(food => {
          currentCalories += food.calories || 0;
        });
      }
    }

    this.setData({
      userInfo: userInfo,
      calorieData: {
        current: currentCalories,
        target: targetCalories,
        percent: Math.min(Math.round((currentCalories / targetCalories) * 100), 100)
      }
    });
  },

  // 加载饮食记录
  loadMealRecords: function() {
    const today = this.formatDate(new Date());
    const mealRecords = wx.getStorageSync('mealRecords') || {};
    const todayRecords = mealRecords[today] || {
      breakfast: [
        { id: 1, name: '全麦面包', image: '/images/food-example1.jpg', amount: '2片', calories: 180 },
        { id: 2, name: '煎蛋', image: '/images/food-example2.jpg', amount: '1个', calories: 90 }
      ],
      lunch: [
        { id: 3, name: '糙米饭', image: '/images/food-example3.jpg', amount: '1碗', calories: 150 },
        { id: 4, name: '清蒸鱼', image: '/images/food-example4.jpg', amount: '100g', calories: 120 }
      ],
      dinner: [],
      snack: []
    };

    this.setData({
      mealRecords: todayRecords
    });
  },

  // 初始化营养图表
  initNutritionChart: function() {
    this.ecComponent = this.selectComponent('#nutritionChart');
    this.ecComponent.init((canvas, width, height) => {
      const chart = echarts.init(canvas, null, {
        width: width,
        height: height
      });

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}%'
        },
        legend: {
          show: false
        },
        series: [
          {
            name: '营养比例',
            type: 'pie',
            radius: ['60%', '80%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 30,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              {
                value: this.data.nutritionData.protein,
                name: '蛋白质',
                itemStyle: { color: '#4A90E2' }
              },
              {
                value: this.data.nutritionData.carb,
                name: '碳水',
                itemStyle: { color: '#7ED321' }
              },
              {
                value: this.data.nutritionData.fat,
                name: '脂肪',
                itemStyle: { color: '#F5A623' }
              }
            ]
          }
        ]
      };

      chart.setOption(option);
      return chart;
    });
  },

  // 格式化日期为YYYY-MM-DD
  formatDate: function(date) {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
  },

  // 跳转到拍照页面
  goToCamera: function() {
    wx.navigateTo({
      url: '/pages/camera/camera'
    });
  }
})