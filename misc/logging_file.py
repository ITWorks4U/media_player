#	A logging for stdout and stderr exists, where the log is hold for 7 days
#	and also has a size limitation of 10MB for each log.
#
#	author:		ITWorks4U
#	created:	July 20th, 2025
#	updated:	July 23rd, 2025
#

import logging
from logging.handlers import TimedRotatingFileHandler
import os

from misc.log_level import LogLevel

class RotatingFileLogging(TimedRotatingFileHandler):
	def __init__(self, log_destination_path: str, when='D', interval=1, backup_count=7, max_bytes=10*1024*1024, encoding="latin-1") -> None:
		"""
		Initializing a new log record with presets. These presets are:
		-	maximum storage duration of 7 days
		-	size limitation of 10 MB
		-	encoding is set to latin-1

		log_destination_path:
		-	where the log record shall be located

		when:
		-	when a rotation is planned to use
		-	defaults to "dayly" ("D")

		interval:
		-	how often the interval is in use
		-	defaults to 1

		backup_count:
		-	the number of days to hold a log record

		max_bytes:
		-	upper boundary for log record size in MB

		encoding:
		-	encoded format for log record
		"""
		full_path_name = os.path.join(log_destination_path, "media_player.log")

		super().__init__(filename=full_path_name, when=when, interval=interval, backupCount=backup_count, encoding=encoding)
		self.max_bytes = max_bytes
	#end constructor

	def shouldRollover(self, record) -> bool:
		"""
		Check, if the current log may rollover. This is true only,
		if a next day appears or if the size exceeds the limitation
		of 10MB.

		record:
		-	current record to check

		returns:
		-	True, if a rollover is required
		-	False, otherwise
		"""

		#time based rollover
		if super().shouldRollover(record):
			return True
		#end if

		#size based rollover
		if self.stream is None:
			self.stream = self._open()
		#end if

		self.stream.flush()

		# summary = f"""
		# current file size: {os.stat(self.baseFilename).st_size} MB
		# max size set: {self.max_bytes} MB
		# """
		# print(summary)

		if os.stat(self.baseFilename).st_size >= self.max_bytes:
			return True
		#end if

		return False
	#end method

	def test_logging(self) -> None:
		"""
		Just a test for logging.
		"""

		#NOTE: does not work fine yet
		for i in range(500000):
			logging.info(f"log message #{i}")
		#end for
	#end function

	def write_to_log(self, message: str, log_level: LogLevel = LogLevel.INFO) -> None:
		"""
		Write the next message to the log file depending on the logging level.

		message:
		-	message to write

		log_level:
		-	certain log level
		-	defaults to INFO
		"""
		match log_level:
			case LogLevel.WARNING:
				logging.warning(message)
			case LogLevel.ERROR:
				logging.error(message)
			case LogLevel.CRITICAL:
				logging.critical(message)
			case LogLevel.DEBUG:
				logging.debug(message)
			case _:
				# defaults to INFO
				logging.info(message)
			#end cases
		#end match
	#end method
#end class

