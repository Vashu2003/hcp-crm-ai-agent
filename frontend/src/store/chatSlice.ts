import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { ChatApi } from '../api/client';
import type { ChatMessage } from '../types';

interface ChatState {
  messages: ChatMessage[];
  sending: boolean;
  error: string | null;
}

const initialState: ChatState = {
  messages: [
    {
      role: 'assistant',
      content:
        "Hi! I'm your CRM assistant. Tell me about an HCP visit (e.g. \"Met Dr. Sharma today, discussed Xarelto dosing, positive, follow up next week\"), or ask me to search, schedule a follow-up, or summarize your activity.",
    },
  ],
  sending: false,
  error: null,
};

export const sendMessage = createAsyncThunk(
  'chat/send',
  async (text: string, { getState }) => {
    const state = getState() as { chat: ChatState };
    const history = state.chat.messages.map((m) => ({ role: m.role, content: m.content }));
    return ChatApi.send(text, history);
  },
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    pushUserMessage(state, action: { payload: string }) {
      state.messages.push({ role: 'user', content: action.payload });
    },
    resetChat(state) {
      state.messages = initialState.messages;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.sending = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.sending = false;
        state.messages.push({
          role: 'assistant',
          content: action.payload.reply || '(no response)',
          tool_calls: action.payload.tool_calls,
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.sending = false;
        state.error = action.error.message ?? 'Failed to reach the agent';
        state.messages.push({
          role: 'assistant',
          content: 'Sorry — I could not reach the agent. Is the backend running and the GROQ_API_KEY set?',
        });
      });
  },
});

export const { pushUserMessage, resetChat } = chatSlice.actions;
export default chatSlice.reducer;
