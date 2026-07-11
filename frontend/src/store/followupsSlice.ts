import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { FollowUpsApi } from '../api/client';
import type { FollowUp } from '../types';

interface FollowUpsState {
  items: FollowUp[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
}

const initialState: FollowUpsState = { items: [], status: 'idle' };

export const fetchFollowups = createAsyncThunk('followups/fetch', () => FollowUpsApi.list());

export const markFollowupDone = createAsyncThunk(
  'followups/markDone',
  (id: number) => FollowUpsApi.update(id, 'done'),
);

const followupsSlice = createSlice({
  name: 'followups',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchFollowups.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchFollowups.fulfilled, (state, action: PayloadAction<FollowUp[]>) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchFollowups.rejected, (state) => {
        state.status = 'failed';
      })
      .addCase(markFollowupDone.fulfilled, (state, action: PayloadAction<FollowUp>) => {
        const idx = state.items.findIndex((f) => f.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      });
  },
});

export default followupsSlice.reducer;
