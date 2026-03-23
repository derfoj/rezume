import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { translations } from '../config/translations';
import {
  Zap,
  CheckCircle,
  Terminal,
  Download,
  Activity,
  AlertCircle,
  LogOut,
  RefreshCw,
  Code,
  Eye,
  X,
  Pencil,
  Check,
  Cpu
} from 'lucide-react';

// Import Avatars for UI
import avatarManLaptop from '../assets/avatar_man_laptop.png';
import avatarWomanLaptop from '../assets/avatar_woman_laptop.png';
import avatarManCoffee from '../assets/avatar_man_coffee.png';
import avatarWomanRocket from '../assets/avatar_woman_rocket.png';
import avatarMarcAurel from '../assets/the_marc_aurel.png';
import avatarFemme from '../assets/avatar_femme.png';

import SwiftLaTeXPreview from '../components/SwiftLaTeXPreview';
import FormattedText from '../components/FormattedText';

const AVATARS = [
  { id: 'man_laptop', src: avatarManLaptop, label: 'le geek du coin' },
  { id: 'woman_laptop', src: avatarWomanLaptop, label: 'la bosseuse ' },
  { id: 'man_coffee', src: avatarManCoffee, label: 'le gars chill' },
  { id: 'woman_rocket', src: avatarWomanRocket, label: 'la rocket girl' },
  { id: 'marc_aurel', src: avatarMarcAurel, label: 'Le Marc Aurel du coin (l\'intello)' },
  { id: 'avatar_femme', src: avatarFemme, label: 'La joyeuse ' },
];

const GlobalStyles = () => (
  <style>{`
    .bg-white-lab {
      background-color: #ffffff;
      background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
      background-size: 20px 20px;
    }
    .dark .bg-white-lab {
      background-color: transparent;
      background-image: radial-gradient(#1e293b 1px, transparent 1px);
    }
    .glass-panel {
      background: rgba(255, 255, 255, 0.7);
      backdrop-filter: blur(10px);
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .dark .glass-panel {
      background: rgba(15, 23, 42, 0.6); 
      border-color: #334155; 
      color: #e2e8f0;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .tech-accent { color: #2563eb; }
    .dark .tech-accent { color: #60a5fa; }
    .animate-dash { transition: stroke-dashoffset 1s ease-in-out; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  `}</style>
);

const MOCK_JOB_OFFER = `Recherche Senior Data Scientist.
Stack: Python, Pandas, Scikit-learn, TensorFlow.
Mission:
- Construire des pipelines ETL robustes.
- Déployer des modèles ML en production (Docker/K8s).
- Optimiser les algos de matching.
XP requise: 5 ans min. Anglais technique.`;

const INITIAL_LOGS = [
  { id: 'init-1', text: "Initializing reZume Orchestrator...", type: 'success' },
  { id: 'init-2', text: "SwiftLaTeX Engine Ready. Waiting for input...", type: 'info' }
];

const TerminalLog = ({ logs }) => {
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-panel p-4 h-48 overflow-hidden relative flex flex-col shadow-inner bg-white/50 dark:bg-slate-900/50 font-mono">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-30"></div>
      <div className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest font-bold mb-2 border-b border-slate-100 dark:border-slate-800 pb-1 flex justify-between">
        <span>System Logs</span>
        <span className="text-green-500">● LIVE</span>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto text-xs space-y-1.5 no-scrollbar text-left">
        {logs.map((log) => (
          <p key={log.id} className="animate-fadeIn">
            <span className="text-slate-400 dark:text-slate-600 mr-2">{'>'}</span>
            <span className={`font-bold ${log.type === 'success' ? 'text-green-600 dark:text-green-400' :
              log.type === 'process' ? 'text-purple-600 dark:text-purple-400' :
                log.type === 'error' ? 'text-red-500 dark:text-red-400' :
                  log.type === 'wait' ? 'text-blue-600 dark:text-blue-400 animate-pulse' :
                    'text-slate-500 dark:text-slate-400'
              }`}>
              {log.text}
            </span>
          </p>
        ))}
      </div>
    </div>
  );
};

const ScoreWidget = ({ score, t }) => {
  const sanitizedScore = Math.max(0, Math.min(100, score || 0));
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (sanitizedScore / 100) * circumference;

  return (
    <div className="glass-panel p-6 flex flex-col items-center justify-center h-full relative overflow-hidden">
      <div className="relative w-40 h-40 flex items-center justify-center mb-4 z-10">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="80" cy="80" r={radius} stroke="currentColor" strokeWidth="10" fill="transparent" className="text-slate-200 dark:text-slate-800" />
          <circle
            cx="80" cy="80" r={radius} stroke="currentColor" strokeWidth="10" fill="transparent"
            strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round"
            className="animate-dash transition-all duration-1000 ease-out text-blue-600 dark:text-blue-500"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-3xl font-bold text-slate-800 dark:text-white">{sanitizedScore}%</span>
        </div>
      </div>
      <div className="text-center z-10">
        <h4 className="text-blue-600 dark:text-blue-400 font-bold uppercase tracking-wider text-sm">{t.builder.widget.title}</h4>
        <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{t.builder.widget.subtitle}</p>
      </div>
    </div>
  );
};

const StatItem = ({ label, value, colorClass }) => (
  <div className="flex justify-between items-center bg-white/80 dark:bg-slate-900/80 border border-gray-100 dark:border-slate-800 p-3 rounded-lg shadow-sm w-full">
    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{label}</span>
    <span className={`${colorClass} font-bold font-mono`}>{value}</span>
  </div>
);

export default function CVBuilderApp() {
  const { token, logout, user, profileData } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const lang = (user?.language && translations[user.language]) ? user.language : 'fr';
  const t = translations[lang];

  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [latexSource, setLatexSource] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const MAX_RETRIES = 2;

  const [score, setScore] = useState(0);
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [results, setResults] = useState(null);
  const [editableExperiences, setEditableExperiences] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [backendStatus, setBackendStatus] = useState('offline');

  const [stats, setStats] = useState({ xp: 0, skills: 0 });
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) setBackendStatus('online');
      } catch (e) {
        setBackendStatus('offline');
      }
    };
    checkBackend();

    if (profileData) {
        setStats({
            xp: profileData.experiences?.length || 0,
            skills: profileData.skills?.length || 0
        });
    }
  }, [API_URL, profileData]);

  const addLog = (text, type = 'process') => {
    const logId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setLogs(prev => [...prev, { id: logId, text, type }]);
  };

  const processJobOffer = async () => {
    if (!input.trim()) return;
    setIsProcessing(true);
    setResults(null);
    setEditableExperiences([]);
    setEditingIndex(null);
    setScore(0);
    setLogs([]);
    setLatexSource(null);
    setRetryCount(0);

    addLog("Initializing Generation sequence...", 'info');
    addLog("Sending input stream to Python Backend...", 'process');

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ raw_text: input }),
      });

      if (!response.ok) throw new Error(response.statusText);

      const data = await response.json();
      addLog("Matching Experiences found.", 'success');
      addLog(`Optimization complete. Score: ${data.score}%`, 'success');
      addToast(t.toasts.analysis_success, 'success');
      setScore(data.score);
      setResults(data);
      setEditableExperiences(data.raw_matches || []);

    } catch (error) {
      addLog(`ERREUR: ${error.message}`, 'error');
      addToast(`${t.toasts.analysis_error} ${error.message}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const startGeneration = async (feedback = null) => {
    if (!editableExperiences || editableExperiences.length === 0) return;
    
    setIsGenerating(true);
    if (!feedback) setLogs([]); 
    
    addLog(feedback ? "Requesting refined version..." : "Generating LaTeX Source...", 'process');

    try {
      const response = await fetch(`${API_URL}/api/generate-cv`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
            experiences: editableExperiences, 
            job_offer_text: input,
            latex_only: true,
            feedback: feedback
        }),
      });

      if (!response.ok) throw new Error("Generation Failed");
      const data = await response.json();
      
      // Poll for LaTeX source
      let attempts = 0;
      const poll = setInterval(async () => {
          attempts++;
          const statusRes = await fetch(`${API_URL}/api/status/${data.job_id}`, {
              headers: { 'Authorization': `Bearer ${token}` }
          });
          const statusData = await statusRes.json();
          
          if (statusData.status === 'success') {
              clearInterval(poll);
              const latexRes = await fetch(`${API_URL}/api/latex/${data.job_id}`, {
                  headers: { 'Authorization': `Bearer ${token}` }
              });
              const latexData = await latexRes.json();
              setLatexSource(latexData.latex);
              setIsGenerating(false);
              addLog("LaTeX Source Ready.", 'success');
          } else if (statusData.status === 'error' || attempts > 20) {
              clearInterval(poll);
              setIsGenerating(false);
              addLog("Generation Failed.", 'error');
          }
      }, 2000);

    } catch (error) {
      addLog(`SYSTEM ERROR: ${error.message}`, 'error');
      addToast("Erreur lors de la génération", 'error');
      setIsGenerating(false);
    }
  };

  const handleSwiftError = (err) => {
      if (err.type === 'page_count' && retryCount < MAX_RETRIES) {
          addLog(`CV too long (${err.count} pages). Retrying with conciseness constraint...`, 'wait');
          setRetryCount(prev => prev + 1);
          startGeneration("Le CV précédent était trop long (plus d'une page). RESTE SUR UNE SEULE PAGE. Sois très concis, élimine le superflu.");
      } else if (err.type === 'page_count') {
          addToast("Impossible de réduire le CV à une page automatiquement.", "error");
      }
  };

  const handleExperienceChange = (index, field, value) => {
    const updated = [...editableExperiences];
    updated[index] = { ...updated[index], [field]: value };
    setEditableExperiences(updated);
  };

  const currentAvatar = user?.avatar_image && AVATARS.find(a => a.id === user.avatar_image);

  return (
    <div className="bg-white-lab dark:bg-transparent min-h-screen flex flex-col p-4 md:p-8 overflow-hidden text-slate-700 dark:text-slate-200 font-mono relative z-10 transition-colors duration-500">
      <GlobalStyles />

      <div className="w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">

        {/* HEADER */}
        <div className="col-span-1 lg:col-span-12 flex justify-between items-end border-b border-gray-200 dark:border-slate-800 pb-4 mb-2">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tighter cursor-pointer" onClick={() => navigate('/dashboard')}>reZume</h1>
            <p className="text-xs tech-accent mt-1 tracking-widest font-bold">/// CV GENERATOR /// SWIFT-LATEX MODE</p>
          </div>
          <div className="flex gap-4 items-center">
            <div className={`flex items-center space-x-2 bg-white dark:bg-slate-900/50 px-3 py-1.5 rounded-full border border-gray-100 dark:border-slate-800 shadow-sm ${backendStatus === 'online' ? 'border-green-200 dark:border-green-900/30' : 'border-red-200 dark:border-red-900/30'}`}>
              <div className={`w-2 h-2 rounded-full animate-pulse ${backendStatus === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={`text-xs font-bold tracking-wider ${backendStatus === 'online' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {backendStatus === 'online' ? 'BACKEND ONLINE' : 'BACKEND OFFLINE'}
              </span>
            </div>
            <button onClick={() => navigate('/dashboard')} className="text-sm font-bold text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 btn-interactive">
              Dashboard
            </button>
            <button onClick={logout} className="text-slate-400 hover:text-red-600 transition btn-interactive" title={t.nav.logout}>
              <LogOut size={20} />
            </button>
          </div>
        </div>

        {/* SIDEBAR */}
        <div className="col-span-1 lg:col-span-3 glass-panel p-6 flex flex-col items-center text-center h-auto">
          <div className="relative mb-6">
            <div className="w-24 h-24 rounded-full border-2 border-blue-200 dark:border-blue-900 p-1 bg-white dark:bg-slate-800 flex items-center justify-center overflow-hidden shadow-lg">
              {user?.avatar_image?.startsWith('http') ? (
                <img src={user.avatar_image} alt="Avatar" className="rounded-full w-full h-full object-cover" />
              ) : currentAvatar ? (
                <img src={currentAvatar.src} alt="Avatar" className="rounded-full w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-3xl font-bold text-blue-600 dark:text-blue-400 rounded-full">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
              )}
            </div>
            <div className="absolute bottom-1 right-1 w-6 h-6 bg-white dark:bg-slate-700 rounded-full flex items-center justify-center shadow border border-blue-100 dark:border-blue-900">
              <Activity size={14} className="text-green-500" />
            </div>
          </div>
          <h3 
            onClick={() => navigate('/profile')}
            className={`font-bold text-lg cursor-pointer hover:text-blue-500 transition-colors ${!user?.full_name ? 'text-slate-400 italic' : 'text-slate-900 dark:text-white'}`}
          >
            {user?.full_name || 'Profil à compléter'}
          </h3>
          <p className="text-xs tech-accent mb-8 font-bold tracking-wider uppercase">{user?.title || 'Candidat'}</p>
          <div className="w-full text-left space-y-4 flex-1">
            <div className="text-[10px] uppercase text-gray-400 dark:text-slate-500 tracking-widest font-bold border-b border-gray-100 dark:border-slate-800 pb-2">Stats Base de Données</div>
            <StatItem label="Vecteurs XP" value={stats.xp} colorClass="tech-accent" />
            <StatItem label="Compétences" value={stats.skills} colorClass="text-purple-600 dark:text-purple-400" />
            
            <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase">
                    <Cpu size={12} className="text-blue-500" /> Moteur WASM Actif
                </div>
            </div>
          </div>
        </div>

        {/* CENTER CONSOLE */}
        <div className="col-span-1 lg:col-span-6 flex flex-col gap-6 h-auto">
          <div className="glass-panel p-6 relative group">
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs text-slate-500 dark:text-slate-400 tracking-widest font-bold flex items-center gap-2">
                <Terminal size={12} /> {t.builder.input.label}
              </label>
              <button onClick={() => setInput(MOCK_JOB_OFFER)} className="text-[10px] text-blue-400 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 font-bold uppercase btn-interactive">
                {t.builder.input.testData}
              </button>
            </div>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="w-full bg-white dark:bg-slate-900/50 border border-gray-200 dark:border-slate-800 rounded-lg p-4 text-sm focus:border-blue-500 dark:focus:border-blue-400 outline-none h-32 font-mono text-slate-700 dark:text-slate-200 shadow-inner resize-none transition-colors"
              placeholder={t.builder.input.placeholder}
            ></textarea>
          </div>

          <button
            onClick={processJobOffer}
            disabled={isProcessing || !input}
            className={`w-full py-4 shadow-md transition-all font-bold tracking-widest uppercase rounded-lg text-sm flex items-center justify-center gap-3 btn-interactive btn-glow ${isProcessing || !input ? 'bg-gray-200 dark:bg-slate-800 text-gray-400 dark:text-slate-600' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          >
            {isProcessing ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
            {isProcessing ? t.builder.actions.processing : t.builder.actions.process}
          </button>

          <div className="flex-1 flex flex-col min-h-0">
            {(!results || isGenerating) ? (
              <TerminalLog logs={logs} />
            ) : (
              <div className="glass-panel p-6 flex-1 animate-fadeIn flex flex-col bg-white/60 dark:bg-slate-900/40 overflow-hidden">
                <div className="flex items-center justify-between mb-4 border-b border-gray-100 dark:border-slate-800 pb-2">
                  <span className="text-xs font-bold text-green-600 dark:text-green-400 flex items-center gap-2">
                    <CheckCircle size={14} /> ANALYSE TERMINÉE
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => startGeneration()}
                      disabled={isGenerating || latexSource}
                      className="text-xs bg-blue-600 text-white px-4 py-1.5 rounded-full font-bold hover:bg-blue-700 transition-all flex items-center gap-2 disabled:opacity-50 btn-interactive shadow-md"
                    >
                      {isGenerating ? <RefreshCw size={14} className="animate-spin" /> : <Zap size={14} />}
                      Générer le CV
                    </button>
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto no-scrollbar space-y-4">
                  
                  {latexSource && (
                      <SwiftLaTeXPreview 
                        latexSource={latexSource} 
                        photoUrl={user?.photo_cv}
                        onError={handleSwiftError}
                      />
                  )}

                  {!latexSource && (
                      <>
                        <div className="p-3 bg-blue-50/50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/30 rounded text-xs text-slate-600 dark:text-slate-300 leading-relaxed text-left">
                            <span className="font-bold text-blue-600 dark:text-blue-400 block mb-1">/// RÉSUMÉ STRATÉGIQUE</span>
                            {results.summary}
                        </div>

                        <div className="space-y-4 text-left">
                            <span className="font-bold text-blue-600 dark:text-blue-400 block text-xs">/// EXPÉRIENCES SÉLECTIONNÉES</span>
                            {editableExperiences.map((exp, idx) => (
                            <div key={idx} className="bg-white dark:bg-slate-800/50 border border-gray-100 dark:border-slate-800 p-3 rounded shadow-sm hover:border-blue-200 dark:hover:border-blue-800 transition-colors space-y-2 group/exp">
                                <div className="flex items-center gap-2">
                                <span className="text-blue-400 dark:text-blue-500 font-bold text-xs">{`0${idx + 1}`}</span>
                                {editingIndex === idx ? (
                                    <input
                                    type="text"
                                    value={exp.title}
                                    onChange={(e) => handleExperienceChange(idx, 'title', e.target.value)}
                                    className="flex-1 bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-800 rounded px-2 py-1 outline-none font-bold text-sm text-slate-800 dark:text-white"
                                    autoFocus
                                    />
                                ) : (
                                    <span className="flex-1 font-bold text-sm text-slate-800 dark:text-white">{exp.title}</span>
                                )}
                                
                                <button 
                                    onClick={() => setEditingIndex(editingIndex === idx ? null : idx)}
                                    className={`p-1.5 rounded-full transition-all ml-2 border ${editingIndex === idx ? 'bg-green-100 text-green-600 border-green-200' : 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-300'}`}
                                >
                                    {editingIndex === idx ? <Check size={14} /> : <Pencil size={14} />}
                                </button>
                                </div>

                                {editingIndex === idx ? (
                                <textarea
                                    value={exp.description}
                                    onChange={(e) => handleExperienceChange(idx, 'description', e.target.value)}
                                    className="w-full bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-800 rounded p-2 text-xs text-slate-600 dark:text-slate-300 min-h-[120px] resize-y outline-none focus:ring-1 ring-blue-400 font-mono"
                                />
                                ) : (
                                <div className="pl-1">
                                    <FormattedText text={exp.description} />
                                </div>
                                )}
                            </div>
                            ))}
                        </div>
                      </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT SIDEBAR */}
        <div className="col-span-1 lg:col-span-3 flex flex-col gap-6 h-auto">
          <div className="h-1/2"><ScoreWidget score={score} t={t} /></div>
          <div className="glass-panel p-6 h-1/2 flex flex-col justify-center items-center text-center bg-slate-50/50 dark:bg-slate-900/20 border-dashed relative">
            <Code size={32} className="text-slate-300 dark:text-slate-700 mb-3" />
            <h4 className="text-slate-500 dark:text-slate-400 font-bold text-sm">SwiftLaTeX WASM</h4>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 px-4 text-center">Compilateur PDF local intégré au navigateur.</p>
          </div>
        </div>

      </div>
    </div>
  );
}
