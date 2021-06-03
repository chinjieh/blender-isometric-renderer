# This script is meant to be run as a blender background python script.
# Given a .blend file with the scene rendering settings already setup,
# it will import the given obj file, and render the object in eight 45 degrees angles.
# Renders are exported to the given render path, with the direction suffix (e.g "-SE")

import bpy
import os
import math

def import_and_export_obj(path_to_obj, render_path_root):
	# import file
	bpy.ops.object.select_all(action='DESELECT')
	filepath = path_to_obj
	bpy.ops.import_scene.obj(filepath=filepath)

	imported_objs = bpy.context.selected_objects[:]
	for imported_obj in imported_objs:

		dirs = ["SE", "S", "SW", "W", "NW", "N", "NE", "E"]
		original_output_path = bpy.data.scenes["Scene"].render.filepath
		output_filename_base = os.path.splitext(os.path.basename(filepath))[0]
		output_path_base = render_path_root
		for dir in dirs:
			output_filename = output_filename_base + "-" + dir
			output_path = os.path.join(output_path_base, output_filename)
			bpy.data.scenes["Scene"].render.filepath = output_path
			print("Exporting to " + output_path)
			bpy.ops.render.render(write_still=True)
			imported_obj.rotation_euler[2] += math.radians(-45)

		# restore path
		bpy.data.scenes["Scene"].render.filepath = original_output_path

		# delete imported obj
		bpy.ops.object.select_all(action='DESELECT')
		imported_obj.select_set(True)
		bpy.ops.object.delete()

def build_render_path_root_matching_structure(root_folder, file_path_in_root_folder, export_folder):
	# Builds a render path as a folder with the same relative path as the file
	relative = os.path.relpath(file_path_in_root_folder, root_folder)
	relative = os.path.splitext(relative)[0] # Gets the relative structure without the file ext
	return os.path.join(export_folder, relative)

def is_obj_file(path_to_obj):
	return os.path.splitext(path_to_obj)[1] == ".obj"

def import_and_export(path_to_obj, render_path_root, is_folder_mode=False):
	if not is_folder_mode:
		if not is_obj_file(path_to_obj):
			print("Error: Obj path provided is not a valid .obj file")
			return;

		import_and_export_obj(path_to_obj, render_path_root)
		return;

	else:
		print("Finding files in folder: " + path_to_obj)
		if not os.path.isdir(path_to_obj):
			print("Error: Folder mode used, obj path is supposed to be a directory.")
			return;
		root_path = path_to_obj
		export_root_folder = render_path_root

		for (dirpath, dirnames, filenames) in os.walk(root_path):
			for filename in filenames:
				if is_obj_file(filename):
					obj_path = os.path.join(dirpath, filename)
					if (os.path.isfile(obj_path)):
						print("Found obj file: " + obj_path)
						render_path_root = build_render_path_root_matching_structure(root_path, obj_path, export_root_folder)
						import_and_export_obj(obj_path, render_path_root)
		

def main():
	import sys       # to get command line args
	import argparse  # to parse options for us and print a nice help message

	# get the args passed to blender after "--", all of which are ignored by
	# blender so scripts may receive their own arguments
	argv = sys.argv

	if "--" not in argv:
		argv = []  # as if no args are passed
	else:
		argv = argv[argv.index("--") + 1:]  # get all args after "--"

	# When --help or no args are given, print this help
	usage_text = (
		"Run blender in background mode with this script:"
		"  blender --background --python " + __file__ + " -- [options]"
		)

	parser = argparse.ArgumentParser(description=usage_text)
	parser.add_argument("-i", "--input", dest="input_obj", type=str, required=True, help="Path to the obj file OR folder (with --foldermode enabled)",)
	parser.add_argument("-o", "--output", dest="output_path", metavar='PATH', help="Save the generated renders to the specified folder. If absent, defaults to an 'exported' folder as a sibling of the input path",)
	parser.add_argument("-f", "--foldermode", default=False, dest="foldermode", action='store_true', help="Folder mode; Assumes the input path is a folder containing obj files")
	
	args = parser.parse_args(argv)
	if not argv:
		parser.print_help()
		return

	if not args.input_obj:
		print("Error: --i=\"some string\" argument not given, aborting.")
		parser.print_help()
		return

	input_obj_path = os.path.abspath(args.input_obj)

	if not args.output_path:
		output_path = os.path.join(os.path.split(input_obj_path)[0], "exported")
	else:
		output_path = os.path.abspath(args.output_path)

	import_and_export(input_obj_path, output_path, is_folder_mode=args.foldermode)
	print("Done.")


if __name__ == "__main__":
	main()




