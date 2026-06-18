import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, MessageSquarePlus, List, Brain, Sparkles } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/submit', label: 'Submit Feedback', icon: MessageSquarePlus, end: false },
  { to: '/feedback', label: 'All Feedback', icon: List, end: false },
];

const Layout = () => {
  return (
    <div className="flex min-h-screen bg-dark-950">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-white/10 bg-dark-900 flex flex-col">
        {/* Brand */}
        <div className="flex flex-col items-center gap-1 px-6 py-8 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 blur-lg opacity-50" />
              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700">
                <Brain className="h-5 w-5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-lg font-bold text-transparent">
                Feedback
              </h1>
              <h1 className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-lg font-bold text-transparent -mt-1">
                Intelligence
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-1.5 mt-2">
            <Sparkles className="h-3 w-3 text-primary-400" />
            <span className="text-xs font-medium text-dark-400">AI-Powered Analytics</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/25'
                    : 'text-dark-400 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon
                    className={`h-5 w-5 transition-colors duration-200 ${
                      isActive ? 'text-white' : 'text-dark-500 group-hover:text-primary-400'
                    }`}
                  />
                  <span>{item.label}</span>
                  {isActive && (
                    <div className="ml-auto h-1.5 w-1.5 rounded-full bg-white animate-pulse" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-white/10 px-6 py-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-dark-500">Version</span>
            <span className="rounded-full bg-primary-500/10 px-2.5 py-0.5 text-xs font-medium text-primary-400">
              v1.0.0
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1 min-h-screen overflow-y-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
