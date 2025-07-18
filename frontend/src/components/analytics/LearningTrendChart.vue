<template>
  <div class="chart-container" style="position: relative; height: 300px;">
    <Line 
      v-if="chartData" 
      :data="chartData" 
      :options="chartOptions" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, toRaw } from 'vue';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// 注册Chart.js组件
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '学习趋势'
  },
  color: {
    type: String,
    default: '#3b82f6' // Tailwind blue-500
  }
});

// 图表数据
const chartData = computed(() => {
  // 使用toRaw确保我们处理的是原始数据，而不是响应式代理
  const rawData = toRaw(props.data);
  
  return {
    labels: rawData.map(item => item.label),
    datasets: [
      {
        label: props.title,
        backgroundColor: props.color + '33', // 添加透明度
        borderColor: props.color,
        data: rawData.map(item => item.value),
        fill: true,
        tension: 0.3, // 曲线平滑度
        pointBackgroundColor: props.color,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4
      }
    ]
  };
});

// 图表配置选项
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#f3f4f6' // 网格线颜色
      }
    },
    x: {
      grid: {
        display: false // 不显示x轴网格线
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      titleColor: '#111827',
      bodyColor: '#111827',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      padding: 10,
      displayColors: false
    }
  }
};
</script> 