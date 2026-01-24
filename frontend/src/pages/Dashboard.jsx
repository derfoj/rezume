import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { Camera, X, Check, ArrowRight, UserPen, Sparkles, LogOut, Settings, Globe, Moon, Sun, Key, Link, Radio, Layout } from 'lucide-react';
import { translations } from '../config/translations';
import DashboardSkeleton from '../components/DashboardSkeleton';
import { motion } from 'framer-motion';

// Import Avatars
import avatarManLaptop from '../assets/avatar_man_laptop.png';
import avatarWomanLaptop from '../assets/avatar_woman_laptop.png';
import avatarManCoffee from '../assets/avatar_man_coffee.png';
import avatarWomanRocket from '../assets/avatar_woman_rocket.png';
import avatarMarcAurel from '../assets/the_marc_aurel.png';
import avatarFemme from '../assets/avatar_femme.png';


const AVATARS = [
    { id: 'man_laptop', src: avatarManLaptop, label: 'le geek du coin' },
    { id: 'woman_laptop', src: avatarWomanLaptop, label: 'la bosseuse ' },
    { id: 'man_coffee', src: avatarManCoffee, label: 'le gars chill' },
    { id: 'woman_rocket', src: avatarWomanRocket, label: 'la rocket girl' },
    { id: 'marc_aurel', src: avatarMarcAurel, label: 'Le Marc Aurel du coin (l\'intello)' },
    { id: 'avatar_femme', src: avatarFemme, label: 'La joyeuse ' },
];

export default function Dashboard() {
    const { token, logout, refreshUser } = useAuth();
    const navigate = useNavigate();
    const [user, setUser] = useState({
        full_name: '',
        email: '',
        avatar_image: 'default',
        language: 'fr',
        theme: 'light',
        linkedin_url: '',
        openai_api_key: '',
        search_status: 'listening',
        llm_provider: 'openai',
        llm_model: 'gpt-4o-mini',
        selected_template: 'classic'

    });
    const [loading, setLoading] = useState(true);
    const [showAvatarSelector, setShowAvatarSelector] = useState(false);
    const [showSettingsModal, setShowSettingsModal] = useState(false);
    const { addToast } = useToast();
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await fetch(`${API_URL}/api/profile/me`, {
                    credentials: 'include'
                });
                if (res.ok) setUser(await res.json());
            } catch (error) {
                console.error("Error fetching user", error);
            } finally {
                // Determine synthetic loading time for smoother skeletal transition
                setTimeout(() => setLoading(false), 800);
            }
        };
        fetchUser();
    }, [API_URL]); // Removed token dependency

    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [newTitle, setNewTitle] = useState('');

    const handleUpdateAvatar = async (avatarId) => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ avatar_image: avatarId }),
                credentials: 'include'
            });
            if (res.ok) {
                const updatedUser = await res.json();
                setUser(updatedUser);
                await refreshUser(); // Sync with global context
                setShowAvatarSelector(false);
                addToast("Avatar mis à jour avec succès !", 'success');
            }
        } catch (error) {
            console.error("Failed to update avatar", error);
            addToast("Echec de la mise à jour de l'avatar", 'error');
        }
    };

    const handleUpdateSettings = async (updates) => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates),
                credentials: 'include'
            });
            if (res.ok) {
                const updatedUser = await res.json();
                setUser(updatedUser);
                await refreshUser();
                addToast("Paramètres mis à jour !", 'success');
            }
        } catch (error) {
            console.error("Failed to update settings", error);
            addToast("Erreur de sauvegarde", 'error');
        }
    };

    const handleUpdateLanguage = (newLang) => handleUpdateSettings({ language: newLang });
    const handleUpdateTheme = (newTheme) => handleUpdateSettings({ theme: newTheme });

    const handleUpdateTitle = async () => {
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle }),
                credentials: 'include'
            });
            if (res.ok) {
                const updatedUser = await res.json();
                setUser(updatedUser);
                await refreshUser();
                setIsEditingTitle(false);
                addToast("Titre mis à jour !", 'success');
            }
        } catch (error) {
            console.error("Failed to update title", error);
            addToast("Erreur lors de la mise à jour du titre", 'error');
        }
    };

    const hasCustomAvatar = user.avatar_image && user.avatar_image !== 'default';
    const currentAvatarSrc = AVATARS.find(a => a.id === user.avatar_image)?.src;
    const isDark = user.theme === 'dark';

    // Get current language dictionary (fallback to 'fr' if undefined)
    const t = translations[user.language] || translations.fr;

    if (loading) {
        return <DashboardSkeleton />;
    }

    return (
        <div className={`min-h-screen transition-colors duration-500 ${isDark ? 'bg-transparent text-white' : 'bg-slate-50 text-slate-900'}`}>

            {/* Content Wrapper to ensure z-index above stars */}
            <div className="relative z-10">

                {/* Navbar (Matches LandingPage) */}
                <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto w-full">
                    <h1 className={`text-2xl font-bold tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'}`}>reZume</h1>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setShowSettingsModal(true)}
                            className={`p-2 rounded-full transition-all btn-interactive ${isDark ? 'text-slate-300 hover:bg-slate-800 hover:text-white' : 'text-slate-500 hover:text-blue-600 hover:bg-blue-50'}`}
                        >
                            <Settings size={20} />
                        </button>
                        <button
                            onClick={logout}
                            className={`flex items-center gap-2 font-medium transition-colors btn-interactive ${isDark ? 'text-slate-300 hover:text-red-400' : 'text-slate-600 hover:text-red-600'}`}
                        >
                            <LogOut size={18} /> <span className="hidden md:inline">{t.nav.logout}</span>
                        </button>
                    </div>
                </nav>

                {/* Main Content */}
                <main className="flex flex-col items-center justify-center max-w-6xl mx-auto px-6 py-12">

                    {/* Hero Section */}
                    <div className="mb-20 flex flex-col items-center gap-8 text-center">

                        {/* Avatar Circle */}
                        <motion.div
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ type: "spring", stiffness: 260, damping: 20 }}
                            onClick={() => setShowAvatarSelector(true)}
                            className="group relative w-32 h-32 md:w-40 md:h-40 bg-white rounded-full p-2 shadow-xl border border-gray-100 cursor-pointer hover:scale-105 transition-transform duration-300"
                        >
                            <div className="w-full h-full rounded-full overflow-hidden bg-blue-50 flex items-center justify-center relative">
                                {hasCustomAvatar ? (
                                    <img src={currentAvatarSrc} alt="Avatar" className="w-full h-full object-cover" />
                                ) : (
                                    <span className="text-4xl font-bold text-blue-200">{user.full_name?.charAt(0) || 'U'}</span>
                                )}
                            </div>

                            {/* Edit Badge */}
                            <div className="absolute bottom-2 right-2 bg-blue-600 text-white p-2 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
                                <Camera size={16} />
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                        >
                            <div className="mb-4 inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50/10 text-blue-600 font-bold text-xs tracking-wider uppercase rounded-full border border-blue-200 backdrop-blur-sm">
                                {isEditingTitle ? (
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="text"
                                            value={newTitle}
                                            onChange={(e) => setNewTitle(e.target.value)}
                                            className="bg-white border-b border-blue-300 outline-none text-blue-700 w-32"
                                            autoFocus
                                        />
                                        <button onClick={handleUpdateTitle} className="text-green-600 hover:text-green-700"><Check size={14} /></button>
                                        <button onClick={() => setIsEditingTitle(false)} className="text-red-500 hover:text-red-600"><X size={14} /></button>
                                    </div>
                                ) : (
                                    <>
                                        <span>{user.title || 'Étudiant'}</span>
                                        <button
                                            onClick={() => { setNewTitle(user.title || ''); setIsEditingTitle(true); }}
                                            className="ml-2 text-blue-400 hover:text-blue-600 transition-colors"
                                        >
                                            <UserPen size={12} />
                                        </button>
                                    </>
                                )}
                            </div>
                            <h2 className={`text-4xl md:text-5xl font-extrabold tracking-tight mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {t.hero.greeting} <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">{user.full_name?.split(' ')[0] || 'Utilisateur'}</span>.
                            </h2>
                            <p className={`text-lg max-w-2xl mx-auto leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                                {t.hero.subtitle}
                            </p>
                        </motion.div>
                    </div>

                    {/* Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-7xl">

                        {/* Profile Editor Card */}
                        <motion.div
                            whileHover={{ scale: 1.05, y: -5 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/editor')}
                            className={`group p-8 rounded-2xl shadow-sm border transition-all duration-300 cursor-pointer flex flex-col relative overflow-hidden ${isDark ? 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-blue-500/50 hover:shadow-blue-900/20' : 'bg-white border-gray-100 hover:shadow-xl hover:border-blue-200'}`}
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform ${isDark ? 'bg-blue-900/30' : 'bg-blue-100'}`}>
                                <UserPen className="text-blue-500" size={24} />
                            </div>
                            <h3 className={`text-2xl font-bold mb-3 transition-colors ${isDark ? 'text-white group-hover:text-blue-400' : 'text-slate-900 group-hover:text-blue-600'}`}>{t.cards.editor.title}</h3>
                            <p className={`mb-8 leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                                {t.cards.editor.desc}
                            </p>
                            <div className="mt-auto flex items-center text-blue-500 font-bold text-sm tracking-wide">
                                {t.cards.editor.action} <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </motion.div>

                        {/* CV Builder Card */}
                        <motion.div
                            whileHover={{ scale: 1.05, y: -5 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/builder')}
                            className={`group p-8 rounded-2xl shadow-sm border transition-all duration-300 cursor-pointer flex flex-col relative overflow-hidden ${isDark ? 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-purple-500/50 hover:shadow-purple-900/20' : 'bg-white border-gray-100 hover:shadow-xl hover:border-purple-200'}`}
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform ${isDark ? 'bg-purple-900/30' : 'bg-purple-100'}`}>
                                <Sparkles className="text-purple-500" size={24} />
                            </div>
                            <h3 className={`text-2xl font-bold mb-3 transition-colors ${isDark ? 'text-white group-hover:text-purple-400' : 'text-slate-900 group-hover:text-purple-600'}`}>{t.cards.builder.title}</h3>
                            <p className={`mb-8 leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                                {t.cards.builder.desc}
                            </p>
                            <div className="mt-auto flex items-center text-purple-500 font-bold text-sm tracking-wide">
                                {t.cards.builder.action} <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </motion.div>

                        {/* Explore Templates Card */}
                        <motion.div
                            whileHover={{ scale: 1.05, y: -5 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/explore')}
                            className={`group p-8 rounded-2xl shadow-sm border transition-all duration-300 cursor-pointer flex flex-col relative overflow-hidden ${isDark ? 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-teal-500/50 hover:shadow-teal-900/20' : 'bg-white border-gray-100 hover:shadow-xl hover:border-teal-200'}`}
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform ${isDark ? 'bg-teal-900/30' : 'bg-teal-100'}`}>
                                <Layout className="text-teal-500" size={24} />
                            </div>
                            <h3 className={`text-2xl font-bold mb-3 transition-colors ${isDark ? 'text-white group-hover:text-teal-400' : 'text-slate-900 group-hover:text-teal-600'}`}>{t.cards.explore.title}</h3>
                            <p className={`mb-8 leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                                {t.cards.explore.desc}
                            </p>
                            <div className="mt-auto flex items-center text-teal-500 font-bold text-sm tracking-wide">
                                {t.cards.explore.action} <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </motion.div>
                    </div>

                </main>
            </div>

            {/* Avatar Selector Modal */}
            {showAvatarSelector && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full p-8 relative">
                        <button
                            onClick={() => setShowAvatarSelector(false)}
                            className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={24} />
                        </button>

                        <div className="text-center mb-10">
                            <h3 className="text-2xl font-bold text-slate-900 mb-2">{t.modals.avatar.title}</h3>
                            <p className="text-slate-500 text-sm">{t.modals.avatar.subtitle}</p>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            {AVATARS.map((avatar) => (
                                <button
                                    key={avatar.id}
                                    onClick={() => handleUpdateAvatar(avatar.id)}
                                    className={`relative p-4 rounded-xl border-2 transition-all duration-200 group flex flex-col items-center ${user.avatar_image === avatar.id
                                        ? 'border-blue-600 bg-blue-50 ring-4 ring-blue-50'
                                        : 'border-slate-100 hover:border-blue-200 hover:bg-slate-50'}`}
                                >
                                    <div className="w-full aspect-square mb-4 overflow-hidden rounded-lg">
                                        <img src={avatar.src} alt={avatar.label} className="w-full h-full object-contain transform group-hover:scale-110 transition-transform duration-300" />
                                    </div>
                                    <span className={`text-xs font-bold uppercase tracking-wider ${user.avatar_image === avatar.id ? 'text-blue-700' : 'text-slate-500 group-hover:text-slate-700'}`}>
                                        {t.avatars[avatar.id] || avatar.label}
                                    </span>

                                    {user.avatar_image === avatar.id && (
                                        <div className="absolute top-3 right-3 bg-blue-600 text-white rounded-full p-1">
                                            <Check size={10} />
                                        </div>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Settings Modal */}
            {showSettingsModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
                        <button
                            onClick={() => setShowSettingsModal(false)}
                            className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={24} />
                        </button>

                        <div className="text-center mb-8">
                            <h3 className="text-2xl font-bold text-slate-900 mb-2 flex items-center justify-center gap-2">
                                <Settings className="text-blue-600" /> {t.modals.settings.title}
                            </h3>
                            <p className="text-slate-500 text-sm">{t.modals.settings.subtitle}</p>
                        </div>

                        <div className="space-y-6">
                            {/* Language & Theme Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                                        <Globe size={16} /> {t.modals.settings.language}
                                    </label>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleUpdateLanguage('fr')}
                                            className={`flex-1 p-3 rounded-xl border-2 font-bold transition-all text-sm ${user.language === 'fr' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-100 hover:border-blue-200 text-slate-600'}`}
                                        >
                                            🇫🇷 FR
                                        </button>
                                        <button
                                            onClick={() => handleUpdateLanguage('en')}
                                            className={`flex-1 p-3 rounded-xl border-2 font-bold transition-all text-sm ${user.language === 'en' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-100 hover:border-blue-200 text-slate-600'}`}
                                        >
                                            🇬🇧 EN
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                                        <Moon size={16} /> {t.modals.settings.theme}
                                    </label>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleUpdateTheme('light')}
                                            className={`flex-1 p-3 rounded-xl border-2 font-bold transition-all text-sm flex items-center justify-center gap-2 ${user.theme === 'light' || !user.theme ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-gray-100 hover:border-amber-200 text-slate-600'}`}
                                        >
                                            <Sun size={14} /> {t.modals.settings.light}
                                        </button>
                                        <button
                                            onClick={() => handleUpdateTheme('dark')}
                                            className={`flex-1 p-3 rounded-xl border-2 font-bold transition-all text-sm flex items-center justify-center gap-2 ${user.theme === 'dark' ? 'border-indigo-600 bg-indigo-950 text-indigo-300' : 'border-gray-100 hover:border-indigo-200 text-slate-600'}`}
                                        >
                                            <Moon size={14} /> {t.modals.settings.dark}
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="border-t border-gray-100 pt-6 space-y-4">
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                                        <Link size={16} /> {t.modals.settings.linkedin}
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="https://linkedin.com/in/..."
                                        value={user.linkedin_url || ''}
                                        onChange={(e) => setUser({ ...user, linkedin_url: e.target.value })}
                                        onBlur={() => handleUpdateSettings({ linkedin_url: user.linkedin_url })}
                                        className="w-full p-3 rounded-xl border border-gray-200 bg-slate-50 focus:bg-white focus:border-blue-500 outline-none text-sm transition-all"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                                        <Key size={16} /> {t.modals.settings.apiKey} <span className="text-xs font-normal text-slate-400 ml-auto">{t.modals.settings.optional}</span>
                                    </label>
                                    <input
                                        type="password"
                                        placeholder="sk-..."
                                        value={user.openai_api_key || ''}
                                        onChange={(e) => setUser({ ...user, openai_api_key: e.target.value })}
                                        onBlur={() => handleUpdateSettings({ openai_api_key: user.openai_api_key })}
                                        className="w-full p-3 rounded-xl border border-gray-200 bg-slate-50 focus:bg-white focus:border-blue-500 outline-none text-sm transition-all font-mono"
                                    />
                                </div>
                            </div>

                            <div className="border-t border-gray-100 pt-6 space-y-4">
                                <h4 className="font-bold text-slate-900 flex items-center gap-2"><Sparkles size={16} className="text-purple-600" /> {t.modals.settings.aiSection}</h4>

                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-2">{t.modals.settings.provider}</label>
                                    <div className="flex gap-2">
                                        {['openai', 'anthropic', 'gemini'].map(p => (
                                            <button
                                                key={p}
                                                onClick={() => handleUpdateSettings({ llm_provider: p })}
                                                className={`flex-1 p-2 rounded-lg border capitalize text-sm transition-all ${user.llm_provider === p
                                                    ? 'bg-purple-50 border-purple-500 text-purple-700 font-bold'
                                                    : 'border-gray-200 hover:border-purple-200 text-slate-600'}`}
                                            >
                                                {p}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-2">{t.modals.settings.model}</label>
                                    <input
                                        type="text"
                                        placeholder="Ex: gpt-4o, claude-3-5-sonnet, gemini-1.5-pro"
                                        value={user.llm_model || ''}
                                        onChange={(e) => setUser({ ...user, llm_model: e.target.value })}
                                        onBlur={() => handleUpdateSettings({ llm_model: user.llm_model })}
                                        className="w-full p-3 rounded-xl border border-gray-200 bg-slate-50 focus:bg-white focus:border-purple-500 outline-none text-sm transition-all font-mono"
                                    />
                                    <p className="text-xs text-slate-400 mt-1">{t.modals.settings.modelHint}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}