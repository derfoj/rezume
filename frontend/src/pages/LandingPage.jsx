import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, CheckCircle, Shield } from 'lucide-react';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col">
            {/* Navbar */}
            <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto w-full">
                <h1 className="text-2xl font-bold text-slate-900 tracking-tighter">reZume</h1>
                <div className="space-x-4">
                    <button onClick={() => navigate('/login')} className="text-slate-600 font-medium hover:text-slate-900">Se connecter</button>
                    <button onClick={() => navigate('/login')} className="bg-blue-600 text-white px-4 py-2 rounded-full font-bold hover:bg-blue-700 transition">
                        Commencer
                    </button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-1 flex flex-col items-center justify-center text-center p-6">
                <div className="mb-8 p-3 bg-blue-50 border border-blue-100 rounded-full text-blue-600 text-sm font-bold tracking-wide animate-fade-in-up">
                    IA PARAMÉTRÉE POUR L'EMPLOI
                </div>
                <h2 className="text-5xl md:text-6xl font-extrabold text-slate-900 mb-6 tracking-tight max-w-3xl">
                    Votre CV, optimisé par <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">l'Intelligence Artificielle</span>.
                </h2>
                <p className="text-lg text-slate-500 mb-10 max-w-2xl leading-relaxed">
                    Passez les filtres ATS et décrochez plus d'entretiens. reZume analyse les offres et adapte votre parcours instantanément.
                </p>

                <div className="flex flex-col md:flex-row gap-4">
                    <button onClick={() => navigate('/login')} className="px-8 py-4 bg-slate-900 text-white rounded-lg font-bold text-lg hover:bg-slate-800 transition flex items-center gap-2 shadow-lg hover:shadow-xl">
                        <Zap size={20} /> Optimiser mon CV maintenant !
                    </button>
                    <button className="px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-lg font-bold text-lg hover:bg-gray-50 transition">
                        Voir la démo
                    </button>
                </div>

                {/* Features */}
                <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto text-left">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                            <CheckCircle className="text-green-600" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">Anti-ATS</h3>
                        <p className="text-slate-500 text-sm">Structure LaTeX optimisée pour être lue par les robots recruteurs.</p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                            <Zap className="text-purple-600" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">Sur-mesure</h3>
                        <p className="text-slate-500 text-sm">L'IA pioche dans vos expériences et les réécrit pour coller parfaitement à chaque offre.</p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                            <Shield className="text-blue-600" size={20} />
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">Données Privées</h3>
                        <p className="text-slate-500 text-sm">Vos données restent dans votre espace personnel sécurisé.</p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="p-6 text-center text-slate-400 text-sm font-medium border-t border-slate-100">
                Développé par NZ Systems
            </footer>
        </div>
    );
}
