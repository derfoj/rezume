
import React from 'react';

const StarryBackground = () => {
    return (
        <div className="fixed inset-0 z-0 overflow-hidden bg-[#0a0e17] pointer-events-none">
            {/* Dark Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#0a0e17] via-[#111827] to-[#1f2937] opacity-80"></div>

            {/* Stars */}
            <div className="stars absolute inset-0"></div>
            <div className="stars2 absolute inset-0"></div>
            <div className="stars3 absolute inset-0"></div>

            {/* Inline Styles for Star Animations */}
            <style>{`
                .stars {
                    width: 1px;
                    height: 1px;
                    background: transparent;
                    box-shadow: ${generateBoxShadow(700)};
                    animation: animStar 50s linear infinite;
                }
                .stars2 {
                    width: 2px;
                    height: 2px;
                    background: transparent;
                    box-shadow: ${generateBoxShadow(200)};
                    animation: animStar 100s linear infinite;
                }
                .stars3 {
                    width: 3px;
                    height: 3px;
                    background: transparent;
                    box-shadow: ${generateBoxShadow(100)};
                    animation: animStar 150s linear infinite;
                }
                
                @keyframes animStar {
                    from { transform: translateY(0px); }
                    to { transform: translateY(-2000px); }
                }

                /* Add a subtle glow/pulse to some stars */
                @keyframes twinkle {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `}</style>
        </div>
    );
};

// Helper to generate random star positions (simulating SASS loop)
const generateBoxShadow = (n) => {
    let value = `${Math.floor(Math.random() * 2000)}px ${Math.floor(Math.random() * 2000)}px #FFF`;
    for (let i = 2; i <= n; i++) {
        value += `, ${Math.floor(Math.random() * 2000)}px ${Math.floor(Math.random() * 2000)}px #FFF`;
    }
    return value;
}

export default StarryBackground;
