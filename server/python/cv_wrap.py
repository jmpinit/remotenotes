import cv2
import numpy as np

class Point:
	def __init__(self, cv_representation):
		coords = cv_representation[0]

		self.x = coords[0]
		self.y = coords[1]

def imread_color(filename):
	return cv2.imread(filename, 1)

def imread_gray(filename):
	return cv2.imread(filename, 0)
