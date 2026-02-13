import client from './client';
import type { DashboardData } from '@/types';

export const dashboardApi = {
  get: () => client.get<DashboardData>('/dashboard').then(r => r.data),
};
