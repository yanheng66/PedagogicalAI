import React, { useEffect, useRef } from "react";
import * as BABYLON from "@babylonjs/core";
import * as GUI from "@babylonjs/gui";

function XPProgressBar({ xp = 0, maxXp = 100 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });
    const scene = new BABYLON.Scene(engine);
    new BABYLON.FreeCamera("camera", new BABYLON.Vector3(0, 0, -1), scene); // No visible 3D

    const gui = GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");

    const panel = new GUI.StackPanel();
    panel.width = "300px";
    panel.top = "-40%";
    panel.horizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
    panel.verticalAlignment = GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
    gui.addControl(panel);

    const xpText = new GUI.TextBlock();
    xpText.height = "30px";
    xpText.color = "white";
    xpText.fontSize = "20px";
    panel.addControl(xpText);

    const xpBarBG = new GUI.Rectangle();
    xpBarBG.width = "280px";
    xpBarBG.height = "20px";
    xpBarBG.color = "white";
    xpBarBG.thickness = 2;
    xpBarBG.background = "gray";
    panel.addControl(xpBarBG);

    const xpFill = new GUI.Rectangle();
    xpFill.width = `${(xp / maxXp) * 280}px`;
    xpFill.height = "20px";
    xpFill.background = "limegreen";
    xpBarBG.addControl(xpFill);

    // Update on XP change
    const update = () => {
      xpText.text = `XP: ${xp} / ${maxXp}`;
      xpFill.width = `${(xp / maxXp) * 280}px`;
    };
    update();

    engine.runRenderLoop(() => {
      scene.render();
    });

    return () => {
      engine.dispose();
    };
  }, [xp, maxXp]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "100px", display: "block", marginTop: "10px" }}
    />
  );
}

export default XPProgressBar;
