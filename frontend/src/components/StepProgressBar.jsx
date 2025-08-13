import React, { useEffect, useRef } from "react";
import * as BABYLON from "@babylonjs/core";
import * as GUI from "@babylonjs/gui";

function StepProgressBar({ stepsCompleted = 0, totalSteps = 5 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const engine = new BABYLON.Engine(canvas, true, {
      preserveDrawingBuffer: true,
      stencil: true,
    });
    const scene = new BABYLON.Scene(engine);
    new BABYLON.FreeCamera("camera", new BABYLON.Vector3(0, 0, -1), scene); // No 3D elements

    const gui = GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");

    const panel = new GUI.StackPanel();
    panel.width = "300px";
    panel.top = "-40%";
    panel.horizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
    panel.verticalAlignment = GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
    gui.addControl(panel);

    const progressText = new GUI.TextBlock();
    progressText.height = "30px";
    progressText.color = "white";
    progressText.fontSize = "20px";
    panel.addControl(progressText);

    const barBG = new GUI.Rectangle();
    barBG.width = "280px";
    barBG.height = "20px";
    barBG.color = "white";
    barBG.thickness = 2;
    barBG.background = "gray";
    panel.addControl(barBG);

    const fill = new GUI.Rectangle();
    fill.width = "1px";
    fill.height = "20px";
    fill.background = "#00ff88";
    fill.horizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_LEFT; // Align to left
    fill.thickness = 0; // no border
    barBG.addControl(fill);

    const update = () => {
      progressText.text = `Progress: ${stepsCompleted} / ${totalSteps} Steps`;
      fill.width = `${(stepsCompleted / totalSteps) * 280}px`;
    };

    update();

    engine.runRenderLoop(() => {
      scene.render();
    });

    return () => {
      engine.dispose();
    };
  }, [stepsCompleted, totalSteps]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: "100%",
        height: "100px",
        display: "block",
        marginTop: "10px",
      }}
    />
  );
}

export default StepProgressBar;
