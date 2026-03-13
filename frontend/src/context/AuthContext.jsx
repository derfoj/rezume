import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import SessionExpiredModal from '../components/SessionExpiredModal';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    // Standardizing on Bearer Token stored in localStorage for cross-domain stability
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [profileData, setProfileData] = useState({
        experiences: [],
        education: [],
        skills: [],
        languages: []
    });
    const [isSessionExpired, setIsSessionExpired] = useState(false);
    const [isServerDown, setIsServerDown] = useState(false);
    
    const [theme, setTheme] = useState(() => {
        if (localStorage.getItem('theme')) return localStorage.getItem('theme');
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    });

    // Automatically uses the VITE_API_URL from Vercel settings or localhost for dev
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'; 
    
    // Debug: Ensure we're hitting the right backend
    if (import.meta.env.PROD) {
        console.log("Production API URL:", API_URL);
    }

    const originalFetchRef = useRef(window.fetch);

    useEffect(() => {
        window.fetch = async (...args) => {
            let [resource, config] = args;
            
            // Ensure resource is an absolute URL if it starts with /api
            if (typeof resource === 'string' && resource.startsWith('/api')) {
                resource = `${API_URL}${resource}`;
            }
            
            config = config ? { ...config } : {};
            
            // 1. Inject Credentials (Cookies) for environments that support them
            config.credentials = 'include';
            
            // 2. Inject Authorization Header (Bearer Token) for Cross-Domain stability
            const storedToken = localStorage.getItem('token');
            if (storedToken) {
                config.headers = {
                    ...config.headers,
                    'Authorization': `Bearer ${storedToken}`
                };
            }

            try {
                const response = await originalFetchRef.current.apply(window, [resource, config]);
                
                if (response.status === 401) {
                    const url = typeof resource === 'string' ? resource : resource?.url;
                    
                    if (url && url.includes('/api/auth/login')) {
                        return response;
                    }

                    if (url && url.includes('/api/profile/me')) {
                        console.warn("Startup Check: Not logged in.");
                        setUser(null);
                        return response;
                    }

                    console.warn("Global Interceptor: Session Expired during action");
                    setIsSessionExpired(true);
                }

                if (response.status >= 500) {
                     const url = typeof resource === 'string' ? resource : resource?.url;
                     console.error(`Global Interceptor: Server Error (${response.status}) at ${url}`);
                     
                     if (url && !url.includes('/api/auth/login')) {
                        setIsServerDown(true);
                     }
                }
                
                return response;
            } catch (error) {
                const url = typeof resource === 'string' ? resource : resource?.url;
                if (url && !url.includes('/api/profile/me') && !url.includes('/api/auth/login')) {
                    console.error(`Global Interceptor: Network Error at ${url}`, error);
                    setIsServerDown(true);
                }
                throw error;
            }
        };

        return () => {
            window.fetch = originalFetchRef.current;
        };
    }, [API_URL]); // Added dependency on API_URL

    const fetchUser = async () => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`);
            if (res.ok) {
                const userData = await res.json();
                setUser(userData);

                const headers = { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' };
                const [expRes, eduRes, skillRes, langRes] = await Promise.all([
                    fetch(`${API_URL}/api/profile/experiences`, { headers }),
                    fetch(`${API_URL}/api/profile/education`, { headers }),
                    fetch(`${API_URL}/api/profile/skills`, { headers }),
                    fetch(`${API_URL}/api/profile/languages`, { headers })
                ]);

                const profileDataUpdates = {};
                if (expRes.ok) profileDataUpdates.experiences = await expRes.json();
                if (eduRes.ok) profileDataUpdates.education = await eduRes.json();
                if (skillRes.ok) profileDataUpdates.skills = await skillRes.json();
                if (langRes.ok) profileDataUpdates.languages = await langRes.json();

                setProfileData(prev => ({ ...prev, ...profileDataUpdates }));

                if (userData.theme) {
                    setTheme(userData.theme);
                    localStorage.setItem('theme', userData.theme);
                }
                return true;
            } else {
                setUser(null);
                setProfileData({ experiences: [], education: [], skills: [], languages: [] });
                return false;
            }
        } catch (error) {
            console.error("Error fetching user profile", error);
            return false;
        }
    };

    useEffect(() => {
        fetchUser();
    }, []);

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
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await res.json();
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            setToken(data.access_token);
        }

        setIsSessionExpired(false);
        setIsServerDown(false);
        
        // Wait a tiny bit for token/cookie propagation
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const success = await fetchUser();
        if (!success) {
            throw new Error("Authentification réussie, mais impossible de charger le profil. Veuillez rafraîchir.");
        }
    };

    const logout = async () => {
        try {
            await fetch(`${API_URL}/api/auth/logout`, {
                method: 'POST'
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
        if (isAuthenticated && user) {
            fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: newTheme })
            }).catch(err => console.error("Failed to sync theme", err));
        }
    };

    return (
        <AuthContext.Provider value={{ token, user, profileData, login, logout, isAuthenticated, refreshUser, theme, toggleTheme }}>
            {children}
            <SessionExpiredModal show={isSessionExpired} type="session" onAction={logout} />
            <SessionExpiredModal show={isServerDown} type="server" onAction={handleRetry} />
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
