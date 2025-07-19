<template>
  <div class="test-ai-quiz">
    <!-- 课程选择和生成按钮 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="flex-grow">
          <label class="block text-sm font-medium text-gray-700 mb-1">选择课程</label>
          <select 
            v-model="selectedCourseId" 
            class="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>
        
        <div class="flex-shrink-0 self-end">
          <button 
            @click="openQuizConfigModal" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            :disabled="!selectedCourseId || isGenerating"
          >
            <span v-if="isGenerating">
              <span class="inline-block animate-spin mr-1">⟳</span> 生成中...
            </span>
            <span v-else>生成自测测验</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 历史自测记录 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <h2 class="text-lg font-semibold mb-4">自测历史记录</h2>
      
      <div v-if="quizHistory.length === 0" class="text-center py-6 text-gray-500">
        暂无自测记录
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">课程</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">题目数量</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">得分</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="quiz in quizHistory" :key="quiz.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ quiz.courseName }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatDate(quiz.createdAt) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ quiz.questionCount }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs rounded-full"
                  :class="{
                    'bg-yellow-100 text-yellow-800': quiz.status === 'generating',
                    'bg-green-100 text-green-800': quiz.status === 'completed',
                    'bg-blue-100 text-blue-800': quiz.status === 'in_progress',
                    'bg-gray-100 text-gray-800': quiz.status === 'abandoned',
                    'bg-orange-100 text-orange-800': quiz.status === 'grading' || quiz.status === 'graded'
                  }"
                >
                  {{ getStatusText(quiz.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ quiz.score !== null ? `${quiz.score}分` : '未完成' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button 
                  @click="continueQuiz(quiz)" 
                  class="text-blue-600 hover:text-blue-800 mr-2"
                >
                  {{ quiz.status === 'completed' ? '查看' : '继续' }}
                </button>
                <button 
                  @click="deleteQuiz(quiz.id)" 
                  class="text-red-600 hover:text-red-800"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 测验配置弹窗 -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">自测测验配置</h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">难度</label>
          <select v-model="quizConfig.difficulty" class="w-full px-3 py-2 border rounded-md">
            <option value="easy">简单</option>
            <option value="medium">中等</option>
            <option value="hard">困难</option>
          </select>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">题目侧重点 (可选)</label>
          <input 
            v-model="quizConfig.focusPoint" 
            type="text" 
            placeholder="例如：数据结构、网络协议、特定章节..." 
            class="w-full px-3 py-2 border rounded-md"
          />
          <p class="mt-1 text-xs text-gray-500">输入您希望题目侧重的知识点或主题</p>
        </div>
        
        <div class="mb-4">
          <div class="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
            <p class="text-sm text-blue-700">
              <span class="font-medium">逐题生成模式：</span>
              题目将逐个生成，每生成一道题即可开始作答，无需等待全部生成完毕。
            </p>
          </div>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">题目类型和数量</label>
          <div class="space-y-2">
            <div v-for="type in questionTypes" :key="type.value" class="flex items-center">
              <input 
                type="checkbox" 
                :id="type.value" 
                v-model="quizConfig.selectedTypes[type.value]"
                class="mr-2"
              />
              <label :for="type.value" class="text-sm flex-grow">{{ type.label }}</label>
              <input 
                v-if="quizConfig.selectedTypes[type.value]"
                v-model="quizConfig.counts[type.value]" 
                type="number" 
                min="1" 
                max="10" 
                class="w-16 px-2 py-1 border rounded-md"
              />
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2">
          <button 
            @click="showConfigModal = false" 
            class="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="generateQuiz" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            :disabled="!isConfigValid"
          >
            开始生成
          </button>
        </div>
      </div>
    </div>
    
    <!-- 测验界面弹窗 -->
    <div v-if="showQuizModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">AI 自测测验</h3>
          <button @click="closeQuizModal" class="text-gray-500 hover:text-gray-700">
            <span class="text-2xl">&times;</span>
          </button>
        </div>
        
        <!-- 测验状态 -->
        <div v-if="currentQuiz" class="mb-4">
          <div class="flex justify-between items-center">
            <div>
              <span class="text-sm text-gray-600">课程: {{ getCourseName(currentQuiz.courseId) }}</span>
            </div>
            <div v-if="currentQuiz.status === 'generating'" class="flex items-center text-sm text-blue-600">
              <div class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
              <span>{{ currentQuiz.config?.generationMode === 'incremental' ? '正在逐题生成...' : '正在生成题目...' }}</span>
            </div>
          </div>
          
          <!-- 逐题生成模式的提示 -->
          <div v-if="currentQuiz.config?.generationMode === 'incremental' && currentQuiz.status === 'generating'" class="mt-2 text-sm text-gray-600">
            <p v-if="currentQuiz.questions && currentQuiz.questions.length > 0" class="mt-1 text-blue-600 font-medium">
              已生成 {{ currentQuiz.questions.length }} 道题目，可以开始作答。
            </p>
          </div>
        </div>
        
                  <!-- 新题目通知已移除 -->
        
        <!-- 题目导航栏 -->
        <div v-if="currentQuiz && (currentQuiz.questions.length > 0 || currentQuiz.status === 'generating')" class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium text-gray-700">题目导航</h4>
            <div class="flex items-center">
              <span v-if="currentQuiz.status === 'generating'" class="animate-pulse mr-2 text-blue-600">●</span>
              <span v-else-if="currentQuiz.status === 'grading'" class="animate-pulse mr-2 text-orange-500">●</span>
              <span v-else-if="currentQuiz.status === 'graded'" class="animate-pulse mr-2 text-orange-500">●</span>
              <span class="text-xs" :class="{
                'text-blue-600': currentQuiz.status === 'generating', 
                'text-green-600': currentQuiz.status === 'in_progress', 
                'text-gray-600': currentQuiz.status === 'completed',
                'text-orange-600': currentQuiz.status === 'grading' || currentQuiz.status === 'graded'
              }">
                {{ currentQuiz.status === 'generating' ? '正在逐题生成中...' : 
                   currentQuiz.status === 'in_progress' ? '全部题目已生成' :
                   currentQuiz.status === 'grading' ? 'AI正在评分中...' :
                   currentQuiz.status === 'graded' ? '正在生成学习建议...' : '已完成' }}
                {{ currentQuiz.questions.length > 0 ? `(已生成${currentQuiz.questions.length}题)` : '' }}
              </span>
            </div>
          </div>
          
          <div class="flex flex-wrap gap-2">
            <!-- 已生成的题目按钮 -->
            <button 
              v-for="(_, index) in currentQuiz.questions" 
              :key="index"
              @click="currentQuestionIndex = index"
              class="w-10 h-10 flex items-center justify-center rounded-md border text-sm font-medium"
              :class="{
                'bg-blue-600 text-white border-blue-600': currentQuestionIndex === index,
                'bg-white text-gray-700 border-gray-300 hover:bg-gray-50': currentQuestionIndex !== index,
                'ring-2 ring-blue-300 ring-offset-1': index === currentQuiz.questions.length - 1 && currentQuiz.status === 'generating'
              }"
            >
              {{ index + 1 }}
            </button>
            
            <!-- 正在生成的题目占位按钮 -->
            <div 
              v-if="currentQuiz.status === 'generating'"
              class="w-10 h-10 flex items-center justify-center rounded-md border border-gray-300 bg-gray-50"
            >
              <div class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          </div>
        </div>
        
        <!-- 题目内容 -->
        <div v-if="currentQuiz && currentQuiz.questions.length > 0" class="space-y-6">
          <!-- 当前题目 -->
          <div class="p-4 border rounded-lg">
            <div class="flex justify-between mb-2">
              <span class="font-medium">问题 {{ currentQuestionIndex + 1 }}</span>
              <span class="text-sm text-gray-500">{{ getQuestionTypeText(currentQuiz.questions[currentQuestionIndex].type) }}</span>
            </div>
            
            <div class="mb-3">{{ currentQuiz.questions[currentQuestionIndex].stem }}</div>
            
            <!-- 选择题 (支持各种选择题类型) -->
            <div v-if="isChoiceQuestion(currentQuiz.questions[currentQuestionIndex].type)" 
                 class="space-y-2">
              <div v-if="!currentQuiz.questions[currentQuestionIndex].options || 
                         currentQuiz.questions[currentQuestionIndex].options.length === 0" 
                   class="text-red-500">
                选项数据缺失，请联系管理员
              </div>
              <div 
                v-else
                v-for="(option, optIndex) in currentQuiz.questions[currentQuestionIndex].options" 
                :key="optIndex"
                class="flex items-center"
              >
                <input 
                  type="radio" 
                  :id="`q${currentQuestionIndex}-opt${optIndex}`" 
                  :name="`question-${currentQuestionIndex}`"
                  :value="String.fromCharCode(65 + optIndex)"
                  v-model="currentQuiz.answers[currentQuestionIndex]"
                  :disabled="currentQuiz.status === 'completed'"
                  class="mr-2"
                />
                <label :for="`q${currentQuestionIndex}-opt${optIndex}`">{{ option }}</label>
              </div>
            </div>
            
            <!-- 填空题 (支持各种填空题类型) -->
            <div v-else-if="isFillBlankQuestion(currentQuiz.questions[currentQuestionIndex].type)" class="mt-2">
              <input 
                type="text" 
                v-model="currentQuiz.answers[currentQuestionIndex]"
                class="w-full px-3 py-2 border rounded-md"
                placeholder="请输入答案..."
                :disabled="currentQuiz.status === 'completed'"
              />
            </div>
            
            <!-- 简答题 (支持各种简答题类型) -->
            <div v-else-if="isShortAnswerQuestion(currentQuiz.questions[currentQuestionIndex].type)" class="mt-2">
              <textarea 
                v-model="currentQuiz.answers[currentQuestionIndex]"
                rows="4"
                class="w-full px-3 py-2 border rounded-md"
                placeholder="请输入答案..."
                :disabled="currentQuiz.status === 'completed'"
              ></textarea>
            </div>
            
            <!-- 未知题型 -->
            <div v-else class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md text-yellow-800">
              <p>未知题型: {{ currentQuiz.questions[currentQuestionIndex].type }}</p>
              <textarea 
                v-model="currentQuiz.answers[currentQuestionIndex]"
                rows="4"
                class="w-full mt-2 px-3 py-2 border rounded-md"
                placeholder="请输入答案..."
                :disabled="currentQuiz.status === 'completed'"
              ></textarea>
            </div>
            
            <!-- 评分和反馈 (在graded或completed状态显示) -->
            <div v-if="(currentQuiz.status === 'completed' || currentQuiz.status === 'graded') && currentQuiz.questionScores" class="mt-3 pt-3 border-t">
              <div class="flex justify-between items-center mb-2">
                <div class="font-medium">
                  <span class="text-lg" :class="{
                    'text-green-600': getScorePercentage(currentQuestionIndex) >= 80,
                    'text-yellow-600': getScorePercentage(currentQuestionIndex) >= 60 && getScorePercentage(currentQuestionIndex) < 80,
                    'text-red-600': getScorePercentage(currentQuestionIndex) < 60
                  }">
                    {{ currentQuiz.questionScores[currentQuestionIndex] || 0 }}
                  </span>
                  <span class="text-gray-600"> / {{ currentQuiz.questions[currentQuestionIndex].score || 10 }}</span>
                </div>
                
                <!-- 正确/错误标志 -->
                <div v-if="isObjectiveQuestion(currentQuiz.questions[currentQuestionIndex].type)">
                  <span v-if="isCorrectAnswer(currentQuestionIndex)" class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                    正确
                  </span>
                  <span v-else class="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    错误
                  </span>
                </div>
                <div v-else class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                  AI评分
                </div>
              </div>
              
              <!-- 评语 -->
              <div class="mt-1 text-sm text-gray-700 p-2 bg-gray-50 rounded">
                <div class="font-medium text-gray-700 mb-1">评语:</div>
                <p>{{ currentQuiz.questionFeedback[currentQuestionIndex] || '无评语' }}</p>
              </div>
              
              <!-- 正确答案 (如果答错) -->
              <div v-if="!isCorrectAnswer(currentQuestionIndex) && isObjectiveQuestion(currentQuiz.questions[currentQuestionIndex].type)" class="mt-2 text-sm text-gray-700 p-2 bg-red-50 rounded">
                <div class="font-medium text-red-700 mb-1">正确答案:</div>
                <p>{{ getCorrectAnswer(currentQuestionIndex) }}</p>
              </div>
            </div>
          </div>
          
          <!-- 题目导航按钮 -->
          <div class="flex justify-between">
            <button 
              @click="previousQuestion" 
              class="px-3 py-1 border rounded-md hover:bg-gray-50"
              :disabled="currentQuestionIndex === 0"
              :class="{'opacity-50 cursor-not-allowed': currentQuestionIndex === 0}"
            >
              上一题
            </button>
            <button 
              @click="nextQuestion" 
              class="px-3 py-1 border rounded-md hover:bg-gray-50"
              :disabled="currentQuestionIndex >= currentQuiz.questions.length - 1"
              :class="{'opacity-50 cursor-not-allowed': currentQuestionIndex >= currentQuiz.questions.length - 1}"
            >
              下一题
            </button>
          </div>
        </div>
        
        <!-- 加载中占位符 - 显示逐题生成的状态 -->
        <div v-else-if="currentQuiz && currentQuiz.status === 'generating'" class="py-8 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p class="text-gray-600">
            {{ currentQuiz.config?.generationMode === 'incremental' 
              ? '正在生成第一道题目，请稍候...' 
              : '正在生成题目，请稍候...' }}
          </p>
        </div>
        
        <!-- 提交按钮或评分中状态 -->
        <div class="mt-6">
          <!-- 提交按钮 -->
          <div v-if="currentQuiz && currentQuiz.questions.length > 0 && !['completed', 'graded', 'grading'].includes(currentQuiz.status)" class="flex justify-end">
            <button 
              @click="submitQuiz" 
              class="px-4 py-2 text-white rounded-md"
              :class="{
                'bg-green-600 hover:bg-green-700': !isSubmitting && currentQuiz.status === 'in_progress',
                'bg-gray-400': isSubmitting || currentQuiz.status === 'generating',
                'hover:bg-green-700': !isSubmitting && currentQuiz.status === 'in_progress'
              }"
              :disabled="isSubmitting || currentQuiz.status === 'generating'"
            >
              <span v-if="isSubmitting" class="flex items-center">
                <div class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                提交中...
              </span>
              <span v-else-if="currentQuiz.status === 'generating'">等待题目生成完成...</span>
              <span v-else>提交答案</span>
            </button>
          </div>
          
          <!-- 评分中状态提示 -->
          <div v-if="currentQuiz && (currentQuiz.status === 'grading' || currentQuiz.status === 'graded' || isSubmitting)" class="flex justify-center">
            <div class="w-full max-w-lg px-6 py-4 bg-blue-50 text-blue-700 rounded-md flex items-center shadow-sm border border-blue-100">
              <div class="relative mr-4">
                <div class="animate-spin rounded-full h-8 w-8 border-4 border-blue-200"></div>
                <div class="absolute top-0 left-0 animate-ping rounded-full h-8 w-8 border-4 border-blue-400 opacity-20"></div>
                <div class="absolute top-0 left-0 animate-spin rounded-full h-8 w-8 border-t-4 border-b-4 border-blue-600"></div>
              </div>
              <div>
                <p class="font-medium text-blue-800">
                  {{ currentQuiz.status === 'graded' ? '正在生成学习建议' : 'AI正在评分中' }}
                </p>
                <p class="text-sm text-blue-600">请耐心等待，这可能需要一点时间...</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 测验结果 -->
        <div v-if="currentQuiz && (currentQuiz.status === 'completed' || currentQuiz.status === 'graded')" class="mt-6">
          <!-- 成绩卡片 -->
          <div class="p-4 bg-white border border-green-200 rounded-lg shadow-sm mb-4">
            <h4 class="font-semibold text-lg text-green-800 mb-3">测验结果</h4>
            <div class="flex justify-between items-center mb-3">
              <div class="flex items-center">
                <div class="text-2xl font-bold text-green-600 mr-2">
                  {{ currentQuiz.score || 0 }} / {{ calculateTotalScore() }}
                </div>
                <div class="text-sm bg-green-100 text-green-800 py-1 px-2 rounded">
                  {{ getScoreLevel(currentQuiz.score, calculateTotalScore()) }}
                </div>
              </div>
              <span class="text-sm text-gray-600">完成时间: {{ formatDate(currentQuiz.completedAt) }}</span>
            </div>
            
            <!-- 成绩图表 -->
            <div class="w-full bg-gray-200 rounded-full h-2.5 mb-4">
              <div class="bg-green-600 h-2.5 rounded-full" 
                   :style="`width: ${calculateScorePercentage(currentQuiz.score, calculateTotalScore())}%`"></div>
            </div>
            
            <!-- 题型得分分布 -->
            <div class="mt-4">
              <h5 class="text-sm font-medium text-gray-700 mb-2">题型得分分布</h5>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
                <div v-for="(score, type) in getScoresByType()" :key="type" 
                     class="bg-gray-50 p-2 rounded border border-gray-100">
                  <div class="text-xs text-gray-500">{{ type }}</div>
                  <div class="flex justify-between items-center">
                    <div class="font-medium">{{ score.earned }}/{{ score.total }}</div>
                    <div class="text-xs" :class="{
                      'text-green-600': (score.earned/score.total) >= 0.8,
                      'text-yellow-600': (score.earned/score.total) >= 0.6 && (score.earned/score.total) < 0.8,
                      'text-red-600': (score.earned/score.total) < 0.6
                    }">{{ Math.round((score.earned/score.total)*100) }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- AI学习建议 -->
          <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-center mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z" clip-rule="evenodd" />
              </svg>
              <h4 class="font-semibold text-blue-800">AI学习建议</h4>
              
              <!-- 学习建议生成中状态 -->
              <div v-if="currentQuiz.status === 'graded'" class="ml-2 flex items-center text-xs text-blue-600">
                <div class="animate-spin rounded-full h-3 w-3 border-t-2 border-b-2 border-blue-500 mr-1"></div>
                正在生成学习建议...
              </div>
            </div>
            
            <!-- 学习建议内容 -->
            <div v-if="currentQuiz.status === 'completed' && currentQuiz.feedback" 
                 class="text-sm text-gray-700 whitespace-pre-line">
              {{ currentQuiz.feedback }}
            </div>
            
            <!-- 学习建议生成中占位符 -->
            <div v-else-if="currentQuiz.status === 'graded'" class="text-sm text-gray-500 italic">
              AI正在分析您的答题情况，生成个性化学习建议，请稍候...
            </div>
            
            <!-- 无学习建议 -->
            <div v-else class="text-sm text-gray-500 italic">
              暂无学习建议
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, inject } from 'vue';
import { courseAPI } from '@/api';
import studentQuizAPI from '@/api/studentQuizAPI';
import notificationService from '@/services/notificationService';
import dialogService from '@/services/dialogService';

// 状态变量
const courses = ref([]);
const selectedCourseId = ref('');
const isGenerating = ref(false);
const isSubmitting = ref(false);
const showConfigModal = ref(false);
const showQuizModal = ref(false);
const quizHistory = ref([]);
const currentQuiz = ref(null);
const currentQuestionIndex = ref(0); // 当前题目索引

// 获取全局通知方法
const showNotification = inject('showNotification') || notificationService.show;

// 问题类型定义
const questionTypes = [
  { label: '选择题', value: 'multiple_choice' },
  { label: '填空题', value: 'fill_in_blank' },
  { label: '简答题', value: 'short_answer' }
];

// 测验配置
const quizConfig = reactive({
  difficulty: 'medium',
  generationMode: 'incremental', // 固定使用逐题生成模式
  focusPoint: '', // 题目侧重点
  selectedTypes: {
    multiple_choice: true,
    fill_in_blank: true,
    short_answer: false
  },
  counts: {
    multiple_choice: 5,
    fill_in_blank: 3,
    short_answer: 2
  }
});

// 计算属性
const isConfigValid = computed(() => {
  // 至少选择一种题型且总题目数大于0
  return Object.keys(quizConfig.selectedTypes).some(type => 
    quizConfig.selectedTypes[type] && quizConfig.counts[type] > 0
  );
});

// 生命周期钩子

onMounted(async () => {
  await fetchCourses();
  await fetchQuizHistory();
  checkActiveQuiz();
});

// 组件销毁前清理轮询
onBeforeUnmount(() => {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
    statusPollingInterval = null;
    console.log('组件卸载，清理轮询');
  }
});

// 方法
async function fetchCourses() {
  try {
    const response = await courseAPI.getCourses();
    if (response && response.courses) {
      courses.value = response.courses;
    } else if (Array.isArray(response)) {
      courses.value = response;
    }
  } catch (error) {
    console.error('获取课程失败:', error);
    notificationService.error('获取课程失败', '无法加载课程列表');
  }
}

// 获取测验历史记录
async function fetchQuizHistory() {
  try {
    // 使用示例学生ID (在实际应用中应该从用户会话中获取)
    const response = await studentQuizAPI.getStudentQuizzes(3);
    console.log('测验历史记录:', response);
    
    if (response && response.quizzes) {
      // 更新历史记录
      quizHistory.value = response.quizzes.map(quiz => ({
        id: quiz.id,
        courseId: quiz.course_id,
        courseName: getCourseName(quiz.course_id),
        status: quiz.status,
        questions: quiz.questions || [],
        answers: quiz.answers || [],
        questionScores: quiz.question_scores || [],
        questionFeedback: quiz.question_feedback || [],
        score: quiz.score,
        overallFeedback: quiz.feedback,
        createdAt: quiz.created_at,
        completedAt: quiz.completed_at,
        questionCount: quiz.questions ? quiz.questions.length : 0,
        config: { ...quizConfig }
      }));
      
      // 保存到localStorage作为备份
      saveQuizHistory();
    }
  } catch (error) {
    console.error('获取测验历史记录失败:', error);
    notificationService.warning('获取历史记录失败', '正在尝试从本地缓存加载');
    // 如果API调用失败，尝试从localStorage加载
    loadQuizHistory();
  }
}

function openQuizConfigModal() {
  showConfigModal.value = true;
}

function closeQuizModal() {
  // 如果测验正在生成中，提示用户
  if (currentQuiz.value && currentQuiz.value.status === 'generating') {
    dialogService.confirm({
      title: '关闭确认',
      message: '测验正在生成中，关闭后可以在历史记录中继续。确定要关闭吗？',
      type: 'warning'
    }).then(result => {
      if (result) {
        showQuizModal.value = false;
        currentQuiz.value = null;
        currentQuestionIndex.value = 0; // 关闭时重置题目索引
      }
    });
  } else {
    showQuizModal.value = false;
    currentQuiz.value = null;
    currentQuestionIndex.value = 0; // 关闭时重置题目索引
  }
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
}

function getStatusText(status) {
  const statusMap = {
    'generating': '生成中',
    'in_progress': '进行中',
    'completed': '已完成',
    'abandoned': '已放弃',
    'grading': '评分中',
    'graded': '评分完成'
  };
  return statusMap[status] || status;
}

function getQuestionTypeText(type) {
  const typeMap = {
    // 选择题类型
    'multiple_choice': '选择题',
    'single_choice': '选择题',
    'choice': '选择题',
    'mcq': '选择题',
    'multiple_choice_question': '选择题',
    'selection': '选择题',
    
    // 填空题类型
    'fill_in_blank': '填空题',
    'fill_in_the_blank': '填空题',
    'fill_blank': '填空题',
    'blank_filling': '填空题',
    'completion': '填空题',
    
    // 简答题类型
    'short_answer': '简答题',
    'short_answer_question': '简答题',
    'brief_answer': '简答题',
    'open_question': '简答题',
    'essay': '简答题'
  };
  return typeMap[type] || `未知类型(${type})`;
}

function getCourseName(courseId) {
  const course = courses.value.find(c => c.id === courseId);
  return course ? course.name : '未知课程';
}

function calculateTotalScore() {
  if (!currentQuiz.value || !currentQuiz.value.questions) return 0;
  return currentQuiz.value.questions.reduce((sum, q) => sum + (q.score || 10), 0);
}

// 生成测验 - 只使用逐题生成模式
async function generateQuiz() {
  if (!selectedCourseId.value) return;
  
  isGenerating.value = true;
  showConfigModal.value = false;
  
  try {
    // 准备请求数据
    const requestData = {
      student_id: 3, // 使用示例学生ID (在实际应用中应该从用户会话中获取)
      course_id: selectedCourseId.value,
      difficulty: quizConfig.difficulty,
      question_types: Object.keys(quizConfig.selectedTypes)
        .filter(type => quizConfig.selectedTypes[type])
        .map(type => ({ type, count: quizConfig.counts[type] }))
    };
    
    // 如果设置了侧重点，添加到请求数据中
    if (quizConfig.focusPoint && quizConfig.focusPoint.trim()) {
      requestData.focus_point = quizConfig.focusPoint.trim();
    }
    
    // 创建新的测验对象
    const newQuiz = {
      id: null,
      courseId: selectedCourseId.value,
      courseName: getCourseName(selectedCourseId.value),
      status: 'generating',
      questions: [],
      answers: [],
      questionScores: [],
      questionFeedback: [],
      score: null,
      overallFeedback: null,
      createdAt: new Date().toISOString(),
      completedAt: null,
      questionCount: 0,
      config: { ...quizConfig, generationMode: 'incremental' } // 强制使用逐题生成模式
    };
    
    // 立即显示测验界面
    currentQuiz.value = newQuiz;
    showQuizModal.value = true;
    
    console.log('使用逐题生成模式');
    const response = await studentQuizAPI.generateQuizIncremental(requestData);
    console.log('生成测验响应:', response);
    
    if (response && response.quiz_id) {
      // 更新测验ID
      newQuiz.id = response.quiz_id;
      currentQuiz.value.id = response.quiz_id;
      
      // 添加到历史记录
      quizHistory.value.unshift({...currentQuiz.value});
      saveQuizHistory();
      
      // 立即开始轮询测验状态，使用生成中状态的轮询间隔
      adjustPollingInterval(response.quiz_id, 'generating');
      
      // 立即执行一次状态检查
      await checkQuizStatus(response.quiz_id);
      
      // 显示成功通知
      notificationService.success('测验生成已开始', '题目将逐个生成，您可以开始作答已生成的题目');
    } else {
      console.error('生成测验失败: 无效的响应');
      notificationService.error('生成测验失败', '请重试');
      // 关闭测验窗口
      showQuizModal.value = false;
      currentQuiz.value = null;
    }
  } catch (error) {
    console.error('生成测验失败:', error);
    notificationService.error('生成测验失败', error.message || '请重试');
    // 关闭测验窗口
    showQuizModal.value = false;
    currentQuiz.value = null;
  } finally {
    isGenerating.value = false;
  }
}

// 轮询测验状态
let statusPollingInterval = null;
let lastPollTime = 0;
const POLL_INTERVAL = 8000;      // 默认轮询间隔
const POLL_INTERVAL_GENERATING = 8000; // 生成中状态的轮询间隔
const POLL_INTERVAL_GRADING = 5000;    // 评分中状态的轮询间隔
const POLL_INTERVAL_ADVICE = 10000;    // 学习建议生成状态的轮询间隔

function startPollingQuizStatus(quizId) {
  // 清除之前的轮询
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
    statusPollingInterval = null;
  }
  
  // 立即执行一次状态检查
  checkQuizStatus(quizId);
  
  // 设置轮询间隔
  statusPollingInterval = setInterval(() => checkQuizStatus(quizId), POLL_INTERVAL);
  console.log(`开始轮询测验状态，间隔: ${POLL_INTERVAL}ms`);
}

// 根据测验状态调整轮询间隔或停止轮询
function adjustPollingInterval(quizId, status) {
  // 清除现有的轮询
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
    statusPollingInterval = null;
  }
  
  // 根据状态设置不同的轮询间隔
  if (status === 'generating') {
    // 生成中状态，使用较长的轮询间隔
    statusPollingInterval = setInterval(() => checkQuizStatus(quizId), POLL_INTERVAL_GENERATING);
    console.log(`调整为生成中轮询间隔: ${POLL_INTERVAL_GENERATING}ms`);
  } else if (status === 'grading') {
    // 评分中状态，使用中等的轮询间隔
    statusPollingInterval = setInterval(() => checkQuizStatus(quizId), POLL_INTERVAL_GRADING);
    console.log(`调整为评分中轮询间隔: ${POLL_INTERVAL_GRADING}ms`);
  } else if (status === 'graded') {
    // 已评分但学习建议生成中状态，使用较长的轮询间隔
    statusPollingInterval = setInterval(() => checkQuizStatus(quizId), POLL_INTERVAL_ADVICE);
    console.log(`调整为学习建议生成中轮询间隔: ${POLL_INTERVAL_ADVICE}ms`);
  } else if (status === 'in_progress') {
    // 进行中状态，继续使用较长的轮询间隔，确保获取到所有题目
    statusPollingInterval = setInterval(() => checkQuizStatus(quizId), POLL_INTERVAL_GENERATING);
    console.log(`测验进行中，继续轮询以获取最新题目，间隔: ${POLL_INTERVAL_GENERATING}ms`);
  } else if (status === 'completed' || status === 'error') {
    // 已完成或出错状态，停止轮询
    console.log('测验已完成或出错，停止轮询');
    // 不设置新的轮询
  }
}

// 检查测验状态
async function checkQuizStatus(quizId) {
  // 记录轮询时间
  lastPollTime = Date.now();
  
  try {
    console.log(`正在获取测验 ${quizId} 的状态...`);
    const response = await studentQuizAPI.getQuizStatus(quizId);
    
    if (!response) {
      console.error('获取测验状态失败: 无响应');
      return;
    }
    
    // 打印详细的响应信息，便于调试
    console.log(`测验 ${quizId} 状态:`, response.status);
    console.log(`测验 ${quizId} 题目数量:`, response.questions ? response.questions.length : 0);
    
    // 更新当前测验状态
    if (currentQuiz.value && currentQuiz.value.id == quizId) {
      // 记录之前的状态和题目数量，用于检测变化
      const previousStatus = currentQuiz.value.status;
      const previousQuestionCount = currentQuiz.value.questions ? currentQuiz.value.questions.length : 0;
      
      // 更新状态
      currentQuiz.value.status = response.status;
      
      // 处理题目更新 - 重点关注逐题生成的情况
      if (response.questions && Array.isArray(response.questions)) {
        const newQuestionCount = response.questions.length;
        
        // 无论题目数量是否变化，都更新题目列表（防止后端数据结构变化导致前端不更新）
        if (newQuestionCount > 0) {
          console.log(`更新题目列表: 当前 ${previousQuestionCount} 道，服务器返回 ${newQuestionCount} 道`);
          
          // 更新题目列表 - 确保ID唯一
          const uniqueQuestions = [];
          const questionIds = new Set();
          
          for (const question of response.questions) {
            const questionId = question.id || `q-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
            if (!questionIds.has(questionId)) {
              question.id = questionId;
              questionIds.add(questionId);
              uniqueQuestions.push(question);
            }
          }
          
          // 更新题目列表
          currentQuiz.value.questions = uniqueQuestions;
          currentQuiz.value.questionCount = uniqueQuestions.length;
          
          // 确保答案数组足够长
          while (currentQuiz.value.answers.length < uniqueQuestions.length) {
            currentQuiz.value.answers.push('');
          }
          
          // 如果是第一道题目，自动显示
          if (previousQuestionCount === 0 && newQuestionCount > 0) {
            console.log('首次显示题目 - 自动切换到第一题');
            currentQuestionIndex.value = 0;
            
            // 显示通知
            notificationService.info('首道题目已生成', '您可以开始作答了');
          }
          
          // 检测到新题目
          if (newQuestionCount > previousQuestionCount && previousQuestionCount > 0) {
            console.log(`新增了 ${newQuestionCount - previousQuestionCount} 道题目`);
            
            // 显示通知
            if (newQuestionCount - previousQuestionCount === 1) {
              notificationService.info('新题目已生成', '已添加1道新题目');
            } else {
              notificationService.info('新题目已生成', `已添加${newQuestionCount - previousQuestionCount}道新题目`);
            }
          }
        }
      }
      
      // 处理测验状态变化
      if (response.status === 'completed' || response.status === 'error' || response.status === 'graded' || response.status === 'grading') {
        // 如果有分数，更新分数
        if (response.score !== undefined) {
          currentQuiz.value.score = response.score;
          currentQuiz.value.questionScores = response.question_scores || [];
          currentQuiz.value.questionFeedback = response.question_feedback || [];
          currentQuiz.value.feedback = response.feedback || '';
          currentQuiz.value.completedAt = response.completed_at;
        }
        
        // 根据状态决定下一步操作
        if (response.status === 'graded') {
          console.log('测验已评分，等待学习建议生成...');
          // 继续轮询，但使用较长的间隔
          adjustPollingInterval(quizId, 'graded');
          // 保持提交状态为true，直到学习建议生成完成
          isSubmitting.value = true;
          
          // 显示通知
          notificationService.info('评分已完成', '正在生成学习建议...');
        } else if (response.status === 'grading') {
          console.log('测验正在评分中...');
          // 继续轮询，使用评分中的轮询间隔
          adjustPollingInterval(quizId, 'grading');
          // 保持提交状态为true
          isSubmitting.value = true;
        } else if (response.status === 'completed' && previousStatus !== 'completed') {
          // 测验已完成，重置提交状态
          isSubmitting.value = false;
          
          // 显示通知
          notificationService.success('测验已完成', `您的得分: ${response.score || 0}分`);
          
          // 测验已完成或出错，停止轮询
          if (statusPollingInterval) {
            clearInterval(statusPollingInterval);
            statusPollingInterval = null;
            console.log('测验已完成，停止轮询');
          }
        } else if (response.status === 'error') {
          // 显示错误通知
          notificationService.error('测验出错', '生成或评分过程中出现错误');
          
          // 测验已完成或出错，停止轮询
          if (statusPollingInterval) {
            clearInterval(statusPollingInterval);
            statusPollingInterval = null;
            console.log('测验出错，停止轮询');
          }
          
          // 重置提交状态
          isSubmitting.value = false;
        }
      } else if (response.status === 'in_progress' && previousStatus === 'generating') {
        // 如果状态从 generating 变为 in_progress，说明题目生成已完成
        console.log('题目生成已完成，状态更新为进行中');
        
        // 显示通知
        notificationService.success('题目生成已完成', '所有题目已生成完毕，您可以开始作答');
        
        // 额外执行一次状态检查，确保获取到所有题目
        setTimeout(async () => {
          try {
            const finalResponse = await studentQuizAPI.getQuizStatus(quizId);
            if (finalResponse && finalResponse.questions && 
                finalResponse.questions.length > currentQuiz.value.questions.length) {
              console.log(`最终检查：发现更多题目 (${finalResponse.questions.length} > ${currentQuiz.value.questions.length})`);
              currentQuiz.value.questions = finalResponse.questions;
              currentQuiz.value.questionCount = finalResponse.questions.length;
              
              // 确保答案数组足够长
              while (currentQuiz.value.answers.length < finalResponse.questions.length) {
                currentQuiz.value.answers.push('');
              }
            }
          } catch (error) {
            console.error('最终题目检查失败:', error);
          }
        }, 1000);
      }
      
      // 根据当前状态调整轮询间隔
      if (previousStatus !== response.status) {
        console.log(`测验状态从 ${previousStatus} 变为 ${response.status}，调整轮询策略`);
        adjustPollingInterval(quizId, response.status);
      }
      
      // 更新历史记录
      saveQuizHistory();
      
      // 更新历史记录中的测验
      const historyQuiz = quizHistory.value.find(q => q.id == quizId);
      if (historyQuiz) {
        historyQuiz.status = response.status;
        historyQuiz.questionCount = response.questions ? response.questions.length : 0;
        
        if (response.status === 'completed') {
          historyQuiz.score = response.score;
          historyQuiz.completedAt = response.completed_at;
        }
      }
    }
  } catch (error) {
    console.error(`获取测验 ${quizId} 状态失败:`, error);
  }
}

// 提交测验
async function submitQuiz() {
  if (!currentQuiz.value) return;
  
  // 检查是否有未回答的题目
  const unansweredCount = currentQuiz.value.answers.filter(a => !a).length;
  if (unansweredCount > 0) {
    const result = await dialogService.confirm({
      title: '提交确认',
      message: `您有 ${unansweredCount} 道题目尚未回答。确定要提交吗？`,
      type: 'warning'
    });
    
    if (!result) return;
  }
  
  // 设置提交中状态 - 这个标志将保持为true直到评分完成
  isSubmitting.value = true;
  
  try {
    // 立即更新UI状态为评分中
    currentQuiz.value.status = 'grading';
    
    // 同时更新历史记录中的状态
    const historyQuiz = quizHistory.value.find(q => q.id == currentQuiz.value.id);
    if (historyQuiz) {
      historyQuiz.status = 'grading';
    }
    
    // 保存状态到本地存储
    saveQuizHistory();
    
    // 显示提交通知
    notificationService.info('测验已提交', 'AI正在评分中，请稍候...');
    
    // 调用API提交答案
    const response = await studentQuizAPI.submitQuizAnswers(currentQuiz.value.id, currentQuiz.value.answers);
    console.log('提交测验响应:', response);
    
    // 使用评分状态的轮询间隔开始轮询结果
    adjustPollingInterval(currentQuiz.value.id, 'grading');
    
    // 立即执行一次状态检查
    await checkQuizStatus(currentQuiz.value.id);
    
    // 注意：这里不设置isSubmitting为false，让它保持为true
    // 直到checkQuizStatus检测到评分完成或学习建议生成完成
    
  } catch (error) {
    console.error('提交测验失败:', error);
    notificationService.error('提交失败', error.message || '请重试');
    // 恢复状态
    currentQuiz.value.status = 'in_progress';
    
    // 同时更新历史记录中的状态
    const historyQuiz = quizHistory.value.find(q => q.id == currentQuiz.value.id);
    if (historyQuiz) {
      historyQuiz.status = 'in_progress';
    }
    
    saveQuizHistory();
    
    // 只有在错误情况下才重置提交状态
    isSubmitting.value = false;
  }
}

// 继续或查看测验
function continueQuiz(quiz) {
  currentQuiz.value = quiz;
  showQuizModal.value = true;
  currentQuestionIndex.value = 0; // 继续时重置题目索引
  
  // 根据测验状态决定是否需要轮询
  if (quiz.status === 'generating') {
    // 如果测验仍在生成中，继续轮询
    adjustPollingInterval(quiz.id, 'generating');
  } else if (quiz.status === 'grading') {
    // 如果测验正在评分中，继续轮询
    adjustPollingInterval(quiz.id, 'grading');
  } else {
    // 其他状态不需要轮询
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval);
      statusPollingInterval = null;
    }
  }
}

// 删除测验
async function deleteQuiz(quizId) {
  const result = await dialogService.confirm({
    title: '删除确认',
    message: '确定要删除这个测验记录吗？此操作不可撤销。',
    type: 'warning'
  });
  
  if (result) {
    try {
      // 调用API删除测验
      await studentQuizAPI.deleteQuiz(quizId);
      
      // 从历史记录中移除
      quizHistory.value = quizHistory.value.filter(q => q.id !== quizId);
      saveQuizHistory();
      
      // 显示成功通知
      notificationService.success('删除成功', '测验记录已删除');
    } catch (error) {
      console.error('删除测验失败:', error);
      notificationService.error('删除失败', error.message || '请重试');
    }
  }
}

// 保存测验历史到localStorage
function saveQuizHistory() {
  localStorage.setItem('aiQuizHistory', JSON.stringify(quizHistory.value));
}

// 从localStorage加载测验历史
function loadQuizHistory() {
  const saved = localStorage.getItem('aiQuizHistory');
  if (saved) {
    try {
      quizHistory.value = JSON.parse(saved);
    } catch (e) {
      console.error('解析测验历史失败:', e);
      quizHistory.value = [];
    }
  }
}

// 检查是否有正在进行的测验
function checkActiveQuiz() {
  const activeQuiz = quizHistory.value.find(q => q.status === 'generating' || q.status === 'in_progress');
  if (activeQuiz) {
    currentQuiz.value = activeQuiz;
    showQuizModal.value = true;
    currentQuestionIndex.value = 0; // 检查时重置题目索引
    
    // 显示通知
    if (activeQuiz.status === 'generating') {
      notificationService.info('继续测验', '您有一个正在生成的测验，已自动恢复');
    } else {
      notificationService.info('继续测验', '您有一个未完成的测验，已自动恢复');
    }
    
    // 如果测验仍在生成中，继续轮询
    if (activeQuiz.status === 'generating') {
      adjustPollingInterval(activeQuiz.id, 'generating');
    }
  }
}

// 题目导航方法
function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < currentQuiz.value.questions.length - 1) {
    currentQuestionIndex.value++;
  }
}

// 跳转到最新题目
function goToLatestQuestion() {
  if (currentQuiz.value && currentQuiz.value.questions.length > 0) {
    // 跳转到最后一道题
    currentQuestionIndex.value = currentQuiz.value.questions.length - 1;
  }
}

// 判断是否为选择题
function isChoiceQuestion(type) {
  const choiceTypes = [
    'multiple_choice', 'single_choice', 'choice', 
    'mcq', 'multiple_choice_question', 'selection'
  ];
  return choiceTypes.includes(type);
}

// 判断是否为填空题
function isFillBlankQuestion(type) {
  const fillBlankTypes = [
    'fill_in_blank', 'fill_in_the_blank', 
    'fill_blank', 'blank_filling', 'completion'
  ];
  return fillBlankTypes.includes(type);
}

// 判断是否为简答题
function isShortAnswerQuestion(type) {
  const shortAnswerTypes = [
    'short_answer', 'short_answer_question', 
    'brief_answer', 'open_question', 'essay'
  ];
  return shortAnswerTypes.includes(type);
}

// 判断是否为客观题（选择题和填空题）
function isObjectiveQuestion(type) {
  return isChoiceQuestion(type) || isFillBlankQuestion(type);
}

// 计算分数级别
function getScoreLevel(score, totalScore) {
  if (!score || !totalScore) return '未评分';
  
  const percentage = (score / totalScore) * 100;
  
  if (percentage >= 90) return '优秀';
  if (percentage >= 80) return '良好';
  if (percentage >= 70) return '中等';
  if (percentage >= 60) return '及格';
  return '需加强';
}

// 计算分数百分比
function calculateScorePercentage(score, totalScore) {
  if (!score || !totalScore) return 0;
  return Math.min(100, Math.max(0, (score / totalScore) * 100));
}

// 获取特定题目的得分百分比
function getScorePercentage(questionIndex) {
  if (!currentQuiz.value || !currentQuiz.value.questionScores || 
      !currentQuiz.value.questions || questionIndex >= currentQuiz.value.questions.length) {
    return 0;
  }
  
  const score = currentQuiz.value.questionScores[questionIndex] || 0;
  const maxScore = currentQuiz.value.questions[questionIndex].score || 10;
  
  return (score / maxScore) * 100;
}

// 检查答案是否正确
function isCorrectAnswer(questionIndex) {
  if (!currentQuiz.value || !currentQuiz.value.questionScores || 
      !currentQuiz.value.questions || questionIndex >= currentQuiz.value.questions.length) {
    return false;
  }
  
  const score = currentQuiz.value.questionScores[questionIndex] || 0;
  const maxScore = currentQuiz.value.questions[questionIndex].score || 10;
  
  // 如果得分是满分或接近满分（>90%），认为是正确答案
  return (score / maxScore) >= 0.9;
}

// 获取正确答案
function getCorrectAnswer(questionIndex) {
  if (!currentQuiz.value || !currentQuiz.value.questions || 
      questionIndex >= currentQuiz.value.questions.length) {
    return '';
  }
  
  const question = currentQuiz.value.questions[questionIndex];
  
  if (isChoiceQuestion(question.type)) {
    // 选择题
    const correctOption = question.answer;
    if (question.options && Array.isArray(question.options)) {
      const optionIndex = correctOption.charCodeAt(0) - 65; // 'A' -> 0, 'B' -> 1, etc.
      if (optionIndex >= 0 && optionIndex < question.options.length) {
        return question.options[optionIndex];
      }
    }
    return correctOption;
  } else if (isFillBlankQuestion(question.type)) {
    // 填空题
    return question.answer;
  }
  
  return '';
}

// 按题型统计得分
function getScoresByType() {
  if (!currentQuiz.value || !currentQuiz.value.questions || 
      !currentQuiz.value.questionScores) {
    return {};
  }
  
  const scoresByType = {};
  
  currentQuiz.value.questions.forEach((question, index) => {
    const type = getQuestionTypeText(question.type);
    const score = currentQuiz.value.questionScores[index] || 0;
    const maxScore = question.score || 10;
    
    if (!scoresByType[type]) {
      scoresByType[type] = { earned: 0, total: 0 };
    }
    
    scoresByType[type].earned += score;
    scoresByType[type].total += maxScore;
  });
  
  return scoresByType;
}
</script> 