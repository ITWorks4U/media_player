class VersionUpdater:
	"""
	customized version updater during development
	"""
	def __init__(self, major: int, minor: int, patch: int, build: int):
		self.major:int = major
		self.minor:int = minor
		self.patch:int = patch
		self.build:int = build
	#end constructor

	@classmethod
	def from_string(cls, version_str: str):
		parts = list(map(int, version_str.strip().split(".")))
		return cls(*parts)
	#end method

	@classmethod
	def load_current_version(cls, file_path: str):
		with open(file_path) as f:
			version_str = f.read().strip()
		#end with

		return cls.from_string(version_str)
	#end method

	def __str__(self):
		return f"{self.major}.{self.minor}.{self.patch}.{self.build}"
	#end method

	def update_version(self, file_path: str):
		with open(file=file_path, mode='w', encoding="latin-1") as f:
			f.write(str(self))
		#end with
	#end method

	def bump_build(self):
		self.build += 1
	#end method

	def bump_patch(self):
		self.patch += 1
		self.build = 0
	#end method

	def bump_minor(self):
		self.minor += 1
		self.patch = 0
		self.build = 0
	#end method

	def bump_major(self):
		self.major += 1
		self.minor = 0
		self.patch = 0
		self.build = 0
	#end method
#end class