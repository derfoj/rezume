import React, { useState, useEffect, useRef } from 'react';
import { 
  Zap, 
  CheckCircle, 
  Terminal, 
  Download,
  Copy,
  RefreshCw,
  Cpu,
  Database,
  Code,
  Activity,
  AlertCircle
} from 'lucide-react';

// --- Styles spécifiques pour le mode White Lab ---
const GlobalStyles = () => (
  <style>{`
    .bg-white-lab {
      background-color: #ffffff;
      background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
      background-size: 20px 20px;
    }
    .glass-panel {
      background: rgba(255, 255, 255, 0.7);
      backdrop-filter: blur(10px);
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .tech-accent { color: #2563eb; }
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
  { id: 1, text: "Initializing Orchestrator...", type: 'success' },
  { id: 2, text: "System ready. Waiting for input stream...", type: 'info' }
];

const TerminalLog = ({ logs }) => {
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-panel p-4 h-48 overflow-hidden relative flex flex-col shadow-inner bg-white/50">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-30"></div>
      <div className="text-[10px] text-slate-400 uppercase tracking-widest font-bold mb-2 border-b border-slate-100 pb-1">
        System Logs
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto font-mono text-xs space-y-1.5 no-scrollbar">
        {logs.map((log) => (
          <p key={log.id} className="animate-fadeIn">
            <span className="text-slate-400 mr-2">{'>'}</span>
            <span className={`font-bold ${
              log.type === 'success' ? 'text-green-600' :
              log.type === 'process' ? 'text-purple-600' :
              log.type === 'error' ? 'text-red-500' :
              log.type === 'wait' ? 'text-blue-600 animate-pulse' :
              'text-slate-500'
            }`}>
              {log.text}
            </span>
          </p>
        ))}
      </div>
    </div>
  );
};

const ScoreWidget = ({ score }) => {
  // Defensive clamping: ensure score is always within 0-100 range.
  const sanitizedScore = Math.max(0, Math.min(100, score || 0));
  
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (sanitizedScore / 100) * circumference;

  return (
    <div className="glass-panel p-6 flex flex-col items-center justify-center h-full relative overflow-hidden">
      <div className="relative w-40 h-40 flex items-center justify-center mb-4 z-10">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="80" cy="80" r={radius} stroke="#e2e8f0" strokeWidth="10" fill="transparent" />
          <circle 
            cx="80" cy="80" r={radius} stroke="#2563eb" strokeWidth="10" fill="transparent" 
            strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round"
            className="animate-dash"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-3xl font-bold text-slate-800">{sanitizedScore}%</span>
        </div>
      </div>
      <div className="text-center z-10">
        <h4 className="text-blue-600 font-bold uppercase tracking-wider text-sm">Colineairty Match</h4>
        <p className="text-xs text-gray-500 mt-1">Vector distance analysis.</p>
      </div>
    </div>
  );
};

const StatItem = ({ label, value, colorClass }) => (
  <div className="flex justify-between items-center bg-white/80 border border-gray-100 p-3 rounded-lg shadow-sm w-full">
    <span className="text-xs text-slate-500 font-medium">{label}</span>
    <span className={`${colorClass} font-bold font-mono`}>{value}</span>
  </div>
);

export default function CVBuilderApp() {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false); // State for download button
  const [score, setScore] = useState(0);
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [results, setResults] = useState(null);
  const [backendStatus, setBackendStatus] = useState('offline');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/');
        if (res.ok) setBackendStatus('online');
      } catch (e) {
        setBackendStatus('offline');
      }
    };
    checkBackend();
  }, []);

  const addLog = (text, type = 'process') => {
    setLogs(prev => [...prev, { id: Date.now(), text, type }]);
  };

  const processJobOffer = async () => {
    if (!input.trim()) return;
    setIsProcessing(true);
    setResults(null);
    setScore(0);
    setLogs([]);
    
    addLog("Initializing Generation sequence...", 'info');
    addLog("Sending input stream to Python Backend...", 'process');

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: input }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || response.statusText;
        throw new Error(detail);
      }
      
      const data = await response.json();

      addLog("Match found in Knowledge Base.", 'success');
      addLog(`Optimization complete. Score: ${data.score}%`, 'success');
      setScore(data.score);
      // Store the entire data object to keep raw_matches
      setResults(data);

    } catch (error) {
      console.error(error);
      addLog(`ERREUR: ${error.message}`, 'error');
      addLog("L'opération a été interrompue.", 'info');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!results || !results.raw_matches) return;
    setIsDownloading(true);
    addLog("Requesting PDF generation with original template...", 'process');

    try {
      const response = await fetch('http://localhost:8000/api/generate-cv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Send only the raw_matches needed for the template
        body: JSON.stringify({ experiences: results.raw_matches }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || `HTTP error ${response.status}`;
        throw new Error(`PDF Generation Failed: ${detail}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "reZume_CV_Optimized.pdf";
      document.body.appendChild(a);
      a.click();
      
      addLog("PDF Download initiated.", 'success');
      
      // Cleanup
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error(error);
      addLog(`${error.message}`, 'error');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="bg-white-lab min-h-screen flex flex-col p-4 md:p-8 overflow-hidden text-slate-700">
      <GlobalStyles />
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
        
        {/* HEADER */}
        <div className="col-span-1 lg:col-span-12 flex justify-between items-end border-b border-gray-200 pb-4 mb-2">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tighter">reZume</h1>
            <p className="text-xs tech-accent mt-1 tracking-widest font-bold">/// SYSTEM ONLINE /// WHITE MODE</p>
          </div>
          <div className={`flex items-center space-x-2 bg-white px-3 py-1.5 rounded-full border border-gray-100 shadow-sm ${backendStatus === 'online' ? 'border-green-200' : 'border-red-200'}`}>
            <div className={`w-2 h-2 rounded-full animate-pulse ${backendStatus === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-xs font-bold tracking-wider ${backendStatus === 'online' ? 'text-green-600' : 'text-red-600'}`}>
                {backendStatus === 'online' ? 'BACKEND CONNECTED' : 'BACKEND OFFLINE'}
            </span>
          </div>
        </div>

        {/* SIDEBAR */}
        <div className="col-span-1 lg:col-span-3 glass-panel p-6 flex flex-col items-center text-center h-auto">
          <div className="relative mb-6">
            <div className="w-24 h-24 rounded-full border-2 border-blue-200 p-1 bg-white">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" className="rounded-full" />
            </div>
            <div className="absolute bottom-1 right-1 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow border border-blue-100">
                <Activity size={14} className="text-green-500" />
            </div>
          </div>
          <h3 className="text-slate-900 font-bold text-lg">Paul Mouyebissi </h3>
          <p className="text-xs tech-accent mb-8 font-bold tracking-wider">Intelligence Artificielle & Data Science </p>
          <div className="w-full text-left space-y-4 flex-1">
            <div className="text-[10px] uppercase text-gray-400 tracking-widest font-bold border-b border-gray-100 pb-2">Database Stats</div>
            <StatItem label="XP Vectors" value="12" colorClass="tech-accent" />
            <StatItem label="Skills" value="48" colorClass="text-purple-600" />
          </div>
        </div>

        {/* CENTER CONSOLE */}
        <div className="col-span-1 lg:col-span-6 flex flex-col gap-6 h-auto">
          <div className="glass-panel p-6 relative group">
             <div className="flex justify-between items-center mb-2">
                <label className="text-xs text-slate-500 tracking-widest font-bold flex items-center gap-2">
                   <Terminal size={12} /> TARGET INPUT STREAM
                </label>
                <button onClick={() => setInput(MOCK_JOB_OFFER)} className="text-[10px] text-blue-400 hover:text-blue-600 font-bold uppercase">
                    Insert Test Data
                </button>
             </div>
            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-lg p-4 text-sm focus:border-blue-500 outline-none h-32 font-mono text-slate-700 shadow-inner resize-none"
              placeholder="Paste raw job data here..."
            ></textarea>
          </div>

          <button 
            onClick={processJobOffer}
            disabled={isProcessing || !input}
            className={`w-full py-4 shadow-md transition-all font-bold tracking-widest uppercase rounded-lg text-sm flex items-center justify-center gap-3 ${isProcessing || !input ? 'bg-gray-200 text-gray-400' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          >
             {isProcessing ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
             {isProcessing ? 'Processing...' : 'Initialize Generation Sequence'}
          </button>

          <div className="flex-1 flex flex-col min-h-0">
             {!results ? (
                 <TerminalLog logs={logs} />
             ) : (
                 <div className="glass-panel p-6 flex-1 animate-fadeIn flex flex-col bg-white/60 overflow-hidden">
                    <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-2">
                        <span className="text-xs font-bold text-green-600 flex items-center gap-2">
                            <CheckCircle size={14} /> OPTIMIZATION COMPLETE
                        </span>
                        <button
                            onClick={handleDownload}
                            disabled={isDownloading}
                            className="text-xs bg-white border border-gray-200 text-blue-600 px-3 py-1 rounded-full font-bold hover:bg-blue-50 transition-all flex items-center gap-2 disabled:opacity-50"
                        >
                            {isDownloading ? <RefreshCw size={14} className="animate-spin" /> : <Download size={14} />}
                            {isDownloading ? 'Génération...' : 'Download CV'}
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto no-scrollbar space-y-4">
                        <div className="p-3 bg-blue-50/50 border border-blue-100 rounded text-xs text-slate-600 leading-relaxed">
                            <span className="font-bold text-blue-600 block mb-1">/// MATCH SUMMARY</span>
                            {results.summary}
                        </div>

                        {results.skills && results.skills.length > 0 && (
                            <div className="p-3 bg-purple-50/50 border border-purple-100 rounded">
                                <span className="font-bold text-purple-600 block mb-2">/// SKILLS DETECTED</span>
                                <div className="flex flex-wrap gap-2">
                                    {results.skills.map((skill, idx) => (
                                        <span key={idx} className="bg-white text-purple-700 text-xs font-bold px-2.5 py-1 rounded-full border border-purple-200 shadow-sm">
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        <ul className="space-y-2">
                            {results.bulletPoints.map((point, idx) => (
                                <li key={idx} className="flex items-start gap-3 text-sm text-slate-700 bg-white border border-gray-100 p-3 rounded shadow-sm hover:border-blue-200">
                                    <span className="text-blue-400 font-bold mt-0.5 text-xs">{`0${idx + 1}`}</span>
                                    <span className="font-medium text-xs md:text-sm">{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                 </div>
             )}
          </div>
        </div>

        {/* RIGHT SIDEBAR */}
        <div className="col-span-1 lg:col-span-3 flex flex-col gap-6 h-auto">
           <div className="h-1/2"><ScoreWidget score={score} /></div>
           <div className="glass-panel p-6 h-1/2 flex flex-col justify-center items-center text-center bg-slate-50/50 border-dashed relative">
              {backendStatus === 'error' && <div className="text-red-500 mb-2"><AlertCircle /></div>}
              <Code size={32} className="text-slate-300 mb-3" />
              <h4 className="text-slate-500 font-bold text-sm">Python Backend</h4>
              <p className="text-[10px] text-slate-400 mt-1 px-4">API Endpoint: <code className="bg-gray-100 px-1 rounded text-blue-500">POST /api/analyze</code></p>
           </div>
        </div>

      </div>
    </div>
  );
}