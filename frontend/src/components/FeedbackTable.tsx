import { useState, useEffect, useCallback } from 'react';
import {
  Star,
  Trash2,
  Brain,
  Loader2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  X,
  Filter,
  Sparkles,
  Tag,
  Gauge,
  RotateCcw,
  Inbox,
} from 'lucide-react';
import { getFeedbacks, deleteFeedback, analyzeExistingFeedback } from '../api/feedback';
import type { Feedback, AnalysisResult } from '../types/feedback';
import type { FeedbackFilters } from '../api/feedback';
import { Category, Sentiment, Priority, Status } from '../types/feedback';

const sentimentBadgeClasses: Record<string, string> = {
  positive: 'bg-emerald-500/20 text-emerald-400',
  negative: 'bg-red-500/20 text-red-400',
  neutral: 'bg-slate-500/20 text-slate-400',
  mixed: 'bg-amber-500/20 text-amber-400',
};

const priorityBadgeClasses: Record<string, string> = {
  low: 'bg-blue-500/20 text-blue-400',
  medium: 'bg-amber-500/20 text-amber-400',
  high: 'bg-orange-500/20 text-orange-400',
  critical: 'bg-red-500/20 text-red-400',
};

const statusBadgeClasses: Record<string, string> = {
  new: 'bg-blue-500/20 text-blue-400',
  in_review: 'bg-amber-500/20 text-amber-400',
  addressed: 'bg-emerald-500/20 text-emerald-400',
  dismissed: 'bg-slate-500/20 text-slate-400',
};

const sentimentDetailClasses: Record<string, string> = {
  positive: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  negative: 'bg-red-500/20 text-red-400 border-red-500/30',
  neutral: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  mixed: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
};

const priorityDetailClasses: Record<string, string> = {
  low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const PAGE_SIZE = 10;

const FeedbackTable = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterCategory, setFilterCategory] = useState<Category | ''>('');
  const [filterSentiment, setFilterSentiment] = useState<Sentiment | ''>('');
  const [filterPriority, setFilterPriority] = useState<Priority | ''>('');
  const [filterStatus, setFilterStatus] = useState<Status | ''>('');

  // Modals
  const [deleteTarget, setDeleteTarget] = useState<Feedback | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [analysisTarget, setAnalysisTarget] = useState<Feedback | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const filters: FeedbackFilters = {};
      if (filterCategory) filters.category = filterCategory;
      if (filterSentiment) filters.sentiment = filterSentiment;
      if (filterPriority) filters.priority = filterPriority;
      if (filterStatus) filters.status = filterStatus;

      const data = await getFeedbacks(page, PAGE_SIZE, filters);
      setFeedbacks(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load feedback');
    } finally {
      setLoading(false);
    }
  }, [page, filterCategory, filterSentiment, filterPriority, filterStatus]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleClearFilters = () => {
    setFilterCategory('');
    setFilterSentiment('');
    setFilterPriority('');
    setFilterStatus('');
    setPage(1);
  };

  const hasFilters = filterCategory || filterSentiment || filterPriority || filterStatus;

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteFeedback(deleteTarget.id);
      setDeleteTarget(null);
      fetchData();
    } catch {
      setError('Failed to delete feedback');
    } finally {
      setDeleting(false);
    }
  };

  const handleAnalyze = async (fb: Feedback) => {
    setAnalysisTarget(fb);
    setAnalysisResult(null);
    setAnalyzing(true);
    try {
      const result = await analyzeExistingFeedback(fb.id);
      setAnalysisResult(result);
    } catch {
      setAnalysisResult(null);
    } finally {
      setAnalyzing(false);
    }
  };

  const selectClasses =
    'rounded-xl border border-white/10 bg-dark-800 px-3 py-2.5 text-sm text-white outline-none transition-all duration-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 appearance-none cursor-pointer';

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  // Loading skeleton
  if (loading && feedbacks.length === 0) {
    return (
      <div className="space-y-4">
        <div className="glass rounded-2xl p-4">
          <div className="flex gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-10 w-36 animate-pulse rounded-xl bg-dark-800" />
            ))}
          </div>
        </div>
        <div className="glass rounded-2xl overflow-hidden">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="flex items-center gap-4 border-b border-white/5 px-6 py-5"
            >
              <div className="h-4 w-48 animate-pulse rounded bg-dark-800" />
              <div className="h-4 w-20 animate-pulse rounded bg-dark-800" />
              <div className="h-4 w-16 animate-pulse rounded bg-dark-800" />
              <div className="h-4 w-16 animate-pulse rounded bg-dark-800" />
              <div className="h-4 w-16 animate-pulse rounded bg-dark-800" />
              <div className="ml-auto h-4 w-24 animate-pulse rounded bg-dark-800" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <div className="glass rounded-2xl p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <Filter className="h-4 w-4 text-dark-400 flex-shrink-0" />
          <select
            value={filterCategory}
            onChange={(e) => { setFilterCategory(e.target.value as Category | ''); setPage(1); }}
            className={selectClasses}
          >
            <option value="" className="bg-dark-800">All Categories</option>
            {Object.values(Category).map((c) => (
              <option key={c} value={c} className="bg-dark-800">
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </option>
            ))}
          </select>
          <select
            value={filterSentiment}
            onChange={(e) => { setFilterSentiment(e.target.value as Sentiment | ''); setPage(1); }}
            className={selectClasses}
          >
            <option value="" className="bg-dark-800">All Sentiments</option>
            {Object.values(Sentiment).map((s) => (
              <option key={s} value={s} className="bg-dark-800">
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
          <select
            value={filterPriority}
            onChange={(e) => { setFilterPriority(e.target.value as Priority | ''); setPage(1); }}
            className={selectClasses}
          >
            <option value="" className="bg-dark-800">All Priorities</option>
            {Object.values(Priority).map((p) => (
              <option key={p} value={p} className="bg-dark-800">
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => { setFilterStatus(e.target.value as Status | ''); setPage(1); }}
            className={selectClasses}
          >
            <option value="" className="bg-dark-800">All Statuses</option>
            {Object.values(Status).map((s) => (
              <option key={s} value={s} className="bg-dark-800">
                {s.replace('_', ' ').charAt(0).toUpperCase() + s.replace('_', ' ').slice(1)}
              </option>
            ))}
          </select>
          {hasFilters && (
            <button
              onClick={handleClearFilters}
              className="flex items-center gap-1.5 rounded-xl bg-dark-800 px-3 py-2.5 text-xs font-medium text-dark-400 hover:text-white transition-colors duration-200"
            >
              <RotateCcw className="h-3 w-3" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4">
          <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
          <p className="text-sm font-medium text-red-400">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-400/50 hover:text-red-400">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && feedbacks.length === 0 && (
        <div className="glass rounded-2xl p-16 text-center">
          <Inbox className="h-12 w-12 text-dark-600 mx-auto" />
          <p className="mt-4 text-lg font-semibold text-dark-300">No feedback found</p>
          <p className="mt-1 text-sm text-dark-500">
            {hasFilters
              ? 'Try adjusting your filters to see more results.'
              : 'Submit some feedback to get started.'}
          </p>
        </div>
      )}

      {/* Table */}
      {feedbacks.length > 0 && (
        <div className="glass rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Text
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Rating
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Category
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Sentiment
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Priority
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Status
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Created
                  </th>
                  <th className="px-4 py-4 text-right text-xs font-semibold uppercase tracking-wider text-dark-400">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {feedbacks.map((fb) => (
                  <tr
                    key={fb.id}
                    className="transition-colors duration-150 hover:bg-white/5"
                  >
                    <td className="px-6 py-4 max-w-xs">
                      <p className="text-sm text-dark-200 truncate" title={fb.text}>
                        {fb.text.length > 200 ? fb.text.slice(0, 200) + '...' : fb.text}
                      </p>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-0.5">
                        {[1, 2, 3, 4, 5].map((s) => (
                          <Star
                            key={s}
                            className={`h-3.5 w-3.5 ${
                              s <= fb.rating ? 'text-amber-400 fill-amber-400' : 'text-dark-700'
                            }`}
                          />
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="rounded-full bg-primary-500/15 px-2.5 py-1 text-xs font-medium text-primary-400 capitalize">
                        {fb.category}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                          sentimentBadgeClasses[fb.sentiment] || 'bg-slate-500/20 text-slate-400'
                        }`}
                      >
                        {fb.sentiment}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                          priorityBadgeClasses[fb.priority] || 'bg-slate-500/20 text-slate-400'
                        }`}
                      >
                        {fb.priority}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                          statusBadgeClasses[fb.status] || 'bg-slate-500/20 text-slate-400'
                        }`}
                      >
                        {fb.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-xs text-dark-400">{formatDate(fb.created_at)}</span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleAnalyze(fb)}
                          className="flex items-center gap-1.5 rounded-lg bg-primary-500/10 px-3 py-1.5 text-xs font-medium text-primary-400 transition-all duration-200 hover:bg-primary-500/20"
                          title="Analyze with AI"
                        >
                          <Brain className="h-3.5 w-3.5" />
                          Analyze
                        </button>
                        <button
                          onClick={() => setDeleteTarget(fb)}
                          className="flex items-center gap-1.5 rounded-lg bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400 transition-all duration-200 hover:bg-red-500/20"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-white/10 px-6 py-4">
              <p className="text-sm text-dark-400">
                Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)} of{' '}
                {total}
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="flex items-center gap-1 rounded-lg bg-dark-800 px-3 py-2 text-xs font-medium text-dark-300 transition-colors duration-200 hover:bg-dark-700 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-3.5 w-3.5" />
                  Previous
                </button>
                <span className="text-sm text-dark-400 px-2">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="flex items-center gap-1 rounded-lg bg-dark-800 px-3 py-2 text-xs font-medium text-dark-300 transition-colors duration-200 hover:bg-dark-700 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-dark-950/80 backdrop-blur-sm"
            onClick={() => !deleting && setDeleteTarget(null)}
          />
          <div className="relative glass rounded-2xl p-8 max-w-md w-full animate-slide-up shadow-2xl">
            <div className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10 mb-4">
                <Trash2 className="h-7 w-7 text-red-400" />
              </div>
              <h3 className="text-lg font-semibold text-white">Delete Feedback</h3>
              <p className="mt-2 text-sm text-dark-400">
                Are you sure you want to delete this feedback? This action cannot be undone.
              </p>
              <p className="mt-3 text-xs text-dark-500 italic line-clamp-2">
                "{deleteTarget.text}"
              </p>
            </div>
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setDeleteTarget(null)}
                disabled={deleting}
                className="flex-1 rounded-xl bg-dark-800 px-4 py-3 text-sm font-medium text-dark-300 transition-colors duration-200 hover:bg-dark-700 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-red-500 px-4 py-3 text-sm font-semibold text-white transition-all duration-200 hover:bg-red-600 disabled:opacity-50"
              >
                {deleting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Modal */}
      {analysisTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-dark-950/80 backdrop-blur-sm"
            onClick={() => !analyzing && (setAnalysisTarget(null), setAnalysisResult(null))}
          />
          <div className="relative glass rounded-2xl p-8 max-w-2xl w-full animate-slide-up shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
                  <p className="text-xs text-dark-400">Intelligence engine results</p>
                </div>
              </div>
              <button
                onClick={() => { setAnalysisTarget(null); setAnalysisResult(null); }}
                className="rounded-lg p-2 text-dark-400 hover:text-white hover:bg-white/5 transition-colors duration-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Original Text */}
            <div className="glass rounded-xl p-4 mb-6">
              <p className="text-xs font-medium text-dark-400 mb-1">Original Feedback</p>
              <p className="text-sm text-dark-200">{analysisTarget.text}</p>
            </div>

            {analyzing ? (
              <div className="flex flex-col items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
                <p className="mt-4 text-sm text-dark-400">Analyzing feedback...</p>
              </div>
            ) : analysisResult ? (
              <div className="space-y-6 animate-fade-in">
                {/* Result Cards */}
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className={`rounded-xl border p-4 ${sentimentDetailClasses[analysisResult.sentiment.label] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="h-4 w-4" />
                      <span className="text-xs font-semibold uppercase tracking-wider">Sentiment</span>
                    </div>
                    <p className="text-xl font-bold capitalize">{analysisResult.sentiment.label}</p>
                    {analysisResult.sentiment.confidence > 0 && (
                      <p className="text-xs opacity-70 mt-1">
                        {(analysisResult.sentiment.confidence * 100).toFixed(0)}% confidence
                      </p>
                    )}
                  </div>

                  <div className="rounded-xl border border-primary-500/30 bg-primary-500/10 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Tag className="h-4 w-4 text-primary-400" />
                      <span className="text-xs font-semibold uppercase tracking-wider text-primary-400">Category</span>
                    </div>
                    <p className="text-xl font-bold capitalize text-primary-300">{analysisResult.category.category}</p>
                    {analysisResult.category.confidence > 0 && (
                      <p className="text-xs text-primary-400/70 mt-1">
                        {(analysisResult.category.confidence * 100).toFixed(0)}% confidence
                      </p>
                    )}
                  </div>

                  <div className={`rounded-xl border p-4 ${priorityDetailClasses[analysisResult.priority.priority] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Gauge className="h-4 w-4" />
                      <span className="text-xs font-semibold uppercase tracking-wider">Priority</span>
                    </div>
                    <p className="text-xl font-bold capitalize">{analysisResult.priority.priority}</p>
                    {analysisResult.priority.score > 0 && (
                      <p className="text-xs opacity-70 mt-1">Score: {analysisResult.priority.score.toFixed(1)}</p>
                    )}
                  </div>
                </div>

                {/* Matched Keywords */}
                {analysisResult.category.matched_keywords.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-dark-300 mb-2">Matched Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.category.matched_keywords.map((kw, i) => (
                        <span
                          key={i}
                          className="rounded-full bg-primary-500/10 border border-primary-500/20 px-3 py-1 text-xs font-medium text-primary-400"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Positive / Negative Words */}
                {(analysisResult.sentiment.positive_words.length > 0 ||
                  analysisResult.sentiment.negative_words.length > 0) && (
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    {analysisResult.sentiment.positive_words.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-emerald-400 mb-2">Positive Words</h4>
                        <div className="flex flex-wrap gap-1.5">
                          {analysisResult.sentiment.positive_words.map((w, i) => (
                            <span
                              key={i}
                              className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-xs text-emerald-400"
                            >
                              {w}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {analysisResult.sentiment.negative_words.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-red-400 mb-2">Negative Words</h4>
                        <div className="flex flex-wrap gap-1.5">
                          {analysisResult.sentiment.negative_words.map((w, i) => (
                            <span
                              key={i}
                              className="rounded-full bg-red-500/10 border border-red-500/20 px-2.5 py-0.5 text-xs text-red-400"
                            >
                              {w}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Priority Reasons */}
                {analysisResult.priority.reasons.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-dark-300 mb-2">Priority Reasons</h4>
                    <ul className="space-y-1">
                      {analysisResult.priority.reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-dark-400">
                          <span className="text-primary-500 mt-0.5">•</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Cleaned Text */}
                {analysisResult.cleaned_text && analysisResult.cleaned_text !== analysisTarget.text && (
                  <div>
                    <h4 className="text-sm font-medium text-dark-300 mb-2">Cleaned Text</h4>
                    <p className="text-xs text-dark-400 bg-dark-800 rounded-lg p-3 border border-white/5">
                      {analysisResult.cleaned_text}
                    </p>
                  </div>
                )}

                {/* Processing Steps */}
                {analysisResult.processing_steps.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-dark-300 mb-2">Processing Pipeline</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.processing_steps.map((step, i) => (
                        <span
                          key={i}
                          className="rounded-full bg-dark-800 px-3 py-1 text-xs text-dark-300 border border-white/5"
                        >
                          {i + 1}. {step}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center py-12">
                <AlertCircle className="h-8 w-8 text-red-400" />
                <p className="mt-4 text-sm text-dark-400">Failed to analyze feedback. Please try again.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackTable;
