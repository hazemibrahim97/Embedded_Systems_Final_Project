import tuio
import socket
import math
from time import sleep, time
import robot as vehicle

TARGET_ID = 0
ROBOT_ID = 3

PERIOD = 200 # ms

def main():

	tracking = tuio.Tracking()
	
	myVehicle = vehicle.Vehicle()
	myVehicle.connect("192.168.1.1", 2001)

	mode = input("Enter mode of operation  : \n 1. Go to a point \n 2. Follow another robot \n 3. Follow trajectory \n")
	mode = int(mode)
	while (mode != 1 and mode != 2 and mode != 3) :
		print "Please enter a valid mode! "
		mode = input("Enter mode of operation  : \n 1. Go to a point \n 2. Follow another robot \n 3. Follow trajectory \n")
		mode = int(mode)

	trajectory = [(0.85, 0.50), (0.83, 0.72), (0.77, 0.84), (0.68, 0.80), (0.56, 0.62), (0.44, 0.38), (0.32, 0.20), (0.23, 0.16), (0.17, 0.28), (0.15, 0.50)]
	trajectoryindex = 0
	target = None
	robot = None

	update_time = time()
	prev_angle = 0
	prev_x = 0
	prev_y = 0

	maxDist = 0.2
	if mode == 3: maxDist = 0.1

	f = open("log.csv", "w")

	while 1:
		try:
			
			tracking.update()
			robotFound = False
			for obj in tracking.objects():
				if obj.id == TARGET_ID:
					target = obj
				elif obj.id == ROBOT_ID:
					robot = obj
					robotFound = True
				else:
					print "undefined object: ", obj
			
			if(mode == 2) :			
				if not robotFound or target == None:
					print "ROBOT NOT FOUND"
					myVehicle.stop()
					continue
			elif (mode == 3):
				if not robotFound:
					print "ROBOT NOT FOUND"
					myVehicle.stop()
					continue
			

			if(mode == 2) :	
				req_or = get_required_orientation(robot.xpos, robot.ypos,target.xpos , target.ypos)
				dist = get_distance(robot.xpos, robot.ypos, target.xpos, target.ypos)

			elif (mode == 3) :
				#print "robot xpos = ", robot.xpos, " robot ypos = ", robot.ypos
				req_or = get_required_orientation(robot.xpos, robot.ypos, trajectory[trajectoryindex][0], trajectory[trajectoryindex][1])
				dist = get_distance(robot.xpos, robot.ypos, trajectory[trajectoryindex][0], trajectory[trajectoryindex][1])

			cur_angle = robot.angle

			if prev_x == robot.xpos and prev_y == robot.ypos and myVehicle.status != 0:
				#print "stuck"
				continue
			elif cur_angle == prev_angle and myVehicle.status != 0 and myVehicle.status != 3 and myVehicle.status != 4 and prev_x == robot.xpos and prev_y == robot.ypos:
				print "rotation stuck"
				continue
			else:
				prev_angle = cur_angle
				prev_x = robot.xpos
				prev_y = robot.ypos
				# print "update time: ", time() - update_time
				# update_time = time()
				#print "loopin"

			
			req = req_or
			if req > 180:
				req = req - 360
			cur = cur_angle
			if cur > 180:
				cur = cur - 360

			if dist < maxDist and mode ==2:
				myVehicle.stop()
			else:
				if not myVehicle.rotate_to(cur, req, dist, 50):
					myVehicle.curve_to(cur, req, 0, dist, 40)
						# myVehicle.go_forward(60)
			

			if mode == 3 and dist < maxDist:
				f.write(str(robot.xpos) + ", " + str(robot.ypos) + ", " + str(time() - update_time) + ", " + str(trajectoryindex) + ", " + str(trajectory[trajectoryindex][0]) + ", " +  str(trajectory[trajectoryindex][1]) + "\n")
				if trajectoryindex < len(trajectory) - 1:
					trajectoryindex += 1
					if trajectoryindex == 1:
						update_time = time()
				else:
					break

		except KeyboardInterrupt:
			break

	myVehicle.stop()
	tracking.stop()
	f.close()
	print "runtime: ", time() - update_time


def get_required_orientation(srcx, srcy, dstx, dsty):
	if(dstx < srcx):
		return math.degrees(math.atan((dsty - srcy) / (dstx - srcx))) + 180
	elif (dstx > srcx):
		if(dsty < srcy):
			return math.degrees(math.atan((dsty - srcy) / (dstx - srcx))) + 360 
		elif (dsty > srcy):
			return math.degrees(math.atan((dsty - srcy) / (dstx - srcx)))
		
def get_distance(srcx, srcy, dstx, dsty):
	return math.sqrt((dstx - srcx)**2 + (dsty - srcy)**2)



if __name__ == '__main__':
	main()




