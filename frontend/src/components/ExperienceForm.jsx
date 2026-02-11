import React, { useState } from 'react';
import { Sparkles, Loader2, Bold, Italic, List, RotateCcw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function ExperienceForm({ onSave, onCancel, initialData, t }) {
    const { token } = useAuth();
    const { addToast } = useToast();
    const [formData, setFormData] = useState(initialData || {
        title: '',
        company: '',
        description: '',
        start_date: '',
        end_date: ''
    });
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [selectedTone, setSelectedTone] = useState("standard");
    const [previousDescription, setPreviousDescription] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    const insertFormat = (format) => {
        const textarea = document.getElementById(`desc-${formData.id || 'new'}`);
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = formData.description || '';
        const before = text.substring(0, start);
        const selected = text.substring(start, end);
        const after = text.substring(end);

        let newText = text;
        
        if (format === 'bold') newText = `${before}**${selected || 'gras'}**${after}`;
        if (format === 'italic') newText = `${before}_${selected || 'italique'}_${after}`;
        if (format === 'list') newText = `${before}\n- ${selected || 'élément'}${after}`;

        setFormData({ ...formData, description: newText });
        setTimeout(() => textarea.focus(), 0);
    };

    const handleUndo = () => {
        if (previousDescription !== null) {
            setFormData(prev => ({ ...prev, description: previousDescription }));
            setPreviousDescription(null);
            addToast("Modification annulée.", "info");
        }
    };

    const handleOptimize = async () => {
        if (!formData.description || formData.description.length < 10) {
            addToast("Description trop courte pour être optimisée.", "info");
            return;
        }

        // Save current state before optimizing
        setPreviousDescription(formData.description);
        setIsOptimizing(true);
        
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/optimize-description`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ text: formData.description, tone: selectedTone })
            });

            if (res.ok) {
                const data = await res.json();
                setFormData(prev => ({ ...prev, description: data.optimized_text }));
                addToast("Description améliorée avec succès !", "success");
            } else {
                addToast("Erreur lors de l'optimisation.", "error");
            }
        } catch (error) {
            console.error(error);
            addToast("Erreur réseau.", "error");
        } finally {
            setIsOptimizing(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 dark:bg-slate-800 p-4 rounded-lg border border-gray-200 dark:border-slate-700">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.title}</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.company}</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.company || ''} onChange={e => setFormData({ ...formData, company: e.target.value })}
                    />
                </div>
            </div>

            <div>
                <div className="flex justify-between items-end mb-2">
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.desc}</label>
                    
                    <div className="flex items-center gap-2">
                        {/* Undo Button - Only visible if there is a previous state */}
                        {previousDescription && (
                            <button 
                                type="button" 
                                onClick={handleUndo} 
                                className="p-1 hover:bg-red-100 rounded text-red-500 transition-colors mr-2"
                                title="Annuler la modification IA"
                            >
                                <RotateCcw size={14} />
                            </button>
                        )}

                        {/* Formatting Toolbar */}
                        <div className="flex gap-1 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded p-1 mr-2">
                            <button type="button" onClick={() => insertFormat('bold')} className="p-1 hover:bg-gray-100 dark:hover:bg-slate-600 rounded text-slate-600 dark:text-slate-300" title="Gras"><Bold size={14}/></button>
                            <button type="button" onClick={() => insertFormat('italic')} className="p-1 hover:bg-gray-100 dark:hover:bg-slate-600 rounded text-slate-600 dark:text-slate-300" title="Italique"><Italic size={14}/></button>
                            <button type="button" onClick={() => insertFormat('list')} className="p-1 hover:bg-gray-100 dark:hover:bg-slate-600 rounded text-slate-600 dark:text-slate-300" title="Liste"><List size={14}/></button>
                        </div>

                        {/* Tone Selector */}
                        <select 
                            value={selectedTone} 
                            onChange={(e) => setSelectedTone(e.target.value)}
                            className="text-xs border border-purple-200 dark:border-purple-700 rounded px-2 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-200 outline-none focus:ring-1 focus:ring-purple-300"
                        >
                            <option value="standard">Standard</option>
                            <option value="dynamic">Dynamique</option>
                            <option value="formal">Formel</option>
                            <option value="explanatory">Explicatif</option>
                        </select>

                        <button
                            type="button"
                            onClick={handleOptimize}
                            disabled={isOptimizing}
                            className="text-xs flex items-center gap-1 text-white bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded-md transition-colors disabled:opacity-50 font-bold shadow-sm"
                        >
                            {isOptimizing ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                            {isOptimizing ? "..." : "Améliorer"}
                        </button>
                    </div>
                </div>
                <textarea
                    id={`desc-${formData.id || 'new'}`}
                    className="w-full p-3 border rounded-lg text-sm h-32 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900 outline-none transition-all font-sans leading-relaxed bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                    placeholder={t.descPlaceholder}
                    value={formData.description || ''} onChange={e => setFormData({ ...formData, description: e.target.value })}
                ></textarea>
                <p className="text-[10px] text-gray-400 mt-1 text-right">Markdown supporté: **gras**, _italique_</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.start}</label>
                    <input
                        type="text" placeholder="ex: Jan 2022"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.start_date || ''} onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.end}</label>
                    <input
                        type="text" placeholder="ex: Présent ou Déc 2023"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.end_date || ''} onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={onCancel} className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white font-medium">{t.cancel}</button>
                <button type="submit" className="px-4 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 font-bold shadow-sm">{t.save}</button>
            </div>
        </form>
    );
}
