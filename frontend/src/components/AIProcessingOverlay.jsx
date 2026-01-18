import React from 'react';
import { Sparkles, Brain, Loader2, FileText } from 'lucide-react';

const AIProcessingOverlay = ({ isVisible }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="relative">
                {/* Pulsing circles */}
                <div className="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-20 blur-xl"></div>
                <div className="absolute inset-0 bg-purple-500 rounded-full animate-ping opacity-20 blur-xl delay-150"></div>
                
                {/* Main Card */}
                <div className="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center max-w-sm text-center relative z-10 border border-white/20">
                    <div className="relative mb-6">
                        <div className="w-20 h-20 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg animate-bounce-slow">
                            <Brain className="text-white w-10 h-10" />
                        </div>
                        <div className="absolute -bottom-2 -right-2 bg-white p-2 rounded-full shadow-md">
                            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                        </div>
                    </div>

                    <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
                        Analyse IA en cours
                    </h3>
                    
                    <p className="text-slate-500 text-sm mb-6">
                        Nous analysons votre CV pour extraire vos compétences et expériences avec précision.
                    </p>

                    <div className="flex gap-4 text-xs font-medium text-slate-400">
                        <div className="flex items-center gap-1">
                            <FileText size={14} className="text-blue-500" />
                            <span>Lecture PDF</span>
                        </div>
                        <div className="w-px h-4 bg-slate-200"></div>
                        <div className="flex items-center gap-1">
                            <Brain size={14} className="text-purple-500" />
                            <span>Extraction</span>
                        </div>
                        <div className="w-px h-4 bg-slate-200"></div>
                        <div className="flex items-center gap-1">
                            <Sparkles size={14} className="text-amber-500" />
                            <span>Structuration</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIProcessingOverlay;
