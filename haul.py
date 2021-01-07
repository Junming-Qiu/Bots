#For hauling in EVE
import cv2
import pyautogui
import time
import numpy as np
import mpld3
from mpld3 import plugins
from matplotlib import pyplot as plt
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

    # cv2.imwrite("crop.png", crop_img)

    # cv2.imshow(crop_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

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
    
    # cv2.imshow("img", crop_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
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

def acceptMissionUndock():
    #Accept Mission
    moveClick(1107, 573)
    time.sleep(1)

    #Click Item Hangar
    moveClick(184, 168)
    time.sleep(0.2)

    #Click Cargo
    pyautogui.moveTo(328, 146, 0.5)
    time.sleep(0.5)

    #Drag Cargo
    pyautogui.mouseDown()
    pyautogui.moveTo(212, 101, 0.5)
    pyautogui.mouseUp()
    time.sleep(1)

    #Undock
    moveClick(1708, 233)

    time.sleep(15)

    #Set Destination
    for i in range(5):
        moveClick(358, 550 + i * 20)


def returnToStation():
    #Complete Mission
    moveClick(1107, 573)
    time.sleep(2)

    #Request New Mission
    moveClick(1107, 573)
    time.sleep(1)

    #Click station Location
    pyautogui.moveTo(748, 140, 0.5)
    pyautogui.rightClick()
    time.sleep(0.5)

    #Set Destination Back to Station
    moveClick(806, 172)
    time.sleep(1)

    #Undock
    moveClick(1708, 233)
    time.sleep(10)


def onRoute(img):
    undock_crop = (207, 256, 1639, 1809)
    undock_colors = [(80, 25, (175, 200, 209)), (97, 20, (154, 185, 197))]

    #Check if in station
    if pix_eval(img, undock_crop, undock_colors, 10):
        return True
    else:
        return False


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def main():
    done = False
    #acceptMissionUndock()
    repeat = 20
    repeat *= 2

    while repeat > 0:
        img = screenshot()
        state = onRoute(img)

        #Stop at downtime
        if time_in_range(6, 7, datetime.now().hour):
            break

        #Stop computer from sleeping
        pyautogui.press('volumedown')
        time.sleep(1)
        pyautogui.press('volumeup')

        if state:
            #print("At Station")
            #break
            #repeat -= 1
            if not done:
                #print("Going Back")
                done = True
                returnToStation()
            elif done:
                #print("Doing Mission")
                done = False
                acceptMissionUndock()
        else:
            #print("Still Warping")
            #Click Warp
            moveClick(1528, 249)
            time.sleep(0.25)

            for i in range(10):
                moveClick(1485, 141)
                time.sleep(1)


time.sleep(3)
main()
#calibrate(screenshot())
#acceptMissionUndock()
#returnToStation()
#mousePos()

