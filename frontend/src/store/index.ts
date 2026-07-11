import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector } from 'react-redux';
import type { TypedUseSelectorHook } from 'react-redux';
import interactionsReducer from './interactionsSlice';
import chatReducer from './chatSlice';
import followupsReducer from './followupsSlice';

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    followups: followupsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
