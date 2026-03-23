import React, { useState, useEffect, useRef, useCallback } from 'react';
import { RefreshCw, Download, FileText, AlertCircle, CheckCircle } from 'lucide-react';

// Fallback Enum in case global EngineStatus is not yet defined
const LOCAL_ENGINE_STATUS = {
    Init: 1,
    Ready: 2,
    Busy: 3,
    Error: 4
};

/**
 * SwiftLaTeXPreview - A component that compiles LaTeX in the browser using WASM.
 * @param {string} latexSource - The LaTeX source code.
 * @param {string} photoUrl - Optional URL of the photo to include in the CV.
 * @param {function} onComplete - Callback when PDF is ready.
 * @param {function} onError - Callback when compilation fails or page count > 1.
 */
const SwiftLaTeXPreview = ({ latexSource, photoUrl, onComplete, onError }) => {
    const [status, setStatus] = useState('idle'); // idle, loading-engine, loading-assets, compiling, success, error
    const [error, setError] = useState(null);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [log, setLog] = useState('');
    const engineRef = useRef(null);

    useEffect(() => {
        return () => {
            if (engineRef.current && typeof engineRef.current.closeWorker === 'function') {
                try {
                    engineRef.current.closeWorker();
                } catch (e) {
                    console.warn("Error closing worker:", e);
                }
            }
        };
    }, []);

    const loadEngine = () => {
        return new Promise((resolve, reject) => {
            // Check if already loaded in window
            if (window.PdfTeXEngine) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            // Adding a timestamp to bypass potential cache during development
            script.src = `/swiftlatex/PdfTeXEngine.js?v=${Date.now()}`;
            script.async = true;
            script.onload = () => {
                if (window.PdfTeXEngine) {
                    // Ensure EngineStatus is also available
                    if (!window.EngineStatus) {
                        window.EngineStatus = LOCAL_ENGINE_STATUS;
                    }
                    resolve();
                } else {
                    reject(new Error("PdfTeXEngine could not be initialized."));
                }
            };
            script.onerror = () => reject(new Error("Failed to load rendering engine script."));
            document.body.appendChild(script);
        });
    };

    const fetchAssetAsUint8Array = async (url) => {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Could not fetch asset: ${url}`);
        const arrayBuffer = await response.arrayBuffer();
        return new Uint8Array(arrayBuffer);
    };

    const compile = useCallback(async () => {
        if (!latexSource) return;
        
        setStatus('loading-engine');
        setError(null);
        try {
            await loadEngine();
            
            if (!engineRef.current) {
                const engine = new window.PdfTeXEngine();
                // Ensure the engine knows where to fetch formats and packages
                if (typeof engine.setTexliveEndpoint === 'function') {
                    engine.setTexliveEndpoint("https://texlive2.swiftlatex.com/");
                }
                await engine.loadEngine();
                engineRef.current = engine;
            }

            const engine = engineRef.current;

            // Handle Photo if present
            if (photoUrl) {
                setStatus('loading-assets');
                try {
                    const photoData = await fetchAssetAsUint8Array(photoUrl);
                    // Use a standard filename that templates will expect
                    engine.writeMemFSFile("photo_cv.png", photoData);
                } catch (assetErr) {
                    console.warn("Could not load CV photo, continuing without it.", assetErr);
                }
            }
            
            setStatus('compiling');
            
            // Clean/Prepare source: ensure image paths point to our virtual file
            let processedSource = latexSource;
            // Replace any absolute or relative paths to avatars with the virtual file name
            processedSource = processedSource.replace(/\{.*?(?:avatar|photo|img).*?\}/g, (match) => {
                if (match.includes('.png') || match.includes('.jpg') || match.includes('.jpeg')) {
                    return "{photo_cv.png}";
                }
                return match;
            });
            
            engine.writeMemFSFile("main.tex", processedSource);
            engine.setEngineMainFile("main.tex");

            const result = await engine.compileLaTeX();
            setLog(result.log || '');

            if (result.status === 0 && result.pdf) {
                // Check page count in logs
                const pageMatch = result.log.match(/Output written on .*? \((\d+) page/);
                const pageCount = pageMatch ? parseInt(pageMatch[1]) : 1;

                if (pageCount > 1) {
                    const errMsg = `CV trop long : ${pageCount} pages. Réduction en cours...`;
                    setError(errMsg);
                    setStatus('error');
                    if (onError) onError({ type: 'page_count', count: pageCount });
                    return;
                }

                const blob = new Blob([result.pdf], { type: 'application/pdf' });
                const url = URL.createObjectURL(blob);
                setPdfUrl(url);
                setStatus('success');
                if (onComplete) onComplete(url);
            } else {
                throw new Error("La compilation LaTeX a échoué. Vérifiez la syntaxe.");
            }
        } catch (err) {
            console.error("SwiftLaTeX Error:", err);
            setError(err.message);
            setStatus('error');
            if (onError) onError({ type: 'compilation', message: err.message });
        }
    }, [latexSource, photoUrl, onComplete, onError]);

    // Auto-compile when source changes and engine is ready
    useEffect(() => {
        if (latexSource && status === 'idle') {
            compile();
        }
    }, [latexSource, status, compile]);

    return (
        <div className="flex flex-col gap-4 p-4 bg-white dark:bg-slate-900 rounded-xl border dark:border-slate-800 shadow-lg animate-fadeIn">
            <div className="flex items-center justify-between border-b dark:border-slate-800 pb-2">
                <h3 className="font-bold text-slate-800 dark:text-white flex items-center gap-2">
                    <FileText size={18} className="text-blue-500" /> 
                    Moteur de Rendu reZume (Local)
                </h3>
                <div className="flex gap-2">
                    {status === 'success' && (
                        <a 
                            href={pdfUrl} 
                            download="reZume_CV.pdf"
                            className="text-xs bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 font-bold flex items-center gap-2 transition-all shadow-sm"
                        >
                            <Download size={14} /> Télécharger PDF
                        </a>
                    )}
                    <button 
                        onClick={compile} 
                        disabled={status === 'loading-engine' || status === 'compiling' || status === 'loading-assets'}
                        className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 font-bold flex items-center gap-2 disabled:opacity-50 transition-all shadow-sm"
                    >
                        <RefreshCw size={14} className={status === 'compiling' ? 'animate-spin' : ''} />
                        {status === 'idle' ? 'Générer' : 'Actualiser'}
                    </button>
                </div>
            </div>

            {(status === 'loading-engine' || status === 'compiling' || status === 'loading-assets') && (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                    <RefreshCw size={32} className="animate-spin text-blue-500" />
                    <p className="text-sm font-bold text-slate-600 dark:text-slate-300">
                        {status === 'loading-engine' && 'Initialisation du moteur LaTeX...'}
                        {status === 'loading-assets' && 'Chargement de votre photo...'}
                        {status === 'compiling' && 'Compilation du PDF en cours...'}
                    </p>
                    <p className="text-[10px] text-slate-400 max-w-[250px] text-center">
                        La compilation s'effectue directement dans votre navigateur pour une confidentialité maximale.
                    </p>
                </div>
            )}

            {status === 'success' && pdfUrl && (
                <div className="w-full h-[650px] bg-slate-100 dark:bg-slate-800 rounded overflow-hidden relative border dark:border-slate-700">
                    <div className="absolute top-2 right-2 z-10">
                        <span className="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
                            <CheckCircle size={10} /> Rendu Local Terminé
                        </span>
                    </div>
                    <iframe src={`${pdfUrl}#toolbar=0&navpanes=0`} className="w-full h-full" title="reZume CV Preview"></iframe>
                </div>
            )}

            {status === 'error' && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-lg space-y-2">
                    <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-bold text-sm">
                        <AlertCircle size={16} /> Erreur de rendu
                    </div>
                    <p className="text-xs text-red-500 dark:text-red-300">{error}</p>
                    {log && (
                        <details className="mt-2">
                            <summary className="text-[10px] text-slate-500 cursor-pointer hover:underline">Voir les logs techniques</summary>
                            <pre className="mt-2 p-2 bg-slate-900 text-slate-300 text-[10px] overflow-x-auto rounded max-h-40 font-mono">
                                {log}
                            </pre>
                        </details>
                    )}
                </div>
            )}
        </div>
    );
};

export default SwiftLaTeXPreview;
