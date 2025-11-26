<!--
  AI Model Selector Component
  Dropdown for selecting AI model
-->
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAiModels } from '../composables/useAiModels'
import { useAiStore } from '../store/useAiStore'

const { models, selectedModel, loadModels, selectModel } = useAiModels()
const aiStore = useAiStore()

const selectFirstModel = async () => {
  if (models.value.length > 0) {
    await selectModel(models.value[0]!.id)
  }
}

onMounted(async () => {
  if (models.value.length === 0) {
    await loadModels()
  }

  if (!selectedModel?.value && models.value.length > 0) {
    await selectFirstModel()
  }
})

const handleModelChange = async (modelId: string) => {
  await selectModel(modelId)
}

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: (value: string) => handleModelChange(value),
})
</script>

<template>
  <Select v-model="selectedModelId">
    <SelectTrigger class="w-[200px]">
      <SelectValue placeholder="Select model" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="model in models"
        :key="model.id"
        :value="model.id"
      >
        <div class="flex flex-col">
          <span class="font-medium">{{ model.name }}</span>
          <span class="text-xs text-muted-foreground">{{ model.provider }}</span>
        </div>
      </SelectItem>
    </SelectContent>
  </Select>
</template>

