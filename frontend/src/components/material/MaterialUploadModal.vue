<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">上传课件</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <MaterialUpload
          :course-id="courseId"
          @success="onUploadSuccess"
          @cancel="$emit('close')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MaterialUpload from './MaterialUpload.vue'

// Props
interface Props {
  show: boolean
  courseId: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  success: [material: any]
}>()

const onUploadSuccess = (material: any) => {
  emit('success', material)
  emit('close')
}
</script> 