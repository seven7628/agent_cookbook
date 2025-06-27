<template>
  <div class="app-container">
    <header>
      <h1>饮食分析助手</h1>
    </header>

    <main class="content">
      <!-- 文件上传区域 -->
      <section class="upload-section">
        <div class="upload-container">
          <input
            type="file"
            id="food-image"
            accept="image/*"
            @change="handleFileUpload"
            class="file-input"
          />
          <label for="food-image" class="upload-label">
            <div v-if="!imagePreview" class="upload-placeholder">
              <svg class="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <p>点击上传饮食照片</p>
            </div>
            <img v-else :src="imagePreview" class="preview-image" alt="饮食照片预览" />
          </label>
        </div>

        <!-- 餐食类型选择 -->
        <div class="meal-type-selector" v-if="imagePreview">
          <p>请选择餐食类型：</p>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="selectedMealType" value="breakfast" required />
              <span>早餐</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="selectedMealType" value="lunch" required />
              <span>午餐</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="selectedMealType" value="dinner" required />
              <span>晚餐</span>
            </label>
          </div>
          <button @click="submitAnalysis" class="submit-btn" :disabled="!selectedMealType">
            开始分析
          </button>
        </div>
      </section>

      <!-- 分析结果区域 -->
      <section class="results-section" v-if="Object.keys(agentResults).length > 0">
        <h2>分析结果</h2>
        <div class="agent-results">
          <!-- 动态渲染所有agent结果 -->
          <div v-for="(content, agentName) in agentResults" :key="agentName" class="agent-card">
            <div class="agent-header">
              <span class="agent-tip">Tips</span>
              <h3>{{ getAgentDisplayName(agentName) }} ({{ agentName }})</h3>
            </div>
            <div class="agent-content" :class="{ 'expanded': expandedAgents[agentName] }">
              <div v-html="renderMarkdown(content)"></div>
            </div>
            <button
              v-if="content.length > 300"
              @click="toggleExpand(agentName)"
              class="expand-btn"
            >
              {{ expandedAgents[agentName] ? '收起' : '展开全部' }}
              <svg class="expand-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" :class="{ 'rotated': expandedAgents[agentName] }"><path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer>
      <p>饮食分析助手 &copy; 2023</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { marked } from 'marked';

// 状态管理
const imagePreview = ref(null);
const selectedMealType = ref('');
const agentResults = ref({});
const expandedAgents = ref({});
const isAnalyzing = ref(false);

// 处理文件上传
function handleFileUpload(e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      imagePreview.value = event.target.result;
      // 重置状态
      selectedMealType.value = '';
      agentResults.value = {};
    };
    reader.readAsDataURL(file);
  }
}

// 切换展开/收起状态
function toggleExpand(agentName) {
  expandedAgents.value[agentName] = !expandedAgents.value[agentName];
}

// 渲染Markdown
function renderMarkdown(content) {
  return marked.parse(content);
}

// 获取agent显示名称
function getAgentDisplayName(agentName) {
  const displayNames = {
    vl_reason: '视觉分析',
    summarizer: '营养总结',
    tool_call_result: '工具调用结果',
    message_chunk: '消息更新',
    tools: '工具调用',
    planner: '规划器',
    eval: '评估器'
  };
  return displayNames[agentName] || agentName;
}

// 提交分析请求
async function submitAnalysis() {
  if (!imagePreview.value || !selectedMealType.value) return;

  isAnalyzing.value = true;
  agentResults.value = {};

  try {
    // 创建FormData
    const formData = new FormData();
    // 从dataURL获取Blob对象
    const response = await fetch(imagePreview.value);
    const blob = await response.blob();
    formData.append('image', blob, 'food.jpg');
    formData.append('content', '帮我计算33+44等于多少')
    formData.append('meal_type', selectedMealType.value);

    // 发送请求并处理流式响应
    const analysisResponse = await fetch('http://localhost:8000/api/stream', {
      method: 'POST',
      body: formData,
    });

    if (!analysisResponse.ok) throw new Error('分析请求失败');
    const reader = analysisResponse.body.getReader();
    const decoder = new TextDecoder();
    let eventBuffer = '';
    let currentEvent = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
    
      // 处理流式数据
      const chunk = decoder.decode(value, { stream: true });
      eventBuffer += chunk;
    
      // 分割事件流 (SSE格式)
      const eventSeparator = '\n\n';
      let eventIndex;
        while ((eventIndex = eventBuffer.indexOf(eventSeparator)) !== -1) {
          const eventData = eventBuffer.substring(0, eventIndex);
        eventBuffer = eventBuffer.substring(eventIndex + eventSeparator.length);
    
        // 解析单个事件
        if (eventData.startsWith('event:tool_calls')) {
          // 已有的tool_calls事件处理逻辑
          const dataLines = eventData.split('\n').filter(line => line.startsWith('data:'));
          if (dataLines.length > 0) {
            const dataContent = dataLines[0].replace('data:', '').trim();
            try {
              const parsedData = JSON.parse(dataContent);
              // 处理tool_calls数据
              if (parsedData.tool_calls && parsedData.tool_calls.length > 0) {
                parsedData.tool_calls.forEach(toolCall => {
                  if (toolCall.name && toolCall.args) {
                    // 构建Markdown内容
                    let content = `### ${toolCall.name}\n`;
                     
                    // 处理步骤信息
                    if (toolCall.args.steps && toolCall.args.steps.length > 0) {
                      content += '#### 处理步骤\n';
                      toolCall.args.steps.forEach((step, index) => {
                        content += `${index + 1}. **${step.title}**\n`;
                        content += `${step.description}\n`;
                        if (step.tool_params) {
                          content += '参数: ' + JSON.stringify(step.tool_params, null, 2) + '\n';
                        }
                      });
                    } else {
                      // 普通JSON数据格式化
                      content += '```json\n';
                      content += JSON.stringify(toolCall.args, null, 2);
                      content += '\n```';
                    }
    
                    // 更新agent结果
                    const existingContent = agentResults.value[toolCall.name] || '';
                    agentResults.value[toolCall.name] = existingContent + '\n---\n' + content;
                    // 控制展开状态
                    if (content.length > 300) {
                      expandedAgents.value[toolCall.name] = false;
                    }
                  }
                });
              }
            } catch (e) {
              console.error('解析工具调用数据失败:', e);
            }
          }
        } else if (eventData.startsWith('event:message_chunk')) {
          // 处理message_chunk事件
          const dataLines = eventData.split('\n').filter(line => line.startsWith('data:'));
          if (dataLines.length > 0) {
            const dataContent = dataLines[0].replace('data:', '').trim();
            try {
              const parsedData = JSON.parse(dataContent);
              // 支持agent和agent_name两种字段格式
              const agentName = parsedData.agent || parsedData.agent_name;
              if (agentName && parsedData.content !== undefined) {
                 
                // 更新对应agent的结果
                const existingContent = agentResults.value[agentName] || '';
                
                if (existingContent != "") {
                  agentResults.value[agentName] = existingContent + parsedData.content;
                }else {
                  agentResults.value[agentName] = `### 消息更新 (${agentName})\n` + parsedData.content;
                }
                if (content.length > 300) {
                  expandedAgents.value[agentName] = false;
                }
              }
            } catch (e) {
              console.error('解析消息块数据失败:', e);
            }
          }
        } else if (eventData.startsWith('event:tool_call_result')) {
           // 处理tool_call_result事件
           const dataLines = eventData.split('\n').filter(line => line.startsWith('data:'));
           if (dataLines.length > 0) {
             const dataContent = dataLines[0].replace('data:', '').trim();
             try {
               const parsedData = JSON.parse(dataContent);
               if (parsedData.agent && parsedData.content !== undefined) {
                 // 构建工具调用结果内容
                 let content = `### 工具调用结果 (${parsedData.agent})\n`;
                 if (parsedData.tool_call_id) {
                   content += `**调用ID**: ${parsedData.tool_call_id}\n\n`;
                 }
                 content += `**结果**: ${parsedData.content}`;
                 
                 // 更新对应agent的结果
                 const existingContent = agentResults.value[parsedData.agent] || '';
                  agentResults.value[parsedData.agent] = existingContent + '\n---\n' + content;
                 if (content.length > 300) {
                   expandedAgents.value[parsedData.agent] = false;
                 }
               }
             } catch (e) {
               console.error('解析工具调用结果失败:', e);
             }
           }
         }
      }
    }
  } catch (error) {
    console.error('分析过程出错:', error);
    alert('分析失败，请重试');
  } finally {
    isAnalyzing.value = false;
  }
}
</script>

<style scoped>
/* 基础样式 */
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  color: #333;
}

header h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

footer {
  text-align: center;
  margin-top: 50px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* 上传区域样式 */
.upload-section {
  max-width: 600px;
  margin: 0 auto 40px;
}

.upload-container {
  border: 2px dashed #3498db;
  border-radius: 10px;
  padding: 30px;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.upload-container:hover {
  border-color: #2980b9;
  background-color: #f8f9fa;
}

.file-input {
  display: none;
}

.upload-label {
  display: block;
  cursor: pointer;
  text-align: center;
}

.upload-placeholder {
  color: #3498db;
  padding: 40px 20px;
}

.upload-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 15px;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 餐食选择器样式 */
.meal-type-selector {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-label input {
  margin-right: 8px;
}

.submit-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.submit-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

/* 结果区域样式 */
.results-section {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.agent-results {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.agent-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.agent-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.agent-tip {
  background-color: #3498db;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 10px;
}

.agent-header h3 {
  margin: 0;
  color: #2c3e50;
}

.agent-content {
  max-height: 300px;
  overflow: hidden;
  transition: max-height 0.3s ease;
  line-height: 1.6;
}

.agent-content.expanded {
  max-height: none;
}

.expand-btn {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
  padding: 5px 0;
}

.expand-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    padding: 15px;
  }

  .upload-container {
    padding: 20px 10px;
  }

  .radio-group {
    flex-direction: column;
    gap: 10px;
  }

  .agent-content {
    max-height: 200px;
  }
}
</style>
