import React, { useEffect, useRef } from "react";
import * as BABYLON from "@babylonjs/core";
import * as GUI from "@babylonjs/gui";

function GameScene({ onXPCollect, xp = 0, maxXp = 100 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const engine = new BABYLON.Engine(canvas, true);
    const scene = new BABYLON.Scene(engine);

    const camera = new BABYLON.ArcRotateCamera("camera", -Math.PI / 2, Math.PI / 2.2, 6, new BABYLON.Vector3(0, 1, 0), scene);
    camera.attachControl(canvas, true);
    new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);

    // Platform and assistant setup (same as before)
    const platform = BABYLON.MeshBuilder.CreateCylinder("platform", { diameter: 4, height: 0.2 }, scene);
    platform.position.y = 0;
    const mat = new BABYLON.StandardMaterial("mat", scene);
    mat.diffuseColor = new BABYLON.Color3(0.2, 0.6, 0.9);
    platform.material = mat;

    const assistant = BABYLON.MeshBuilder.CreateSphere("assistant", { diameter: 0.5 }, scene);
    assistant.position.y = 1;
    assistant.material = new BABYLON.StandardMaterial("glow", scene);
    assistant.material.emissiveColor = new BABYLON.Color3(1, 0.8, 0.2);

    const xpOrb = BABYLON.MeshBuilder.CreateSphere("xp", { diameter: 0.2 }, scene);
    xpOrb.position.set(1, 1, 0);
    xpOrb.material = new BABYLON.StandardMaterial("xpMat", scene);
    xpOrb.material.emissiveColor = new BABYLON.Color3(0.4, 1, 0.4);

    scene.onBeforeRenderObservable.add(() => {
      xpOrb.position.y = 1 + Math.sin(performance.now() * 0.002) * 0.1;
    });

    scene.onPointerObservable.add((pointerInfo) => {
      if (
        pointerInfo.type === BABYLON.PointerEventTypes.POINTERDOWN &&
        pointerInfo.pickInfo?.pickedMesh?.name === "xp"
      ) {
        xpOrb.dispose();
        if (onXPCollect) {
          onXPCollect(10); // Add 10 XP
        }
      }
    });

    // ✅ Create GUI
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
    xpText.text = `XP: ${xp}/${maxXp}`;
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

    // Update on XP prop change
    const updateXPBar = () => {
      xpText.text = `XP: ${xp}/${maxXp}`;
      xpFill.width = `${(xp / maxXp) * 280}px`;
    };

    updateXPBar();

    engine.runRenderLoop(() => {
      scene.render();
    });

    return () => {
      engine.dispose();
    };
  }, [xp, maxXp, onXPCollect]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "300px", display: "block", marginTop: "20px" }}
    />
  );
}

export default GameScene;
