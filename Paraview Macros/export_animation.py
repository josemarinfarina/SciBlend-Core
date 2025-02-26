from paraview.simple import GetActiveSource, GetActiveViewOrCreate, Show
from paraview.simple import GetAnimationScene, GetTimeKeeper, ExportView
import os
import sys

if len(sys.argv) > 2:
    folder_selected = sys.argv[1]
    num_frames = int(sys.argv[2])
else:
    folder_selected = input("Enter the full path where frames will be saved: ")
    num_frames = int(input("Enter the number of frames to export: "))

if os.path.isdir(folder_selected):
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
