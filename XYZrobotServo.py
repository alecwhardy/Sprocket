import time
import serial

ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

class XYZrobotServo:

	CMD_EEPROM_WRITE = 0x01
	CMD_EEPROM_READ  = 0x02
	CMD_RAM_WRITE    = 0x03
	CMD_RAM_READ     = 0x04
	CMD_I_JOG        = 0x05
	CMD_S_JOG        = 0x06
	CMD_STAT         = 0x07
	CMD_ROLLBACK     = 0x08
	CMD_REBOOT       = 0x09

	def __init__(self, stream, id, debug = False):
		self.stream = stream
		self.id = id
		self.lastError = None

	def sendRequest(self, cmd, data1, data2 = None):
		"""Sends a command to the servos.

		Args:
			cmd (byte): Use command constants from self.CMD_*.  Between 0x01 - 0x09
			data1 (bytearray): Data
			data2 (bytearray, optional): Data. Defaults to None.
		"""

		header = bytearray(7)
		size = len(data1) + len(data2) + len(header)
		checksum = size ^ self.id ^ cmd

		# Calculate checksum
		for i in range(len(data1)):
			checksum ^= data1[i]
		for j in range(len(data2)):
			checksum ^= data2[j]

		header[0] = 0xFF;
		header[1] = 0xFF;
		header[2] = size;
		header[3] = self.id;
		header[4] = cmd;
		header[5] = checksum & 0xFE;
		header[6] = ~checksum & 0xFE;

		self.stream.write(header)

		# TODO: Write Data!





	def readStatus(self):
		self.sendRequest(self.CMD_STAT, None, 0);

