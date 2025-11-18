import type { TContainerColor } from '../types/gear.types'

export const CONTAINER_COLORS: TContainerColor[] = [
  'default',
  'blue',
  'green',
  'red',
  'yellow',
  'purple',
  'orange',
  'pink',
  'teal',
  'indigo',
]

export const COLOR_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-100 border-gray-300 text-gray-800 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200',
  blue: 'bg-blue-100 border-blue-300 text-blue-800 dark:bg-blue-900 dark:border-blue-700 dark:text-blue-200',
  green: 'bg-green-100 border-green-300 text-green-800 dark:bg-green-900 dark:border-green-700 dark:text-green-200',
  red: 'bg-red-100 border-red-300 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200',
  yellow: 'bg-yellow-100 border-yellow-300 text-yellow-800 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-200',
  purple: 'bg-purple-100 border-purple-300 text-purple-800 dark:bg-purple-900 dark:border-purple-700 dark:text-purple-200',
  orange: 'bg-orange-100 border-orange-300 text-orange-800 dark:bg-orange-900 dark:border-orange-700 dark:text-orange-200',
  pink: 'bg-pink-100 border-pink-300 text-pink-800 dark:bg-pink-900 dark:border-pink-700 dark:text-pink-200',
  teal: 'bg-teal-100 border-teal-300 text-teal-800 dark:bg-teal-900 dark:border-teal-700 dark:text-teal-200',
  indigo: 'bg-indigo-100 border-indigo-300 text-indigo-800 dark:bg-indigo-900 dark:border-indigo-700 dark:text-indigo-200',
}

export const COLOR_DOT_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-400',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  red: 'bg-red-500',
  yellow: 'bg-yellow-500',
  purple: 'bg-purple-500',
  orange: 'bg-orange-500',
  pink: 'bg-pink-500',
  teal: 'bg-teal-500',
  indigo: 'bg-indigo-500',
}

