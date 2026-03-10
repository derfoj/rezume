import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft, Ghost } from 'lucide-react';
import errorImage from '../assets/error_page.jpeg';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4">
      <div className="max-w-2xl w-full bg-white dark:bg-slate-900 rounded-3xl shadow-xl overflow-hidden border border-slate-100 dark:border-slate-800 flex flex-col md:flex-row">
        
        {/* Visual Side */}
        <div className="md:w-1/2 relative group">
          <img 
            src={errorImage} 
            alt="Page non trouvée" 
            className="h-full w-full object-cover min-h-[300px] transition-transform duration-700 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent"></div>
          <div className="absolute bottom-6 left-6 text-white">
            <p className="text-4xl font-bold font-mono">404</p>
            <p className="text-sm font-medium opacity-80 uppercase tracking-widest">Lost in hyperspace</p>
          </div>
        </div>

        {/* Content Side */}
        <div className="md:w-1/2 p-8 md:p-12 flex flex-col justify-center text-center md:text-left">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center mb-6 mx-auto md:mx-0">
            <Ghost className="text-blue-600 dark:text-blue-400" size={24} />
          </div>
          
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4 leading-tight">
            Cette page a disparu dans le vide sidéral.
          </h1>
          
          <p className="text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
            L'URL que vous recherchez n'existe pas ou a été déplacée. Pas de panique, vos CV sont en sécurité.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <button 
              onClick={() => navigate('/')}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
            >
              <Home size={18} />
              Accueil
            </button>
            <button 
              onClick={() => navigate(-1)}
              className="flex-1 px-6 py-3 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl font-bold transition-all flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-700"
            >
              <ArrowLeft size={18} />
              Retour
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
