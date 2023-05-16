import threading
import os
import subprocess

class LogPipe(threading.Thread):
	def __init__(self, logger, level):
		threading.Thread.__init__(self)
		self.daemon = False
		self.logger = logger
		self.level = level
		self.fdRead, self.fdWrite = os.pipe()
		self.pipeReader = os.fdopen(self.fdRead)
		self.start()

	def fileno(self):
		return self.fdWrite

	def run(self):
		for line in iter(self.pipeReader.readline, ''):
			self.logger.log(self.level, line.strip('\n'))
		self.pipeReader.close()

	def close(self):
		os.close(self.fdWrite)
