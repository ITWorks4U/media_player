#	Test cases for config file.
#
#	author:		ITWorks4U
#	created:	July 24th, 2025
#	updated:	July 25th, 2025
#

import unittest as ut
from os.path import join, dirname
from pathlib import Path

from settings.config_settings import ConfigSettings

class ConfigTester(ut.TestCase):
	"""
	Test cases for the config file. These are:

	-	test, if the config file exists
	-	test, if a log path exists
		-	if true, test, if the path is relative or absolute => must not contain a file
	-	test, if the USB mount point exists
		-	if true, test, if the path is also relative or absolute => must also not contain a file
	-	test, if the config file contains expected data to handle
	-	...
	"""
	_key_random_order = "play_in_random_order"
	_key_path_logging = "path_for_logging"
	_key_usb_mount_point = "usb_mount_point"

	def setUp(self) -> None:
		self.cs: ConfigSettings = ConfigSettings()

		self.config_files: list[str] = [
			join(Path(__file__).resolve().parents[2], "settings", "options.conf"),
			join(dirname(__file__), "dummy_windows.conf"),
			join(dirname(__file__), "dummy_linux.conf"),
			join(dirname(__file__), "dummy_any_other_config.conf")
		]
	#end setup

	def tearDown(self):
		self.cs = None
	#end teardown

	def test_0_if_file_exists(self) -> None:
		#	the config file settings/options.conf must exist
		for cfg in self.config_files:
			self.assertTrue(Path(cfg).exists())
		#end for
	#end test

	def test_1_if_values_exists(self) -> None:
		#	since the config file may not contain any value for
		#	the keys, an empty expression results, thus these
		#	key value pairs exists
		for cfg in self.config_files:
			self.assertTrue(self.cs.load_config_file(cfg_file=cfg))
			self.assertTrue(self._key_path_logging in self.cs.ConfigStorage, msg="Key does not exist.")
			self.assertTrue(self._key_usb_mount_point in self.cs.ConfigStorage, msg="Key does not exist.")
			self.assertTrue(self._key_random_order in self.cs.ConfigStorage, msg="Key does not exist.")
		#end for
	#end test

	@ut.expectedFailure
	def test_2_if_values_are_valid(self) -> None:
		#	the values of the config storage must not be an empty expression
		for cfg in self.config_files:
			self.cs.load_config_file(cfg_file=cfg)
			self.assertTrue(len(self.cs.ConfigStorage[self._key_path_logging]) > 0)
			self.assertTrue(len(self.cs.ConfigStorage[self._key_usb_mount_point]) > 0)
			self.assertTrue(len(self.cs.ConfigStorage[self._key_random_order]) > 0)
		#end for
	#end test

	@ut.expectedFailure
	def test_3_if_log_path_is_path(self) -> None:
		#	The internal config file comes with an empty expression
		#	for "path_for_logging" by default.
		#
		#	A failure results, if:
		#	-	the key does not exist (possibly by using a foreign config file)
		#	-	the value is not a string
		#	-	the word is empty
		#	-	the value is not a path, e. g. a file
		#	-	the path can't be found
		#	-	insufficient access rights

		#	expected a failure, because this file does not come with a log path
		for cfg in self.config_files:
			self.cs.load_config_file(cfg_file=cfg)
			self.assertTrue(self.cs.on_existsing_log_path(), msg="Usually, this mount point shall not existing...")
		#end for
	#end test

	@ut.expectedFailure
	def test_4_if_mount_point_is_path(self) -> None:
		#	Same action for USB mount point.
		for cfg in self.config_files:
			self.cs.load_config_file(cfg_file=cfg)
			self.assertTrue(self.cs.on_existing_mount_point(), msg="Mount path does not exist.")
		#end for
	#end test

	def test_5_for_convert_true(self) -> None:
		#	when "true" or "True" has been found,
		#	storage["play_in_random_order"] contains True

		values = ["true", "True"]
		for v in values:
			self.cs.ConfigStorage[self._key_random_order] = v
			self.cs.check_on_random_order()
			self.assertTrue(self.cs.ConfigStorage[self._key_random_order])
		#end for
	#end test

	def test_6_for_convert_false(self) -> None:
		#	when "false" or "False" or any other value has been found,
		#	storage["play_in_random_order"] contains False
		values = ["false", "False", "abc", "madamimadam.", "123", "0", "1", "", None]

		for v in values:
			self.cs.ConfigStorage[self._key_random_order] = v
			self.cs.check_on_random_order()
			self.assertFalse(self.cs.ConfigStorage[self._key_random_order])
		#end for
	#end test
#end class