import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Check, Layout, ArrowLeft } from 'lucide-react';
import { useToast } from '../context/ToastContext';

export default function Explore() {
    const { token, user, refreshUser } = useAuth();
    const navigate = useNavigate();
    const { addToast } = useToast();
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(true);
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        fetchTemplates();
    }, []);

    const fetchTemplates = async () => {
        try {
            const res = await fetch(`${API_URL}/api/templates`);
            if (res.ok) {
                setTemplates(await res.json());
            }
        } catch (error) {
            console.error("Failed to fetch templates", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectTemplate = async (templateId) => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ selected_template: templateId })
            });

            if (res.ok) {
                await refreshUser(); // Update context to reflect change
                addToast("Template sélectionné !", 'success');
            }
        } catch (error) {
            addToast("Erreur lors de la sélection", 'error');
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-transparent p-8 text-slate-900 dark:text-slate-100 font-sans relative z-10 transition-colors duration-500">
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-center bg-white dark:bg-slate-800/90 backdrop-blur-sm p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-700">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
                            <Layout className="text-blue-600" /> Galerie de Templates
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Choisissez le style qui correspond à votre personnalité.</p>
                    </div>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="text-slate-600 dark:text-slate-300 font-bold hover:text-blue-600 dark:hover:text-blue-400 transition-colors bg-slate-50 dark:bg-slate-700/50 px-4 py-2 rounded-lg flex items-center gap-2 btn-interactive"
                    >
                        <ArrowLeft size={18} /> Retour
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-20 text-slate-400">Chargement des designs...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {templates.map(tpl => {
                            const isSelected = user?.selected_template === tpl.id;
                            return (
                                <div
                                    key={tpl.id}
                                    onClick={() => handleSelectTemplate(tpl.id)}
                                    className={`group cursor-pointer bg-white dark:bg-slate-800 rounded-2xl overflow-hidden border-2 transition-all duration-300 relative btn-interactive ${isSelected ? 'border-blue-600 shadow-xl ring-4 ring-blue-50 dark:ring-blue-900/30' : 'border-gray-100 dark:border-slate-700 hover:border-blue-300 hover:shadow-lg'}`}
                                >
                                    {/* Preview Image or Placeholder */}
                                    <div className="h-64 w-full relative overflow-hidden bg-slate-100 dark:bg-slate-900">
                                        {tpl.preview ? (
                                            <img
                                                src={`/templates/${tpl.preview}`}
                                                alt={tpl.name}
                                                className="w-full h-full object-cover object-top group-hover:scale-110 transition-transform duration-500"
                                                onError={(e) => {
                                                    e.target.onerror = null;
                                                    e.target.src = ""; // Clear src to show placeholder if image fails to load
                                                    e.target.classList.add('hidden');
                                                }}
                                            />
                                        ) : null}

                                        {/* Fallback Gradient (visible if no image or image fails) */}
                                        <div className={`absolute inset-0 flex items-center justify-center text-4xl font-bold text-white uppercase tracking-widest -z-10 ${tpl.id === 'modern' ? 'bg-gradient-to-br from-blue-500 to-cyan-400' : 'bg-gradient-to-br from-indigo-500 to-purple-600'}`}>
                                            {tpl.name.split(' ')[0]}
                                        </div>
                                    </div>

                                    <div className="p-6">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className={`font-bold text-xl ${isSelected ? 'text-blue-600' : 'text-slate-900 dark:text-white'}`}>{tpl.name}</h3>
                                            {isSelected && <div className="bg-blue-600 text-white p-1 rounded-full"><Check size={14} /></div>}
                                        </div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
                                            {tpl.description}
                                        </p>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
