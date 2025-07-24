#	Playing mp3 files from the first detected USB device.
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#	updated:	July 23rd, 2025
#

#	global setting, if the player module is available or not
#	defaults to true
PLAYER_AVAILABLE: bool = True

#	base modules
from random import shuffle
from time import sleep
from dataclasses import dataclass
from pathlib import Path
from threading import Event

#	custom module(s)
from misc.logging_file import RotatingFileLogging
from misc.log_level import LogLevel
from misc.import_print_stdout import print_to_stdout
from thread_handling.usb_monitor import USBMonitor

#	3rd party module(s)
try:
	import pygame.mixer as mix
except ImportError:
	PLAYER_AVAILABLE = False
	print_to_stdout(module_name="pygame")
#end try

@dataclass
class MediaPlayer:
	"""
	Offers to play mp3 files from an USB device or a local folder.
	"""
	#	---------------
	#	USB mount point; can also be used for a local drive
	usb_mount_point: str

	#	if set, then the music files are playing in a random order
	play_in_random_order: bool

	#	handler for logging; can be None, if no log has been detected
	log_handler: RotatingFileLogging

	#	internal flag for 'for-loop' in play_audio_files
	_on_continue: bool = True

	def play_audio_files(self) -> None:
		"""
		-	playing the mp3 files
		-	this works only, if at least one mp3 file has been found
		-	each 100ms it checks, if the next media file can be loaded
		-	if the current mp3 file can't be found, a warning into the log file is going to write instead,
			if logging is active

		---
		A second thread checks, if at any time an USB device has been unplugged
		to stop the playback immediately.
		"""
		mp3_files: list[Path] = [p for p in Path(self.usb_mount_point).rglob("*.mp3")]
		if len(mp3_files) == 0:
			if self.log_handler is not None:
				self.log_handler.write_to_log(message="No mp3 files have been found. Terminating...")
			#end if

			return
		#end if

		if self.play_in_random_order:
			shuffle(mp3_files)
		#end if

		#	initialize the mixer
		mix.init()

		try:
			for file in mp3_files:
				if not self._on_continue:
					break
				#end if

				if not file.exists():
					if self.log_handler is not None:
						self.log_handler.write_to_log(
							message=f"skipped missing file: {str(file)}",
							log_level = LogLevel.WARNING
						)
					#end if
					continue
				#end if

				if self.log_handler is not None:
					self.log_handler.write_to_log(message=f"playing file: {str(file)}")
				#end if

				event_listener: Event = Event()
				monitoring: USBMonitor = USBMonitor(
					usb_mount_point = self.usb_mount_point,
					mp3_file_path = file,
					unplugged_event=event_listener,
					handler=self.log_handler
				)
				monitoring.start()

				mix.music.load(str(file))
				mix.music.play()

				while mix.music.get_busy():
					if event_listener.is_set():
						#NOTE:
						#	If the second thread has detected, that the
						#	USB device has been unplugged, then stop the
						#	player immediately.
						self._on_continue = False
						mix.stop()
						break
					#end if

					#	wait 100ms for the next iteration
					sleep(0.1)
				#end while

				mix.music.unload()
			#end for
		except Exception as e:
			#NOTE:	can be an error by the mixer, Pathlib.exists(), ...
			if self.log_handler is not None:
				self.log_handler.write_to_log(
					message=f"playback error ({type(e)}): {e.args}",
					log_level = LogLevel.ERROR
				)
			#end if

		finally:
			mix.quit()
		#end try
	#end method
#end class