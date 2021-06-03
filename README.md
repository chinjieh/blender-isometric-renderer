# About

This is a simple Blender background script that automates importing of an .obj model, and renders it in 8 directions.

## How to Use

First, prepare a Blender `.blend` file that has the cameras and settings prepared for the render. The .obj model will be imported into the origin of the Scene.
**Currently, the .blend file should be setup so that the first image rendered should have the object facing Southeast.**

From the command line, run it as you would a Blender [background script](https://docs.blender.org/manual/en/dev/advanced/command_line/arguments.html):

```sh
$ cd blender-isometric-renderer

$ blender --background "<path_to_blend_file>" -x 1 --python blender-isometric-renderer.py -- -i "<path_to_obj>"
```

This takes the .blend file located at `path_to_blend_file` and runs the script, importing an .obj at `path_to_obj` and renderering images at the default folder "export" created in the same root folder as the .obj file.

The output will be eight images of the name **obj_name-<DIRECTION>** in the export folder.

For example, if the obj file name was **model.obj**, the images would be named **model-SE**, **model-S**, **model-SW** etc.

## How it works

The script imports an .obj file, and triggers a render. Then it rotates the model 45 degrees clockwise, and renders it again, repeating the steps for all eight directions.

## Arguments

These are additional arguments for the python script, which have to be located *after* the `--` so that they are passed into the script.

`-i` / `--input` : The path to the .obj file (if no `foldermode`), or the path to the folder containing .obj files (if `foldermode` is active)

`-o` / `--output` : The path where exported renders will be created. If absent, a folder "export" will be created in the same folder as the obj file.

`-f` / `--foldermode` : Enables "foldermode", which means that the input path is intended to be a folder. All .obj files found (and in subfolders) will be imported and rendered (see below)

## Foldermode

By enabling Foldermode with the argument `--foldermode`, the script expects that the input argument is now a folder. 
All .obj files located in the folder and subfolders will then be rendered in 8 directions, and a folder with the same names and hierarchy as the .obj files will be created to contain the eight renders.
