import axios from 'axios';
import type {
  Feedback,
  FeedbackCreate,
  FeedbackUpdate,
  FeedbackListResponse,
  FeedbackStats,
  AnalysisResult,
  SmartFeedbackCreate,
} from '../types/feedback';
import type { Category, Sentiment, Priority, Status } from '../types/feedback';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

export interface FeedbackFilters {
  category?: Category;
  sentiment?: Sentiment;
  priority?: Priority;
  status?: Status;
}

export const createFeedback = async (data: FeedbackCreate): Promise<Feedback> => {
  const response = await api.post<Feedback>('/feedback', data);
  return response.data;
};

export const getFeedbacks = async (
  page: number = 1,
  size: number = 10,
  filters?: FeedbackFilters
): Promise<FeedbackListResponse> => {
  const params: Record<string, string | number> = { page, size };
  if (filters?.category) params.category = filters.category;
  if (filters?.sentiment) params.sentiment = filters.sentiment;
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.status) params.status = filters.status;

  const response = await api.get<FeedbackListResponse>('/feedback', { params });
  return response.data;
};

export const getFeedback = async (id: string): Promise<Feedback> => {
  const response = await api.get<Feedback>(`/feedback/${id}`);
  return response.data;
};

export const updateFeedback = async (
  id: string,
  data: FeedbackUpdate
): Promise<Feedback> => {
  const response = await api.put<Feedback>(`/feedback/${id}`, data);
  return response.data;
};

export const deleteFeedback = async (id: string): Promise<void> => {
  await api.delete(`/feedback/${id}`);
};

export interface StatsFilters {
  start_date?: string;
  end_date?: string;
  category?: string;
  priority?: string;
  sentiment?: string;
}

export const getStats = async (filters?: StatsFilters): Promise<FeedbackStats> => {
  const params: Record<string, string> = {};
  if (filters?.start_date) params.start_date = filters.start_date;
  if (filters?.end_date) params.end_date = filters.end_date;
  if (filters?.category) params.category = filters.category;
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.sentiment) params.sentiment = filters.sentiment;

  const response = await api.get<FeedbackStats>('/feedback/stats/summary', { params });
  return response.data;
};

export const analyzeText = async (text: string, rating?: number): Promise<AnalysisResult> => {
  const response = await api.post<AnalysisResult>('/intelligence/analyze', { text, rating });
  return response.data;
};

export const analyzeExistingFeedback = async (id: string): Promise<AnalysisResult> => {
  const response = await api.post<AnalysisResult>(`/intelligence/analyze/${id}`);
  return response.data;
};

export const smartSubmitFeedback = async (data: SmartFeedbackCreate): Promise<Feedback> => {
  const response = await api.post<Feedback>('/intelligence/smart-submit', data);
  return response.data;
};

export default api;
