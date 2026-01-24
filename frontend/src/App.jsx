import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ToastContainer from './components/ToastContainer';
import AnimatedRoutes from './components/AnimatedRoutes';
import StarryBackground from './components/StarryBackground';

// Theme Synchronizer
const ThemeSync = () => {
  const { theme } = useAuth();
  React.useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);
  return null;
};

export default function App() {
  return (
    <AuthProvider>
      <ThemeSync />
      <WrappedApp />
    </AuthProvider>
  );
}

// Separate component to useAuth context
const WrappedApp = () => {
  const { theme } = useAuth();

  return (
    <ToastProvider>
      <ToastContainer />
      {theme === 'dark' && <StarryBackground />}
      <Router>
        <AnimatedRoutes />
      </Router>
    </ToastProvider>
  );
};