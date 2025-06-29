<template>
  <div class="assessment-editor">
    <!-- 评估头部信息 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <div class="flex justify-between items-center mb-4">
        <div>
          <input 
            v-model="assessment.title" 
            class="text-2xl font-bold mb-2 px-2 py-1 border rounded-md w-full"
            placeholder="输入评估标题"
          />
          <textarea 
            v-model="assessment.description" 
            class="text-gray-600 mb-4 px-2 py-1 border rounded-md w-full"
            placeholder="输入评估描述"
            rows="2"
          ></textarea>
          <div class="flex gap-4 mb-2">
            <div>
              <label class="text-sm text-gray-600">总分</label>
              <input 
                v-model="assessment.total_score" 
                type="number" 
                class="px-2 py-1 border rounded-md"
              />
            </div>
            <div>
              <label class="text-sm text-gray-600">时间限制（分钟）</label>
              <input 
                v-model="assessment.duration" 
                type="number" 
                class="px-2 py-1 border rounded-md"
              />
            </div>
            <div>
              <label class="text-sm text-gray-600">截止日期</label>
              <input 
                v-model="assessment.due_date" 
                type="date" 
                class="px-2 py-1 border rounded-md"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="space-y-6">
      <div v-for="(section, sectionIndex) in assessment.sections" :key="sectionIndex" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <div class="flex-1">
            <select 
              v-model="section.type" 
              class="px-2 py-1 border rounded-md mr-4"
            >
              <option value="multiple_choice">选择题</option>
              <option value="multiple_select">多选题</option>
              <option value="fill_in_blank">填空题</option>
              <option value="true_false">判断题</option>
              <option value="short_answer">简答题</option>
              <option value="essay">论述题</option>
            </select>
            <input 
              v-model="section.description" 
              class="px-2 py-1 border rounded-md flex-1"
              placeholder="输入题型说明"
            />
          </div>
          <div class="flex items-center gap-4">
            <div>
              <label class="text-sm text-gray-600 mr-2">每题分数</label>
              <input 
                v-model="section.score_per_question" 
                type="number" 
                class="px-2 py-1 border rounded-md w-20"
              />
            </div>
            <button 
              @click="removeSection(sectionIndex)" 
              class="text-red-600 hover:text-red-800"
            >
              删除题型
            </button>
          </div>
        </div>

        <!-- 题目列表 -->
        <div class="space-y-4">
          <div 
            v-for="(question, qIndex) in section.questions" 
            :key="qIndex"
            class="border rounded-md p-4"
          >
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="font-medium">第 {{ qIndex + 1 }} 题</span>
                  <button 
                    @click="removeQuestion(sectionIndex, qIndex)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    删除
                  </button>
                </div>
                <textarea 
                  v-model="question.stem" 
                  class="w-full px-2 py-1 border rounded-md"
                  rows="2"
                  placeholder="输入题目内容"
                ></textarea>
              </div>
            </div>

            <!-- 选择题选项 -->
            <div v-if="section.type === 'multiple_choice' || section.type === 'multiple_select'" class="space-y-2">
              <div v-for="(option, optIndex) in question.options" :key="optIndex" class="flex items-center gap-2">
                <span>{{ String.fromCharCode(65 + optIndex) }}.</span>
                <input 
                  v-model="question.options[optIndex]" 
                  class="flex-1 px-2 py-1 border rounded-md"
                  :placeholder="`选项 ${String.fromCharCode(65 + optIndex)}`"
                />
                <button 
                  @click="removeOption(sectionIndex, qIndex, optIndex)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  删除
                </button>
              </div>
              <button 
                @click="addOption(sectionIndex, qIndex)"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                添加选项
              </button>
              <div class="mt-2">
                <label class="text-sm text-gray-600 mr-2">正确答案</label>
                <div v-if="section.type === 'multiple_choice'" class="flex gap-2">
                  <select 
                    v-model="question.answer"
                    class="px-2 py-1 border rounded-md"
                  >
                    <option 
                      v-for="(_, optIndex) in question.options" 
                      :key="optIndex"
                      :value="String.fromCharCode(65 + optIndex)"
                    >
                      {{ String.fromCharCode(65 + optIndex) }}
                    </option>
                  </select>
                </div>
                <div v-else class="flex gap-2">
                  <div 
                    v-for="(_, optIndex) in question.options" 
                    :key="optIndex"
                    class="flex items-center gap-1"
                  >
                    <input 
                      type="checkbox"
                      :value="String.fromCharCode(65 + optIndex)"
                      v-model="question.answer"
                    />
                    <label>{{ String.fromCharCode(65 + optIndex) }}</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- 判断题答案 -->
            <div v-if="section.type === 'true_false'" class="mt-2">
              <label class="text-sm text-gray-600 mr-2">正确答案</label>
              <select 
                v-model="question.answer"
                class="px-2 py-1 border rounded-md"
              >
                <option value="true">正确</option>
                <option value="false">错误</option>
              </select>
            </div>

            <!-- 填空题答案 -->
            <div v-if="section.type === 'fill_in_blank'" class="mt-2">
              <label class="text-sm text-gray-600 block mb-1">正确答案（多个答案用逗号分隔）</label>
              <input 
                v-model="question.answer" 
                class="w-full px-2 py-1 border rounded-md"
                placeholder="输入正确答案"
              />
            </div>

            <!-- 简答题和论述题参考答案 -->
            <div v-if="section.type === 'short_answer' || section.type === 'essay'" class="mt-2">
              <label class="text-sm text-gray-600 block mb-1">参考答案</label>
              <textarea 
                v-model="question.reference_answer" 
                class="w-full px-2 py-1 border rounded-md"
                rows="3"
                placeholder="输入参考答案"
              ></textarea>
            </div>
          </div>

          <button 
            @click="addQuestion(sectionIndex)"
            class="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-gray-500 hover:text-gray-700 hover:border-gray-400"
          >
            添加题目
          </button>
        </div>
      </div>

      <button 
        @click="addSection"
        class="w-full py-3 border-2 border-dashed border-gray-300 rounded-md text-gray-500 hover:text-gray-700 hover:border-gray-400"
      >
        添加题型
      </button>
    </div>

    <!-- 保存按钮 -->
    <div class="mt-6 flex justify-end gap-4">
      <button 
        @click="cancel" 
        class="px-6 py-2 border rounded-md hover:bg-gray-50"
      >
        取消
      </button>
      <button 
        @click="save" 
        class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        保存
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const props = defineProps({
  initialAssessment: {
    type: Object,
    required: false,
    default: () => ({
      title: '',
      description: '',
      total_score: 100,
      duration: 60,
      due_date: '',
      sections: []
    })
  }
});

const emit = defineEmits(['save', 'cancel']);

const assessment = reactive(JSON.parse(JSON.stringify(props.initialAssessment)));

// 添加题型
const addSection = () => {
  assessment.sections.push({
    type: 'multiple_choice',
    description: '',
    score_per_question: 5,
    questions: []
  });
};

// 删除题型
const removeSection = (sectionIndex) => {
  assessment.sections.splice(sectionIndex, 1);
};

// 添加题目
const addQuestion = (sectionIndex) => {
  const section = assessment.sections[sectionIndex];
  const newQuestion = {
    stem: '',
    options: section.type === 'multiple_choice' || section.type === 'multiple_select' ? ['', ''] : undefined,
    answer: section.type === 'multiple_select' ? [] : '',
    reference_answer: section.type === 'short_answer' || section.type === 'essay' ? '' : undefined
  };
  section.questions.push(newQuestion);
};

// 删除题目
const removeQuestion = (sectionIndex, qIndex) => {
  assessment.sections[sectionIndex].questions.splice(qIndex, 1);
};

// 添加选项
const addOption = (sectionIndex, qIndex) => {
  assessment.sections[sectionIndex].questions[qIndex].options.push('');
};

// 删除选项
const removeOption = (sectionIndex, qIndex, optIndex) => {
  assessment.sections[sectionIndex].questions[qIndex].options.splice(optIndex, 1);
};

// 保存评估
const save = () => {
  emit('save', JSON.parse(JSON.stringify(assessment)));
};

// 取消编辑
const cancel = () => {
  emit('cancel');
};
</script> 