from graphicstest import Ui_Form
from PyQt4 import QtCore
from PyQt4.QtGui import *

import sys

import random

class App(QWidget, Ui_Form):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setupUi(self)
		
	@QtCore.pyqtSlot()
	def on_pushButton_clicked(self):
		 print ("button clicked")
		 map = createMap(60, 0.2, 0.2)
		 img2 = QImage(mapToImage(map, (0,0,0)))
		 pixmap2 = QPixmap.fromImage(img2)
		 pixmap2 = pixmap2.scaledToWidth(self.label.width())
		 pixmap2 = pixmap2.scaledToHeight(self.label.height())
		 self.label.setPixmap(pixmap2)
		 
def mapToImage(map, baseColor):
	"""
		This function maps a python object of the in RFC defined map to an image.
	"""
	print ("mapping map to image "+str(map["dimensions"]))
	img = QImage(map["dimensions"][0], map["dimensions"][1], QImage.Format_RGB32);
	#clear image with black pixels before adding
	for x in range(img.width()):
		for y in range (img.height()):
			img.setPixel(x, y, qRgb(baseColor[0],baseColor[1],baseColor[2]))
	
	#add blocking elements - red colors
	for block in map["blockingElements"]:
		img.setPixel(block["x"], block["y"], qRgb(255,0,0))
	#add robots - blue colors
	for block in map["robots"]:
		img.setPixel(block["x"], block["y"], qRgb(0,0,255))	
	#add ressources - green colors
	for block in map["ressources"]:
		img.setPixel(block["x"], block["y"], qRgb(0,255,0))	
		
	img.setPixel(0,0, 	qRgb(255,255,255))
	#mirror image on x axis to represent up down commands...
	img = img.mirrored(horizontal = False, vertical = True)
	return img
	
		 
def createMap(size, blockingElements, ressources):
    """
    :param size: size of map
    blockingElements: percentage as float between 0 and 1 of blocking elements covering the map
    ressources: percentage as float between 0 and 1 of ressources covering the map.
    blockingElements + ressources must be < 1
    :return: a dictionnary with dimensions, blocking elements, ressources and robots.
    the latter is an initially empty array.
    """
    if blockingElements+ressources>1.0:
        print ("blocking elements and ressources together cant be higher than 1.0")
        exit(1)
    blocktypes = ["rock", "plant", "hole"]
    ressourcetypes = ["Gold", "Diamant"]
    map = {"dimensions": [size, size], "blockingElements":[], "ressources": [], "robots":[]}
    #Create blocking elements on map....
    #make a list of distinct coords
    print ("Populating map with " +str(round(size*size*blockingElements))+ " blocking Elements...")
    coords = set()
    while len(coords) < int(round(size*size*blockingElements)):
        coords.add((random.randint(0, size-1), random.randint(0, size-1)))
    for coordinate in coords:
        map["blockingElements"].append({"name": blocktypes[random.randint(0,len(blocktypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    #Create Ressources for map...
    # make a list of distinct coords: copy coords, make it until size + size*ressources and the diff coords
    ress_coords = coords.copy()
    print ("Populating map with " + str(round(size*size*ressources)) + " ressources...")
    while len(ress_coords) < int(round(size*size*blockingElements)+round(size*size*ressources)):
        ress_coords.add((random.randint(0, size-1), random.randint(0, size-1)))
    ress_coords = ress_coords.difference(coords)
    for coordinate in ress_coords:
        map["ressources"].append({"name": ressourcetypes[random.randint(0,len(ressourcetypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    print ("Map Creation Finished")
    return map

		 
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	win = App()
	win.show()
	sys.exit(app.exec_())
