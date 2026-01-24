import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import SessionExpiredModal from '../components/SessionExpiredModal';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [isSessionExpired, setIsSessionExpired] = useState(false);
    const [isServerDown, setIsServerDown] = useState(false);
    
    // Initialize theme from localStorage or system preference, default to 'light'
    const [theme, setTheme] = useState(() => {
        if (localStorage.getItem('theme')) return localStorage.getItem('theme');
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    });

    // Use relative path by default to leverage Vite proxy in dev and same-origin in prod
    const API_URL = import.meta.env.VITE_API_URL || '';

    // --- Global Fetch Interceptor for 401 & 500 Handling ---
    const originalFetchRef = useRef(window.fetch);

    useEffect(() => {
        // Only setup interceptor once
        window.fetch = async (...args) => {
            // Normalize arguments to ensure we have an options object
            let [resource, config] = args;
            
            // Create or clone config object
            config = config ? { ...config } : {};
            
            // FORCE cookies to be sent with every request
            config.credentials = 'include';
            
            // REMOVE Authorization header if present. 
            // We rely strictly on cookies. Sending a manual header (especially a dummy one)
            // causes the backend to try (and fail) to decode it as a JWT, blocking the valid cookie.
            if (config.headers && config.headers.Authorization) {
                delete config.headers.Authorization;
            }
            // Also handle Headers object case if used
            if (config.headers instanceof Headers && config.headers.has('Authorization')) {
                config.headers.delete('Authorization');
            }

            try {
                // Use .apply to preserve window context
                const response = await originalFetchRef.current.apply(window, [resource, config]);
                
                // Check for 401 Unauthorized
                if (response.status === 401) {
                    const url = typeof resource === 'string' ? resource : resource?.url;
                    
                    // Don't trigger on login failure itself
                    if (url && url.includes('/api/auth/login')) {
                        return response;
                    }

                    // For startup check, just accept we are logged out
                    if (url && url.includes('/api/profile/me')) {
                        console.warn("Startup Check: Not logged in.");
                        setUser(null);
                        return response;
                    }

                    // For real actions, it means session really expired
                    console.warn("Global Interceptor: Session Expired during action");
                    setIsSessionExpired(true);
                }

                // Check for Server Errors (500+)
                if (response.status >= 500) {
                     const url = typeof resource === 'string' ? resource : resource?.url;
                     console.error("Global Interceptor: Server Error (5xx)");
                     
                     if (url && !url.includes('/api/auth/login')) {
                        setIsServerDown(true);
                     }
                }
                
                return response;
            } catch (error) {
                const url = typeof resource === 'string' ? resource : resource?.url;
                
                if (url && !url.includes('/api/profile/me') && !url.includes('/api/auth/login')) {
                    console.error("Global Interceptor: Network Error", error);
                    setIsServerDown(true);
                }
                
                throw error;
            }
        };

        return () => {
            window.fetch = originalFetchRef.current;
        };
    }, []);

    // Helper to fetch user profile
    const fetchUser = async () => {
        try {
            // credentials: 'include' is now auto-injected by interceptor
            const res = await fetch(`${API_URL}/api/profile/me`);
            if (res.ok) {
                const userData = await res.json();
                setUser(userData);

                // Sync local theme with user preference if it exists
                if (userData.theme) {
                    setTheme(userData.theme);
                    localStorage.setItem('theme', userData.theme);
                }
                return true;
            } else {
                setUser(null);
                return false;
            }
        } catch (error) {
            console.error("Error fetching user profile", error);
            return false;
        }
    };

    // Initial load
    useEffect(() => {
        fetchUser();
    }, []);

    // Persist theme to localStorage whenever it changes
    useEffect(() => {
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

    const login = async (email, password) => {
        const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            // credentials injected by interceptor
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Login failed');
        }

        // We do NOT set a fake token anymore.
        setIsSessionExpired(false);
        setIsServerDown(false);
        
        await fetchUser();
    };

    const logout = async () => {
        try {
            await fetch(`${API_URL}/api/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error("Logout failed", error);
        }
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        setIsSessionExpired(false);
        window.location.href = '/login';
    };

    const handleRetry = () => {
        setIsServerDown(false);
        window.location.reload();
    }

    const isAuthenticated = !!user;

    const refreshUser = () => {
        return fetchUser();
    };

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        // If logged in, update user profile
        if (isAuthenticated && user) {
            fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: newTheme }),
                credentials: 'include'
            }).catch(err => console.error("Failed to sync theme", err));
        }
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated, refreshUser, theme, toggleTheme }}>
            {children}
            <SessionExpiredModal 
                show={isSessionExpired} 
                type="session" 
                onAction={logout} 
            />
            <SessionExpiredModal 
                show={isServerDown} 
                type="server" 
                onAction={handleRetry} 
            />
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
