import React, { useState, useEffect } from 'react';
import { Terminal, Cpu, Database, CheckSquare, Loader2 } from 'lucide-react';

const AIProcessingOverlay = ({ isVisible }) => {
    const [logs, setLogs] = useState([]);
    const [progress, setProgress] = useState(0);

    // Simulation de logs style terminal
    useEffect(() => {
        if (!isVisible) {
            setLogs([]);
            setProgress(0);
            return;
        }

        const steps = [
            { msg: "Initializing Neural Uplink...", time: 500 },
            { msg: "Reading PDF binary stream...", time: 1500 },
            { msg: "Parsing text layer (OCR)...", time: 2500 },
            { msg: "Extracting entities via Llama-3...", time: 4500 },
            { msg: "Structuring data schema...", time: 6000 },
            { msg: "Finalizing profile injection...", time: 7000 },
        ];

        let timeouts = [];
        steps.forEach((step, index) => {
            const timeout = setTimeout(() => {
                setLogs(prev => [...prev, `> ${step.msg}`]);
                setProgress(((index + 1) / steps.length) * 100);
            }, step.time);
            timeouts.push(timeout);
        });

        return () => timeouts.forEach(clearTimeout);
    }, [isVisible]);

    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/95 font-mono text-slate-600 animate-in fade-in duration-200">
            {/* Background Grid Effect - Light version */}
            <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>

            <div className="relative w-full max-w-lg p-8 border border-blue-100 bg-white shadow-[0_20px_70px_rgba(59,130,246,0.1)] rounded-2xl backdrop-blur-md">
                
                {/* Header */}
                <div className="flex items-center gap-3 mb-6 border-b border-slate-100 pb-4">
                    <div className="p-2 bg-blue-50 rounded-lg">
                        <Terminal className="animate-pulse text-blue-600" size={20} />
                    </div>
                    <h3 className="text-lg font-bold tracking-tight uppercase text-slate-900">AI Core Processing</h3>
                </div>

                {/* Progress Bar High-Tech Style */}
                <div className="mb-8">
                    <div className="flex justify-between text-[10px] font-bold mb-2 text-blue-500 tracking-widest">
                        <span>ANALYSIS_PROTOCOL_V2</span>
                        <span>{Math.round(progress)}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-50">
                        <div 
                            className="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-purple-500 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>

                {/* Logs Area */}
                <div className="space-y-2 h-40 overflow-hidden font-medium text-sm">
                    {logs.map((log, index) => (
                        <div key={index} className="opacity-90 animate-in slide-in-from-left-2 duration-300 flex items-center gap-2">
                            <span className="text-blue-400 text-xs font-bold">»</span>
                            <span className="text-slate-600 italic">{log.replace('> ', '')}</span>
                        </div>
                    ))}
                    <div className="flex items-center gap-2 mt-2 text-blue-500 animate-pulse">
                        <span className="w-1.5 h-4 bg-blue-500 block"></span>
                    </div>
                </div>

                {/* Footer Icons */}
                <div className="mt-6 pt-4 border-t border-slate-100 flex justify-around text-slate-300">
                    <Cpu size={20} className={progress > 30 ? "text-blue-500 animate-bounce" : ""} />
                    <Database size={20} className={progress > 60 ? "text-purple-500 animate-pulse" : ""} />
                    <CheckSquare size={20} className={progress > 90 ? "text-cyan-500" : ""} />
                </div>
            </div>
        </div>
    );
};

export default AIProcessingOverlay;