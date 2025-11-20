import { z } from 'zod'

// Schema dla kontenera
// Type can be a default type or any string (for custom container types)
export const containerSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  description: z.string().optional(),
  type: z.string().min(1, 'Typ jest wymagany'), // Allow any string for custom container types
  color: z.enum(['default', 'blue', 'green', 'red', 'yellow', 'purple', 'orange', 'pink', 'teal', 'indigo']).optional(),
  parentContainerId: z.string().uuid().optional().nullable(),
  brand: z.string().optional(),
  price: z.number().min(0, 'Cena nie może być ujemna').optional(),
  weight: z.number().min(0, 'Waga nie może być ujemna').optional(),
  weightUnit: z.enum(['g', 'kg', 'oz', 'lb']).optional(),
  url: z.string().url('Nieprawidłowy URL').optional().or(z.literal('')),
})

// Schema dla przedmiotu
// Category can be a default category or any string (for custom categories)
export const itemSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  category: z.string().min(1, 'Kategoria jest wymagana'), // Allow any string for custom categories
  quantity: z.number().int().min(1, 'Ilość musi być większa od 0'),
  weight: z.number().min(0, 'Waga nie może być ujemna'),
  weightUnit: z.enum(['g', 'kg', 'oz', 'lb']),
  notes: z.string().optional(),
  expirationDate: z.string().optional(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  status: z.enum(['owned', 'missing', 'toBuy']),
  containerId: z.union([z.string().uuid(), z.literal('')]).optional(), // Reference to nested container (empty string = no container)
  price: z.number().min(0, 'Cena nie może być ujemna').optional(),
  url: z.string().url('Nieprawidłowy URL').optional().or(z.literal('')),
  brand: z.string().optional(),
  color: z.string().optional(),
  quality: z.enum(['low', 'medium', 'high']).optional(),
})

// Type inference dla TypeScript
export type ContainerFormData = z.infer<typeof containerSchema>
export type ItemFormData = z.infer<typeof itemSchema>

