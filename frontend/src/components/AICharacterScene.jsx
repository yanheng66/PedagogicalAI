import React from "react";

function AICharacterScene({ pose, size = 120, animation = "bounce", style = {} }) {
  return (
    <img
      src={pose}
      alt="AI Assistant"
      style={{
        width: size,
        animation: `${animation} 1.5s infinite ease-in-out`,
        marginBottom: 16,
        ...style,
      }}
    />
  );
}

export default AICharacterScene;
