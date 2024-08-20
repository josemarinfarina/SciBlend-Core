from paraview.simple import *
import os
import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw()

folder_selected = simpledialog.askstring(
    "Input", "Please enter the full directory path where you want to save the frames (e.g., /home/user/folder):")

if folder_selected and os.path.isdir(folder_selected):
    num_frames = simpledialog.askinteger(
        "Input", "Enter the number of frames to export:")

    selected_object = GetActiveSource()

    if selected_object:
        renderView = GetActiveViewOrCreate('RenderView')
        display = Show(selected_object, renderView)
        animationScene = GetAnimationScene()
        timeKeeper = GetTimeKeeper()
        animationScene.UpdateAnimationUsingDataTimeSteps()

        renderView.UseLight = 0
        renderView.CameraParallelProjection = 1

        for i in range(num_frames):
            current_time = timeKeeper.TimestepValues[i]
            animationScene.TimeKeeper.Time = current_time
            renderView.Update()

            file_path = os.path.join(folder_selected, f"tempfile{i+1}.x3d")
            ExportView(file_path, view=renderView)

            print(f"Exported frame {i+1} to {file_path} successfully.")
    else:
        print("No active object to export.")
else:
    print("No valid folder selected.")
