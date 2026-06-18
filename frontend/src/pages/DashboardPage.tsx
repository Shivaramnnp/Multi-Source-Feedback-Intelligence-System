import Dashboard from '../components/Dashboard';

const DashboardPage = () => {
  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-dark-400 mt-1">Real-time overview of customer feedback and AI-driven intelligence.</p>
      </div>
      <Dashboard />
    </div>
  );
};

export default DashboardPage;
