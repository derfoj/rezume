import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2, Pencil, Briefcase, Code, X, User, BookOpen, Languages as LanguagesIcon, Save, ExternalLink, FileUp, Loader2 } from 'lucide-react';
import ExperienceForm from '../components/ExperienceForm';
import EducationForm from '../components/EducationForm';
import AIProcessingOverlay from '../components/AIProcessingOverlay';
import { translations } from '../config/translations';

export default function ProfileEditor() {
    const { token, user } = useAuth();
    const { addToast } = useToast();
    const navigate = useNavigate();
    const fileInputRef = useRef(null);
    
    const lang = user?.language || 'fr';
    const t = translations[lang];

    // Data States
    const [userProfile, setUserProfile] = useState({
        full_name: '',
        title: '',
        summary: '',
        portfolio_url: '',
        linkedin_url: '',
        email: ''
    });
    const [experiences, setExperiences] = useState([]);
    const [education, setEducation] = useState([]);
    const [skills, setSkills] = useState([]);
    const [languages, setLanguages] = useState([]);

    // UI States
    const [showExpForm, setShowExpForm] = useState(false);
    const [editingExp, setEditingExp] = useState(null); 
    
    const [showEduForm, setShowEduForm] = useState(false);
    const [editingEdu, setEditingEdu] = useState(null); 

    const [newSkill, setNewSkill] = useState('');
    const [newLang, setNewLang] = useState({ name: '', level: 'Intermédiaire' });
    const [isSavingProfile, setIsSavingProfile] = useState(false);
    const [isImporting, setIsImporting] = useState(false);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (token) fetchData();
    }, [token]);

    const fetchData = async () => {
        try {
            const headers = { Authorization: `Bearer ${token}` };
            
            const [profileRes, expRes, eduRes, skillRes, langRes] = await Promise.all([
                fetch(`${API_URL}/api/profile/me`, { headers }),
                fetch(`${API_URL}/api/profile/experiences`, { headers }),
                fetch(`${API_URL}/api/profile/education`, { headers }),
                fetch(`${API_URL}/api/profile/skills`, { headers }),
                fetch(`${API_URL}/api/profile/languages`, { headers })
            ]);

            if (profileRes.ok) setUserProfile(await profileRes.json());
            if (expRes.ok) setExperiences(await expRes.json());
            if (eduRes.ok) setEducation(await eduRes.json());
            if (skillRes.ok) setSkills(await skillRes.json());
            if (langRes.ok) setLanguages(await langRes.json());

        } catch (error) {
            console.error("Error fetching profile data", error);
        }
    };

    // --- Profile General Info Handlers ---
    const handleProfileChange = (e) => {
        setUserProfile({ ...userProfile, [e.target.name]: e.target.value });
    };

    const handleSaveProfile = async () => {
        setIsSavingProfile(true);
        try {
            const res = await fetch(`${API_URL}/api/profile/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(userProfile)
            });
            if (res.ok) {
                addToast(t.profile.actions.save + " !", 'success');
            }
        } catch (error) {
            console.error("Failed to save profile", error);
            addToast("Erreur sauvegarde profil", 'error');
        } finally {
            setIsSavingProfile(false);
        }
    };

    // --- Experience Handlers ---
    const handleEditExperience = (exp) => {
        setEditingExp(exp);
        setShowExpForm(true);
    };

    const handleSaveExperience = async (data) => {
        try {
            const method = editingExp && !String(editingExp.id).startsWith('temp') ? 'PUT' : 'POST';
            const url = method === 'PUT'
                ? `${API_URL}/api/profile/experiences/${editingExp.id}`
                : `${API_URL}/api/profile/experiences`;

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                setShowExpForm(false);
                setEditingExp(null);
                fetchData();
            }
        } catch (error) { console.error(error); }
    };

    const handleCancelExperience = () => {
        setShowExpForm(false);
        setEditingExp(null);
    }

    const handleDeleteExperience = async (id) => {
        if (String(id).startsWith('temp')) {
            setExperiences(experiences.filter(e => e.id !== id));
            return;
        }
        if (!confirm("Supprimer cette expérience ?")) return;
        await fetch(`${API_URL}/api/profile/experiences/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` }
        });
        fetchData();
    };

    // --- Education Handlers ---
    const handleEditEducation = (edu) => {
        setEditingEdu(edu);
        setShowEduForm(true);
    };

    const handleSaveEducation = async (data) => {
        try {
            const method = editingEdu && !String(editingEdu.id).startsWith('temp') ? 'PUT' : 'POST';
            const url = method === 'PUT'
                ? `${API_URL}/api/profile/education/${editingEdu.id}`
                : `${API_URL}/api/profile/education`;

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                setShowEduForm(false);
                setEditingEdu(null);
                fetchData();
            }
        } catch (error) { console.error(error); }
    };

    const handleCancelEducation = () => {
        setShowEduForm(false);
        setEditingEdu(null);
    }

    const handleDeleteEducation = async (id) => {
        if (String(id).startsWith('temp')) {
            setEducation(education.filter(e => e.id !== id));
            return;
        }
        if (!confirm("Supprimer cette formation ?")) return;
        await fetch(`${API_URL}/api/profile/education/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` }
        });
        fetchData();
    };

    // --- Skills Handlers ---
    const handleAddSkill = async (e) => {
        e.preventDefault();
        if (!newSkill.trim()) return;
        await fetch(`${API_URL}/api/profile/skills`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ name: newSkill, category: 'Hard Skills' })
        });
        setNewSkill('');
        fetchData();
    };

    const handleDeleteSkill = async (id) => {
        if (String(id).startsWith('temp')) {
            setSkills(skills.filter(s => s.id !== id));
            return;
        }
        await fetch(`${API_URL}/api/profile/skills/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` }
        });
        fetchData();
    };

    // --- Languages Handlers ---
    const handleAddLanguage = async (e) => {
        e.preventDefault();
        if (!newLang.name.trim()) return;
        await fetch(`${API_URL}/api/profile/languages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify(newLang)
        });
        setNewLang({ name: '', level: 'Intermédiaire' });
        fetchData();
    };

    const handleDeleteLanguage = async (id) => {
        if (String(id).startsWith('temp')) {
            setLanguages(languages.filter(l => l.id !== id));
            return;
        }
        await fetch(`${API_URL}/api/profile/languages/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` }
        });
        fetchData();
    };

    const handleImportCV = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsImporting(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_URL}/api/profile/upload-cv`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
                body: formData
            });
            if (res.ok) {
                const result = await res.json();
                const extracted = result.data;

                // 1. Update Profile General Info (UI only)
                setUserProfile(prev => ({
                    ...prev,
                    full_name: extracted.full_name || prev.full_name,
                    title: extracted.title || prev.title,
                    summary: extracted.summary || prev.summary,
                    linkedin_url: extracted.linkedin_url || prev.linkedin_url,
                    portfolio_url: extracted.portfolio_url || prev.portfolio_url,
                }));

                // 2. Update Experiences (UI only with temp IDs)
                setExperiences((extracted.experiences || []).map((exp, i) => ({ id: `temp-exp-${i}`, ...exp })));

                // 3. Update Education (UI only with temp IDs)
                setEducation((extracted.education || []).map((edu, i) => ({ id: `temp-edu-${i}`, ...edu })));

                // 4. Update Skills (UI only with temp IDs)
                const combinedSkills = [
                    ...(extracted.skills || []).map((s, i) => ({ id: `temp-h-${i}`, name: s, category: 'Hard Skills' })),
                    ...(extracted.soft_skills || []).map((s, i) => ({ id: `temp-s-${i}`, name: s, category: 'Soft Skills' }))
                ];
                setSkills(combinedSkills);

                // 5. Update Languages (UI only with temp IDs)
                setLanguages((extracted.languages || []).map((l, i) => ({ id: `temp-l-${i}`, ...l })));

                addToast("CV analysé ! Vérifiez et enregistrez les sections souhaitées.", 'success');
            } else {
                const err = await res.json();
                addToast(err.detail || "Échec de l'importation", 'error');
            }
        } catch (error) {
            console.error("Import error:", error);
            addToast("Erreur réseau", 'error');
        } finally {
            setIsImporting(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    // --- Helper to format dates ---
    const formatDateRange = (start, end) => {
        return [start, end].filter(Boolean).join(' - ');
    };

    return (
        <div className="min-h-screen bg-slate-50 p-8 text-slate-900 font-sans">
            <AIProcessingOverlay isVisible={isImporting} />
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">{t.profile.title}</h1>
                        <p className="text-slate-500 text-sm mt-1">{t.profile.subtitle}</p>
                    </div>
                    <div className="flex gap-3">
                        <input 
                            type="file" 
                            ref={fileInputRef} 
                            onChange={handleImportCV} 
                            accept=".pdf" 
                            className="hidden" 
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isImporting}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-bold text-sm hover:bg-blue-100 transition-colors disabled:opacity-50"
                        >
                            {isImporting ? <Loader2 className="animate-spin" size={18} /> : <FileUp size={18} />}
                            {isImporting ? t.profile.actions.importing : t.profile.actions.importCV}
                        </button>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="text-slate-600 font-bold hover:text-blue-600 transition-colors bg-slate-50 px-4 py-2 rounded-lg"
                        >
                            {t.profile.back}
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Left Column: General Info & Skills & Languages */}
                    <div className="space-y-8">
                        
                        {/* General Info Card */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                                <div className="p-2 bg-slate-100 rounded-lg text-slate-600"><User size={20} /></div>
                                {t.profile.sections.general}
                            </h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">{t.profile.fields.fullName} <span className="text-red-500">*</span></label>
                                    <input type="text" name="full_name" required value={userProfile.full_name || ''} onChange={handleProfileChange} className="w-full p-2 border rounded-lg text-sm bg-slate-50" />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">{t.profile.fields.currentTitle} <span className="text-red-500">*</span></label>
                                    <input type="text" name="title" required value={userProfile.title || ''} onChange={handleProfileChange} className="w-full p-2 border rounded-lg text-sm bg-slate-50" />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">{t.profile.fields.summary}</label>
                                    <textarea name="summary" rows="4" value={userProfile.summary || ''} onChange={handleProfileChange} className="w-full p-2 border rounded-lg text-sm bg-slate-50" placeholder={t.profile.fields.summaryPlaceholder}></textarea>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">{t.profile.fields.portfolio}</label>
                                    <div className="flex gap-2">
                                        <input type="text" name="portfolio_url" value={userProfile.portfolio_url || ''} onChange={handleProfileChange} className="w-full p-2 border rounded-lg text-sm bg-slate-50" />
                                        {userProfile.portfolio_url && <a href={userProfile.portfolio_url} target="_blank" rel="noreferrer" className="p-2 text-blue-600 hover:bg-blue-50 rounded"><ExternalLink size={18}/></a>}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">{t.profile.fields.linkedin}</label>
                                    <div className="flex gap-2">
                                        <input type="text" name="linkedin_url" value={userProfile.linkedin_url || ''} onChange={handleProfileChange} className="w-full p-2 border rounded-lg text-sm bg-slate-50" />
                                        {userProfile.linkedin_url && <a href={userProfile.linkedin_url} target="_blank" rel="noreferrer" className="p-2 text-blue-600 hover:bg-blue-50 rounded"><ExternalLink size={18}/></a>}
                                    </div>
                                </div>
                                <button onClick={handleSaveProfile} disabled={isSavingProfile} className="w-full py-2 bg-slate-900 text-white rounded-lg font-bold text-sm hover:bg-slate-800 transition flex justify-center items-center gap-2">
                                    <Save size={16} /> {isSavingProfile ? t.profile.actions.saving : t.profile.actions.save}
                                </button>
                            </div>
                        </div>

                        {/* Skills Card */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                                <div className="p-2 bg-purple-100 rounded-lg text-purple-600"><Code size={20} /></div>
                                {t.profile.sections.skills}
                            </h2>
                            <form onSubmit={handleAddSkill} className="flex gap-2 mb-4">
                                <input
                                    type="text" value={newSkill} onChange={e => setNewSkill(e.target.value)}
                                    placeholder={t.profile.fields.skillPlaceholder}
                                    className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50"
                                />
                                <button type="submit" className="bg-purple-600 text-white px-3 py-2 rounded-lg hover:bg-purple-700 transition"><Plus size={18} /></button>
                            </form>
                            <div className="flex flex-wrap gap-2">
                                {skills.map(skill => (
                                    <span key={skill.id} className="bg-white border border-slate-200 text-slate-700 px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-2 group hover:border-purple-200 hover:text-purple-700 transition-colors shadow-sm">
                                        {skill.name}
                                        <button onClick={() => handleDeleteSkill(skill.id)} className="text-slate-300 hover:text-red-500 transition-colors"><X size={14} /></button>
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Languages Card */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                                <div className="p-2 bg-green-100 rounded-lg text-green-600"><LanguagesIcon size={20} /></div>
                                {t.profile.sections.languages}
                            </h2>
                            <form onSubmit={handleAddLanguage} className="flex gap-2 mb-4">
                                <input
                                    type="text" value={newLang.name} onChange={e => setNewLang({...newLang, name: e.target.value})}
                                    placeholder={t.profile.fields.langName}
                                    className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 w-24"
                                />
                                <select 
                                    value={newLang.level} onChange={e => setNewLang({...newLang, level: e.target.value})}
                                    className="px-2 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50"
                                >
                                    <option value="Débutant">{t.profile.fields.levels.beginner}</option>
                                    <option value="Intermédiaire">{t.profile.fields.levels.intermediate}</option>
                                    <option value="Avancé">{t.profile.fields.levels.advanced}</option>
                                    <option value="Bilingue">{t.profile.fields.levels.fluent}</option>
                                    <option value="Natif">{t.profile.fields.levels.native}</option>
                                </select>
                                <button type="submit" className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition"><Plus size={18} /></button>
                            </form>
                            <div className="space-y-2">
                                {languages.map(lang => (
                                    <div key={lang.id} className="flex justify-between items-center bg-slate-50 px-3 py-2 rounded-lg border border-slate-100">
                                        <div>
                                            <span className="font-bold text-slate-700 text-sm">{lang.name}</span>
                                            <span className="text-xs text-slate-500 ml-2">({lang.level})</span>
                                        </div>
                                        <button onClick={() => handleDeleteLanguage(lang.id)} className="text-slate-300 hover:text-red-500 transition-colors"><X size={14} /></button>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>

                    {/* Right Column: Experiences & Education */}
                    <div className="lg:col-span-2 space-y-8">
                        
                        {/* Experiences */}
                        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                    <div className="p-2 bg-blue-100 rounded-lg text-blue-600"><Briefcase size={20} /></div>
                                    {t.profile.sections.experiences}
                                </h2>
                                <button onClick={() => { setEditingExp(null); setShowExpForm(true); }} className="flex items-center gap-2 text-xs bg-blue-600 text-white px-3 py-2 rounded-full font-bold hover:bg-blue-700 transition">
                                    <Plus size={14} /> {t.profile.actions.add}
                                </button>
                            </div>

                            {showExpForm && (
                                <div className="mb-8 p-6 bg-slate-50 rounded-xl border border-slate-200 animate-fade-in-down">
                                    <ExperienceForm 
                                        initialData={editingExp} 
                                        onSave={handleSaveExperience} 
                                        onCancel={handleCancelExperience} 
                                        t={t.forms.exp}
                                    />
                                </div>
                            )}

                            <div className="space-y-6">
                                {experiences.map(exp => (
                                    <div key={exp.id} className="group relative border-l-4 border-blue-500 pl-6 py-2 hover:bg-slate-50/50 rounded-r-lg transition-colors">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-bold text-lg text-slate-800">{exp.title}</h3>
                                                <p className="text-sm text-blue-600 font-semibold mb-2">{exp.company} • {formatDateRange(exp.start_date, exp.end_date)}</p>
                                            </div>
                                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition duration-200">
                                                <button onClick={() => handleEditExperience(exp)} className="text-slate-300 hover:text-blue-500">
                                                    <Pencil size={18} />
                                                </button>
                                                <button onClick={() => handleDeleteExperience(exp.id)} className="text-slate-300 hover:text-red-500">
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </div>
                                        <p className="text-slate-600 text-sm leading-relaxed whitespace-pre-line">{exp.description}</p>
                                    </div>
                                ))}
                                {experiences.length === 0 && !showExpForm && (
                                    <p className="text-center text-slate-400 py-4 italic">{t.profile.empty.experiences}</p>
                                )}
                            </div>
                        </div>

                        {/* Education */}
                        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                    <div className="p-2 bg-orange-100 rounded-lg text-orange-600"><BookOpen size={20} /></div>
                                    {t.profile.sections.education}
                                </h2>
                                <button onClick={() => { setEditingEdu(null); setShowEduForm(true); }} className="flex items-center gap-2 text-xs bg-orange-600 text-white px-3 py-2 rounded-full font-bold hover:bg-orange-700 transition">
                                    <Plus size={14} /> {t.profile.actions.add}
                                </button>
                            </div>

                            {showEduForm && (
                                <div className="mb-8 p-6 bg-slate-50 rounded-xl border border-slate-200 animate-fade-in-down">
                                    <EducationForm 
                                        initialData={editingEdu}
                                        onSave={handleSaveEducation} 
                                        onCancel={handleCancelEducation}
                                        t={t.forms.edu}
                                    />
                                </div>
                            )}

                            <div className="space-y-6">
                                {education.map(edu => (
                                    <div key={edu.id} className="group relative border-l-4 border-orange-500 pl-6 py-2 hover:bg-slate-50/50 rounded-r-lg transition-colors">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-bold text-lg text-slate-800">{edu.degree}</h3>
                                                <p className="text-sm text-orange-600 font-semibold mb-1">{edu.institution} • {formatDateRange(edu.start_date, edu.end_date)}</p>
                                                {edu.mention && <span className="text-xs bg-orange-100 text-orange-800 px-2 py-0.5 rounded-full">{t.forms.edu.mention} {edu.mention}</span>}
                                            </div>
                                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition duration-200">
                                                <button onClick={() => handleEditEducation(edu)} className="text-slate-300 hover:text-blue-500">
                                                    <Pencil size={18} />
                                                </button>
                                                <button onClick={() => handleDeleteEducation(edu.id)} className="text-slate-300 hover:text-red-500">
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </div>
                                        {edu.description && <p className="text-slate-600 text-sm mt-2">{edu.description}</p>}
                                    </div>
                                ))}
                                {education.length === 0 && !showEduForm && (
                                    <p className="text-center text-slate-400 py-4 italic">{t.profile.empty.education}</p>
                                )}
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
