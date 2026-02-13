import client from './client';
import type { LineItem } from '@/types';

export const lineItemsApi = {
  list: (params?: Record<string, string | number>) =>
    client.get<{ items: LineItem[]; total: number; page: number; per_page: number }>('/line-items', { params }).then(r => r.data),
  update: (id: string, data: Partial<LineItem>) =>
    client.put<LineItem>(`/line-items/${id}`, data).then(r => r.data),
  export: (params?: Record<string, string>, format: string = 'csv') =>
    client.get(`/line-items/export`, { params: { ...params, format }, responseType: 'blob' }).then(r => r.data),
  spendAnalysis: () =>
    client.get('/line-items/spend-analysis').then(r => r.data),
};
