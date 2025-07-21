#	Playing mp3 files from the first detected USB device.
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#	updated:	July 21st, 2025
#

#	system modules
import sys
import platform
from signal import signal, SIGINT, SIGTERM
import os

#	custom modules
from custom_media_player import MediaPlayer, PLAYER_AVAILABLE
from misc.signal_handling import handle_signal

#	---------------
#	GLOBAL SETTINGS
#	---------------
#	config dictionary
_config_settings: dict[str, str] = {}

#	default config file name
_default_config_file: str = os.path.join(os.path.dirname(__file__), "settings", "options.conf")

#	location of the version.ini file
_version_file: str = os.path.join(os.path.dirname(__file__), "version.ini")

#	keys for config_settings dictionary
_key_random_order = "play_in_random_order"
_key_mount_point = "usb_mount_point"
_key_operating_system = "os"

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

	> Displaying >>this<< help, when -h or --help or /? has been detected.
	> This help is also going to print, if no USB mount point has been spotted.
	> All arguments are optional.

	-----------------
	IMPORTANT:
	> Depending on your used OS system, the log file path and also the mount point differs.
	=> Take a look to the options.conf file, if existing.
	-----------------

	By default the options.conf file is going to load the settings to use. These are:
	path_for_logging:
	-	A path for logging. If nothing was given, no log will be used.
	-	Make sure, that the path is valid, otherwise an error during runtime appears
		and the error message is going to print to stdout.

	usb_mount_point:
	-	A path for the USB device. Optionally, a local path can also be used.
	-	If no input was given, then you're reading >>this<< output. ;-)
	-	If the path is invalid, then an error during runtime appears and the error message
		is going to print to stdout.

	play_in_random_order:
	-	Offers to play the mp3 files in a random order, if set with true or True.
		Any other input, like false, False, ... and also nothing results to false
		and the mp3 files are playing in the sequental order instead. 

	-----------------
	IMPORTANT:
	-	If the module pygame was not detected on your system, you should already seen the
		error message on stdout. Make sure to install this module to listen to music.
	
		No audio will play.
	-----------------

	arguments:
	[-h | --help |/?]:
	-	displaying >>this<< help and terminates the application with 0

	[-c | --create]
	-	If given, then a new options.conf is going to create without given settings.
	-	location of the config file: settings/options.conf
	-	ATTENTION: If this file already exists, this will be overwritten!
	-	Finally, the application terminates in the normal way.

	[custom config file]
	-	Uses the custom config file to set up the player. Make sure, that the option keys
		are identical, otherwise the application terminates with an error.
	"""
	print(summary)
	sys.exit(0)
#end function

def create_config_file() -> None:
	"""
	Create an empty config file and terminate the application with exit code 0.
	If any error appers, usually IOError, the error message will be printed and
	the application is also going to terminate with exit code 0.

	---
	**THIS OVERWRITES THE ALREADY EXISTING CONFIG FILE!**

	---
	"""

	config_content = f"""
; config options for the music player

; ---------------
; Given path for logging. Use an absolute path only.
; If no logging path is given, no log is going to use.
; ---------------
path_for_logging=

; ---------------
; Mount point for the USB device. Can also be a local path, when no USB device is in use.
; If no mount point is given, no action is going to do.
; ---------------
usb_mount_point=

; ---------------
; Play the detected mp3 files in a random order, if the value is set to true or True.
; If no value is given or differs to {{true, True, false, False}}, then false is set by default.
; ---------------
play_in_random_order="""
	try:
		with open(_default_config_file, mode="w", encoding="latin-1") as dest:
			_ = dest.write(config_content)
		#end with
	except IOError as e:
		print(f"ERROR: unable to write data to {_default_config_file}: {e.args}")
	finally:
		sys.exit(0)
	#end try
#end function

def load_options(cfg_file: str = "") -> None:
	"""
	Load the options.conf file, if existing. If this file does not exist, or
	any other IOError or any general exception appears, the current message will
	be printed to stdout followed by application termination with 1.

	By default the options.conf, located in settings/, contains all required data
	to work with.

	---
	*If you're using a **custom** config file, then make sure, that the expected **keywords**
	in the config file **exists**!*

	---
	cfg_file:
	-	use an own custom config file, if given
	-	defaults to an empty string
	"""
	file_to_use: str = _default_config_file \
		if cfg_file == "" \
		else os.path.join(os.path.dirname(__file__), cfg_file)

	try:
		with open(file_to_use, encoding="latin-1") as src:
			for line in src.readlines():
				#	skip every empty line and commentary
				if line in ["", "\n", "\r\n", "\r"] or line.startswith(";"):
					continue
				#end if

				kvp = line.strip().split("=")
				_config_settings[kvp[0]] = kvp[1]
			#end for
		#end with
	except Exception as e:
		if isinstance(e, IOError):
			print(f"ERROR: ({_default_config_file}): {e.args}")
		else:
			print(f"Common error detected: {e.args}")
		#end if

		sys.exit(1)
	#end try

	return _config_settings
#end function

def main() -> None:
	signal(SIGINT, handle_signal)
	signal(SIGTERM, handle_signal)

	#	print help and terminate the application
	if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "/?"]:
		print_help(sys.argv[0])
	#end if

	#	create a new config file, which overwrites the existing config file,
	#	if exists, and terminate the application
	if len(sys.argv) > 1 and sys.argv[1] in ["-c", "--create"]:
		create_config_file()
	#end if

	#	loading options.conf or an alternative config file (argv[1]) and assign the values to the variables
	#
	#	If no logging path is given, no log is going to use.
	#	If no mount point is given, the application is going to terminate with 0.
	#	Playing the mp3 files in a random order, if given.
	load_options(cfg_file=sys.argv[1] if len(sys.argv) > 1 else "")

	if not _key_random_order in _config_settings:
		#	if this key might be missing, add this key
		#	and set the value to False
		_config_settings[_key_random_order] = False
	#end if

	if not isinstance(_config_settings[_key_random_order], bool):
		#	check, if the key for random order does not contain {True or False}
		#	=> set to False 
		_config_settings[_key_random_order] = False
	elif _config_settings[_key_random_order] in ["true", "false"]:
		#	set to True, if "true" has been detected
		#	=> set to False, otherwise
		_config_settings[_key_random_order] = True if "true" else False
	#end if

	#	appending the current OS
	_config_settings[_key_operating_system] = platform.system()

	if _config_settings[_key_mount_point] == "":
		#	 no mount point has been spotted
		#	=> display help and terminate the application
		print_help(sys.argv[0])
	#end if

	if PLAYER_AVAILABLE:
		mp = MediaPlayer(**_config_settings)
		# print(mp)
		mp.init_logging()
		mp.play_audio_files()
	#end if
#end main

if __name__ == "__main__":
	main()
#end entry point