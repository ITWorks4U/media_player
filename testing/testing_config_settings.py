#	Test cases for config file.
#
#	author:		ITWorks4U
#	created:	July 24th, 2025
#	updated:	July 25th, 2025
#

import unittest as ut

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
	