import React, { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
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

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    const handleOptimize = async () => {
        if (!formData.description || formData.description.length < 10) {
            addToast("Description trop courte pour être optimisée.", "info");
            return;
        }

        setIsOptimizing(true);
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/analysis/optimize-description`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ text: formData.description })
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
        <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase">{t.title}</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded text-sm"
                        value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase">{t.company}</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded text-sm"
                        value={formData.company || ''} onChange={e => setFormData({ ...formData, company: e.target.value })}
                    />
                </div>
            </div>

            <div>
                <div className="flex justify-between items-end mb-1">
                    <label className="block text-xs font-bold text-gray-500 uppercase">{t.desc}</label>
                    <button
                        type="button"
                        onClick={handleOptimize}
                        disabled={isOptimizing}
                        className="text-xs flex items-center gap-1 text-purple-600 hover:text-purple-800 bg-purple-50 px-2 py-1 rounded-md transition-colors disabled:opacity-50"
                    >
                        {isOptimizing ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                        {isOptimizing ? "Optimisation..." : "Améliorer avec l'IA"}
                    </button>
                </div>
                <textarea
                    className="w-full p-2 border rounded text-sm h-32 focus:ring-2 focus:ring-purple-100 outline-none transition-all"
                    placeholder={t.descPlaceholder}
                    value={formData.description || ''} onChange={e => setFormData({ ...formData, description: e.target.value })}
                ></textarea>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase">{t.start}</label>
                    <input
                        type="text" placeholder="ex: Jan 2022"
                        className="w-full p-2 border rounded text-sm"
                        value={formData.start_date || ''} onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase">{t.end}</label>
                    <input
                        type="text" placeholder="ex: Présent ou Déc 2023"
                        className="w-full p-2 border rounded text-sm"
                        value={formData.end_date || ''} onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={onCancel} className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 font-medium">{t.cancel}</button>
                <button type="submit" className="px-4 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 font-bold shadow-sm">{t.save}</button>
            </div>
        </form>
    );
}