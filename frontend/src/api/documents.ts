import client from './client';
import type { Document } from '@/types';

export const documentsApi = {
  list: (params?: Record<string, string | number>) =>
    client.get<{ documents: Document[]; total: number }>('/documents', { params }).then(r => r.data),
  get: (id: string) =>
    client.get<Document>(`/documents/${id}`).then(r => r.data),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data);
  },
  process: (id: string) =>
    client.post<Document>(`/documents/${id}/process`).then(r => r.data),
  update: (id: string, data: Partial<Document>) =>
    client.put<Document>(`/documents/${id}`, data).then(r => r.data),
  approve: (id: string) =>
    client.put<Document>(`/documents/${id}/approve`).then(r => r.data),
  reprocess: (id: string) =>
    client.put<Document>(`/documents/${id}/reprocess`).then(r => r.data),
  delete: (id: string) =>
    client.delete(`/documents/${id}`).then(r => r.data),
};
