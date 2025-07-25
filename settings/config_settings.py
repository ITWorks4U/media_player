#	Outsourced settings for configuration, which are in use in main only.
#
#	author:		ITWorks4U
#	created:	July 23rd, 2025
#	updated:	July 25th, 2025
#

from os.path import join, dirname
from pathlib import Path
from sys import stderr

class ConfigSettings:
	#	---------------
	#	constructor
	#	---------------
	def __init__(self) -> None:
		"""
		Initializing the configuration settings.

		used_os:
		-	holds the information which OS is in use => more required for special methods
		"""
		#	config dictionary
		self._settings: dict[str, str] = {}

		#	keys for self.settings dictionary
		self._key_path_for_logging = "path_for_logging"
		self._key_random_order = "play_in_random_order"
		self._key_mount_point = "usb_mount_point"

		self.cfgfile = join(dirname(__file__), "options.conf")
	#end constructor

	#	---------------
	#	properties
	#	---------------
	@property
	def LogPath(self):
		"""Return the path for logging."""
		return self._settings[self._key_path_for_logging]
	#end property

	@property
	def ConfigStorage(self):
		"""Return the full config storage."""
		return self._settings
	#end property

	#	---------------
	#	methods
	#	---------------
	def load_config_file(self, cfg_file: str = "") -> bool:
		"""
		Load the config file. By default the local config file is in use. Alternatively, if the
		cfg_file argument is not empty, then this config file is in use instead.

		If the used config file does not exist, or any other IOError or any general exception
		appears, an error message is going to print to stderr and this method returns False.

		---
		cfg_file:

		-	an alternative config file to use, defaults to an empty string

		---
		returns:

		-	True, if the config file was successfully loaded

		-	False, otherwise
		"""
		if not isinstance(cfg_file, str):
			#	if the argument does not fit with a string
			return False
		#end if

		file_to_use: str = self.cfgfile if cfg_file == "" else join(dirname(__file__), cfg_file)

		try:
			with open(file_to_use, encoding="latin-1") as src:
				for line in src.readlines():
					#	skip every empty line and commentary
					if line in ["", "\n", "\r\n", "\r"] or line.startswith(";"):
						continue
					#end if

					kvp = line.strip().split("=")
					self._settings[kvp[0]] = kvp[1]
				#end for
			#end with
		except Exception as e:
			detailed_message = f"""
{type(e)} in file {file_to_use} detected:
{e.args}
"""
			print(detailed_message, file=stderr)
			return False
		#end try

		return True
	#end method

	def create_config_file(self) -> bool:
		"""
			Create an empty config file. This config file is going to
			write to *settings/options.conf*.

			In case of any error False a message to stderr is going to
			print and False returns.

			---
			**THIS OVERWRITES THE ALREADY EXISTING CONFIG FILE!**
		"""

		config_content = f"""
; config options for the music player

; ---------------
; Given path for logging. The path can be absolute or relative. Don't add a file
; to the path, just the path for logging. The log file "media_player.log" will
; automatically be appended to this path.
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
			with open(self.cfgfile, mode="w", encoding="latin-1") as dest:
				_ = dest.write(config_content)
			#end with
		except Exception as e:
			detailed_message = f"""
{type(e)} for writing into config file {self.cfgfile} detected:
{e.args}
"""
			print(detailed_message, file=stderr)
			return False
		#end try

		return True
	#end method

	def check_on_random_order(self) -> None:
		"""
		Check, if the random order key has been found
		and also check, which value contains that key.

		---
		-	the key might not exist => set to False
		-	the key has a value of ["true", "True", "false", "False"] => set certain value
		-	the key contains anything => set to False
		"""
		if not self._key_random_order in self._settings:
			self._settings[self._key_random_order] = False
		#end if

		match self._settings[self._key_random_order]:
			case ("true" | "True"):
				#	contains "true" or "True"
				self._settings[self._key_random_order] = True
			case _:
				#	contains "false" or "False" or anything else
				self._settings[self._key_random_order] = False
			#end cases
		#end match
	#end method

	def on_existing_mount_point(self) -> bool:
		"""
		Checks, if the mount point has been set and if this
		path (relative or absolute) potentially exists.

		---
		A failure results, if:

		-	the key does not exist (possibly by using a foreign config file)
		-	the value is not a string
		-	the word is empty
		-	the value is not a path, e. g. a file
		-	the path can't be found
		-	insufficient access rights

		---
		returns:

		-	True, if this path is given and also exists

		-	False, otherwise 
		"""
		return (
			self._key_mount_point in self._settings and
			isinstance(self._settings[self._key_mount_point], str) and 
			len(self._settings[self._key_mount_point]) > 0 and
			Path(self._settings[self._key_mount_point]).is_dir()
		)
	#end method

	def on_existsing_log_path(self) -> bool:
		"""
		Checks, if the path for logging is set and if
		this path (relative or absolute) potentially exists.

		---
		A failure results, if:

		-	the key does not exist (possibly by using a foreign config file)
		-	the value is not a string
		-	the word is empty
		-	the value is not a path, e. g. a file
		-	the path can't be found
		-	insufficient access rights

		---
		returns:

		-	True, if this path is given and also exists

		-	False, otherwise
		"""
		return (
			self._key_path_for_logging in self._settings and
			isinstance(self._settings[self._key_path_for_logging], str) and 
			len(self._settings[self._key_path_for_logging]) > 0 and
			Path(self._settings[self._key_path_for_logging]).is_dir()
		)
	#end function
#end class