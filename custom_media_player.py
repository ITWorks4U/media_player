#	Playing mp3 files from the first detected USB device.
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#	updated:	July 21st, 2025
#

#	global setting, if the player module is available or not
#	defaults to true
PLAYER_AVAILABLE: bool = True

#	base modules
from random import shuffle
from time import sleep
import platform
from dataclasses import dataclass
from pathlib import Path

#	custom module(s)
from misc.logging_file import RotatingFileLogging, logging
from misc.log_level import LogLevel
from misc.import_print_stdout import print_to_stdout

#	3rd party module(s)
try:
	import pygame.mixer as mix
except ImportError:
	PLAYER_AVAILABLE = False
	print_to_stdout(module_name="pygame")
#end try

try:
	import wmi
except ImportError:
	if platform.system() == "Windows":
		print_to_stdout(module_name="wmi")
	#end if
#end try

@dataclass
class MediaPlayer:
	"""
	Offers to play mp3 files from an USB device or a local folder.
	"""

	#	---------------
	#	path for logging; if no path is given, no log is in use
	path_for_logging: str

	#	USB mount point; can also be used for a local drive
	usb_mount_point: str

	#	if set, then the music files are playing in a random order
	play_in_random_order: bool

	#	the current operating system for some special methods
	os: str

	#	if logging is available, then the messages are going to write into the
	#	log file; no output on console or else, if this flag is false
	log_path_exists: bool = False
	#	---------------

	def init_logging(self) -> None:
		"""
		Initialize logging, if a logging path exists.
		"""
		if self.path_for_logging is not None and self.path_for_logging != "":
			self.log_path_exists = True

			self.log_handler = RotatingFileLogging(file_name=self.path_for_logging)

			formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
			self.log_handler.setFormatter(formatter)

			logging.basicConfig(level=logging.DEBUG, handlers=[self.log_handler])

			if False:
				self.log_handler.test_logging()
			#end if
		#end if
	#end method

	def _init_usb_detection_windows(self) -> None:
		"""
		Initial scan for USB devices.

		---
		**This works for Windows only.**

		---
		"""
		#	instance for scanning USB ports
		self.wmi = wmi.WMI()

		#	this collection holds for each key (the device ID) the
		#	path as the value
		self.usb_devices: dict[str, str] = self._collect_all_usb_decices_windows()
	#end method

	def _on_unplugged_usb_device_windows(self) -> bool:
		"""
		Check, if an USB device has been unplugged from the system.
		If no USB device has been detected on init, there's no need
		to continue and False always returns.

		Otherwise the path of the USB device on application call might
		no longer exist. If true, then this USB device has been plugged off
		from the system and the player stops immediately.

		---
		**This works for Windows only.**

		---
		returns:
		-	True, if the USB device has been unplugged
		-	False, otherwise
		"""
		if len(self.usb_devices) == 0:
			#	if no USB device has been detected earlier, there's no
			#	need to check for an unplugged USB device
			return False
		#end if

		devices_left: list[str, str] = self._collect_all_usb_decices_windows()

		#	the certain USB path should still be a valid value in the dictionary
		#	if not, then this USB device has been unplugged during runtime
		return self.usb_mount_point not in devices_left.values()
	#end method

	def _collect_all_usb_decices_windows(self) -> dict[str, str]:
		"""
		Collect each dected USB device on the Windows system, if any.
		A dictionary of type [device-id; path] returns. If no USB device has
		been detected on the system, this dictionary is still empty.

		returns:
		-	a dictionary of all detected USB devices, if any,
			otherwise an empty dictionary
		"""
		devices: dict[str, str] = {}

		for usb in self.wmi.WIn32_PnPEntity(PNPClass="USB"):
			#NOTE:
			#in English: "USB Mass Storage Device"
			#in German: "USB-Massenspeichergerät"

			if "USB-Massenspeichergerät" in usb.Description:
				devices[usb.DeviceID] = self.usb_mount_point
			#end if
		#end for

		return devices
	#end method

	def play_audio_files(self) -> None:
		"""
		-	playing the mp3 files
		-	this works only, if at least one mp3 file has been found
		-	each 500ms it checks, if the next media file can be loaded
		-	if the current mp3 file can't be found, a warning into the log file is going to write instead,
			if logging is active

		---
		If the USB stick has been unplugged during playing, depending on given OS, a critical error is
		going to write into the log file, followed by to stop playing the current music file.

		On UNIX/Linux (and also possibly for macOS) supports:
		-	Path(mount_path).is_mount()

		On Windows:
		-	a help function is in use for USB device unplugging

		---
		"""
		#NOTE:	for Windows only
		if self.os == "Windows":
			self._init_usb_detection_windows()
		#end if

		mp3_files = [p for p in Path(self.usb_mount_point).rglob("*.mp3")]
		if len(mp3_files) == 0:
			if self.log_path_exists:
				self.log_handler.write_to_log(
					message="No mp3 files has been found.",
					log_level = LogLevel.WARNING
				)

			return
		#end if

		if self.play_in_random_order:
			shuffle(mp3_files)
		#end if

		mix.init()

		try:
			for file in mp3_files:
				if not file.exists():
					if self.log_path_exists:
						self.log_handler.write_to_log(
							message=f"skipped missing file: {str(file)}",
							log_level = LogLevel.WARNING
						)
					#end if
					continue
				#end if

				if self.log_path_exists:
					self.log_handler.write_to_log(message=f"playing file: {str(file)}")

				mix.music.load(str(file))
				mix.music.play()

				while mix.music.get_busy():
					#	check, if the USB device has suddenly been unplugged
					#	during playing music

					on_unplugged: bool = \
						(self.os == "linux" and not Path(self.usb_mount_point).is_mount()) or\
						(self.os == "Windows" and self._on_unplugged_usb_device_windows())

					if on_unplugged:
						if self.log_path_exists:
							self.log_handler.write_to_log(
								message=f"Mount lost during playback. Stopping...",
								log_level = LogLevel.CRITICAL
							)
						#end if

						mix.music.stop()
						mix.music.unload()
						mix.quit()
						return
					#end if

					#	wait 500ms for the next iteration
					sleep(0.5)
				#end while

				mix.music.unload()
			#end for
		except Exception as e:
			#NOTE:	can be an error by the mixer, Pathlib.exists(), ...
			self.log_handler.write_to_log(
				message=f"playback error ({type(e)}): {e.args}",
				log_level = LogLevel.ERROR,
				use_log_file=self.log_path_exists
			)

		finally:
			mix.quit()
		#end try
	#end method
#end class