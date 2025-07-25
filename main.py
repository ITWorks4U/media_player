#	Playing mp3 files from the first detected USB device.
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#	updated:	July 25th, 2025
#

#	system modules
from sys import argv, exit, stderr
from signal import signal, SIGINT, SIGTERM
from os.path import join, dirname
from dataclasses import fields

#	custom modules
from custom_media_player import MediaPlayer, PLAYER_AVAILABLE
from settings.config_settings import ConfigSettings
from misc.signal_handling import handle_signal
from misc.logging_file import RotatingFileLogging, logging
from misc.version_updater import VersionUpdater
from misc.readme_updater import update_readme

#	---------------
#	GLOBAL SETTINGS
#	---------------
#	location of the version.ini file
_version_file: str = join(dirname(__file__), "version.ini")

#	instance to ConfigSettings class
_settings: ConfigSettings = ConfigSettings()

#	---------------
#	FUNCTIONS
#	---------------
def print_help(own_file_name: str) -> None:
	"""
	Print a simple usage description and terminate the application with 0.
	"""
	file_version: str
	try:
		with open(_version_file, encoding="latin-1") as src:
			file_version = src.readline()
		#end with
	except IOError:
		file_version = ""
	#end try

	summary = f"""
	-----------------
	custom media player {file_version}
	-----------------
	usage: python[3|.exe] {own_file_name} [[-h | --help |/?] [-c | --create] [custom config file]]

	> Displaying >>this<< help, when:
	-h or --help or /? has been detected -OR-
	using more than two arguments -OR-
	using any other kind of argument(s)

	> All arguments are optional.

	-----------------
	NOTE:
	> Depending on your used OS system, the log file path and also the mount point differs.
	> Take a look to the options.conf file.
	> If this file might not exist, this can easily be created by using an the argument -c or --create.
	-----------------

	By default the options.conf file is going to load the settings to use. These are:
	path_for_logging:
	-	A path for logging. If nothing was given, no log will be used.
	-	use an absolute or relative path only
	-	a file must not be appended, otherwise an error appears during runtime
	-	the path must be valid, too

	usb_mount_point:
	-	A path for the USB device. Optionally, a local path can also be used.
	-	If no path has been detected, an error message will be printed to stderr
		and the application is going to terminate with exit code 1
	-	This path must also be valid.

	play_in_random_order:
	-	Offers to play the mp3 files in a random order, if set with true or True.
		Any other input, like false, False, ... and also nothing results to false
		and the mp3 files are playing in the sequental order instead. 

	-----------------
	IMPORTANT:
	-	If the module pygame was not detected on your system, a message is going to
		print to stderr and the application will be termianted with exit code 1.
	-----------------

	arguments:
	[-h | --help |/?]:
	-	displaying >>this<< help and terminates the application with 0

	[-c | --create]
	-	if given, then a new options.conf is going to create without given settings
	-	location of the config file: settings/options.conf
	-	termiantes the application with exit code 0

	-	ATTENTION: If this file already exists, this will be overwritten!

	[custom config file]
	-	Uses the custom config file to set up the player. Make sure, that the option keys
		are identical, otherwise the application terminates with an error.
	"""
	print(summary)
	exit(0)
#end function

def init_logging(destination_path: str) -> RotatingFileLogging:
	"""
	Initializing a logging system for the application. This works only,
	if a log path has been given.

	If the log file can't be created, because insufficient permissions were
	detected, the path is invalid, not existing, ..., the error message
	is going to print to stderr followed by returning None for logging.

	destination_path:
	-	where the log file is going to write

	returns:
	-	used log handler
	"""
	log_handler: RotatingFileLogging = None
	
	try:
		log_handler = RotatingFileLogging(log_destination_path=destination_path)
		formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
		log_handler.setFormatter(formatter)

		logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])
	except Exception as e:
		#	any kind of exception is going to print to stderr
		detailed_message = f"""
{type(e)} for writing into config file {destination_path} detected:
{e.args}
"""
		print(detailed_message, file=stderr)
	#end try

	return log_handler
#end function

def error_terminate(message: str) -> None:
	"""
	Print a message to stderr and terminate with exit code 1.

	message:
	-	the message to print
	"""
	print(f"ERROR: {message}", file=stderr)
	exit(1)
#end function

def main() -> None:
	signal(SIGINT, handle_signal)
	signal(SIGTERM, handle_signal)

	if False:
		#	just for development
		v: VersionUpdater = VersionUpdater.load_current_version(file_path=_version_file)
		# v.bump_minor()
		# v.bump_patch()
		# v.bump_build()
		v.update_version(_version_file)
		update_readme(v)
	#end if

	#	---------------
	#	check arguments
	#	---------------
	#	print help and terminate the application
	#	also in use, when more than two arguments are given
	on_help: bool = (
		(len(argv) == 2 and argv[1] in ["-h", "--help", "/?"]) or
		len(argv) > 2
	)

	if on_help:
		print_help(argv[0])
	#end if

	#	create a new config file, which overwrites the existing config file,
	#	if exists, and terminate the application
	if len(argv) == 2 and argv[1] in ["-c", "--create"]:
		ret_state: bool = _settings.create_config_file()
		exit(0 if ret_state == True else 1)
	#end if

	if not PLAYER_AVAILABLE:
		#	if the player module can't be found, print a message to stderr;
		#	the application is going to terminate
		error_terminate(message="No pygame module has been found. Terminating...")
	#end if

	#	---------------
	#	loading options.conf or an alternative config file (argv[1]) and assign the values to the variables
	#
	#	If no logging path is given, no log is going to use.
	#	If no mount point is given, the application is going to terminate with 0.
	#	Playing the mp3 files in a random order, if given.
	#	---------------
	if not _settings.load_config_file(cfg_file=argv[1] if len(argv) == 2 else ""):
		#	in case of False returned an error message has already been printed
		#	to stderr and this application is going to terminate with exit code 1
		exit(1)
	#end if

	#	---------------
	#	if the mount point does not exists, then display a message to stderr
	#	and termiante the application
	#	---------------
	if not _settings.on_existing_mount_point():
		error_terminate(message="No mount path detected. Please update your config file.")
	#end if

	#	---------------
	#	check key for random order:
	#	- key might not exist => set to False
	#	- key is in ["true", "True", "false", "False"] => set certain value
	#	- key contains anything => set to False
	#	---------------
	_settings.check_on_random_order()

	#	filter the values for the media player only
	detected_keys = {f.name for f in fields(MediaPlayer)}
	new_kwargs = {k : v for k, v in _settings.ConfigStorage.items() if k in detected_keys}

	#	---------------
	#	check, if a log path has been detected; it not, then
	#	nothing will be written into any log file
	#	---------------
	handler: RotatingFileLogging = None

	if not _settings.on_existsing_log_path():
		print("Info: No log output has been detected.")
	else:
		handler = init_logging(_settings.LogPath)
	#end if
	new_kwargs["log_handler"] = handler

	mp = MediaPlayer(**new_kwargs)
	# print(mp)
	mp.play_audio_files()
#end main

if __name__ == "__main__":
	main()
#end entry point