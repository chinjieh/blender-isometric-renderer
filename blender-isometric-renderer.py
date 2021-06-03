# This script is meant to be run as a blender background python script.
# Given a .blend file with the scene rendering settings already setup,
# it will import the given obj file, and render the object in eight 45 degrees angles.
# Renders are exported to the given render path, with the direction suffix (e.g "-SE")

import os
import math

class ImportSettings:
	""" Contains settings that control how the model is imported """

	def __init__(self, position_x=0, position_y=0, position_z=0):
		self.position_x = position_x
		self.position_y = position_y
		self.position_z = position_z


def import_and_export_obj(path_to_obj, render_path_root, import_settings):
	import bpy

	# import file
	bpy.ops.object.select_all(action='DESELECT')
	filepath = path_to_obj
	bpy.ops.import_scene.obj(filepath=filepath)

	imported_objs = bpy.context.selected_objects[:]
	for imported_obj in imported_objs:

		# Set the object position
		imported_obj.location[0] = import_settings.position_x
		imported_obj.location[1] = import_settings.position_y
		imported_obj.location[2] = import_settings.position_z

		dirs = ["SE", "S", "SW", "W", "NW", "N", "NE", "E"]
		original_output_path = bpy.data.scenes["Scene"].render.filepath
		output_filename_base = os.path.splitext(os.path.basename(filepath))[0]
		for dir in dirs:
			output_filename = output_filename_base + "-" + dir
			output_path = os.path.join(render_path_root, output_filename)
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
	relative = os.path.splitext(relative)[0] # Gets the relative structure without the file extension
	return os.path.join(export_folder, relative)


def is_obj_file(path_to_obj):
	return os.path.splitext(path_to_obj)[1] == ".obj"


def import_and_export(input_path, render_path_root, import_settings, is_folder_mode=False):
	if not is_folder_mode:
		if not is_obj_file(input_path):
			print("Error: Obj path provided is not a valid .obj file")
			return;

		import_and_export_obj(input_path, render_path_root, import_settings)
		return;

	else:
		print("Finding files in folder: " + input_path)
		if not os.path.isdir(input_path):
			print("Error: Folder mode is active, so the input path is supposed to be a directory.")
			return;

		for (dirpath, dirnames, filenames) in os.walk(input_path):
			for filename in filenames:
				if is_obj_file(filename):
					obj_path = os.path.join(dirpath, filename)
					if (os.path.isfile(obj_path)):
						print("Found obj file: " + obj_path)
						export_root_folder = build_render_path_root_matching_structure(input_path, obj_path, render_path_root)
						import_and_export_obj(obj_path, export_root_folder, import_settings)


def build_import_settings(args):
	import_settings = ImportSettings()

	if args.positions:
		import_settings.position_x = args.positions[0]
		import_settings.position_y = args.positions[1]
		import_settings.position_z = args.positions[2]

	return import_settings


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
		"  blender --background <path_to_blend_file> --python " + __file__ + " -- [options]"
		)

	parser = argparse.ArgumentParser(description=usage_text)
	parser.add_argument("-i", "--input", dest="input_path", type=str, required=True, 
		help="Path to the obj file OR folder (with --foldermode enabled)",)

	parser.add_argument("-o", "--output", dest="output_path", metavar='PATH', 
		help="Save the generated renders to the specified folder. If absent, defaults to an 'export' folder as a sibling of the input path",)

	parser.add_argument("-f", "--foldermode", default=False, dest="foldermode", action='store_true', 
		help="Folder mode; Assumes the input path is a folder containing obj files",)

	parser.add_argument("-p", "--pos", dest="positions", metavar="X Y Z", nargs=3, type=float,
		help="Defines the position of the object in the Scene. Provide as 3 floats separated by a space.")
	
	args = parser.parse_args(argv)
	if not argv:
		parser.print_help()
		return

	if not args.input_path:
		print("Error: --i=\"input_path\" argument not given, aborting.")
		parser.print_help()
		return

	input_obj_path = os.path.abspath(args.input_path)

	if not args.output_path:
		output_path = os.path.join(os.path.split(input_obj_path)[0], "export")
	else:
		output_path = os.path.abspath(args.output_path)

	if os.path.exists(output_path) and os.path.samefile(input_path, output_path):
		print("Error: The input path and output paths are the same, aborting to prevent overwriting source work.")
		print("Input: %s" % input_path)
		return

	import_settings = build_import_settings(args)

	import_and_export(input_obj_path, output_path, import_settings, is_folder_mode=args.foldermode)
	print("Done.")


if __name__ == "__main__":
	main()




