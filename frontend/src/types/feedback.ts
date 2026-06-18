export const Category = {
  BUG: 'bug',
  FEATURE: 'feature',
  IMPROVEMENT: 'improvement',
  COMPLAINT: 'complaint',
  PRAISE: 'praise',
  OTHER: 'other',
} as const;
export type Category = typeof Category[keyof typeof Category];

export const Sentiment = {
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral',
  MIXED: 'mixed',
} as const;
export type Sentiment = typeof Sentiment[keyof typeof Sentiment];

export const Priority = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;
export type Priority = typeof Priority[keyof typeof Priority];

export const Source = {
  WEB: 'web',
  EMAIL: 'email',
  API: 'api',
  SOCIAL: 'social',
  SUPPORT: 'support',
} as const;
export type Source = typeof Source[keyof typeof Source];

export const Status = {
  NEW: 'new',
  IN_REVIEW: 'in_review',
  ADDRESSED: 'addressed',
  DISMISSED: 'dismissed',
} as const;
export type Status = typeof Status[keyof typeof Status];

export interface Feedback {
  id: string;
  text: string;
  rating: number;
  category: Category;
  sentiment: Sentiment;
  priority: Priority;
  source: Source;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface FeedbackCreate {
  text: string;
  rating: number;
  category: Category;
  sentiment: Sentiment;
  priority: Priority;
  source: Source;
}

export interface FeedbackUpdate {
  text?: string;
  rating?: number;
  category?: Category;
  sentiment?: Sentiment;
  priority?: Priority;
  source?: Source;
  status?: Status;
}

export interface FeedbackListResponse {
  items: Feedback[];
  total: number;
  page: number;
  size: number;
}

export interface FeedbackStats {
  total_count: number;
  average_rating: number;
  sentiment_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  rating_distribution: Record<string, number>;
  trends: any[];
  priority_heatmap: Record<string, Record<string, number>>;
  recent_feedback: Feedback[];
}

// Intelligence Engine types
export interface SentimentResult {
  label: string;
  score: number;
  confidence: number;
  positive_words: string[];
  negative_words: string[];
}

export interface CategoryResult {
  category: string;
  confidence: number;
  matched_keywords: string[];
}

export interface PriorityResult {
  priority: string;
  score: number;
  reasons: string[];
}

export interface AnalysisResult {
  cleaned_text: string;
  sentiment: SentimentResult;
  category: CategoryResult;
  priority: PriorityResult;
  processing_steps: string[];
}

export interface SmartFeedbackCreate {
  text: string;
  rating: number;
  source: string;
}
