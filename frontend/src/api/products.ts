import client from './client';
import type { CanonicalProduct } from '@/types';

export const productsApi = {
  list: (params?: Record<string, string | number>) =>
    client.get<{ products: CanonicalProduct[]; total: number }>('/products', { params }).then(r => r.data),
  get: (id: string) =>
    client.get<CanonicalProduct>(`/products/${id}`).then(r => r.data),
  igce: (id: string, data: { quantity: number; escalation_rate?: number }) =>
    client.post(`/products/${id}/igce`, data).then(r => r.data),
  rebuild: () =>
    client.post('/products/rebuild').then(r => r.data),
};
