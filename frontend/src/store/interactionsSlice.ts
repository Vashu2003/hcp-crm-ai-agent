import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { InteractionsApi } from '../api/client';
import type { Interaction, InteractionCreate } from '../types';

interface InteractionsState {
  items: Interaction[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  creating: boolean;
  error: string | null;
  lastCreated: Interaction | null;
}

const initialState: InteractionsState = {
  items: [],
  status: 'idle',
  creating: false,
  error: null,
  lastCreated: null,
};

export const fetchInteractions = createAsyncThunk(
  'interactions/fetch',
  (params?: Record<string, string>) => InteractionsApi.list(params),
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  (payload: InteractionCreate) => InteractionsApi.create(payload),
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  ({ id, patch }: { id: number; patch: Partial<InteractionCreate> }) =>
    InteractionsApi.update(id, patch),
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    clearLastCreated(state) {
      state.lastCreated = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action: PayloadAction<Interaction[]>) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message ?? 'Failed to load interactions';
      })
      .addCase(createInteraction.pending, (state) => {
        state.creating = true;
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.creating = false;
        state.lastCreated = action.payload;
        state.items.unshift(action.payload);
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.creating = false;
        state.error = action.error.message ?? 'Failed to log interaction';
      })
      .addCase(updateInteraction.pending, (state) => {
        state.creating = true;
        state.error = null;
      })
      .addCase(updateInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.creating = false;
        const idx = state.items.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.creating = false;
        state.error = action.error.message ?? 'Failed to save changes';
      });
  },
});

export const { clearLastCreated } = interactionsSlice.actions;
export default interactionsSlice.reducer;
