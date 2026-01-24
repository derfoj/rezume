import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import Dashboard from '../pages/Dashboard';
import ProfileEditor from '../pages/ProfileEditor';
import Explore from '../pages/Explore';
import CVBuilder from '../pages/CVBuilder';
import PageTransition from './PageTransition';
import { useAuth } from '../context/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated } = useAuth();
    if (!isAuthenticated) return <Navigate to="/login" />;
    return children;
};

const AnimatedRoutes = () => {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={<PageTransition><LandingPage /></PageTransition>} />
                <Route path="/login" element={<PageTransition><LoginPage /></PageTransition>} />

                {/* Protected Routes */}
                <Route path="/dashboard" element={
                    <ProtectedRoute>
                        <PageTransition><Dashboard /></PageTransition>
                    </ProtectedRoute>
                } />

                <Route path="/editor" element={
                    <ProtectedRoute>
                        <PageTransition><ProfileEditor /></PageTransition>
                    </ProtectedRoute>
                } />

                <Route path="/explore" element={
                    <ProtectedRoute>
                        <PageTransition><Explore /></PageTransition>
                    </ProtectedRoute>
                } />

                <Route path="/builder" element={
                    <ProtectedRoute>
                        <PageTransition><CVBuilder /></PageTransition>
                    </ProtectedRoute>
                } />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </AnimatePresence>
    );
};

export default AnimatedRoutes;
