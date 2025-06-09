import React from "react";
import XPProgressBar from "../components/XPProgressBar";

function PracticePage({ user, progress }) {
  return (
    <div style={{ padding: 32 }}>
      <h2>Practice Mode</h2>
      <XPProgressBar xp={progress.xp} maxXp={100} />
      <p>Write INNER JOIN queries based on what you’ve learned!</p>
    </div>
  );
}

export default PracticePage;
