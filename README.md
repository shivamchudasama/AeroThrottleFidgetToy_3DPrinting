# Parametric CAD Project Setup

## Create a project

1. Put `setup_cad_project.bat` in the folder where you want the new project created.
2. Double-click `setup_cad_project.bat`.
3. Enter a simple project folder name, for example `phone-stand`.

The script creates `<project-name>` in that folder and initializes its CAD workflow files. You can also open Command Prompt in the destination folder and run:

```bat
setup_cad_project.bat phone-stand
```

## Start the 3D design

1. Open the new project folder.
2. Open `prompts\START_CAD_PROJECT.md`.
3. Copy its full contents into Claude (or your design-planning assistant).
4. Replace every `[ ... ]` placeholder with your product details, dimensions, material, manufacturing method, and any reference images.
5. Send the completed prompt. The first phase creates `DESIGN_SPEC.md`, `PARAMETERS.md`, and `design\ALGORITHM.md`; it does not write CAD code yet.

### Example first prompt

> Design a parametric FDM-printable desk phone stand for a 6.7-inch phone. Use PETG. Make it 90 mm wide, 110 mm high, and 100 mm deep, with a 12 mm front lip, a 15-degree viewing angle, 2 mm minimum wall thickness, and 0.4 mm assembly clearance. The phone width, thickness, viewing angle, and front-lip height must be adjustable. Output OpenSCAD and STL. First produce the design specification, parameter list, and geometry algorithm only; do not write implementation code.
