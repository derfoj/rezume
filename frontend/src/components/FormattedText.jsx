import React from 'react';

const FormattedText = ({ text }) => {
  if (!text) return null;

  // Split by newlines to handle bullet points
  const lines = text.split('\n');
  
  return (
    <div className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed space-y-1">
      {lines.map((line, i) => {
        // Handle Bullet Points
        const isBullet = line.trim().startsWith('-') || line.trim().startsWith('•');
        const content = isBullet ? line.trim().substring(1).trim() : line;
        
        // Handle Bold (**text**)
        const parts = content.split(/(\*\*.*?\*\*)/g);
        
        const formattedLine = (
          <span>
            {parts.map((part, j) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={j} className="text-slate-800 dark:text-slate-100 font-bold">{part.slice(2, -2)}</strong>;
              }
              return part;
            })}
          </span>
        );

        if (isBullet) {
          return (
            <div key={i} className="flex gap-2 items-start pl-1">
              <span className="text-blue-400 dark:text-blue-500 mt-1.5 text-xs">•</span>
              <span className="flex-1">{formattedLine}</span>
            </div>
          );
        }

        return <p key={i} className="min-h-[1em]">{formattedLine}</p>;
      })}
    </div>
  );
};

export default FormattedText;