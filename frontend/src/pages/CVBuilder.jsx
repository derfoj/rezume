import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { translations } from '../config/translations';
import { 
  FileText, Sparkles, Send, Download, RefreshCw, Eye, 
  ChevronRight, Layout, CheckCircle2, AlertCircle, Clock
} from 'lucide-react';

export default function CVBuilder() {
  const { user, profileData, lang, token } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  // Safety check for translations
  const currentLang = lang || 'fr';
  const t = translations[currentLang]?.builder;

  const [jobOffer, setJobOffer] = useState("");
  const [isGenerating, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [pdfReady, setPdfReady] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // --- Background Generation Logic (Polling) ---
  useEffect(() => {
    let pollInterval;

    if (jobId && isGenerating) {
      pollInterval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/api/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const data = await res.json();

          if (data.status === 'completed') {
            setProgress(100);
            setIsLoading(false);
            setPdfReady(true);
            setStatusMessage("CV prêt pour le téléchargement !");
            addToast("Génération terminée avec succès", "success");
            clearInterval(pollInterval);
          } else if (data.status === 'failed') {
            setIsLoading(false);
            setStatusMessage("Échec : " + data.error);
            addToast("La génération a échoué", "error");
            clearInterval(pollInterval);
          } else {
            setProgress(data.progress || 20);
            setStatusMessage("Traitement en cours...");
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 2000); // Check every 2 seconds
    }

    return () => clearInterval(pollInterval);
  }, [jobId, isGenerating, token, API_URL, addToast]);

  const handleGenerate = async () => {
    if (isGenerating) return;
    
    setIsLoading(true);
    setPdfReady(false);
    setProgress(10);
    setStatusMessage("Initialisation...");

    try {
      const res = await fetch(`${API_URL}/api/generate-cv`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_offer_text: jobOffer,
          experiences: profileData.experiences,
          template_name: user.selected_template || 'modern'
        }),
      });

      if (!res.ok) throw new Error("Impossible de lancer la génération.");
      const data = await res.json();
      setJobId(data.job_id);
    } catch (err) {
      addToast(err.message, "error");
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!jobId) return;
    window.open(`${API_URL}/api/download/${jobId}?token=${token}`, '_blank');
  };

  if (!t) return null; // Prevent crash if translations aren't loaded

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8 mt-12 md:mt-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <Sparkles size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white leading-tight">AI CV Architect</h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Génération asynchrone haute performance</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-[10px] font-bold text-slate-600 dark:text-slate-300 uppercase tracking-wider">Moteur IA Actif</span>
          </div>
        </div>

        {/* Main Interface */}
        <div className="grid grid-cols-1 gap-8">
          
          {/* Input Section */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-50 dark:border-slate-800 flex items-center justify-between">
              <h3 className="font-bold flex items-center gap-2 text-slate-900 dark:text-white">
                <Layout size={18} className="text-blue-500" /> Ciblage de l'offre
              </h3>
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-tighter">Optionnel</span>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="relative group">
                <textarea
                  value={jobOffer}
                  onChange={(e) => setJobOffer(e.target.value)}
                  placeholder="Copiez-collez l'offre d'emploi ici pour que l'IA adapte votre CV..."
                  className="w-full h-48 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl p-4 text-sm focus:border-blue-500 focus:ring-0 transition-all outline-none resize-none placeholder:text-slate-400 dark:text-white"
                />
                <div className="absolute bottom-4 right-4 text-[10px] font-bold text-slate-400 bg-white dark:bg-slate-900 px-2 py-1 rounded-md border border-slate-100 dark:border-slate-800">
                  {jobOffer.length} caractères
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <Clock size={14} />
                  <span>Temps estimé : ~45s</span>
                </div>
                
                {!pdfReady ? (
                  <button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className={`px-8 py-3 rounded-2xl font-bold flex items-center gap-2 transition-all shadow-lg ${
                      isGenerating 
                      ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed' 
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/20'
                    }`}
                  >
                    {isGenerating ? <RefreshCw size={18} className="animate-spin" /> : <Send size={18} />}
                    {isGenerating ? "Architecturation..." : "Générer mon CV"}
                  </button>
                ) : (
                  <button
                    onClick={handleDownload}
                    className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-2xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-green-500/20 animate-bounce"
                  >
                    <Download size={18} />
                    Télécharger le PDF
                  </button>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            {isGenerating && (
              <div className="px-6 pb-8 space-y-3">
                <div className="flex justify-between items-end mb-1">
                  <span className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest">{statusMessage}</span>
                  <span className="text-xs font-mono text-slate-400">{progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(37,99,235,0.5)]"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Tips Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex gap-3">
              <CheckCircle2 size={18} className="text-green-500 shrink-0" />
              <p className="text-[11px] text-slate-500 leading-relaxed">
                <strong className="text-slate-900 dark:text-slate-300 block mb-1">Ciblage Automatique</strong>
                L'IA analyse les mots-clés de l'offre pour mettre en avant vos meilleures expériences.
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex gap-3">
              <CheckCircle2 size={18} className="text-green-500 shrink-0" />
              <p className="text-[11px] text-slate-500 leading-relaxed">
                <strong className="text-slate-900 dark:text-slate-300 block mb-1">Standard LaTeX</strong>
                Un format professionnel reconnu par tous les recruteurs et les systèmes ATS.
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex gap-3">
              <AlertCircle size={18} className="text-orange-500 shrink-0" />
              <p className="text-[11px] text-slate-500 leading-relaxed">
                <strong className="text-slate-900 dark:text-slate-300 block mb-1">Vérification</strong>
                Une auto-correction est appliquée pour garantir que le CV tient sur une seule page.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
