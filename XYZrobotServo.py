from enum import Enum
from struct import *
import math

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

	SET_POSITION_CONTROL = 0
	SET_SPEED_CONTROL = 1
	SET_TORQUE_OFF = 2
	SET_POSITION_CONTROL_SERVO_ON = 3

	DEFAULT_RESPONSE_SIZE = 64

	class CommunicationError(Enum):
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

	class LED_Color():
		OFF = b'\x00'
		WHITE = b'\x01'
		BLUE = b'\x02'
		MAGENTA = b'\x0a'

	class ServoAckPolicy():
		ONLY_STAT = b'\x00'
		ONLY_READ_AND_STAT = b'\x01'
		ALL = b'\x02'

	class Status:
		
		def __init__(self, bytes_in):
			self.bytes = bytes_in
			raw = unpack('BBHHHH', bytes_in)
			self.statusError = raw[0]
			self.statusDetail = raw[1]
			self.pwm = raw[2]
			self.posRef = raw[3]
			self.position = raw[4]
			self.iBus = raw[5]

		def __repr__(self):

			resp = "PWM: " + str(self.pwm) + "\nP_R: " + str(self.posRef) + "\nPos: " + str(self.position) + "\n"
			return resp

		def __bytes__(self):
			return self.bytes


	def __init__(self, stream, id, debug = False):
		self.stream = stream
		self.id = id
		self.lastComError = None
		self.debug = debug

	def flushRead(self):
		""" Clears the serial buffer """
		# This is the equivalent of stream.available()
		while self.stream.in_waiting:
			self.stream.read()

	def memoryRead(self, cmd, startAddress, returnSize):
		
		self.flushRead()
		request = bytearray(2)
		request[0] = startAddress
		request[1] = returnSize

		self.sendRequest(cmd, request)

		response = bytearray(4)
		data = bytearray(returnSize)
		self.readAck(cmd, response, 4, data, returnSize)

		if self.lastComError != self.CommunicationError.NoError:
			return

		if response[2] != request[0]:
			self.lastComError = self.CommunicationError.ReadOffsetWrong
			return

		if response[3] != request[1]:
			self.lastComError = self.CommunicationError.ReadLengthWrong
			return

		return data

	def memoryWrite(self, cmd, startAddress, data):
		request = bytearray(2)
		request[0] = startAddress
		request[1] = len(data)
		self.sendRequest(cmd, request, data)

	def RAMRead(self, startAddress, dataSize):
		return self.memoryRead(self.CMD_RAM_READ, startAddress, dataSize)

	def EEPROMRead(self, startAddress, dataSize):
		return self.memoryRead(self.CMD_EEPROM_READ, startAddress, dataSize)

	def RAMWrite(self, startAddress, data):
		return self.memoryWrite(self.CMD_RAM_WRITE, startAddress, data)

	def writeAckPolicyRam(self, policy):
		self.RAMWrite(1, policy)

	def writeIDRAM(self, ID):
		ID_bytes = bytearray(1)
		ID_bytes[0] = ID
		self.RAMWrite(0, ID_bytes)

	def writeIDEEPROM(self, ID):
		ID_bytes = bytearray(1)
		ID_bytes[0] = ID
		self.memoryWrite(self.CMD_EEPROM_WRITE, 6, ID_bytes)

	def readIDEEPROM(self):
		ret = self.memoryRead(self.CMD_EEPROM_READ, 6, 1)
		return ret[0]


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
			print("Sending serial command: " + str(header))
		self.stream.write(header)

		if data1size > 0:
			self.stream.write(data1)
		if data2size > 0:
			self.stream.write(data2)
		self.lastComError = self.CommunicationError.NoError


	def readAck(self, cmd, data1, data1size, data2 = None, data2size = 0):
		""" Reads the response from the servo.  You must specify expected data return size to check for timeout

		Args:
			cmd (byte): [description]
			data1 (bytearray): [description]
			data1size (int): [description]
			data2 (bytearray, optional): [description]. Defaults to None.
			data2size (int, optional): [description]. Defaults to 0.

		Returns:
			header (bytes): header contents
		"""

		#The CMD byte for an acknowledgment always has bit 6 set.
		cmd |= 0x40

		response = bytearray(self.DEFAULT_RESPONSE_SIZE)
		header = bytearray(7)
		size = len(header) + data1size + data2size

		response = self.stream.read(len(header))
		if self.debug:
			print("Received serial data: " + str(response))
		
		# Check for timeout
		if len(response) != len(header):
			self.lastComError = self.CommunicationError.HeaderTimeout
			return
		
		# If no timeout, fill the contents of header with the contents of the response
		header[:] = response
		if header[0] != 0xFF:
			self.lastComError = self.CommunicationError.HeaderByte1Wrong
			return
		if header[1] != 0xFF:
			self.lastComError = self.CommunicationError.HeaderByte2Wrong
			return
		if header[3] != self.id:
			self.lastComError = self.CommunicationError.IdWrong
			return
		if header[4] != cmd:
			self.lastComError = self.CommunicationError.CmdWrong
			return
		if header[2] != size:
			self.lastComError = self.CommunicationError.SizeWrong
			return
		

		if data1size > 0:
			# Read the data
			response = self.stream.read(data1size)
			if self.debug:
				print("Received serial data1: " + str(response))
			if len(response) != data1size:
				self.lastComError = self.CommunicationError.Data1Timeout
				return
			# Copy the contents of response into data1
			data1[:] = response
		
		if data2size > 0:
			# Read the data
			response = self.stream.read(data2size)
			if self.debug:
				print("Received serial data2: " + response)
			if len(response) != data2size:
				self.lastComError = self.CommunicationError.Data2Timeout
				return
			# Copy the contents of response into data2
			data2[:] = response

		# Check the checksum!!!
		checksum = size ^ self.id ^ cmd
		for i in range(data1size):
			checksum ^= data1[i]
		for i in range(data2size):
			checksum ^= data2[i]

		if header[5] != checksum & 0xFE:
			self.lastComError = self.CommunicationError.Checksum1Wrong
			return
		if(header[6] != ~checksum & 0xFE):
			self.lastComError = self.CommunicationError.Checksum2Wrong
			return
		
		# If we get here, there is no error, set lastError appropriately
		self.lastComError = self.CommunicationError.NoError
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

	def setPosition(self, position, playtime):
		self.sendIJog(position, self.SET_POSITION_CONTROL, playtime)

	# TODO: TEST THIS!!!
	def getPosition(self):
		status = self.readStatus
		return status.position


	def set_position_deg(self, position_deg, playtime):
		
		x1 = -165
		x2 = position_deg
		x3 = 165
		y1 = 0
		y3 = 1023

		deg_setpoint = math.ceil((((x2-x1)*(y3-y1))/(x3-x1))+y1)
		self.setPosition(deg_setpoint, playtime)
		
	def sendIJog(self, goal, type, playtime):
		data = bytearray(5)
		data[0] = goal & 0xFF
		data[1] = goal >> 8 & 0xFF
		data[2] = type
		data[3] = self.id
		data[4] = playtime
		self.sendRequest(self.CMD_I_JOG, data)

	def readPID_RAM(self):
		ret_data = self.RAMRead(24, 6)
		Kp = ret_data[0] + (ret_data[1] << 8)
		Kd = ret_data[2] + (ret_data[3] << 8)
		Ki = ret_data[4] + (ret_data[5] << 8)
		return Kp, Ki, Kd

	def readP_RAM(self):
		ret_data = self.RAMRead(24, 2)
		return ret_data

	def torqueOff(self):
		self.sendIJog(0, self.SET_TORQUE_OFF, 0)


		led_color = bytearray(1)
		led_color[0] = 0b0010

		self.set_LED_alarm_policy()   # Set LED policy to user choice
		self.RAMWrite(53, led_color)  # LED turns Blue

	def reboot(self):
		self.sendRequest(self.CMD_REBOOT, None)

	def getVoltage(self):
		return int(self.RAMRead(54, 1)[0])/16

	def set_LED(self, color_policy_byte):
		self.RAMWrite(53, color_policy_byte)

	def set_LED_alarm_policy(self, all_LEDs = True, policy_byte = None):
		""" Set the LED alarm policy. Defaults to user controlled if no arguments are passed

		Args:
			all_LEDs (bool, optional): Set this False and pass a policy_byte if not controlling all LEDs. Defaults to True.
		"""
		if all_LEDs:
			policy_byte = b'\x0f'
		self.RAMWrite(2, policy_byte)

	def reset_LED_alarm_policy(self,  EEPROM=False):
		""" Restore the original LED Alarm policy (change color on servo error)

		Args:
			EEPROM (bool, optional): Write to EEPROM. Defaults to False.  Not supported.
		"""
		if EEPROM:
			print("Unimplemented: Write LED policy to EEPROM")
		else:
			# Write the LED Alarm policy back to default (0)
			self.RAMWrite(2, b'\x00')



class XYZrobotServos:

	status = [None] * 12

	def __init__(self, servos):
		self.servos = servos

	def __getitem__(self, key):
		return self.servos[key]

	def updateAllStatus(self):
		for idx, servo in enumerate(self.servos):
			self.status[idx] = servo.readStatus()

	def __bytes__(self):
		output = bytearray()
		for servo_status in self.status:
			output += servo_status.bytes
		return bytes(output)



if __name__ == "__main__":
	import serial, time
	
	ser = serial.Serial('/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
	i = 0 # motor number
	leg_servo = XYZrobotServo(ser, i+1, debug=False)
	while True:
		status = leg_servo.readStatus()
		print(status)
		time.sleep(0.01)


