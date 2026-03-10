import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Users, BarChart3, Activity, ShieldCheck, Database, RefreshCw, 
  ChevronLeft, Briefcase, Cpu, CheckCircle2, AlertCircle 
} from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, colorClass }) => (
  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm hover:shadow-md transition-all">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wider">{title}</p>
        <h3 className="text-3xl font-bold text-slate-900 dark:text-white font-mono">{value}</h3>
      </div>
      <div className={`p-3 rounded-xl ${colorClass} bg-opacity-10 dark:bg-opacity-20`}>
        <Icon className={colorClass.replace('bg-', 'text-')} size={24} />
      </div>
    </div>
  </div>
);

export default function AdminDashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const [statsRes, usersRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/stats`, { headers }),
        fetch(`${API_URL}/api/admin/users`, { headers })
      ]);

      if (!statsRes.ok || !usersRes.ok) throw new Error("Accès refusé.");
      setStats(await statsRes.json());
      setUsers(await usersRes.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Only redirect if we ARE CERTAIN the user is not an admin
    if (user && user.role !== 'admin') {
      navigate('/dashboard');
    } else if (user && user.role === 'admin') {
      fetchData();
    }
  }, [user, token, navigate]);

  if (!user || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <RefreshCw className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-200 font-sans p-4 md:p-8">
      {/* Rest of the UI remains the same... */}
      <div className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors">
            <ChevronLeft size={24} />
          </button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
              <ShieldCheck className="text-blue-600" /> Control Center
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Administration Système</p>
          </div>
        </div>
        <button onClick={fetchData} className="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-2 rounded-xl text-sm font-bold hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
          <RefreshCw size={16} /> Actualiser
        </button>
      </div>

      <div className="max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard title="Utilisateurs" value={stats?.overview.users} icon={Users} colorClass="bg-blue-500 text-blue-600" />
          <StatCard title="CV Générés" value={stats?.overview.cv_generated} icon={Cpu} colorClass="bg-purple-500 text-purple-600" />
          <StatCard title="Analyses" value={stats?.overview.analysis_performed} icon={BarChart3} colorClass="bg-orange-500 text-orange-600" />
          <StatCard title="Succès" value={`${stats?.performance.success_rate}%`} icon={CheckCircle2} colorClass="bg-green-500 text-green-600" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
              <h3 className="font-bold text-lg flex items-center gap-2"><Users size={20} className="text-blue-500" /> Base Utilisateurs</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider">
                    <th className="px-6 py-4 font-bold">Email</th>
                    <th className="px-6 py-4 font-bold">Nom</th>
                    <th className="px-6 py-4 font-bold">Rôle</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">{u.email}</td>
                      <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-300">{u.full_name || '-'}</td>
                      <td className="px-6 py-4">
                        <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full ${u.role === 'admin' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' : 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'}`}>
                          {u.role}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
              <h3 className="font-bold text-lg mb-6 flex items-center gap-2"><Activity size={20} className="text-orange-500" /> Activité</h3>
              <div className="space-y-6">
                {stats?.recent_activity.map(log => (
                  <div key={log.id} className="relative pl-6 border-l-2 border-slate-100 dark:border-slate-800">
                    <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 border-white dark:border-slate-900 ${log.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white uppercase">{log.action.replace('_', ' ')}</p>
                    <p className="text-xs text-slate-500 mt-1">{new Date(log.timestamp).toLocaleTimeString()}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
