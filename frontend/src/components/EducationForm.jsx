import React, { useState } from 'react';

export default function EducationForm({ onSave, onCancel, initialData, t }) {
    const [formData, setFormData] = useState(initialData || {
        institution: '',
        degree: '',
        start_date: '',
        end_date: '',
        description: '',
        mention: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 dark:bg-slate-800 p-4 rounded-lg border border-gray-200 dark:border-slate-700">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.degree} <span className="text-red-500">*</span></label>
                    <input
                        type="text" required
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        placeholder={t.degreePlaceholder}
                        value={formData.degree} onChange={e => setFormData({ ...formData, degree: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.school} <span className="text-red-500">*</span></label>
                    <input
                        type="text" required
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        placeholder={t.schoolPlaceholder}
                        value={formData.institution} onChange={e => setFormData({ ...formData, institution: e.target.value })}
                    />
                </div>
            </div>

             <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.mention}</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        placeholder={t.mentionPlaceholder}
                        value={formData.mention || ''} onChange={e => setFormData({ ...formData, mention: e.target.value })}
                    />
                </div>
                 <div>
                     {/* Placeholder for alignment or extra field */}
                 </div>
            </div>

            <div>
                <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.desc}</label>
                <textarea
                    className="w-full p-2 border rounded text-sm h-20 bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                    placeholder={t.descPlaceholder}
                    value={formData.description || ''} onChange={e => setFormData({ ...formData, description: e.target.value })}
                ></textarea>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.start}</label>
                    <input
                        type="text" placeholder="ex: 2020"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.start_date} onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">{t.end}</label>
                    <input
                        type="text" placeholder="ex: 2022"
                        className="w-full p-2 border rounded text-sm bg-white dark:bg-slate-900 dark:border-slate-600 dark:text-white"
                        value={formData.end_date || ''} onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2">
                <button type="button" onClick={onCancel} className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">{t.cancel}</button>
                <button type="submit" className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 font-bold">{t.save}</button>
            </div>
        </form>
    );
}