# SciBlend: Bridging Paraview and Blender for Scientific Visualization v.2.0.0

SciBlend is a powerful add-on for Blender 4.2 that serves as a crucial bridge between Paraview and Blender, revolutionizing the way scientific simulations are visualized. By combining Paraview's advanced data processing capabilities with Blender's superior rendering engine, SciBlend enables researchers and scientists to create stunning, photorealistic visualizations of complex scientific data in real-time.

## Table of Contents

1. [Why SciBlend?](#why-sciblend)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
   - [Paraview Macros Installation](#1-paraview-macros-installation)
   - [Blender Addon Installation](#2-blender-addon-installation)
5. [Exporting Data from Paraview](#exporting-data-from-paraview)
   - [Using Paraview Macros](#using-paraview-macros)
     - [Static Export](#static-export)
     - [Animation Export](#animation-export)
6. [Usage in Blender](#usage-in-blender)
   - [Importing Paraview Data](#1-importing-paraview-data)
   - [Data Visualization](#2-data-visualization)
   - [Scene Setup](#3-scene-setup)
   - [Real-time Interaction](#4-real-time-interaction)
   - [Final Rendering](#5-final-rendering)
7. [Contributing](#contributing)
8. [Support](#support)
9. [Demos](#demos)


https://github.com/user-attachments/assets/675cdb0f-2aca-4328-be14-432923eab8e2

## Updated Features

- **Advanced X3D Import**: Import static and animated X3D data with customizable settings.
- **Material Management**: Easily create and apply shared materials to represent different data attributes.
- **Null Object Manipulation**: Create and manipulate null objects for better scene organization and data representation.
- **Object Grouping**: Efficiently group objects by type for improved scene management.
- **Quick Scene Setup**: Set up scenes with predefined lighting and render settings optimized for scientific visualization.
- **Dynamic Boolean Operations**: Perform boolean operations to create cutaways and cross-sections of your data.
- **User-Friendly Interface**: Access all functions through a streamlined UI panel designed for scientists and researchers.

## Major Changes from Previous Version

- **Code Reorganization**: The code has been reorganized into separate modules for better maintainability and scalability.

## Why SciBlend?

Scientific simulations often produce complex, multi-dimensional data that can be challenging to visualize effectively. While Paraview excels at processing and analyzing this data, it may fall short in creating visually appealing, publication-quality renders. On the other hand, Blender offers unparalleled rendering capabilities but lacks specialized tools for handling scientific datasets.

SciBlend bridges this gap, allowing scientists to:

1. **Seamlessly import Paraview data**: Bring your simulation data directly into Blender without losing fidelity.
2. **Create real-time visualizations**: Leverage Blender's real-time rendering capabilities for interactive data exploration.
3. **Produce photorealistic renders**: Utilize Blender's advanced rendering engines to create stunning, publication-ready visualizations.
4. **Enhance scientific communication**: Make complex data more accessible and engaging through high-quality visual representations.

## Features

- **Advanced Paraview Import**: Import static and animated data from Paraview with customizable settings.
- **Material Management**: Easily manage and apply materials to represent different data attributes.
- **Null Object Manipulation**: Create and manipulate null objects for better scene organization and data representation.
- **Object Grouping**: Efficiently group objects by type for improved scene management.
- **Quick Scene Setup**: Set up scenes with predefined lighting and render settings optimized for scientific visualization.
- **Dynamic Boolean Operations**: Perform boolean operations to create cutaways and cross-sections of your data.
- **User-Friendly Interface**: Access all functions through a streamlined UI panel designed for scientists and researchers.

## Requirements

- Blender 4.2 or higher
- Paraview (for initial data processing)
- Python 3.11 (bundled with Blender 4.2)

## Installation

SciBlend consists of two main components: Paraview Macros for data export and a Blender Addon for data import and visualization. Follow these steps to install both components.

### 1. Paraview Macros Installation

1. Locate the `export_static.py` and `export_animation.py` files in the Paraview Macros directory of the SciBlend folder.
2. Open Paraview.
3. Go to `Macros > Import New Macro`.
4. Select the `export_static.py` file and click "OK".
5. Repeat steps 3-4 for `export_animation.py`.
6. The macros will now appear in the Macros menu of Paraview.

### 2. Blender Addon Installation

1. Locate the SciBlend folder containing all the Blender addon files.
2. Create a zip file of the entire SciBlend folder. On most systems, you can right-click the folder and select "Compress" or "Create archive".
3. Open Blender and go to `Edit > Preferences > Add-ons`.
4. Click on `Install...` and select the SciBlend zip file you created.
5. Enable the addon by checking the box next to `SciBlend`.

## Exporting Data from Paraview

Now that you have installed the Paraview Macros, you can use them to export your data:

### Using Paraview Macros

#### Static Export

1. Open your data in Paraview and set up the view as desired.
2. Select the object you want to export in the Pipeline Browser.
3. Go to `Macros > Export Static`.
4. A dialog will appear asking for the export directory. Enter the full path and click "OK".
5. The macro will export the selected object in the specified directory.

#### Animation Export

1. Open your animated data in Paraview and set up the view as desired.
2. Select the object you want to export in the Pipeline Browser.
3. Go to `Macros > Export Animation`.
4. A dialog will appear asking for the export directory. Enter the full path and click "OK".
5. Another dialog will ask for the number of frames to export. Enter the desired number and click "OK".
6. The macro will export each frame of your animation in the specified directory.

Note: These macros use a simple GUI to ask for the export directory and, in the case of animations, the number of frames. You can select multiple objects in case that you need more than one from the Pipeline Browser.

## Usage in Blender

Once the Addon is installed, SciBlend adds a new panel to the 3D Viewport sidebar. Here's a brief overview of the main functions:

### 1. Importing Paraview Data

#### Static Import
- Use the "Import Static" option for single-frame data.
- Customize import settings such as axis orientation and scale factor to match your Paraview export.

#### Animated Import
- Use "Import Animation" for time-series data.
- Specify the range of frames to import using two sliders:
  - Start Frame Number: Set the first frame of your animation sequence.
  - End Frame Number: Set the last frame of your animation sequence.
- Adjust the orientation of the imported data:
  - Forward Axis: Choose which axis (X, Y, Z, -X, -Y, -Z) should be considered as "forward" in Blender.
  - Up Axis: Choose which axis should be considered as "up" in Blender.
- Set a scale factor to resize your imported data as needed.

### 2. Data Visualization

- Apply and manage materials to represent different data attributes.
- Use null objects and grouping to organize complex datasets.
- Perform boolean operations to create cutaways and cross-sections.

### 3. Scene Setup

- Quickly set up a scene with lighting and render settings optimized for scientific visualization.

### 4. Real-time Interaction

- Utilize Blender's real-time rendering capabilities to interactively explore your data.

### 5. Final Rendering

- Leverage Blender's advanced rendering engines to create publication-quality images and animations of your scientific data.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## Support

For questions, issues, or feature requests, please use the GitHub issue tracker or contact the maintainer at marinfarinajose@gmail.com.

## Demos

https://github.com/user-attachments/assets/4bc2184c-d9bc-4ba3-8bc3-a18c295fea1e


https://github.com/user-attachments/assets/2374c9a9-43c7-4ce7-8629-3a7adeb4e3d4


https://github.com/user-attachments/assets/e3b058e8-eb94-497c-853a-d520418599cf