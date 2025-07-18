<template>
  <div class="chart-container" style="position: relative; height: 300px;">
    <Radar 
      v-if="chartData" 
      :data="chartData" 
      :options="chartOptions" 
    />
  </div>
</template>

<script setup>
import { computed, toRaw } from 'vue';
import { Radar } from 'vue-chartjs';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';

// 注册Chart.js组件
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '知识点掌握情况'
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
        data: rawData.map(item => item.value),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3b82f6'
      }
    ]
  };
});

// 图表配置选项
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      beginAtZero: true,
      max: 100,
      ticks: {
        stepSize: 20,
        display: false
      },
      pointLabels: {
        font: {
          size: 12
        }
      },
      grid: {
        color: '#f3f4f6'
      },
      angleLines: {
        color: '#e5e7eb'
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
      callbacks: {
        label: function(context) {
          return `掌握度: ${context.raw}%`;
        }
      }
    }
  }
};
</script> 