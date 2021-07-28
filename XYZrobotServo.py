from io import RawIOBase
import serial
from enum import Enum
from struct import *

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

	class Error(Enum):
		# No error.
		NoError = 0

		# There was a timeout waiting to receive the 7-byte acknowledgment header.
		HeaderTimeout = 1

		# The first byte of received header was not 0xFF.
		HeaderByte1Wrong = 2

		# The second byte of the received header was not 0xFF.
		HeaderByte2Wrong = 3

		# The ID byte in the received header was wrong.
		IdWrong = 4

		# The CMD bytes in the received header was wrong.
		CmdWrong = 5

		# The size byte in the received header was wrong.
		SizeWrong = 6

		# There was a timeout reading the first expected block of data in the
		# acknowledgment.
		Data1Timeout = 7

		# There was a timeout reading the second expected block of data in the
		# acknowledgment.
		Data2Timeout = 8

		# The first byte of the checksum was wrong.
		Checksum1Wrong = 9

		# The second byte of the checksum was wrong.
		Checksum2Wrong = 10

		# The offset byte returned by an EEPROM Read or RAM Read command was wrong.
		ReadOffsetWrong = 16

		# The length byte returned by an EEPROM Read or RAM Read command was wrong.
		ReadLengthWrong = 17

	class Status:
		def __init__(self, bytes):
			raw = unpack('BBHHHH', bytes)
			self.statusError = raw[0]
			self.statusDetail = raw[1]
			self.pwm = raw[2]
			self.posRef = raw[3]
			self.position = raw[4]
			self.iBus = raw[5]


	def __init__(self, stream, id, debug = False):
		self.stream = stream
		self.id = id
		self.lastError = None
		self.debug = debug

	def flushRead(self):
		""" Clears the serial buffer """
		# This is the equivalent of stream.available()
		while self.stream.in_waiting:
			self.stream.read()


	def sendRequest(self, cmd, data1, data2 = None):
		""" Sends a command to the servos.

		Args:
			cmd (byte): Use command constants from self.CMD_*.  Between 0x01 - 0x09
			data1 (bytearray): Data
			data2 (bytearray, optional): Data. Defaults to None.
		"""

		data1size = 0 if data1 is None else len(data1)
		data2size = 0 if data2 is None else len(data2)

		header = bytearray(7)
		size = data1size + data2size + len(header)
		checksum = size ^ self.id ^ cmd

		# Calculate checksum
		for i in range(data1size):
			checksum ^= data1[i]
		for j in range(data2size):
			checksum ^= data2[j]

		header[0] = 0xFF
		header[1] = 0xFF
		header[2] = size
		header[3] = self.id
		header[4] = cmd
		header[5] = checksum & 0xFE
		header[6] = ~checksum & 0xFE

		if self.debug:
			print(header)
		self.stream.write(header)

		# TODO: Write actual data here


	def readAck(self, cmd, data1, data1size, data2 = None, data2size = 0):
		""" Reads the response from the servo.  You must specify expected data return size to check for timeout

		Args:
			cmd (byte): [description]
			data1 (bytearray): [description]
			data1size (int): [description]
			data2 (bytearray, optional): [description]. Defaults to None.
			data2size (int, optional): [description]. Defaults to 0.
		"""

		#The CMD byte for an acknowledgment always has bit 6 set.
		cmd |= 0x40

		response = bytearray(100)
		header = bytearray(7)
		size = len(header) + data1size + data2size

		response = self.stream.read(len(header))
		header = response
		if len(response) != len(header):
			self.lastError = self.Error.HeaderTimeout
			return
		if header[0] != 0xFF:
			self.lastError = self.Error.HeaderByte1Wrong
			return
		if header[1] != 0xFF:
			self.lastError = self.Error.HeaderByte2Wrong
			return
		if header[3] != self.id:
			self.lastError = self.Error.IdWrong
			return
		if header[4] != cmd:
			self.lastError = self.Error.CmdWrong
			return
		if header[2] != size:
			self.lastError = self.Error.SizeWrong
			return
		

		if data1size > 0:
			# Read the data
			response = self.stream.read(data1size)
			if len(response) != data1size:
				self.lastError = self.Error.Data1Timeout
				return
			# Copy the contents of response into data1
			data1[:] = response
		
		if data2size > 0:
			# Read the data
			response = self.stream.read(data2size)
			if len(response) != data2size:
				self.lastError = self.Error.Data2Timeout
				return
			# Copy the contents of response into data2
			data2[:] = response

		# TODO: Check the checksum!!!
		"""  
		uint8_t checksum = size ^ id ^ cmd;
		for (uint8_t i = 0; i < data1Size; i++) { checksum ^= data1[i]; }
		for (uint8_t i = 0; i < data2Size; i++) { checksum ^= data2[i]; }

		if (header[5] != (checksum & 0xFE))
		{
			lastError = XYZrobotServoError::Checksum1Wrong;
			return;
		}

		if (header[6] != (~checksum & 0xFE))
		{
			lastError = XYZrobotServoError::Checksum2Wrong;
			return;
		}
  		"""

		self.lastError = self.Error.NoError
		return header

	def readStatus(self):
		""" Reads the status of the servo and returns a Status object

		Returns:
			[XYZrobotServo.Status]: Status of the servo
		"""
		status_response = bytearray(10)

		self.flushRead()
		self.sendRequest(self.CMD_STAT, None)
		ack_header = self.readAck(self.CMD_STAT, status_response, 10)
		return self.Status(status_response)
		


