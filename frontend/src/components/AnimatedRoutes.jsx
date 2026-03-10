import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import PageTransition from './PageTransition';
import { RefreshCw } from 'lucide-react';

// --- Lazy Loading (Les composants ne sont chargés que SI la route est active) ---
const LandingPage = lazy(() => import('../pages/LandingPage'));
const LoginPage = lazy(() => import('../pages/LoginPage'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const ProfileEditor = lazy(() => import('../pages/ProfileEditor'));
const Explore = lazy(() => import('../pages/Explore'));
const CVBuilder = lazy(() => import('../pages/CVBuilder'));
const AdminDashboard = lazy(() => import('../pages/AdminDashboard'));
const NotFound = lazy(() => import('../pages/NotFound'));

// Loading Fallback
const LoadingScreen = () => (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <RefreshCw className="animate-spin text-blue-600" size={32} />
    </div>
);

const AnimatedRoutes = () => {
    const location = useLocation();
    const { user, isAuthenticated } = useAuth();

    return (
        <Suspense fallback={<LoadingScreen />}>
            <AnimatePresence mode="wait">
                <Routes location={location} key={location.pathname}>
                    {/* Public Routes */}
                    <Route path="/" element={<PageTransition><LandingPage /></PageTransition>} />
                    <Route path="/login" element={<PageTransition><LoginPage /></PageTransition>} />

                    {/* Conditional Auth Routes - Non-existent if not logged in */}
                    {isAuthenticated && (
                        <>
                            <Route path="/dashboard" element={<PageTransition><Dashboard /></PageTransition>} />
                            <Route path="/editor" element={<PageTransition><ProfileEditor /></PageTransition>} />
                            <Route path="/profile" element={<PageTransition><ProfileEditor /></PageTransition>} />
                            <Route path="/explore" element={<PageTransition><Explore /></PageTransition>} />
                            <Route path="/builder" element={<PageTransition><CVBuilder /></PageTransition>} />
                        </>
                    )}

                    {/* Strict Admin Route - Code and Route strictly not loaded if not admin */}
                    {isAuthenticated && user?.role === 'admin' && (
                        <Route path="/admin" element={<PageTransition><AdminDashboard /></PageTransition>} />
                    )}

                    {/* Redirect to login if trying to access auth routes without session */}
                    {!isAuthenticated && (
                        <Route path="/dashboard" element={<Navigate to="/login" />} />
                    )}

                    {/* Fallback 404 */}
                    <Route path="*" element={<PageTransition><NotFound /></PageTransition>} />
                </Routes>
            </AnimatePresence>
        </Suspense>
    );
};

export default AnimatedRoutes;
