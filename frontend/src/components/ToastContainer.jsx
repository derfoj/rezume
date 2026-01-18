
import React from 'react';
import { useToast } from '../context/ToastContext';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const ToastContainer = () => {
    const { toasts, removeToast } = useToast();

    const getIcon = (type) => {
        switch (type) {
            case 'success': return <CheckCircle size={20} className="text-green-500" />;
            case 'error': return <AlertCircle size={20} className="text-red-500" />;
            case 'warning': return <AlertTriangle size={20} className="text-orange-500" />;
            default: return <Info size={20} className="text-blue-500" />;
        }
    };

    const getStyles = (type) => {
        switch (type) {
            case 'success': return 'bg-green-50 border-green-200 text-green-900';
            case 'error': return 'bg-red-50 border-red-200 text-red-900';
            case 'warning': return 'bg-orange-50 border-orange-200 text-orange-900';
            default: return 'bg-blue-50 border-blue-200 text-blue-900';
        }
    };

    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
            {toasts.map((toast) => (
                <div
                    key={toast.id}
                    className={`
            pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border min-w-[300px] 
            animate-in slide-in-from-right fade-in duration-300
            ${getStyles(toast.type)}
          `}
                >
                    {getIcon(toast.type)}
                    <p className="flex-1 text-sm font-medium">{toast.message}</p>
                    <button
                        onClick={() => removeToast(toast.id)}
                        className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                        <X size={16} />
                    </button>
                </div>
            ))}
        </div>
    );
};

export default ToastContainer;
