import client from './client';

interface ChatResponse {
  answer: string;
  sources: Array<{ document_id: string; document_number: string; vendor_name: string; original_filename: string }>;
  query_type: string;
}

export const chatApi = {
  send: (message: string, history: Array<{ role: string; content: string }> = []) =>
    client.post<ChatResponse>('/chat', { message, history }).then(r => r.data),
  suggestions: () =>
    client.get<{ suggestions: string[] }>('/chat/suggestions').then(r => r.data),
};
