#	Outsourced settings for configuration, which are in use in main only.
#
#	author:		ITWorks4U
#	created:	July 23rd, 2025
#	updated:	July 24th, 2025
#

from os.path import exists

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
		self._key_logging_handler = "log_handler"

		#	set the log handler
		self._log_handler = None
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
	def LogHandler(self):
		"""Returning the log handler."""
		return self._settings[self._key_logging_handler]
	#end property

	@LogHandler.setter
	def LogHandler(self, value):
		"""Update the log handler. If None, then no logging is in use."""
		self._settings[self._key_logging_handler] = value
	#end property

	@property
	def ConfigStorage(self):
		"""Return the full config storage."""
		return self._settings
	#end property

	#	---------------
	#	methods
	#	---------------
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

		returns:
		-	True, if this path is given and also exists
		-	False, otherwise 
		"""
		return (
			self._key_mount_point in self._settings and
			exists(self._settings[self._key_mount_point])
		)
	#end method

	def on_existsing_log_path(self) -> bool:
		"""
		Checks, if the path for logging is set and if
		this path (relative or absolute) potentially exists.

		returns:
		-	True, if this path is given and also exists
		-	False, otherwise
		"""
		return (
			self._key_path_for_logging in self._settings and
			exists(self._settings[self._key_path_for_logging])
		)
	#end function
#end class