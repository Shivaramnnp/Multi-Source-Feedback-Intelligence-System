import FeedbackForm from '../components/FeedbackForm';

const FeedbackSubmitPage = () => {
  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Submit Feedback</h1>
        <p className="text-dark-400 mt-1">Submit new feedback with real-time AI categorization, sentiment, and priority detection.</p>
      </div>
      <div className="max-w-3xl mx-auto">
        <FeedbackForm />
      </div>
    </div>
  );
};

export default FeedbackSubmitPage;
