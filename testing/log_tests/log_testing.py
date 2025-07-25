#	Test cases for file logging.
#
#	author:		ITWorks4U
#	created:	July 25th, 2025
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
		self.log_handler: RotatingFileHandler
		self._detected_os = system()

		if self._detected_os == "Windows":
			#	only for Windows
			self.cfg_file = join(Path(__file__).resolve().parents[1], "config_tests", "dummy_windows.conf")
		else:
			#	for Linux / macOS
			self.cfg_file = join(Path(__file__).resolve().parents[1], "config_tests", "dummy_linux.conf")
		#end if

		self._arguments = {}
		self._arguments["maxBytes"] = 10*10*1024
		self._arguments["backupCount"] = 10
		self._arguments["encoding"] = "latin-1"
	#end setup

	def tearDown(self) -> None:
		self.cs = None
		self.log_handler = None
	#end teardown

	def get_config_path(self) -> str:
		self.cs.load_config_file(self.cfg_file)
		self.assertTrue(self.cs.on_existsing_log_path(), msg="Usually, a log path shall be there...")

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
		self.assertIsNot(log_destination_path, None, msg="The log destination path shall be able to use...")

		if self._detected_os == "Windows":
			#NOTE:	In C:\ drive usually it's not able to crate a log file there. 
			self._arguments["filename"] = log_destination_path

			with self.assertRaises(PermissionError):
				self.log_handler = RotatingFileHandler(**self._arguments)
			#end with
		else:
			#TODO:	Check, how /dev/null would looks like for Linux / macOS
			pass
		#end if
	#end test

	def test_2_successfully_create_log_file(self) -> None:
		#	Use this current path instead to create a log file.
		self._arguments["filename"] = join(dirname(__file__), "test.log")

		self.log_handler = RotatingFileHandler(**self._arguments)
		formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
		self.log_handler.setFormatter(formatter)

		logging.basicConfig(level=logging.DEBUG, handlers=[self.log_handler])
		# self.log_handler.test_logging()

		for i in range(500000):
			logging.debug(f"log message #{i}")
		#end for
	#end test
#end class