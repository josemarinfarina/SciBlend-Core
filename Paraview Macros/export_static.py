from paraview.simple import *
import os
import sys

if len(sys.argv) > 1:
    folder_selected = sys.argv[1]
else:
    folder_selected = input("Please enter the full directory path where you want to save the file: ")

if folder_selected and os.path.isdir(folder_selected):
    file_name = "tmpfile.x3d"
    file_path = os.path.join(folder_selected, file_name)

    selected_object = GetActiveSource()

    if selected_object:
        renderView = GetActiveViewOrCreate('RenderView')
        display = Show(selected_object, renderView)
        renderView.Update()

        ExportView(file_path, view=renderView)

        print(f"Export to {file_path} completed.")
    else:
        print("No active object to export.")
else:
    print("No valid folder selected.")
