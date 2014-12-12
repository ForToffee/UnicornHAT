import urllib2
import json
import time
import unicornhat as UH

lastID = 0      #most recent entry_id
refresh = 15    #refresh time in secs
urlRoot = "http://api.thingspeak.com/channels/1417/"
pixels = []    #list of pixels and their colours
pattern =        [[3,0],
  	    [2,1],[3,1],[4,1],
      [1,2],[2,2],[3,2],[4,2],[5,2],
            [2,3],[3,3],[4,3],
      [1,4],[2,4],[3,4],[4,4],[5,4],
[0,5],[1,5],[2,5],[3,5],[4,5],[5,5],[6,5],
		  [3,6],
		  [3,7]]

maxPixels = len(pattern)

namesToRGB = {'red': [0xFF, 0, 0],
                'green': [0, 0x80, 0],
                'blue': [0, 0, 0xFF],
                'cyan': [0, 0xFF, 0xFF],
                'white': [0xFF, 0xFF, 0xFF],
                'warmwhite': [0xFD, 0xF5, 0xE6],
                'purple': [0x80, 0, 0x80],
                'magenta': [0xFF, 0, 0xFF],
                'yellow': [0xFF, 0xFF, 0],
                'orange': [0xFF, 0xA5, 0],
                'pink': [0xFF, 0xC0, 0xCB],
                'oldlace': [0xFD, 0xF5, 0xE6]}


#retrieve and load the JSON data into a JSON object
def getJSON(url):
    jsonFeed = urllib2.urlopen(urlRoot + url)
    feedData = jsonFeed.read()
    #print feedData
    jsonFeed.close()

    data = json.loads(feedData)
    return data

#use the JSON object to identify the colour in use,
#update the last entry_id processed
def parseColour(feedItem):
    global lastID
    global pixels

    for name in namesToRGB.keys():
        if feedItem["field1"] == name:
            pixels.insert(0, namesToRGB[name])    #add the colour to the head
            break

    lastID = getEntryID(feedItem)

#read the last entry_id
def getEntryID(feedItem):
    return int(feedItem["entry_id"])

#refresh the displayed pixels
def showPixels():
    global pixels
    index = 0

    for pixel in pixels:
        coords = pattern[index]
	UH.set_pixel(coords[0],coords[1], pixel[0], pixel[1], pixel[2])
        index += 1
        if index >= maxPixels:
            #print index, maxPixels
            pixels = pixels[:maxPixels-1]    #trim the list as we've maxed out
            break
    UH.show()

#show all pixels one colour
def showColour(c):
    for coords in pattern:
        UH.set_pixel(coords[0], coords[1], c[0], c[1], c[2])
    UH.show()
                  
#main program

UH.rotation(180)

#process the currently available list of colours
data = getJSON("feed.json")
for feedItem in data["feeds"]:
    parseColour(feedItem)
showPixels()

#check for new colour requests
while True:
    data = getJSON("field/1/last.json")
    
    if getEntryID(data) > lastID:   #Has this entry_id been processed before?
        parseColour(data)
        showColour(pixels[0])
        time.sleep(5)
        showPixels()
    else:
        time.sleep(refresh)

