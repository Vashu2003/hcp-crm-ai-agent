import axios from 'axios';
import type { Interaction, InteractionCreate, HCP } from '../types';

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const api = axios.create({ baseURL });

export const InteractionsApi = {
  list: (params?: Record<string, string>) =>
    api.get<Interaction[]>('/api/interactions', { params }).then((r) => r.data),

  create: (payload: InteractionCreate) =>
    api.post<Interaction>('/api/interactions', payload).then((r) => r.data),

  update: (id: number, payload: Partial<InteractionCreate>) =>
    api.patch<Interaction>(`/api/interactions/${id}`, payload).then((r) => r.data),

  hcps: () => api.get<HCP[]>('/api/hcps').then((r) => r.data),
};

export interface ChatApiResponse {
  reply: string;
  tool_calls: string[];
}

export const ChatApi = {
  send: (message: string, history: { role: string; content: string }[]) =>
    api.post<ChatApiResponse>('/api/chat', { message, history }).then((r) => r.data),
};
