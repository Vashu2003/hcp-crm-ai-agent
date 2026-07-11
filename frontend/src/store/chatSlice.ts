import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { ChatApi } from '../api/client';
import { updateInteraction } from './interactionsSlice';
import type { ChatMessage, Interaction } from '../types';

interface ChatState {
  messages: ChatMessage[];
  sending: boolean;
  error: string | null;
  // The interaction the agent last logged/edited — drives the live form fill.
  lastInteraction: Interaction | null;
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
  lastInteraction: null,
};

export const sendMessage = createAsyncThunk(
  'chat/send',
  async (text: string, { getState }) => {
    const state = getState() as { chat: ChatState };
    // Exclude the just-pushed current user message; the backend appends `text` itself,
    // so including it here would send the turn to the LLM twice.
    const history = state.chat.messages
      .slice(0, -1)
      .map((m) => ({ role: m.role, content: m.content }));
    return ChatApi.send(text, history, state.chat.lastInteraction?.id ?? null);
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
      state.lastInteraction = null;
    },
    clearLastInteraction(state) {
      state.lastInteraction = null;
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
        if (action.payload.interaction) state.lastInteraction = action.payload.interaction;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.sending = false;
        state.error = action.error.message ?? 'Failed to reach the agent';
        state.messages.push({
          role: 'assistant',
          content: 'Sorry — I could not reach the agent. Is the backend running and the GROQ_API_KEY set?',
        });
      })
      // A manual form save returns the recomputed record — keep the form's AI
      // summary/sentiment display in sync with what was just persisted.
      .addCase(updateInteraction.fulfilled, (state, action) => {
        if (state.lastInteraction && state.lastInteraction.id === action.payload.id) {
          state.lastInteraction = action.payload;
        }
      });
  },
});

export const { pushUserMessage, resetChat, clearLastInteraction } = chatSlice.actions;
export default chatSlice.reducer;
