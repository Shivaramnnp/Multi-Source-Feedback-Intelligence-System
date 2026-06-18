import { useState } from 'react';
import {
  Star,
  Send,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Zap,
  PenLine,
  Brain,
  Sparkles,
  Tag,
  Gauge,
  X,
} from 'lucide-react';
import { createFeedback, smartSubmitFeedback } from '../api/feedback';
import { Category, Sentiment, Priority, Source } from '../types/feedback';
import type { FeedbackCreate, AnalysisResult } from '../types/feedback';

const FeedbackForm = () => {
  const [mode, setMode] = useState<'smart' | 'manual'>('smart');

  // Form fields
  const [text, setText] = useState('');
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [category, setCategory] = useState<Category>(Category.OTHER);
  const [sentiment, setSentiment] = useState<Sentiment>(Sentiment.NEUTRAL);
  const [priority, setPriority] = useState<Priority>(Priority.MEDIUM);
  const [source, setSource] = useState<Source>(Source.WEB);

  // State
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const resetForm = () => {
    setText('');
    setRating(0);
    setHoverRating(0);
    setCategory(Category.OTHER);
    setSentiment(Sentiment.NEUTRAL);
    setPriority(Priority.MEDIUM);
    setSource(Source.WEB);
    setAnalysisResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Feedback text is required');
      return;
    }
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setAnalysisResult(null);

    try {
      if (mode === 'smart') {
        const result = await smartSubmitFeedback({
          text: text.trim(),
          rating,
          source,
        });
        // Build analysis result from the returned feedback for display
        setAnalysisResult({
          cleaned_text: text.trim(),
          sentiment: {
            label: result.sentiment,
            score: 0,
            confidence: 0,
            positive_words: [],
            negative_words: [],
          },
          category: {
            category: result.category,
            confidence: 0,
            matched_keywords: [],
          },
          priority: {
            priority: result.priority,
            score: 0,
            reasons: [],
          },
          processing_steps: ['Text cleaned', 'Sentiment analyzed', 'Category detected', 'Priority assigned'],
        });
      } else {
        const payload: FeedbackCreate = {
          text: text.trim(),
          rating,
          category,
          sentiment,
          priority,
          source,
        };
        await createFeedback(payload);
      }
      setSuccess(true);
      resetForm();
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to submit feedback';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const selectClasses =
    'w-full rounded-xl border border-white/10 bg-dark-800 px-4 py-3 text-sm text-white outline-none transition-all duration-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 appearance-none cursor-pointer';

  const sentimentBadgeClasses: Record<string, string> = {
    positive: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    negative: 'bg-red-500/20 text-red-400 border-red-500/30',
    neutral: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    mixed: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  };

  const priorityBadgeClasses: Record<string, string> = {
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Mode Toggle */}
      <div className="glass rounded-2xl p-2 inline-flex gap-1">
        <button
          type="button"
          onClick={() => { setMode('smart'); setAnalysisResult(null); }}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-medium transition-all duration-200 ${
            mode === 'smart'
              ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/25'
              : 'text-dark-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Zap className="h-4 w-4" />
          Smart Mode
        </button>
        <button
          type="button"
          onClick={() => { setMode('manual'); setAnalysisResult(null); }}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-medium transition-all duration-200 ${
            mode === 'manual'
              ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/25'
              : 'text-dark-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <PenLine className="h-4 w-4" />
          Manual Mode
        </button>
      </div>

      {/* Mode Description */}
      <div className="flex items-start gap-3 glass rounded-xl p-4">
        {mode === 'smart' ? (
          <>
            <Brain className="h-5 w-5 text-primary-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-white">AI-Powered Submission</p>
              <p className="text-xs text-dark-400 mt-0.5">
                Just enter your feedback text, rating, and source. Our intelligence engine will automatically
                detect sentiment, category, and priority.
              </p>
            </div>
          </>
        ) : (
          <>
            <PenLine className="h-5 w-5 text-dark-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-white">Manual Submission</p>
              <p className="text-xs text-dark-400 mt-0.5">
                Manually specify all feedback fields including category, sentiment, and priority.
              </p>
            </div>
          </>
        )}
      </div>

      {/* Success Banner */}
      {success && (
        <div className="flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4 animate-slide-up">
          <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-emerald-400">Feedback submitted successfully!</p>
            <p className="text-xs text-emerald-400/70 mt-0.5">
              {mode === 'smart' ? 'AI analysis complete. See results below.' : 'Your feedback has been recorded.'}
            </p>
          </div>
          <button onClick={() => setSuccess(false)} className="ml-auto text-emerald-400/50 hover:text-emerald-400">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 animate-slide-up">
          <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
          <p className="text-sm font-medium text-red-400">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-400/50 hover:text-red-400">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 space-y-6">
        {/* Feedback Text */}
        <div>
          <label className="mb-2 block text-sm font-medium text-dark-300">
            Feedback Text <span className="text-red-400">*</span>
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Share your feedback, experience, or suggestion..."
            rows={5}
            className="w-full rounded-xl border border-white/10 bg-dark-800 px-4 py-3 text-sm text-white placeholder-dark-500 outline-none transition-all duration-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 resize-none"
          />
          <p className="mt-1.5 text-xs text-dark-500">{text.length} characters</p>
        </div>

        {/* Star Rating */}
        <div>
          <label className="mb-2 block text-sm font-medium text-dark-300">
            Rating <span className="text-red-400">*</span>
          </label>
          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                className="rounded-lg p-1 transition-transform duration-150 hover:scale-110"
              >
                <Star
                  className={`h-8 w-8 transition-colors duration-150 ${
                    star <= (hoverRating || rating)
                      ? 'text-amber-400 fill-amber-400'
                      : 'text-dark-600 hover:text-dark-500'
                  }`}
                />
              </button>
            ))}
            {rating > 0 && (
              <span className="ml-3 text-sm text-dark-400">{rating} / 5</span>
            )}
          </div>
        </div>

        {/* Source dropdown (always shown) */}
        <div>
          <label className="mb-2 block text-sm font-medium text-dark-300">Source</label>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value as Source)}
            className={selectClasses}
          >
            {Object.values(Source).map((s) => (
              <option key={s} value={s} className="bg-dark-800">
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Manual mode fields */}
        {mode === 'manual' && (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 animate-fade-in">
            <div>
              <label className="mb-2 block text-sm font-medium text-dark-300">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as Category)}
                className={selectClasses}
              >
                {Object.values(Category).map((c) => (
                  <option key={c} value={c} className="bg-dark-800">
                    {c.charAt(0).toUpperCase() + c.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-dark-300">Sentiment</label>
              <select
                value={sentiment}
                onChange={(e) => setSentiment(e.target.value as Sentiment)}
                className={selectClasses}
              >
                {Object.values(Sentiment).map((s) => (
                  <option key={s} value={s} className="bg-dark-800">
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-dark-300">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as Priority)}
                className={selectClasses}
              >
                {Object.values(Priority).map((p) => (
                  <option key={p} value={p} className="bg-dark-800">
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-primary-500/25 transition-all duration-200 hover:scale-[1.02] hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              {mode === 'smart' ? 'Analyzing & Submitting...' : 'Submitting...'}
            </>
          ) : (
            <>
              {mode === 'smart' ? <Sparkles className="h-4 w-4" /> : <Send className="h-4 w-4" />}
              {mode === 'smart' ? 'Analyze & Submit' : 'Submit Feedback'}
            </>
          )}
        </button>
      </form>

      {/* Analysis Results (Smart Mode) */}
      {analysisResult && (
        <div className="glass rounded-2xl p-8 space-y-6 animate-slide-up">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">AI Analysis Results</h3>
              <p className="text-xs text-dark-400">Automatically detected by the intelligence engine</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {/* Sentiment */}
            <div className={`rounded-xl border p-4 ${sentimentBadgeClasses[analysisResult.sentiment.label] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">Sentiment</span>
              </div>
              <p className="text-2xl font-bold capitalize">{analysisResult.sentiment.label}</p>
            </div>

            {/* Category */}
            <div className="rounded-xl border border-primary-500/30 bg-primary-500/10 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Tag className="h-4 w-4 text-primary-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-primary-400">Category</span>
              </div>
              <p className="text-2xl font-bold capitalize text-primary-300">{analysisResult.category.category}</p>
            </div>

            {/* Priority */}
            <div className={`rounded-xl border p-4 ${priorityBadgeClasses[analysisResult.priority.priority] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
              <div className="flex items-center gap-2 mb-2">
                <Gauge className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">Priority</span>
              </div>
              <p className="text-2xl font-bold capitalize">{analysisResult.priority.priority}</p>
            </div>
          </div>

          {/* Processing Steps */}
          {analysisResult.processing_steps.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-dark-300 mb-2">Processing Steps</h4>
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
      )}
    </div>
  );
};

export default FeedbackForm;
