import logging
import zerorpc
import cv_wrap
import paper 
import cv2

class NoteProcessorRPC(object):
	def save(self, filename):
		raw = cv_wrap.imread_color(filename)
		note = paper.deskew_and_crop(raw)

		if note != None:
			cv2.imwrite(filename, note)
			return True
		else:
			return False

logging.basicConfig()
s = zerorpc.Server(NoteProcessorRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
