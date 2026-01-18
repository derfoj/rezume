import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Helper to fetch user profile
    const fetchUser = async (currentToken) => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                headers: { Authorization: `Bearer ${currentToken}` }
            });
            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
            } else {
                // If token is invalid, logout
                logout();
            }
        } catch (error) {
            console.error("Error fetching user profile", error);
        }
    };

    // Initial load
    useEffect(() => {
        if (token) {
            fetchUser(token);
        }
    }, [token]);

    const login = async (email, password) => {
        const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await res.json();
        const newToken = data.access_token;

        setToken(newToken);
        localStorage.setItem('token', newToken);
        await fetchUser(newToken);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    const isAuthenticated = !!token;

    const refreshUser = () => {
        if (token) {
            return fetchUser(token);
        }
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
