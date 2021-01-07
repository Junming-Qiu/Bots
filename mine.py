#For mining in EVE
import pyautogui
import time
import cv2
import numpy as np
import copy
from matplotlib import pyplot as plt
import mpld3
from mpld3 import plugins
from datetime import datetime


def getCropCoords(img):
    def nothing(stuff):
        pass

    cv2.namedWindow('SC',cv2.WINDOW_NORMAL)
    cv2.createTrackbar('X1', 'SC', 0, 3360, nothing)
    cv2.createTrackbar('Y1', 'SC', 0, 2100, nothing)
    cv2.createTrackbar('X2', 'SC', 0, 3360, nothing)
    cv2.createTrackbar('Y2', 'SC', 0, 2100, nothing)
    
    cv2.resizeWindow('SC', 1600, 1000)
    
    while True:
        new_img = np.copy(img)
        x_one = cv2.getTrackbarPos("X1", "SC")
        y_one = cv2.getTrackbarPos("Y1", "SC")
        x_two = cv2.getTrackbarPos("X2", "SC")
        y_two = cv2.getTrackbarPos("Y2", "SC")
        
        new_img = cv2.rectangle(new_img, (x_one, y_one), (x_two, y_two), (255, 0, 0), 2) 
        cv2.imshow("SC", new_img)
        #print(x_one, y_one, x_two, y_two)
        
        key = cv2.waitKey(1)

        if key == 27:
            break
        
    return y_one, y_two, x_one, x_two


def getColors(pixels, crop_img):
    res = []
    for pixel in pixels:
        BGR = (pixel[0], pixel[1], (crop_img[pixel[1]][pixel[0]][0], crop_img[pixel[1]][pixel[0]][1], crop_img[pixel[1]][pixel[0]][2]))
        res.append(BGR)
        
    print(res)


def calibrate(img):
    y_one, y_two, x_one, x_two = getCropCoords(img)
    
    print("Your crop selection is:", (y_one, y_two, x_one, x_two))
    
    crop_img = crop(img, (y_one, y_two, x_one, x_two))

    #cv2.imwrite("crop.png", crop_img)

    #cv2.imshow(crop_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    fig, ax = plt.subplots()

    im = ax.imshow(crop_img, interpolation='none')
    fig.colorbar(im, ax=ax)

    ax.set_title('An Image', size=20)

    plugins.connect(fig, plugins.MousePosition(fontsize=14))

    mpld3.show()

    pixels = []
    
    print("Select Pixels: (enter 'stop' to stop)")
    
    while True:
        x = input("Enter x: ")
        y = input("Enter y: ")
        if x.isnumeric() and y.isnumeric():
            pixels.append((int(x), int(y)))
        elif x == 'stop' or y == 'stop':
            break  
        
    getColors(pixels, crop_img)
            
    
def moveClick(x, y):
    pyautogui.moveTo(x, y, 0.1)
    time.sleep(0.25)
    pyautogui.click()


def mousePos(seconds=10):
    for i in range(seconds):
        time.sleep(1)
        print(pyautogui.position())
        

def screenshot():
    img = pyautogui.screenshot("screenshot.png")
    time.sleep(1)
    img = cv2.imread("screenshot.png", 1)
    return img


def crop(img, crop_dim):
    return img[crop_dim[0]:crop_dim[1], crop_dim[2]:crop_dim[3]]
  
  
def pix_eval(img, crop_dim, point_colors, variance):
    crop_img = crop(img, crop_dim)
    
    #cv2.imshow("img", crop_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    #Compare pixels
    for pix in point_colors:
        crop_check = crop_img[pix[1]:pix[1] + 1, pix[0]:pix[0] + 1][0][0]
        #print()
        #print(crop_check)
        #print(pix[2])
        for i in range(len(crop_check)):
            
            pix_thresh = [pix[2][i]]
            for j in range(variance * -1, variance + 1):
                pix_thresh.append(pix[2][i] + j)
                
            if crop_check[i] not in pix_thresh:
                return False             
    return True


def go_to_field(curr_belt=1): 
    #Undock
    
    #Regular station
    #moveClick(1560, 226)
    
    #Player station
    moveClick(1734, 312)
    
    print("Undocking")
    time.sleep(30)
    
    #Click menu
    pyautogui.moveTo(148, 60, 0.1)
    time.sleep(0.25)

    #Go to belt menu, select belt
    pyautogui.rightClick()
    time.sleep(.1)
    pyautogui.moveTo(232, 125, 0.25)
    
    y = 125
    y_now = 0
    for i in range(curr_belt):
        pyautogui.moveTo(450, y, 0.25)
        y_now = copy.copy(y)
        y += 17
        
        if i > 0 and i % 4 == 0:
            y -= 1
        
    pyautogui.moveTo(650, y_now, 0.25)
    pyautogui.click()
    
    
def mine():
    #Scroll out
    pyautogui.moveTo(878, 175, 0.25)
    pyautogui.scroll(1000)
    time.sleep(1)

    # Open mining in cargo
    moveClick(199, 479)

    time.sleep(3)
    #Click mining tab
    moveClick(1792, 215)

    #Click new asteroid
    pyautogui.moveTo(1577, 260, 0.25)
    pyautogui.click()
    time.sleep(0.1)
    
    #Approach asteroid
    pyautogui.keyDown("q")
    time.sleep(0.1)
    pyautogui.keyUp("q")
    
    time.sleep(20)
    
    #Lock asteroid
    pyautogui.keyDown("u")
    time.sleep(0.1)
    pyautogui.keyUp("u")
    
    time.sleep(10)
    
    #Mine
    pyautogui.keyDown("f1")
    time.sleep(0.5)
    pyautogui.keyUp("f1")
    
    pyautogui.keyDown("f2")
    time.sleep(0.5)
    pyautogui.keyUp("f2")
    
    time.sleep(1)
        
    
def isMining(img):
    #(x, y, color)
    #BGR colors
    point_colors_l_u = [(14, 14, (36, 135, 184)), (55, 10, (224, 228, 229))]
    point_colors_l_d = [(26, 15, (36, 135, 185)), (66, 18, (5, 10, 17))]
    #(y1, y2, x1, x2)
    crop_dim_l_u = (185, 224, 1302, 1376)
    crop_dim_l_d = (198, 231, 1290, 1381)
    
    point_colors_m_u = [(20, 17, (67, 149, 187)), (31, 13, (164, 166, 166))]
    point_colors_m_d = [(27, 33, (67, 149, 188)), (38, 28, (195, 197, 198))]
    crop_dim_m_u = (182, 221, 1311, 1364)
    crop_dim_m_d = (180, 230, 1304, 1385)
    
    
    if (pix_eval(img, crop_dim_m_u, point_colors_m_u, 20) or pix_eval(img, crop_dim_m_d, point_colors_m_d, 20)) == True:
        pyautogui.keyDown("f1")
        time.sleep(0.5)
        pyautogui.keyUp("f1")
        time.sleep(2)
        
        img = screenshot()
        
        if (pix_eval(img, crop_dim_l_u, point_colors_l_u, 20) or pix_eval(img, crop_dim_l_d, point_colors_l_d, 20))  == False:
            pyautogui.keyDown("f1")
            time.sleep(0.5)
            pyautogui.keyUp("f1") 
        
        pyautogui.keyDown("f2")
        time.sleep(0.5)
        pyautogui.keyUp("f2")
        time.sleep(2)
        img = screenshot()
        
        if (pix_eval(img, crop_dim_l_u, point_colors_l_u, 20) or pix_eval(img, crop_dim_l_d, point_colors_l_d, 20))  == False:
            pyautogui.keyDown("f2")
            time.sleep(0.5)
            pyautogui.keyUp("f2")
        else:
            return True
            
    #Crop and return if is mining
    return pix_eval(img, crop_dim_l_u, point_colors_l_u, 20) or pix_eval(img, crop_dim_l_d, point_colors_l_d, 20)

    
def oreFull(img):
    point_colors = [(148, 2, (85, 67, 4)), (148, 12, (86, 67, 4))]
    crop_dim = (425, 441, 275, 426)
    
    return pix_eval(img, crop_dim, point_colors, 20)


def returnToStation(station_num):
    moveClick(1442, 213)
    y = 255
    pyautogui.moveTo(1442, y, 0.1)
    
    for i in range(station_num - 1):
        time.sleep(0.1)
        y += 20
        
        if i > 0 and i % 4 == 0:
            y -= 2
            
        pyautogui.moveTo(1442, y, 0.1)
    
    #Enter warp
    pyautogui.click()
    pyautogui.keyDown("s")
    time.sleep(0.25)
    pyautogui.keyUp("s")
    
    time.sleep(65)
    
    #Dock
    moveClick(1492, 140)
    
    pyautogui.click()
    time.sleep(1)
    

def storeOre():
    frigate = [150, 450, 190, 520]
    venture = []
    
    #Click ore cargo tab location
    moveClick(202, 445)
    
    #Move to ore to right click
    pyautogui.moveTo(294, 447, 0.25)
    pyautogui.rightClick()
    
    #Select all 
    moveClick(322, 455)
    
    #Drag ore to cargo
    pyautogui.moveTo(351, 452)
    pyautogui.mouseDown()
    pyautogui.moveTo(198, 494, 0.25)
    pyautogui.mouseUp()
    

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def main():
    TOTAL_BELTS = 16
    CURRENT_BELT = 7
    REPEAT = 0
    STATION = 3
    
    pyautogui.FAILSAFE = True

    print("Starting")
    for i in range(5):
        time.sleep(1)
        print(".")

    go_to_field(CURRENT_BELT)
    time.sleep(60)
    #Afterburner on
    pyautogui.keyDown("f3")
    time.sleep(1)
    pyautogui.keyUp("f3")
    
    run = True
    
    while run == True:
        #Take screenshot and read
        img = screenshot()
        pyautogui.press('volumedown')
        time.sleep(1)
        pyautogui.press('volumeup')

        if time_in_range(6, 7, datetime.now().hour):
            break

        elif oreFull(img) or REPEAT > 4:
            REPEAT = 0
            print("Ore full!")
            print("Returning to station")
            
            #Afterburner off
            pyautogui.keyDown("f3")
            time.sleep(1)
            pyautogui.keyUp("f3")

            returnToStation(STATION)

            time.sleep(20)
            storeOre()
            time.sleep(3)
            
            if CURRENT_BELT > TOTAL_BELTS:
                run = False
                break
            
            go_to_field(CURRENT_BELT)
            time.sleep(60)
            
            #Afterburner on
            pyautogui.keyDown("f3")
            time.sleep(1)
            pyautogui.keyUp("f3")
        
        elif isMining(img) == True:
            print("Still mining")
            REPEAT = 0
            time.sleep(20)
            
        else:
            print("Approaching new asteroid")
            REPEAT += 1
            if REPEAT > 4:
                CURRENT_BELT += 1
                print("Switching to belt:", CURRENT_BELT)
                CURRENT_BELT %= TOTAL_BELTS
            else:
                mine()
    
    print("End")


main()

#Testing code

#time.sleep(2)
#img = pyautogui.screenshot("screenshot.png")
#time.sleep(1)
#img = cv2.imread("screenshot.png", 1)

#calibrate(img)

#storeOre()
#mine()
#go_to_field(10)
#mousePos()
#print(oreFull(img))
#returnToStation(3)

#1 miner
#up x
#print(pix_eval(img, (182, 221, 1311, 1364), [(20, 17, (67, 149, 187)), (31, 13, (164, 166, 166))], 20))
#down x
#print(pix_eval(img, (180, 230, 1304, 1385), [(27, 33, (67, 149, 188)), (38, 28, (195, 197, 198))], 20))

#2 miners
#up x
#print(pix_eval(img, (185, 224, 1302, 1376), [(14, 14, (36, 135, 184)), (55, 10, (224, 228, 229))], 20))
#down
#print(pix_eval(img, (198, 231, 1290, 1381), [(26, 15, (36, 135, 185)), (66, 18, (5, 10, 17))], 20))

