import numpy as np
import cv2
import math

from cv_wrap import *

paper_width, paper_height = (8.5*50, 11*50) # FIXME

def angle(pt1, pt2, pt0):
	pt0 = Point(pt0)
	pt1 = Point(pt1)
	pt2 = Point(pt2)
	
	dx1 = pt1.x - pt0.x;
	dy1 = pt1.y - pt0.y;
	dx2 = pt2.x - pt0.x;
	dy2 = pt2.y - pt0.y;

	return (dx1*dx2 + dy1*dy2)/math.sqrt(abs((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10))

def find_squares(img):
	blurred = cv2.medianBlur(img, 9)

	height, width, depth = blurred.shape
	gray0 = blurred.copy()
	#gray0 = cv2.convertScaleAbs(cv2.cvtColor(np.empty((height, width, 1), dtype=np.uint16), cv2.COLOR_GRAY2BGR))
	# gray = np.zeros((blurred.size()[0], blurred.size()[1], 1), dtype=np.uint8)
	
	squares = []
	
	# find squares in every color plane of the image
	for c in range(0, 3):
		ch = [c, 0]
		cv2.mixChannels(blurred, gray0, ch)
		
		# try several threshold levels
		threshold_level = 8
		for l in range(0, threshold_level):
			# Use Canny instead of zero threshold level!
			# Canny helps to catch squares with gradient shading
			if l == 0:
				gray = cv2.Canny(gray0, 10, 20, apertureSize=3)
				
				# Dilate helps to remove potential holes between edge segments
				gray = cv2.dilate(gray, np.ones((11,11),'uint8'))
			else:
				#gray = 1 if (gray0.any() >= (l+1) * 255 / threshold_level) else 0
				gray = cv2.cvtColor(cv2.threshold(gray0, int(l/float(threshold_level)*255), 128, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_BGR2GRAY)

			# Find contours and store them in a list
			#print gray
			contours = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
			contours = contours[1]
	
			# Test contours
			for i in range(0, len(contours)):
				# approximate contour with accuracy proportional
				# to the contour perimeter
				arclength = cv2.arcLength(np.array(contours[i], copy=True), True)*0.02
				approx = cv2.approxPolyDP(contours[i], arclength, True)

				# Note: absolute value of an area is used because
				# area may be positive or negative - in accordance with the
				# contour orientation
				if len(approx) == 4 and abs(cv2.contourArea(np.array(approx, copy=True))) > 1000 and cv2.isContourConvex(np.array(approx, copy=True)):
					maxCosine = 0
	
					for j in range(2, 5):
						cosine = abs(angle(approx[j%4], approx[j-2], approx[j-1]))
						maxCosine = max([maxCosine, cosine])
	
					if maxCosine > math.pi:
						squares.append(approx)

	return squares

def find(img):
	squares = find_squares(img)

	if len(squares) > 0:
		# get rid of squares the same size as the image
		good_squares = []
		for sqr in squares:
			pts = [Point(pt) for pt in sqr]
			if not (pts[0].x == 1 and pts[0].y == 1):
				good_squares.append(sqr)

		# find the biggest square
		max_area = 0
		biggest = None

		for sqr in good_squares:
			area = cv2.contourArea(sqr)
			if area > max_area:
				max_area = area
				biggest = sqr

		return biggest
	else:
		return None

def dist(pt1, pt2):
	x1, y1 = pt1[0]
	x2, y2 = pt2[0]

	return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def get_transform(img):
	paper = find(img)

	if paper != None and len(paper) > 0:
		height, width, depth = img.shape

		pts1 = np.float32(paper)

		if dist(paper[0], paper[1]) > dist(paper[0], paper[3]):
			pts2 = np.float32([
				[paper_width, 0],
				[paper_width, paper_height],
				[0, paper_height],
				[0, 0]
			])
		else:
			pts2 = np.float32([
				[0, 0],
				[paper_width, 0],
				[paper_width, paper_height],
				[0, paper_height]
			])
		
		return cv2.getPerspectiveTransform(pts1, pts2)
	else:
		return None

def deskew(img):
	height, width, depth = img.shape
	transform = get_transform(img)

	if transform != None:
		return cv2.warpPerspective(img, transform, (width, height))
	else:
		print "deskew: No paper!"
		return None

def deskew_and_crop(img):
	height, width, depth = img.shape
	transform = get_transform(img)

	if transform != None:
		deskewed = cv2.warpPerspective(img, transform, (width, height))
		return deskewed[0:paper_height, 0:paper_width]
	else:
		print "deskew: No paper!"
		return None

def draw_squares(img, squares):
	for sqr in squares:
		pts = [Point(pt) for pt in sqr]
		for i in range(0, 4):
			cv2.line(img, (pts[i].x, pts[i].y), (pts[(i+1)%4].x, pts[(i+1)%4].y), (255,0,0), 8)
