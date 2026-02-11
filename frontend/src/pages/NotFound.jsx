import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import errorIllustration from '../assets/error_page.jpeg';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4 font-mono transition-colors duration-500">
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-xl max-w-lg w-full text-center border border-gray-100 dark:border-slate-700 animate-fadeIn">
        
        <div className="mb-8 overflow-hidden rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm relative">
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent z-10"></div>
            <img src={errorIllustration} alt="404 Illustration" className="w-full h-auto object-cover opacity-90 transform hover:scale-105 transition-transform duration-700" />
            <div className="absolute bottom-4 left-0 right-0 text-white z-20">
                <h2 className="text-4xl font-bold tracking-widest">404</h2>
            </div>
        </div>

        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Page Introuvable
        </h1>
        
        <p className="text-slate-500 dark:text-slate-400 mb-8 text-sm leading-relaxed">
          Il semblerait que vous ayez dérivé trop loin dans l'espace. Cette page n'existe pas ou a été déplacée.
        </p>

        <div className="flex gap-4 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 rounded-xl font-bold transition-all flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-600 btn-interactive"
          >
            <ArrowLeft size={18} />
            Retour
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20 btn-interactive"
          >
            <Home size={18} />
            Accueil
          </button>
        </div>
      </div>
    </div>
  );
}
