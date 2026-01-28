
import React, { useState, useEffect } from 'react';
import Landing from './pages/Landing';
import OrderWizard from './pages/OrderWizard';
import OrderStatusPage from './pages/OrderStatusPage';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import AIChat from './components/AIChat';

enum Page {
  LANDING = 'landing',
  WIZARD = 'wizard',
  STATUS = 'status',
  ADMIN_LOGIN = 'admin_login',
  ADMIN_DASHBOARD = 'admin_dashboard'
}

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>(Page.LANDING);
  
  // Basic routing based on hash for SPA behavior without path change
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      switch (hash) {
        case 'wizard': setCurrentPage(Page.WIZARD); break;
        case 'status': setCurrentPage(Page.STATUS); break;
        case 'admin': setCurrentPage(Page.ADMIN_LOGIN); break;
        case 'dashboard': setCurrentPage(Page.ADMIN_DASHBOARD); break;
        default: setCurrentPage(Page.LANDING); break;
      }
    };
    
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Initial load
    
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigate = (page: Page) => {
    const hash = {
      [Page.LANDING]: '',
      [Page.WIZARD]: 'wizard',
      [Page.STATUS]: 'status',
      [Page.ADMIN_LOGIN]: 'admin',
      [Page.ADMIN_DASHBOARD]: 'dashboard'
    }[page];
    window.location.hash = hash;
  };

  return (
    <div className="min-h-screen">
      {currentPage === Page.LANDING && <Landing onStart={() => navigate(Page.WIZARD)} onCheckStatus={() => navigate(Page.STATUS)} onAdmin={() => navigate(Page.ADMIN_LOGIN)} />}
      {currentPage === Page.WIZARD && <OrderWizard onBack={() => navigate(Page.LANDING)} />}
      {currentPage === Page.STATUS && <OrderStatusPage onBack={() => navigate(Page.LANDING)} />}
      {currentPage === Page.ADMIN_LOGIN && <AdminLogin onSuccess={() => navigate(Page.ADMIN_DASHBOARD)} onBack={() => navigate(Page.LANDING)} />}
      {currentPage === Page.ADMIN_DASHBOARD && <AdminDashboard onLogout={() => navigate(Page.ADMIN_LOGIN)} />}
      
      {/* Floating Global Chatbot */}
      <AIChat />
    </div>
  );
};

export default App;
