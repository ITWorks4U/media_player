#	Print a summary message to stdout, when a module to import
#	was not found on the system
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#

def print_to_stdout(module_name: str) -> None:
	"""
	Print to stdout, that the current module to load was not found on the system.

	module_name:
	-	the name of the module to use
	"""

	summary = f"""
	ERROR: {module_name} module was not found...
	Please install {module_name} by pip(3|.exe) {module_name}.

	Alternatively, commonly in UNIX/Linux/macOS, install {module_name} by using:

	> sudo apt install python3-{module_name}

	if pip ran into an error.
	"""
	print(summary)
#end function