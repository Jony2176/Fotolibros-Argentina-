
import React, { useState, useEffect } from 'react';
import Landing from './pages/Landing';
import Designs from './pages/Designs';
import OrderWizard from './pages/OrderWizard';
import OrderTracking from './pages/OrderTracking';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import AIChat from './components/AIChat';

enum Page {
  LANDING = 'landing',
  DESIGNS = 'designs',
  WIZARD = 'wizard',
  TRACKING = 'tracking',
  ADMIN_LOGIN = 'admin_login',
  ADMIN_DASHBOARD = 'admin_dashboard'
}

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>(Page.LANDING);
  const [selectedProductFromDesign, setSelectedProductFromDesign] = useState<string | null>(null);

  // Basic routing based on hash for SPA behavior without path change
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      switch (hash) {
        case 'designs': setCurrentPage(Page.DESIGNS); break;
        case 'wizard': setCurrentPage(Page.WIZARD); break;
        case 'tracking': setCurrentPage(Page.TRACKING); break;
        case 'status': setCurrentPage(Page.TRACKING); break; // Backward compat
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
      [Page.DESIGNS]: 'designs',
      [Page.WIZARD]: 'wizard',
      [Page.TRACKING]: 'tracking',
      [Page.ADMIN_LOGIN]: 'admin',
      [Page.ADMIN_DASHBOARD]: 'dashboard'
    }[page];
    window.location.hash = hash;
  };

  return (
    <div className="min-h-screen">
      {currentPage === Page.LANDING && (
        <Landing
          onStart={() => navigate(Page.WIZARD)}
          onCheckStatus={() => navigate(Page.TRACKING)}
          onAdmin={() => navigate(Page.ADMIN_LOGIN)}
          onViewDesigns={() => navigate(Page.DESIGNS)}
        />
      )}
      {currentPage === Page.DESIGNS && (
        <Designs
          onBack={() => navigate(Page.LANDING)}
          onSelectDesign={(code) => {
            setSelectedProductFromDesign(code);
            navigate(Page.WIZARD);
          }}
        />
      )}
      {currentPage === Page.WIZARD && (
        <OrderWizard
          onBack={() => {
            setSelectedProductFromDesign(null);
            navigate(Page.LANDING);
          }}
          initialProductCode={selectedProductFromDesign || undefined}
        />
      )}
      {currentPage === Page.TRACKING && <OrderTracking onBack={() => navigate(Page.LANDING)} />}
      {currentPage === Page.ADMIN_LOGIN && <AdminLogin onSuccess={() => navigate(Page.ADMIN_DASHBOARD)} onBack={() => navigate(Page.LANDING)} />}
      {currentPage === Page.ADMIN_DASHBOARD && <AdminDashboard onLogout={() => navigate(Page.ADMIN_LOGIN)} />}

      {/* Floating Global Chatbot */}
      <AIChat />
    </div>
  );
};

export default App;
