// result.js
Page({
  data: {
    imagePath: '',
    foodInfo: {
      name: '未知食物',
      confidence: 0,
      nutrition: {
        calories: 0,
        protein: 0,
        carb: 0,
        fat: 0
      }
    },
    similarFoods: [],
    portion: 1,
    unit: '份',
    mealType: 'lunch' // 默认午餐
  },

  onLoad: function(options) {
    // 获取图片路径和餐次类型
    this.setData({
      imagePath: options.imagePath || '',
      mealType: options.mealType || 'lunch'
    });

    // 模拟AI识别结果
    this.simulateRecognition();
  },

  // 模拟AI识别结果
  simulateRecognition: function() {
    // 模拟不同食物的识别结果
    const foodOptions = [
      {
        name: '烤鸡胸肉',
        confidence: 92,
        nutrition: {
          calories: 165,
          protein: 31,
          carb: 0,
          fat: 3.6
        },
        similar: ['鸡胸肉', '水煮鸡胸', '煎鸡胸']
      },
      {
        name: '糙米饭',
        confidence: 88,
        nutrition: {
          calories: 111,
          protein: 2.6,
          carb: 23,
          fat: 0.9
        },
        similar: ['白米饭', '燕麦饭', '藜麦饭']
      },
      {
        name: '炒青菜',
        confidence: 85,
        nutrition: {
          calories: 35,
          protein: 2.6,
          carb: 7,
          fat: 0.4
        },
        similar: ['水煮青菜', '凉拌青菜', '西兰花']
      }
    ];

    // 随机选择一个食物作为识别结果
    const randomIndex = Math.floor(Math.random() * foodOptions.length);
    const selectedFood = foodOptions[randomIndex];

    this.setData({
      foodInfo: selectedFood,
      similarFoods: selectedFood.similar.map(name => ({name}))
    });
  },

  // 返回上一页
  navigateBack: function() {
    wx.navigateBack({
      delta: 1
    });
  },

  // 选择相似食物
  selectSimilarFood: function(e) {
    const index = e.currentTarget.dataset.index;
    const selectedFoodName = this.data.similarFoods[index].name;

    // 模拟切换到相似食物的营养数据
    this.setData({
      foodInfo: {
        ...this.data.foodInfo,
        name: selectedFoodName,
        confidence: 80 + Math.floor(Math.random() * 15)
      }
    });
  },

  // 减少份量
  decreasePortion: function() {
    if (this.data.portion > 0.5) {
      this.setData({
        portion: this.data.portion - 0.5
      });
    }
  },

  // 增加份量
  increasePortion: function() {
    this.setData({
      portion: this.data.portion + 0.5
    });
  },

  // 设置单位
  setUnit: function(e) {
    const unit = e.currentTarget.dataset.unit;
    this.setData({
      unit: unit
    });
  },

  // 添加到今日饮食
  addToRecord: function() {
    // 计算基于份量的营养数据
    const nutrition = {
      calories: Math.round(this.data.foodInfo.nutrition.calories * this.data.portion),
      protein: Math.round(this.data.foodInfo.nutrition.protein * this.data.portion * 10) / 10,
      carb: Math.round(this.data.foodInfo.nutrition.carb * this.data.portion * 10) / 10,
      fat: Math.round(this.data.foodInfo.nutrition.fat * this.data.portion * 10) / 10
    };

    // 创建要添加的食物记录
    const foodRecord = {
      name: this.data.foodInfo.name,
      image: this.data.imagePath,
      portion: `${this.data.portion}${this.data.unit}`,
      calories: nutrition.calories,
      protein: nutrition.protein,
      carb: nutrition.carb,
      fat: nutrition.fat,
      timestamp: new Date().getTime()
    };

    // 模拟保存到本地存储
    const mealType = this.data.mealType;
    let meals = wx.getStorageSync('mealRecords') || {};
    const today = new Date().toISOString().split('T')[0];

    if (!meals[today]) {
      meals[today] = {
        breakfast: [],
        lunch: [],
        dinner: [],
        snack: []
      };
    }

    meals[today][mealType].push(foodRecord);
    wx.setStorageSync('mealRecords', meals);

    // 显示成功提示并返回记录页面
    wx.showToast({
      title: '添加成功',
      icon: 'success',
      duration: 1500,
      success: () => {
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/record/record'
          });
        }, 1500);
      }
    });
  }
})