import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import errorIllustration from '../assets/error_page.jpeg';

class GlobalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught Error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4 font-mono">
          <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-xl max-w-lg w-full text-center border border-gray-100 dark:border-slate-700">
            
            <div className="mb-8 overflow-hidden rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm">
                <img src={errorIllustration} alt="Error Illustration" className="w-full h-auto object-cover opacity-90" />
            </div>

            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="text-red-600 dark:text-red-500" size={32} />
            </div>
            
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              Oups ! Une erreur critique est survenue.
            </h1>
            
            <p className="text-slate-500 dark:text-slate-400 mb-8 text-sm leading-relaxed">
              Ne vous inquiétez pas, aucune donnée n'a été perdue. L'application a rencontré un problème inattendu d'affichage.
            </p>

            {/* Error Details (Only in Dev) */}
            {import.meta.env.DEV && this.state.error && (
               <div className="text-left bg-slate-100 dark:bg-slate-950 p-4 rounded-lg mb-6 overflow-auto max-h-40 text-xs text-red-500 font-mono border border-slate-200 dark:border-slate-800">
                 {this.state.error.toString()}
               </div>
            )}

            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReload}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20"
              >
                <RefreshCw size={18} />
                Rafraîchir
              </button>
              <button
                onClick={this.handleGoHome}
                className="px-6 py-3 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 rounded-xl font-bold transition-all flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-600"
              >
                <Home size={18} />
                Accueil
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default GlobalErrorBoundary;
