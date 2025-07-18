<template>
  <div class="chart-container" style="position: relative; height: 220px;">
    <Pie 
      v-if="chartData" 
      :data="chartData" 
      :options="chartOptions" 
    />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Pie } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// 注册Chart.js组件
ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  completed: {
    type: Number,
    required: true
  },
  inProgress: {
    type: Number,
    required: true
  },
  notStarted: {
    type: Number,
    required: true
  }
});

// 图表数据
const chartData = computed(() => {
  return {
    labels: ['已完成', '进行中', '未开始'],
    datasets: [
      {
        data: [props.completed, props.inProgress, props.notStarted],
        backgroundColor: [
          '#3b82f6', // 蓝色 - 已完成
          '#f59e0b', // 黄色 - 进行中
          '#9ca3af'  // 灰色 - 未开始
        ],
        borderWidth: 0
      }
    ]
  };
});

// 图表配置选项
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      titleColor: '#111827',
      bodyColor: '#111827',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      padding: 10,
      callbacks: {
        label: function(context) {
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const value = context.raw;
          const percentage = Math.round((value / total) * 100);
          return `${context.label}: ${value} (${percentage}%)`;
        }
      }
    }
  }
};
</script> 