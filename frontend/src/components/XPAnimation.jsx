import React from "react";

const XPAnimation = ({ amount, show, style = {}, className = "" }) => {
  if (!show) return null;
  return (
    <>
      <style>{`
        @keyframes xp-pop {
          0% { opacity: 0; transform: translateX(-50%) translateY(10px) scale(0.8);}
          20% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1.1);}
          80% { opacity: 1; }
          100% { opacity: 0; transform: translateX(-50%) translateY(-20px) scale(1);}
        }
      `}</style>
      <div
        className={className}
        style={{
          position: "absolute",
          left: "50%",
          top: -30,
          fontSize: 24,
          color: "#4CAF50",
          fontWeight: "bold",
          textShadow: "0 2px 8px #fff",
          pointerEvents: "none",
          animation: "xp-pop 1.5s ease",
          ...style,
        }}
      >
        +{amount} XP!
      </div>
    </>
  );
};

export default XPAnimation; 