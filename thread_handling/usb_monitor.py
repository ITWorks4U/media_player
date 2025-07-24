#	Monitoring the USB device in an own thread to check,
#	if the USB device has suddenly been unplugged.
#
#	author:		ITWorks4U
#	created:	July 23rd, 2025
#	updated:	July 24th, 2025
#

from threading import Thread, Event
from time import sleep
from pathlib import Path
from platform import system

from misc.logging_file import RotatingFileLogging, LogLevel

class USBMonitor(Thread):
	"""
	Monitoring the USB device in an own thread to reduce
	usage on main CPU core and speed up the performance.

	This shall work on every OS.
	"""
	def __init__(self, usb_mount_point: str, mp3_file_path: str, unplugged_event: Event, handler: RotatingFileLogging) -> None:
		"""
		Create a new background thread for the current used mp3 file to check, whenever
		an used USB device has suddenly been detached from the system. This check repeats
		every 100ms.

		usb_mount_point:
		-	used mount point

		mp3_file_path:
		-	currently used mp3 file

		unplugged_event:
		-	registered event, whenever an unplug has been detected

		handler:
		-	used file handler for logging, if given
		"""

		super().__init__(daemon=True)

		#	stores the current used OS
		self._os = system()

		#	mount point (more in use for Linux, macOS)
		self._usb_mount_point: Path = Path(usb_mount_point)

		#	mp3 file (more in use for Windows)
		self._mp3_file_path: Path = Path(mp3_file_path)

		#	thread event for USB unplug detection
		self._on_unplugged_event: Event = unplugged_event

		#	handler for logging
		self._log_handler: RotatingFileLogging = handler

		#	interval of 100ms for USB unplugging detection
		self._check_interval: float = 0.1

		#	flag for thread run
		self._running: bool = True
	#end constructor

	#	---------------
	#	methods
	#	---------------
	def run(self) -> None:
		"""
		Run the monitoring thread. Whenever in a time interval of 100ms the USB device has
		suddenly been detached from the system, a message is going to write to the log file
		followed by stopping the monitoring and also stopping the playback.
		"""
		while self._running:
			is_unplugged: bool = \
				self._os in ["linux", "darwin"] and not self._usb_mount_point.is_mount() or \
				self._os == "windows" and not self._mp3_file_path.exists()

			if is_unplugged and self._log_handler is not None:
				self._log_handler.write_to_log(
					message="[Monitoring] USB device has been unplugged",
					log_level=LogLevel.CRITICAL
				)
				self._on_unplugged_event.set()
				self._running = False
			#end if

			sleep(self._check_interval)
		#end while
	#end method
#end class