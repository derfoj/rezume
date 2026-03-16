import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, CheckCircle, Shield, Moon, Sun } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
    const navigate = useNavigate();
    const { theme, toggleTheme } = useAuth();

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-transparent transition-colors duration-500 flex flex-col relative z-10">
            {/* Navbar */}
            <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto w-full">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tighter">reZume</h1>
                <div className="flex items-center gap-4">
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
                        aria-label="Toggle Theme"
                    >
                        {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
                    </button>
                    <button onClick={() => navigate('/login')} className="text-slate-600 dark:text-slate-300 font-medium hover:text-slate-900 dark:hover:text-white">Se connecter</button>
                    <button onClick={() => navigate('/login')} className="bg-blue-600 text-white px-4 py-2 rounded-full font-bold hover:bg-blue-700 transition btn-interactive">
                        Commencer
                    </button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-1 flex flex-col items-center justify-center text-center p-6">
                <div className="mb-8 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-full text-blue-600 dark:text-blue-400 text-sm font-bold tracking-wide animate-fade-in-up">
                    IA PARAMÉTRÉE POUR L'EMPLOI
                </div>
                <h2 className="text-5xl md:text-6xl font-extrabold text-slate-900 dark:text-white mb-6 tracking-tight max-w-3xl">
                    Votre CV, optimisé par <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">l'Intelligence Artificielle</span>.
                </h2>
                <p className="text-lg text-slate-500 dark:text-slate-400 mb-10 max-w-2xl leading-relaxed">
                    Passez les filtres ATS et décrochez plus d'entretiens. reZume analyse les offres et adapte votre parcours instantanément.
                </p>

                <div className="flex flex-col md:flex-row gap-4">
                    <button onClick={() => navigate('/login')} className="px-8 py-4 bg-slate-900 dark:bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-slate-800 dark:hover:bg-blue-700 transition flex items-center gap-2 shadow-lg hover:shadow-xl btn-interactive btn-glow">
                        <Zap size={20} /> Optimiser mon CV maintenant !
                    </button>
                    <button className="px-8 py-4 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-lg font-bold text-lg hover:bg-gray-50 dark:hover:bg-slate-700 transition btn-interactive">
                        Voir la démo
                    </button>
                </div>

                {/* Features */}
                <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto text-left">
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700">
                        <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-4">
                            <CheckCircle className="text-green-600 dark:text-green-400" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 dark:text-white mb-2">Anti-ATS</h3>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">Structure LaTeX optimisée pour être lue par les robots recruteurs.</p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700">
                        <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-4">
                            <Zap className="text-purple-600 dark:text-purple-400" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 dark:text-white mb-2">Sur-mesure</h3>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">L'IA pioche dans vos expériences et les réécrit pour coller parfaitement à chaque offre.</p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                            <Shield className="text-blue-600 dark:text-blue-400" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 dark:text-white mb-2">Données Privées</h3>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">Vos données restent dans votre espace personnel sécurisé.</p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="p-6 text-center text-slate-400 dark:text-slate-600 text-sm font-medium border-t border-slate-100 dark:border-slate-800">
                Développé par NZ Systems
            </footer>
        </div>
    );
}
