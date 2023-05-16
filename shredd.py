import time, sys, logging, signal
import pyudev
import subprocess
from concurrent.futures import ThreadPoolExecutor as Pool
from daemon import Daemon
from logpipe import LogPipe
import re

logFile = "/root/shredd/a.log"

loggerRoot = logging.getLogger()
loggerRoot.setLevel(logging.DEBUG)
formatString = "%(asctime)s | %(name)s | %(process)05d | %(threadName)-10s | %(levelname)s | %(message)s"
formatterRoot = logging.Formatter(formatString)
file_handler_root = logging.FileHandler(logFile)
file_handler_root.setFormatter(formatterRoot)
loggerRoot.addHandler(file_handler_root)

pool = Pool(max_workers=6)

class Device(object):
	@classmethod
	def shred(self, device, logger):
		logpipe = LogPipe(logger, logging.INFO)
#		proc = subprocess.Popen(['shred', '-v', '-z', '-n1', device.device_node], stdout=logpipe, stderr=logpipe)
##		logger.info(proc)
#		logger.info(proc.pid)
#		return proc

	@classmethod
	def add(self, device, logger):
		logger.info("adding ...")
		logger.info(device)

#		worker = pool.submit(self.shred, device, logger)
#		worker = pool.submit(subprocess.Popen, ['shred', '-v', '-z', '-n1', device.device_node], stdout=logpipe, stderr=logpipe)
#		logger.info(worker)
		proc = self.shred(device, logger)
		return proc

	@classmethod
	def remove(self, device, logger):
		logger.info("removed")
		logger.info(device)
		logger.info(pool)
		print('\a')

class MyDaemon(Daemon):
	running = {}

	def createLogger(self, job_name, log_file):
		logger = logging.getLogger(job_name)
		## create a file handler ##
		handler = logging.FileHandler(log_file)
		## create a logging format ##
		formatter = logging.Formatter(formatString)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		return logger

	def monitorProc(self, proc, logger):
		while 1:
			time.sleep(2)
			logger.info(proc)
			logger.info(proc.communicate())
			logger.info(proc.send_signal(signal.SIGTTIN))

	def run(self):
		while True:
			try:
				context = pyudev.Context()
				monitor = pyudev.Monitor.from_netlink(context)
#				monitor.filter_by(subsystem='usb')
#				monitor.filter_by('block')
				for device in iter(monitor.poll, None):
					if (
#						device.device_path.index("/devices/pci0000:00/0000:00:17.0") == 0
						device.device_type == "disk"
					):
						try:
							re.search('ata.?/', device.device_path).group()

							try:
								host = re.search('host.?', device.device_path).group()

								logger = self.createLogger(host, logFile)

								logger.info(host)

								if device.action == 'add':
									self.running[host] = Device.add(device, logger)
#									logger.info(self.running)

#									self.monitorProc(self.running[host], logger)
								elif device.action == 'remove':
									Device.remove(device, logger)
							except AttributeError as e:
								loggerRoot.info(e)

						except AttributeError:
							loggerRoot.info("not an ata device")
			except ValueError:
				loggerRoot.info("Device not whitelisted")
			except AttributeError:
				loggerRoot.info("host could not be determined or is not an ata device")
			except Exception as e:
				loggerRoot.exception(e)

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/shredd.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print("Unknown command")
			sys.exit(2)
		sys.exit(0)
	else:
		print("usage: %s start|stop|restart" % sys.argv[0])
		sys.exit(2)
