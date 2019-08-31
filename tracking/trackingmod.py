from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import datetime
import os.path
import math

class MultiTissueTracker():
	def __init__(self, params):
		#Initalize trackers
		self.trackers = cv2.MultiTracker_create()
		#Initalize video stream
		self.vs = cv2.VideoCapture(params['VIDEOPATH'])
		#Initialize tissue dictionary from PARAMS we will get TissueID, and generate file names
		self.tissuedict = {}
		#Populate tissue dictionary
		for i in range(params['LASTTISSUE'] + 1 - params['FIRSTTISSUE']):
			dummy = {}
			dummy["abstissueID"] = (params['FIRSTTISSUE'] + i)
			dummy["crosssect"] = 0
			dummy["txtfile"] = open('{2}/T{0}@{1}Hz_{3}.txt'.format((params['FIRSTTISSUE'] + i), params['PACINGFREQ'], params['SAVE'], params['DAY']), "w")
			dummy["csvfile"] = open('{2}/T{0}@{1}Hz_{3}.csv'.format((params['FIRSTTISSUE'] + i), params['PACINGFREQ'], params['SAVE'], params['DAY']), "w")
			#dummy["datfile"] = open('{2}/T{0} @ {1} hz 001.dat'.format((params['FIRSTTISSUE'] + i), params['PACINGFREQ'], params['SAVE']), "w")
			dummy["nummeasurments"] = 0
			self.tissuedict[i] = dummy
			self.tissuedict[i]['csvfile'].write('time' + ',' + 'disp' + ',' + 'x1' + ',' + 'y1' + ',' + 'x2' + ',' + 'y2' + ',' + 'crosssect' + '\n')

		#Initialize the opencv trackers
		self.OPENCV_OBJECT_TRACKERS = {
			"csrt": cv2.TrackerCSRT_create,
			"kcf": cv2.TrackerKCF_create,
			"boosting": cv2.TrackerBoosting_create,
			"mil": cv2.TrackerMIL_create,
			"tld": cv2.TrackerTLD_create,
			"medianflow": cv2.TrackerMedianFlow_create,
			"mosse": cv2.TrackerMOSSE_create
		}
		#Set calib factor to 0, used as a check to make sure system has been calibrated
		self.calib_factor = 0
		#start the program
		self.loopframes(params)

	def loopframes(self, params):
		#Loop while frames still exist and 'q' hasnt been pressed
		while True:
			#Read in the frame, [1] is the image part of the vs.read
			frame = self.vs.read()[1]

			#Break if and write text file if there are no more frames
			if frame is None:
				self.writetotxt(params)
				break

			#Resize the frame, maybe add user input
			#frame = imutils.rotate(frame, angle=90)
			frame = imutils.resize(frame, width=params['FRAMEWIDTH'])
			#Needed to read in q, s, c, l
			key = cv2.waitKey(1) & 0xFF

			#If 's' is pressed select post
			if key == ord('s'):
				#If the calib_factor has not been changed from 0 do not select posts
				if (self.calib_factor) == 0:
					print("Calibration Needed, press c")
				#If cross sect has not been done do not select posts
				elif (self.tissuedict[0]['crosssect']) == 0:
					print("Cross sections needed, press l")
				#select post
				else:
					for i in range(2*(params['LASTTISSUE'] + 1 - params['FIRSTTISSUE'])):
						self.postselection(frame, params['TRACKER'])
			#Press C to call the calibrate function
			if key == ord('c'):
				self.calibrate(frame, params['CALIBDIST'])
			#Press L to call the cross sect function
			if key == ord('l'):
				for i in range(params['LASTTISSUE'] + 1 - params['FIRSTTISSUE']):
					self.crosssection(frame, i)
			#Press q to break and write text files
			if key == ord('q'):
				self.writetotxt(params)
				break
			#Process the current frame
			self.processframe(frame)


	def processframe(self, frame):
		#Read the tracker from the frame
		posts = self.trackers.update(frame)[1]
		#Initialize list used to call centroid function, Can maybe cut out centroidtracker.py, LOOK INTO THIS
		postcords = []
		# loop over the bounding boxes and draw then on the frame
		for post in posts:
			#Used float for more acuracy but rectangle needs int
			(x, y, w, h) = [float(i) for i in post]
			(rx, ry, rw, rh) = [int(i) for i in (x, y, w, h)]
			cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
			#Populate list for centroid tracking
			postcords.append((x, y, x + w, y + h))
		#Process the object created
		self.processposts(frame, self.centroid(postcords))
		#Show the frame
		cv2.imshow("Frame", frame)


	def processposts(self, frame, posts):
		for (objectID, centroid) in posts.items():
			# draw both the ID of the object and the centroid of the
			# object on the output frame
			text = "{}".format(objectID)

			cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

			#If the object ID is even that means it does not have a pair, so save it but do nothing
			if (objectID % 2) == 0:
				#Save the x position of the even post
				evenX = centroid[0]/self.calib_factor
				#Save the y position of the even post
				evenY = centroid[1]/self.calib_factor
				evenID = objectID
			#If objectID is odd it has a pair so do stuff
			elif (objectID - 1) == evenID:
				#Calculate tissue number based on object ID
				reltissueID = int((objectID - 1)/2)
				#Save the x position of the odd post
				oddX = (centroid[0]/self.calib_factor)
				#Save the y position of the odd post
				oddY = (centroid[1]/self.calib_factor)
				#Get the time in seconds
				time = self.vs.get(cv2.CAP_PROP_POS_MSEC)/1000
				disp = np.sqrt(((oddX - evenX)**2) + ((oddY - evenY)**2))
				self.tissuedict[reltissueID]['nummeasurments'] += 1
				self.writetocsv(reltissueID, disp, evenX, evenY, oddX, oddY, self.tissuedict[reltissueID]['crosssect'], time)

	def calibrate(self, frame, calibration_dist):
		#Draw box on current frame
		line = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
		#Take width of box(pixels), divide by calibration distance(mm) to get calibration factor
		(x, y, w, h) = [int(v) for v in line]
		dist = np.sqrt(((w)**2) + (h)**2)
		self.calib_factor = dist/calibration_dist

	def crosssection(self, frame, reltissueID):
		#Draw box on current frame
		line = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
		#Divide height of box(pixels) by calibration factor (pixels/mm) to get height(mm)
		(x, y, w, h) = [int(v) for v in line]
		dist = np.sqrt(((w)**2) + (h)**2)
		height = dist/self.calib_factor
		cx = ((height/2)**2) * np.pi
		#Write cross sectional area (assuming cylinder) to list
		self.tissuedict[reltissueID]["crosssect"] = cx

	def postselection(self, frame, trackertype):
		#Draw box on current frame
		box = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
		# create a new object tracker for the bounding box and add it
		# to our multi-object tracker
		tracker = self.OPENCV_OBJECT_TRACKERS[trackertype]()
		self.trackers.add(tracker, frame, box)

	def writetotxt(self, params):
		#Write text file, I dont actually use this so that may not be needed, talk to irene about exactly what data they want. 
		for i in range(params['LASTTISSUE'] + 1 - params['FIRSTTISSUE']):
			self.tissuedict[i]['txtfile'].write(str('T{0}@{1}Hz.dat'.format((params['FIRSTTISSUE'] + i), params['PACINGFREQ'])) + "\n" +
														"Number of Measurements: " + str(self.tissuedict[i]['nummeasurments']) + "\n" +
														"Base Time: " + str(time.ctime(os.path.getctime(params['VIDEOPATH']))) + "\n" +
														"Distance calibration (pixels/mm): " + str(self.calib_factor) + "\n" +
														"Cross-sectional Area (mm^2): " + str(self.tissuedict[i]['crosssect']) + " " + str(self.tissuedict[i]['crosssect']) + " " + str(self.tissuedict[i]['crosssect']) + "\n" +
														"Pacing frequency (Hz): " + str(params['PACINGFREQ']) + "\n" +
														"Excitation threshold (V): " + str(params['EXCITTHRESH']) + "\n" +
														"Electrode spacing (mm): " + str(params['ELECTRODESPACING']) + "\n" +
														"Pacing voltage (V): " + str(params['PACINGVOLT']) + "\n"
														)

	def writetocsv(self, reltissueID, disp, x1, y1, x2, y2, cross, time):
		#time = self.vs.get(cv2.CAP_PROP_POS_MSEC)
		self.tissuedict[reltissueID]['csvfile'].write(str(time) + ','  + str(disp) + ',' + str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) + ',' + str(cross) + "\n")

		#self.tissuedict[reltissueID]['datfile'].write(str(time) + '	' + str(y1) + ' ' + str(x2) + ' ' + str(y2) + ' ' + str(y2) + "\n")
	
	def centroid(self, postcords):
		#Create a dictionary to hold the x, y for each pots
		posts = {}

		#For each post calculate the centroid for this frame and add it to the dict
		for (i, (x, y, x2, y2)) in enumerate(postcords):
			centroidX = int((x + x2) / 2.0)
			centroidY = int((y + y2) / 2.0)
			posts[i] = (centroidX, centroidY)

		#Return this dict of centroids with object ID as the key
		return posts

	def cleanup(self):
		#ALSO CLOSE FILES
		for key in self.tissuedict.keys():
			#self.tissuedict[key]["datfile"].close()
			self.tissuedict[key]["csvfile"].close()
			self.tissuedict[key]["txtfile"].close()
		#RELEASE VIDEO STREAM
		self.vs.release()
		#CLOSE ALL WINDOWS
		cv2.destroyAllWindows()

