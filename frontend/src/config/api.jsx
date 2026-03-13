// frontend/src/config/api.jsx
// Centralized API configuration to run smoothly on both localhost and production

// VITE_API_URL should be set in Vercel/Render env vars (e.g., https://my-backend.onrender.com)
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getAuthHeaders = (token) => ({
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
});
