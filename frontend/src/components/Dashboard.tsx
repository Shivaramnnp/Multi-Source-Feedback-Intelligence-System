import { useState, useEffect } from 'react';
import {
  MessageSquare,
  Star,
  TrendingUp,
  Loader2,
  AlertCircle,
  Calendar,
  Filter,
  X,
  SlidersHorizontal,
  Flame,
  Activity,
  ThumbsUp,
} from 'lucide-react';
import {
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area,
  CartesianGrid,
} from 'recharts';
import { getStats } from '../api/feedback';
import type { FeedbackStats, Feedback } from '../types/feedback';
import type { StatsFilters } from '../api/feedback';

const PIE_COLORS = ['#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];

const sentimentColors: Record<string, string> = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#64748b',
  mixed: '#f59e0b',
};

const sentimentBadgeClasses: Record<string, string> = {
  positive: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  negative: 'bg-red-500/10 text-red-400 border border-red-500/20',
  neutral: 'bg-slate-500/10 text-slate-400 border border-slate-500/20',
  mixed: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
};

const priorityBadgeClasses: Record<string, string> = {
  low: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  medium: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  high: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
  critical: 'bg-red-500/10 text-red-400 border border-red-500/20',
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  gradient: string;
  description?: string;
  children?: React.ReactNode;
}

const StatCard = ({ title, value, icon: Icon, gradient, description, children }: StatCardProps) => (
  <div className="glass rounded-2xl p-6 flex flex-col justify-between min-h-[160px] relative overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:border-white/20">
    <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-bl-full -z-10 pointer-events-none" />
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs font-semibold text-dark-400 uppercase tracking-wider">{title}</p>
        <p className="mt-2 text-3xl font-extrabold text-white tracking-tight">{value}</p>
      </div>
      <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} shadow-lg shadow-black/30`}>
        <Icon className="h-5 w-5 text-white" />
      </div>
    </div>
    <div className="mt-4">
      {description && <p className="text-xs text-dark-400 font-medium">{description}</p>}
      {children}
    </div>
  </div>
);

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="glass rounded-xl px-4 py-3 shadow-xl border border-white/15 bg-dark-900/90 backdrop-blur-md">
      {label && <p className="text-xs font-bold text-dark-300 mb-1.5 border-b border-white/10 pb-1">{label}</p>}
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-semibold flex items-center gap-2" style={{ color: entry.color || entry.payload.color || '#fff' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    </div>
  );
};


const RecentFeedbackCard = ({ feedback }: { feedback: Feedback }) => (
  <div className="glass rounded-xl p-4 glass-hover flex flex-col justify-between h-44">
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((s) => (
            <Star
              key={s}
              className={`h-3 w-3 ${s <= feedback.rating ? 'text-amber-400 fill-amber-400' : 'text-dark-600'}`}
            />
          ))}
        </div>
        <span className="text-[10px] text-dark-400 font-medium">
          {new Date(feedback.created_at).toLocaleDateString()}
        </span>
      </div>
      <p className="text-xs text-dark-200 line-clamp-4 leading-relaxed font-normal">{feedback.text}</p>
    </div>
    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/5">
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${sentimentBadgeClasses[feedback.sentiment]}`}>
        {feedback.sentiment}
      </span>
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${priorityBadgeClasses[feedback.priority]}`}>
        {feedback.priority}
      </span>
      <span className="text-[10px] font-semibold text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-full border border-primary-500/15 capitalize ml-auto">
        {feedback.category}
      </span>
    </div>
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [sentiment, setSentiment] = useState('');

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters: StatsFilters = {};
      if (startDate) filters.start_date = startDate;
      if (endDate) filters.end_date = endDate;
      if (category) filters.category = category;
      if (priority) filters.priority = priority;
      if (sentiment) filters.sentiment = sentiment;

      const data = await getStats(filters);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [startDate, endDate, category, priority, sentiment]);

  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
    setCategory('');
    setPriority('');
    setSentiment('');
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-primary-500 mx-auto" />
          <p className="mt-4 text-sm text-dark-400">Loading intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="glass rounded-2xl p-8 text-center max-w-md border border-red-500/20">
          <AlertCircle className="h-10 w-10 text-red-400 mx-auto" />
          <p className="mt-4 text-lg font-semibold text-white">Failed to Load Dashboard</p>
          <p className="mt-2 text-sm text-dark-400">{error}</p>
          <button 
            onClick={fetchStats} 
            className="mt-6 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-sm font-semibold transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  // Process data for charts
  const categoryData = Object.entries(stats.category_distribution || {}).map(([name, value]) => ({ name, value }));
  
  // Rating distribution processing
  const ratingOrder = ['1', '2', '3', '4', '5'];
  const ratingData = ratingOrder.map((rating) => ({
    name: `${rating} Star`,
    value: stats.rating_distribution?.[rating] || 0,
  }));

  // Heatmap processing: Category vs Priority
  const allCategories = ['bug', 'feature', 'improvement', 'complaint', 'praise', 'other'];
  const allPriorities = ['low', 'medium', 'high', 'critical'];

  // Trend Data processing for charts
  const trendsList = stats.trends || [];
  const trendChartData = trendsList.map((item: any) => {
    const formatted: any = { date: item.date };
    formatted['Total Feedback'] = item.count;
    
    allCategories.forEach((cat) => {
      formatted[`cat_${cat}`] = item.categories?.[cat] || 0;
    });

    Object.keys(sentimentColors).forEach((sent) => {
      formatted[`sent_${sent}`] = item.sentiments?.[sent] || 0;
    });

    return formatted;
  });

  // Sentiment percentages
  const totalSentiment = Object.values(stats.sentiment_distribution || {}).reduce((a, b) => a + b, 0);
  const getSentimentPercent = (label: string) => {
    const val = stats.sentiment_distribution?.[label] || 0;
    return totalSentiment > 0 ? Math.round((val / totalSentiment) * 100) : 0;
  };

  return (
    <div className="space-y-8">
      {/* Premium Filter Panel */}
      <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl">
        <div className="flex items-center gap-2 mb-4 text-white font-semibold text-sm">
          <SlidersHorizontal className="h-4 w-4 text-primary-400" />
          <h2>Dashboard Analytics Filters</h2>
          {(startDate || endDate || category || priority || sentiment) && (
            <button
              onClick={clearFilters}
              className="ml-auto text-xs font-semibold text-red-400 hover:text-red-300 flex items-center gap-1 bg-red-500/10 px-2.5 py-1 rounded-lg border border-red-500/20 transition-all"
            >
              <X className="h-3.5 w-3.5" /> Clear Filters
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Date Range Selector */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-dark-400 flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" /> Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-primary-500 transition-all"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-dark-400 flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" /> End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-primary-500 transition-all"
            />
          </div>

          {/* Dropdown Filters */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-dark-400 flex items-center gap-1.5">
              <Filter className="h-3.5 w-3.5" /> Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-primary-500 transition-all capitalize"
            >
              <option value="">All Categories</option>
              {allCategories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-dark-400 flex items-center gap-1.5">
              <Filter className="h-3.5 w-3.5" /> Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-primary-500 transition-all capitalize"
            >
              <option value="">All Priorities</option>
              {allPriorities.map((prio) => (
                <option key={prio} value={prio}>{prio}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-dark-400 flex items-center gap-1.5">
              <Filter className="h-3.5 w-3.5" /> Sentiment
            </label>
            <select
              value={sentiment}
              onChange={(e) => setSentiment(e.target.value)}
              className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-primary-500 transition-all capitalize"
            >
              <option value="">All Sentiments</option>
              {Object.keys(sentimentColors).map((sent) => (
                <option key={sent} value={sent}>{sent}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Widgets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        {/* Widget 1: Total Feedback */}
        <StatCard
          title="Total Feedback"
          value={stats.total_count}
          icon={MessageSquare}
          gradient="from-blue-500 to-blue-700"
          description={`${stats.recent_feedback?.length || 0} entries added recently`}
        />

        {/* Widget 2: Average Rating */}
        <StatCard
          title="Average Rating"
          value={stats.average_rating?.toFixed(1) || '0.0'}
          icon={Star}
          gradient="from-amber-500 to-amber-700"
        >
          <div className="flex gap-1 mt-1">
            {[1, 2, 3, 4, 5].map((s) => (
              <Star
                key={s}
                className={`h-4.5 w-4.5 ${s <= Math.round(stats.average_rating || 0) ? 'text-amber-400 fill-amber-400' : 'text-dark-600'}`}
              />
            ))}
          </div>
        </StatCard>

        {/* Widget 3: Sentiment Breakdown */}
        <StatCard
          title="Sentiment Breakdown"
          value={`${getSentimentPercent('positive')}%`}
          icon={ThumbsUp}
          gradient="from-emerald-500 to-emerald-700"
        >
          <div className="space-y-1.5 mt-1">
            <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden flex">
              <div style={{ width: `${getSentimentPercent('positive')}%` }} className="bg-emerald-400 h-full" />
              <div style={{ width: `${getSentimentPercent('neutral')}%` }} className="bg-slate-400 h-full" />
              <div style={{ width: `${getSentimentPercent('negative')}%` }} className="bg-red-400 h-full" />
            </div>
            <div className="flex items-center justify-between text-[9px] font-bold uppercase text-dark-300">
              <span className="text-emerald-400">Pos: {getSentimentPercent('positive')}%</span>
              <span className="text-slate-400">Neu: {getSentimentPercent('neutral')}%</span>
              <span className="text-red-400">Neg: {getSentimentPercent('negative')}%</span>
            </div>
          </div>
        </StatCard>

        {/* Widget 4: Category Distribution */}
        <StatCard
          title="Categories"
          value={categoryData.length}
          icon={Activity}
          gradient="from-indigo-500 to-indigo-700"
        >
          <div className="flex flex-wrap gap-1 mt-1 max-h-[40px] overflow-y-auto">
            {categoryData.map((item) => (
              <span key={item.name} className="text-[9px] font-bold px-1.5 py-0.5 rounded-md bg-white/5 text-dark-200 border border-white/5 capitalize">
                {item.name}: {item.value}
              </span>
            ))}
          </div>
        </StatCard>

        {/* Widget 5: Trend Sparkline widget */}
        <StatCard
          title="Feedback Trend"
          value={trendChartData.length > 0 ? trendChartData[trendChartData.length - 1]['Total Feedback'] : 0}
          icon={TrendingUp}
          gradient="from-purple-500 to-purple-700"
          description="Daily activity tracking"
        >
          {trendChartData.length > 0 && (
            <div className="h-10 w-full overflow-hidden mt-1">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendChartData.slice(-7)}>
                  <Area type="monotone" dataKey="Total Feedback" stroke="#a855f7" fill="#a855f7" fillOpacity={0.15} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </StatCard>

        {/* Widget 6: Priority Heatmap mini card representation */}
        <StatCard
          title="Priority Heatmap"
          value={stats.priority_distribution?.critical || 0}
          icon={Flame}
          gradient="from-red-500 to-red-700"
          description="Critical issues flagged"
        >
          <div className="grid grid-cols-4 gap-1.5 mt-1 border-t border-white/5 pt-2">
            {allPriorities.map((prio) => {
              const val = stats.priority_distribution?.[prio] || 0;
              let bg = 'bg-white/5 text-dark-300';
              if (prio === 'critical' && val > 0) bg = 'bg-red-500/20 text-red-400 border border-red-500/35 animate-pulse';
              else if (prio === 'high' && val > 0) bg = 'bg-orange-500/20 text-orange-400';
              else if (prio === 'medium' && val > 0) bg = 'bg-yellow-500/10 text-yellow-400';
              return (
                <div key={prio} className={`flex flex-col items-center py-0.5 rounded-lg ${bg}`}>
                  <span className="text-[7px] uppercase font-extrabold">{prio}</span>
                  <span className="text-[10px] font-black">{val}</span>
                </div>
              );
            })}
          </div>
        </StatCard>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Feedback trends over time */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">Feedback Trends Over Time</h2>
            <span className="text-xs text-dark-400 font-semibold flex items-center gap-1.5"><Activity className="h-3.5 w-3.5 text-indigo-400" /> Daily Volume</span>
          </div>
          {trendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendChartData}>
                <defs>
                  <linearGradient id="totalFeedbackGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="Total Feedback" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#totalFeedbackGrad)" name="Total Feedback" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-dark-500 text-sm">No trend data available</div>
          )}
        </div>

        {/* Chart 2: Category growth trends */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">Category Growth & Volume</h2>
            <span className="text-xs text-dark-400 font-semibold flex items-center gap-1.5"><Activity className="h-3.5 w-3.5 text-emerald-400" /> Stacked Trends</span>
          </div>
          {trendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                {allCategories.map((cat, i) => (
                  <Area
                    key={cat}
                    type="monotone"
                    stackId="1"
                    dataKey={`cat_${cat}`}
                    stroke={PIE_COLORS[i % PIE_COLORS.length]}
                    fill={PIE_COLORS[i % PIE_COLORS.length]}
                    fillOpacity={0.25}
                    name={cat.replace('_', ' ')}
                  />
                ))}
                <Legend wrapperStyle={{ fontSize: '10px', marginTop: '10px' }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-dark-500 text-sm">No category growth data available</div>
          )}
        </div>

        {/* Chart 3: Sentiment trends */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">Sentiment Trends</h2>
            <span className="text-xs text-dark-400 font-semibold flex items-center gap-1.5"><Activity className="h-3.5 w-3.5 text-yellow-400" /> Daily Mood</span>
          </div>
          {trendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                {Object.entries(sentimentColors).map(([sent, color]) => (
                  <Area
                    key={sent}
                    type="monotone"
                    stackId="1"
                    dataKey={`sent_${sent}`}
                    stroke={color}
                    fill={color}
                    fillOpacity={0.25}
                    name={sent}
                  />
                ))}
                <Legend wrapperStyle={{ fontSize: '10px', marginTop: '10px' }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-dark-500 text-sm">No sentiment trend data available</div>
          )}
        </div>

        {/* Chart 4: Rating distribution bar chart */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">Rating Distribution</h2>
            <span className="text-xs text-dark-400 font-semibold flex items-center gap-1.5"><Star className="h-3.5 w-3.5 text-amber-400" /> Customer Ratings</span>
          </div>
          {ratingData.some((r) => r.value > 0) ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={ratingData} barCategoryGap="25%">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={{ stroke: '#334155' }} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} name="Total Feedbacks">
                  {ratingData.map((_entry, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-dark-500 text-sm">No rating data available</div>
          )}
        </div>
      </div>

      {/* Grid: Heatmap & Recent Feedback */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Heatmap Widget: Category vs Priority matrix */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl xl:col-span-1">
          <h2 className="text-lg font-bold text-white mb-6">Priority Heatmap</h2>
          <div className="space-y-4">
            <p className="text-xs text-dark-400 leading-relaxed font-medium">
              Distribution matrix of feedback category vs priority. Hotter cells represent a higher volume of items.
            </p>
            <div className="grid grid-cols-5 gap-2 text-center text-[10px] font-bold uppercase text-dark-400 select-none">
              <div className="col-span-1" />
              {allPriorities.map((prio) => (
                <div key={prio} className="truncate capitalize">{prio}</div>
              ))}
            </div>

            <div className="space-y-2">
              {allCategories.map((cat) => (
                <div key={cat} className="grid grid-cols-5 gap-2 items-center text-center">
                  <div className="text-[10px] font-bold text-left text-white capitalize truncate">{cat}</div>
                  {allPriorities.map((prio) => {
                    const count = stats.priority_heatmap?.[cat]?.[prio] || 0;
                    
                    // Determine styling based on count volume
                    let cellBg = 'bg-white/5 border border-white/5 text-dark-500';
                    if (count > 5) {
                      cellBg = 'bg-red-500 text-white font-extrabold border border-red-400 shadow-md shadow-red-500/20';
                    } else if (count > 2) {
                      cellBg = 'bg-orange-500/80 text-white font-extrabold border border-orange-400';
                    } else if (count > 0) {
                      cellBg = 'bg-primary-500/40 text-primary-200 border border-primary-500/30';
                    }

                    return (
                      <div
                        key={prio}
                        className={`h-8 rounded-lg flex items-center justify-center text-xs font-semibold transition-all duration-300 ${cellBg}`}
                        title={`${count} feedback(s) with ${prio} priority in category ${cat}`}
                      >
                        {count}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Feedback Feed */}
        <div className="glass rounded-2xl p-6 border border-white/10 shadow-xl xl:col-span-2">
          <h2 className="text-lg font-bold text-white mb-6">Recent Activity feed</h2>
          {stats.recent_feedback && stats.recent_feedback.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {stats.recent_feedback.slice(0, 4).map((fb) => (
                <RecentFeedbackCard key={fb.id} feedback={fb} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Loader2 className="h-8 w-8 text-dark-600 animate-pulse mb-3" />
              <p className="text-sm font-semibold text-white">No recent feedback matches the filters</p>
              <p className="text-xs text-dark-400 mt-1">Try clearing or adjusting filters to expand results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
