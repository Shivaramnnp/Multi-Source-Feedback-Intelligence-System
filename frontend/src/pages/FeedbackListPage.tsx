import FeedbackTable from '../components/FeedbackTable';

const FeedbackListPage = () => {
  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">All Feedback</h1>
        <p className="text-dark-400 mt-1">Browse, filter, and inspect detailed AI analysis for all user feedback.</p>
      </div>
      <FeedbackTable />
    </div>
  );
};

export default FeedbackListPage;
