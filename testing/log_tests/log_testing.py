#	Test cases for file logging.
#
#	author:		ITWorks4U
#	created:	July 25th, 2025
#	updated:	July 26th, 2025
#

import unittest as ut
from os.path import join, dirname
from pathlib import Path
from platform import system

from settings.config_settings import ConfigSettings
import logging
from logging.handlers import RotatingFileHandler

class LogTesting(ut.TestCase):
	def setUp(self) -> None:
		self.cs: ConfigSettings = ConfigSettings()
		self._detected_os = system()

		if self._detected_os == "Windows":
			#	only for Windows
			self.cfg_file = join(Path(__file__).resolve().parents[1], "config_tests", "dummy_windows.conf")
		else:
			#	for Linux / macOS
			self.cfg_file = join(Path(__file__).resolve().parents[1], "config_tests", "dummy_linux.conf")
		#end if

		#NOTE:
		#	10MB file size
		#	keep up to 10 files
		#	encoding is set to "latin-1"
		self._arguments = {}
		self._arguments["maxBytes"] = 10*10*1024
		self._arguments["backupCount"] = 10
		self._arguments["encoding"] = "latin-1"
	#end setup

	def tearDown(self) -> None:
		self.cs = None
	#end teardown

	def get_config_path(self) -> str:
		self.cs.load_config_file(self.cfg_file)

		if self._detected_os == "Windows":
			#NOTE:	assertion failure for /dev/null (Linux/macOS)
			self.assertTrue(self.cs.on_existsing_log_path(), msg="Usually, a log path shall be there...")
		#end if

		return join(self.cs.LogPath, "test.log")
	#end method

	def test_0_log_path_exists(self) -> None:
		_ = self.get_config_path()
	#end test

	def test_1_fail_to_create_log_file(self) -> None:
		#	receive the path for logging and try
		#	to create a log to that path
		#
		#	Since an invalid path or insufficient permissions
		#	are given, e. g. Windows <=> C:\, Linux <=> /dev/null
		#	this log file can't be created
		log_destination_path = self.get_config_path()

		#NOTE:
		#	for Linux/macOS: /dev/null is a "valid path", when the assertion
		#	in get_config_path has been skipped
		self.assertIsNot(log_destination_path, None, msg="The log destination path shall be able to use...")
		self._arguments["filename"] = log_destination_path

		#NOTE:
		#	Windows:	In C:\ drive usually it's not able to crate a log file there.
		#	Linux:		/dev/null raises a NotADirectoryError instead

		if self._detected_os == "Windows":
			with self.assertRaises(PermissionError):
				_ = RotatingFileHandler(**self._arguments)
			#end with
		else:
			with self.assertRaises(NotADirectoryError):
				_ = RotatingFileHandler(**self._arguments)
			#end with
		#end if
	#end test

	#NOTE:	No need to run this test over and over again.
	@ut.skip
	def test_2_successfully_create_log_file(self) -> None:
		#	Use this current path instead to create a log file.
		self._arguments["filename"] = join(dirname(__file__), "test.log")

		log_handler: RotatingFileHandler = RotatingFileHandler(**self._arguments)
		formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
		log_handler.setFormatter(formatter)

		logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])

		for i in range(500000):
			logging.debug(f"log message #{i}")
		#end for
	#end test
#end class