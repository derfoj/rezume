import React from 'react';
import { LogOut, AlertTriangle, ServerCrash, RefreshCw } from 'lucide-react';

const SessionExpiredModal = ({ show, type = 'session', onAction }) => {
  if (!show) return null;

  const isSession = type === 'session';

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-8 relative border border-gray-100 dark:border-slate-700 mx-4">
        
        <div className="flex flex-col items-center text-center">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-6 ${isSession ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-red-100 dark:bg-red-900/30'}`}>
            {isSession ? (
                <AlertTriangle className="text-amber-600 dark:text-amber-500" size={32} />
            ) : (
                <ServerCrash className="text-red-600 dark:text-red-500" size={32} />
            )}
          </div>
          
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {isSession ? "Session Expirée" : "Erreur Serveur"}
          </h3>
          
          <p className="text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
            {isSession 
              ? "Votre session de connexion a expiré par mesure de sécurité. Veuillez vous reconnecter pour poursuivre votre travail."
              : "Le serveur rencontre des difficultés ou est inaccessible. Veuillez réessayer dans quelques instants."
            }
          </p>

          <button
            onClick={onAction}
            className={`w-full py-3.5 text-white rounded-xl font-bold shadow-lg transition-all flex items-center justify-center gap-2 ${isSession ? 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/30' : 'bg-red-600 hover:bg-red-700 shadow-red-500/30'}`}
          >
            {isSession ? <LogOut size={18} /> : <RefreshCw size={18} />}
            {isSession ? "Se reconnecter" : "Réessayer"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SessionExpiredModal;
