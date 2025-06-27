// pages/record/record.js
const app = getApp();

Page({
  data: {
    currentYear: 0,
    currentMonth: '',
    selectedDay: 0,
    lastMonthDays: [],
    currentMonthDays: [],
    nextMonthDays: [],
    mealRecords: {
      breakfast: [],
      lunch: [],
      dinner: [],
      snack: []
    }
  },

  onLoad: function() {
    // 初始化当前日期
    const today = new Date();
    this.setData({
      currentYear: today.getFullYear(),
      selectedDay: today.getDate()
    });
    // 初始化日历
    this.initCalendar(today.getFullYear(), today.getMonth() + 1);
    // 加载饮食记录
    this.loadMealRecords();
  },

  // 初始化日历
  initCalendar: function(year, month) {
    // 设置当前年月显示
    this.setData({
      currentMonth: `${year}年${month}月`
    });

    // 获取当月第一天是星期几 (0-6)
    const firstDay = new Date(year, month - 1, 1).getDay();
    // 获取当月天数
    const daysInMonth = this.getDaysInMonth(year, month);
    // 获取上月天数
    const daysInLastMonth = month > 1 ? this.getDaysInMonth(year, month - 1) : this.getDaysInMonth(year - 1, 12);

    // 生成上月日期
    const lastMonthDays = [];
    for (let i = 0; i < firstDay; i++) {
      lastMonthDays.push(daysInLastMonth - firstDay + i + 1);
    }

    // 生成当月日期
    const currentMonthDays = [];
    for (let i = 1; i <= daysInMonth; i++) {
      currentMonthDays.push(i);
    }

    // 生成下月日期
    const nextMonthDays = [];
    const totalDays = lastMonthDays.length + currentMonthDays.length;
    const nextMonthDaysCount = 7 - (totalDays % 7) || 7;
    for (let i = 1; i <= nextMonthDaysCount; i++) {
      nextMonthDays.push(i);
    }

    this.setData({
      lastMonthDays: lastMonthDays,
      currentMonthDays: currentMonthDays,
      nextMonthDays: nextMonthDays
    });
  },

  // 获取月份天数
  getDaysInMonth: function(year, month) {
    return new Date(year, month, 0).getDate();
  },

  // 切换到上月
  prevMonth: function() {
    const currentDate = new Date(this.data.currentYear, this.getMonthFromDisplay() - 1, 1);
    currentDate.setMonth(currentDate.getMonth() - 1);
    this.setData({
      currentYear: currentDate.getFullYear()
    });
    this.initCalendar(currentDate.getFullYear(), currentDate.getMonth() + 1);
    this.loadMealRecords();
  },

  // 切换到下月
  nextMonth: function() {
    const currentDate = new Date(this.data.currentYear, this.getMonthFromDisplay() - 1, 1);
    currentDate.setMonth(currentDate.getMonth() + 1);
    this.setData({
      currentYear: currentDate.getFullYear()
    });
    this.initCalendar(currentDate.getFullYear(), currentDate.getMonth() + 1);
    this.loadMealRecords();
  },

  // 从显示文本中获取月份
  getMonthFromDisplay: function() {
    return parseInt(this.data.currentMonth.split('年')[1].replace('月', ''));
  },

  // 回到今天
  goToToday: function() {
    const today = new Date();
    this.setData({
      currentYear: today.getFullYear(),
      selectedDay: today.getDate()
    });
    this.initCalendar(today.getFullYear(), today.getMonth() + 1);
    this.loadMealRecords();
  },

  // 选择日期
  selectDate: function(e) {
    const day = e.currentTarget.dataset.day;
    this.setData({
      selectedDay: day
    });
    this.loadMealRecords();
  },

  // 加载饮食记录
  loadMealRecords: function() {
    const year = this.data.currentYear;
    const month = this.getMonthFromDisplay();
    const day = this.data.selectedDay;
    const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

    // 从本地存储获取记录
    const mealRecords = wx.getStorageSync('mealRecords') || {};
    const records = mealRecords[dateStr] || {
      breakfast: [],
      lunch: [],
      dinner: [],
      snack: []
    };

    this.setData({
      mealRecords: records
    });
  },

  // 检查日期是否有记录
  hasRecord: function(day) {
    const year = this.data.currentYear;
    const month = this.getMonthFromDisplay();
    const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    const mealRecords = wx.getStorageSync('mealRecords') || {};
    const records = mealRecords[dateStr] || {};

    // 检查是否有任何一餐有记录
    for (const meal in records) {
      if (records[meal] && records[meal].length > 0) {
        return true;
      }
    }
    return false;
  },

  // 获取餐次总热量
  getMealCalories: function(mealType) {
    const meal = this.data.mealRecords[mealType] || [];
    return meal.reduce((total, food) => total + (food.calories || 0), 0);
  },

  // 添加食物
  addFood: function(e) {
    const mealType = e.currentTarget.dataset.meal;
    // 跳转到拍照页面，并传递餐次类型
    wx.navigateTo({
      url: `/pages/camera/camera?mealType=${mealType}`
    });
  },

  // 删除食物
  deleteFood: function(e) {
    const { meal, id } = e.currentTarget.dataset;
    const mealRecords = this.data.mealRecords;

    // 过滤掉要删除的食物
    mealRecords[meal] = mealRecords[meal].filter(item => item.id !== id);

    // 更新本地存储
    const year = this.data.currentYear;
    const month = this.getMonthFromDisplay();
    const day = this.data.selectedDay;
    const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    const allRecords = wx.getStorageSync('mealRecords') || {};
    allRecords[dateStr] = mealRecords;
    wx.setStorageSync('mealRecords', allRecords);

    // 更新页面数据
    this.setData({
      mealRecords: mealRecords
    });

    // 显示删除成功提示
    wx.showToast({
      title: '已删除',
      icon: 'success',
      duration: 1000
    });
  },

  // 跳转到拍照页面
  goToCamera: function() {
    wx.navigateTo({
      url: '/pages/camera/camera'
    });
  }
})