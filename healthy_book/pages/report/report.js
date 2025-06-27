// report.js
Page({
  data: {
    // 健康评分
    healthScore: 85,
    // 报告日期范围
    reportDateRange: '2023年10月20日 - 10月26日',
    // 健康评分描述
    scoreDescription: {
      title: '本周饮食整体均衡',
      content: '蛋白质摄入充足，但碳水化合物略高，建议增加蔬菜比例。'
    },
    // 热量摄入数据
    calorieData: {
      days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      consumed: [1850, 2100, 1950, 2200, 1800, 2300, 1900],
      target: [2000, 2000, 2000, 2000, 2000, 2000, 2000]
    },
    // 营养结构数据
    nutritionData: {
      protein: { actual: 25, target: 20 },
      carb: { actual: 55, target: 50 },
      fat: { actual: 20, target: 30 }
    },
    // 饮食建议
    suggestions: [
      {
        icon: '/images/suggestion-icon1.png',
        title: '增加蔬菜摄入',
        desc: '建议每日摄入不少于300g蔬菜，增加膳食纤维。'
      },
      {
        icon: '/images/suggestion-icon2.png',
        title: '控制精制碳水',
        desc: '减少白米饭、面包等精制碳水，替换为粗粮。'
      },
      {
        icon: '/images/suggestion-icon3.png',
        title: '保证优质蛋白',
        desc: '继续保持优质蛋白摄入，如鸡蛋、鱼类、瘦肉。'
      }
    ]
  },

  onLoad: function() {
    // 绘制热量趋势图
    this.drawCalorieChart();
    // 绘制营养结构图表
    this.drawNutritionCharts();
  },

  // 绘制热量趋势图
  drawCalorieChart: function() {
    const ctx = wx.createCanvasContext('calorieChart', this);
    const data = this.data.calorieData;
    const canvasWidth = wx.getSystemInfoSync().windowWidth - 60; // 减去padding
    const canvasHeight = 400;
    const padding = { top: 40, right: 30, bottom: 60, left: 50 };
    const chartWidth = canvasWidth - padding.left - padding.right;
    const chartHeight = canvasHeight - padding.top - padding.bottom;

    // 设置X轴和Y轴刻度
    const xStep = chartWidth / (data.days.length - 1);
    const maxCalorie = Math.max(...data.consumed, ...data.target) * 1.2;
    const yStep = chartHeight / maxCalorie;

    // 绘制网格线
    ctx.setStrokeStyle('#f0f0f0');
    ctx.setLineWidth(1);
    // 横向网格线
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + chartHeight - (i * chartHeight / 5);
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
      ctx.stroke();
      // 绘制Y轴刻度
      ctx.setFontSize(20);
      ctx.setFillStyle('#999');
      ctx.fillText(Math.round(maxCalorie * i / 5), padding.left - 40, y + 5);
    }

    // 绘制X轴刻度
    data.days.forEach((day, index) => {
      const x = padding.left + index * xStep;
      ctx.setFontSize(20);
      ctx.setFillStyle('#666');
      ctx.fillText(day, x - 15, padding.top + chartHeight + 30);
    });

    // 绘制摄入热量线
    ctx.setStrokeStyle('#4A90E2');
    ctx.setLineWidth(4);
    data.consumed.forEach((value, index) => {
      const x = padding.left + index * xStep;
      const y = padding.top + chartHeight - value * yStep;
      if (index === 0) {
        ctx.beginPath();
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      // 绘制数据点
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, 2 * Math.PI);
      ctx.setFillStyle('#4A90E2');
      ctx.fill();
    });
    ctx.stroke();

    // 绘制目标热量线
    ctx.setStrokeStyle('#F5A623');
    ctx.setLineWidth(2);
    ctx.setLineDash([5, 5]);
    data.target.forEach((value, index) => {
      const x = padding.left + index * xStep;
      const y = padding.top + chartHeight - value * yStep;
      if (index === 0) {
        ctx.beginPath();
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.draw();
  },

  // 绘制营养结构图表
  drawNutritionCharts: function() {
    this.drawNutritionChart('proteinChart', this.data.nutritionData.protein, '#4A90E2');
    this.drawNutritionChart('carbChart', this.data.nutritionData.carb, '#F5A623');
    this.drawNutritionChart('fatChart', this.data.nutritionData.fat, '#7ED321');
  },

  // 绘制单个营养结构图表
  drawNutritionChart: function(canvasId, data, color) {
    const ctx = wx.createCanvasContext(canvasId, this);
    const centerX = 100;
    const centerY = 100;
    const radius = 80;
    const actualPercent = Math.min(data.actual / data.target, 1); // 最大100%
    const targetPercent = 1;

    // 绘制背景圆环
    ctx.setStrokeStyle('#f0f0f0');
    ctx.setLineWidth(15);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // 绘制目标圆环
    ctx.setStrokeStyle('#e0e0e0');
    ctx.setLineWidth(15);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -0.5 * Math.PI, (targetPercent * 2 - 0.5) * Math.PI);
    ctx.stroke();

    // 绘制实际圆环
    ctx.setStrokeStyle(color);
    ctx.setLineWidth(15);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -0.5 * Math.PI, (actualPercent * 2 - 0.5) * Math.PI);
    ctx.stroke();

    // 绘制文字
    ctx.setFontSize(30);
    ctx.setFillStyle('#333');
    ctx.setTextAlign('center');
    ctx.setTextBaseline('middle');
    ctx.fillText(`${data.actual}%`, centerX, centerY);

    ctx.draw();
  },

  // 分享报告
  shareReport: function() {
    wx.showActionSheet({
      itemList: ['分享到微信好友', '分享到朋友圈', '保存图片'],
      success: (res) => {
        switch(res.tapIndex) {
          case 0:
            // 分享到微信好友
            this.shareToWeChat();
            break;
          case 1:
            // 分享到朋友圈
            this.shareToTimeline();
            break;
          case 2:
            // 保存图片
            this.saveReportImage();
            break;
        }
      }
    });
  },

  // 分享到微信好友
  shareToWeChat: function() {
    wx.showToast({
      title: '分享给微信好友',
      icon: 'none'
    });
    // 实际项目中调用微信分享API
  },

  // 分享到朋友圈
  shareToTimeline: function() {
    wx.showToast({
      title: '分享到朋友圈',
      icon: 'none'
    });
    // 实际项目中调用微信分享API
  },

  // 保存报告图片
  saveReportImage: function() {
    wx.showToast({
      title: '保存图片到相册',
      icon: 'none'
    });
    // 实际项目中调用canvas生成图片并保存
  }
})