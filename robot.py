
from socket import socket
from binascii import hexlify

STOP 		= bytearray.fromhex("FF000000FF")
FORWARD 	= bytearray.fromhex("FF000100FF")
BACKWARD 	= bytearray.fromhex("FF000200FF")
ROTL 		= bytearray.fromhex("FF000300FF")
ROTR 		= bytearray.fromhex("FF000400FF")
SETRIGHT 	= "ff0201xff"
SETLEFT 	= "ff0202xff"

class Vehicle:
	def __init__(self):
		self.sock = socket()
		self.status = 0
		self.connected = False
		self.correctlyOriented = False
		self.rotated = False
		self.arrived = False
		self.mode = 0
		self.leftspeed = 0
		self.rightspeed = 0

	def rotate_to(self, cur_angle, req_angle, dist, error):
		angle = req_angle - cur_angle

		anglediff = abs(angle)
		if anglediff > 180:
			anglediff = 360 - anglediff

		if anglediff < error: return False
		# we are definitely going to turn
		if self.status != 1 and self.status != 2:
			self.stop()

		direction = 1 # CW
		if angle > 180 or (angle < 0 and angle > -180):
			direction = 0
		
		rotation_speed = int(anglediff / (180 * 4) * 100)
		# setting the speeds is an action in itself
		self.set_left_speed(rotation_speed)
		self.set_right_speed(rotation_speed)
		if direction == 0:
			if self.status == 1: self.stop()
			self.rotate_left()
		else:
			if self.status == 2: self.stop()
			self.rotate_right()

		return True

	def curve_to(self, cur_angle, req_angle, error, dist, fwd):
		angle = req_angle - cur_angle

		anglediff = abs(angle)
		if anglediff > 180:
			anglediff = 360 - anglediff

		if anglediff < error: return False
		if anglediff < 10:
			self.go_forward(fwd)
			return True
		# we are definitely going to turn

		if self.status != 5 and self.status != 6:
			self.stop()

		direction = 1 # CW
		if angle > 180 or (angle < 0 and angle > -180):
			direction = 0
		
		rotation_speed = int( anglediff/50 *100)
		# setting the speeds is an action in itself

		if direction == 1:
			self.curve_left(fwd, rotation_speed)
		else:
			self.curve_right(fwd, rotation_speed)

		return True


	def curve_right(self, forwardSpeed, difference):
		mySpeedRight = int(forwardSpeed - difference*forwardSpeed/100)
		mySpeedLeft = int(forwardSpeed + difference*forwardSpeed/100)
		print "curve right"
		self.set_right_speed(mySpeedRight)
		self.set_left_speed(mySpeedLeft)
		self.forward()
		self.status = 5

	def curve_left(self, forwardSpeed,difference):

		mySpeedRight = int(forwardSpeed + difference*forwardSpeed/100)
		mySpeedLeft = int(forwardSpeed - difference*forwardSpeed/100)
		print "curve left"
		self.set_right_speed(mySpeedRight)
		self.set_left_speed(mySpeedLeft)
		self.forward()
		self.status = 6

	def connect(self, ipAddr, port):
		try:
			self.sock.connect((ipAddr, port))
			self.connected = True
			self.stop()
		except:
			self.connected = False

	def stop(self):
		if self.status == 0: return
		print "Stop"
		self.sock.send(STOP)
		self.status = 0

	def go_forward(self, speed):
		print "moving forward"
		self.set_left_speed(speed)
		self.set_right_speed(speed)
		self.sock.send(FORWARD)
		self.status = 3

	def forward(self):
		if self.status == 3 or self.status == 5 or self.status == 6: return
		print "curving"
		self.sock.send(FORWARD)

	def backward(self):
		if self.status == 4: return
		self.sock.send(BACKWARD)
		self.status = 4

	def rotate_left(self):
		if self.status == 2: return
		print "rotating left"
		self.sock.send(ROTL)
		self.status = 2

	def rotate_right(self):
		if self.status == 1: return
		print "rotating right"
		self.sock.send(ROTR)
		self.status = 1

	def set_left_speed(self, leftspeed):
		if self.status != 0 and self.status != 3 and self.status != 5 and self.status != 6: return
		# print "set left speed = ", leftspeed
		commandleft = SETLEFT.replace("x", hex(leftspeed).replace("0x", "").zfill(2))
		self.sock.send(bytearray.fromhex(commandleft))

	def set_right_speed(self, rightspeed):
		if self.status != 0 and self.status != 3 and self.status != 5 and self.status != 5: return
		# print "set right speed = ", rightspeed
		rightspeed = hex(int(rightspeed))
		rightspeed = rightspeed.replace("0x","")
		rightspeed = rightspeed.zfill(2)
		commandright = SETRIGHT.replace("x", rightspeed)
		self.sock.send(bytearray.fromhex(commandright))

	def __del__(self):
		self.sock.shutdown(2)












