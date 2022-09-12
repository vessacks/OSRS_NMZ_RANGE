#Thisi s a totally borked chop-job of nmz range. You've repalced some variables and cut some cdoe, no idea if it works.
#dont' trust any of the notes or documentation, itw as all written for nmz range.

from msilib.schema import Feature
import cv2 as cv
from cv2 import threshold
from cv2 import _InputArray_STD_BOOL_VECTOR
import numpy as np
import os
from windmouse import wind_mouse
from windowcapture import WindowCapture
from vision import Vision
import pyautogui
from pyHM import Mouse
import time
from action import Action

#RUN notes:
# 1. run in classic fixed
# 2. it searches partly in color. don't throw black and white code in willy nilly
# 3. prayer hotkey set to f5 (standard)
# 4. inventory hotkey set to f1 (NOT STANDARD)
# 5. you have to enter the dream and rock down to 1hp before starting the program. 
# 5.1 don't take any rangings! it will do that for you, and if you do it will mess up the timing and observation
# 6. you must also eat 5m of sorbs before starting 
# 7. game chat must be on so it can see the max_sorb message
# 8. don't change inv. /prayer tabs while it's running. it will get confused and give up. 
# 9. don't have anything typed in your chatbox/drafting window. it will mess up the ranging_off and max_sorb checks. 
# 10. set new KNOWN_OFFSCREEN_POINT
#11. stay away from the corners. it loves to think of black spots on the minimap as low prayer indicators with inf. confidence.


#DEV notes
# 1 I've changed how the screen mover works. Now it moves off screen AFTER clicking, not before. also when it tries to correct failures it does so by switching tab and movnig mouse offscreen. it's untested whether it works reliably. 
# it can't handle running out of praye rpots. the low=prayer signal it looks for (flashing blue) only appears when there is a prayer pot left to take. Without hta tther is no flashing blue and it doesn't realize it's out of prayer.
#it used to get caught in a sub loop when it ran out of rangings, but I think I fixed it. solution implemented but not tested.
#1/3 times it picks up an extra hp, no idea why. I don't think it's always operator error. bring a rock cake in future
#add spec weapon support. a gmaul would clean up

#thoughts
# 1. consider adding an auto-guzzle every 5 mins or so. if your flicker makes mistakes this will take you back donw to 1hp reliably. 
# 2. USEFUL: consider remaking the low prayer indicator with a much larger hitbox (close to the size of the minimap) w. a new mask. That way it will stop seeing low prayer in the black spots of the minimap. DONE.
# 3. USEFUL: add some way to stop the program once you're out of the dream. perhaps a combat bar observer that shuts off if you aren't in combat for 60s or something. DONE: it uses the protect_melee_on searcher

input('make sure you have complied with the run notes. then press enter to begin setup...')
print('Click into game. you have 10 seconds...')
time.sleep(2)
print('Click into game. you have 8 seconds...')
time.sleep(2)
print('Click into game. you have 6 seconds...')
time.sleep(2)
print('Click into game. you have 4 seconds...')
time.sleep(2)
print('Click into game. you have 2 seconds...')
time.sleep(2)
print('we are setting up parameters and taking first values. this relies on hotkeys and may fail perniciously if you are not clicked into game ...')
time.sleep(2)


# initialize the WindowCapture class
wincap = WindowCapture('RuneLite - Vessacks')


# initialize the Vision class
#do these color
rapid_heal_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\rapid_heal.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
protect_melee_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\protect_melee.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
protect_melee_on_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\protect_melee_on.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
wake_up_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\wake_up.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)


#do these color or you (MAY) mix them with praypots 
sorb_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
sorb_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
sorb_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
sorb_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)

#color
max_sorb_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\max_sorb.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
#ranging_off_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_off.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
#color
prayer_open_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\prayer_open.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)

#I've turned off the zero prayer vision mask because this will cause it to look for the flashing blue light. without the blue light it looks for black, and sees it in the minimap too often. this may not work ebcause the blue light is intermittant
#zero_prayer_vision_mask = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\0_prayer_vision_mask.png', cv.IMREAD_COLOR)
zero_prayer_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\0_prayer.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)#, search_mask = zero_prayer_vision_mask)

#do these grayscale
ranging_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
ranging_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
ranging_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
ranging_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)

#do these color, or you mix them up with absorbtions (they look the same in grayscale)
praypot_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\praypot_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
praypot_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\praypot_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
praypot_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\praypot_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
praypot_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\praypot_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)

#ranging_active_vision = #I dont' think I use this

#color and mask
fifty_one_health_vision_mask= cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\51_hp_vision_mask.png', cv.IMREAD_COLOR)
fifty_one_health_vision= Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\51_hp.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask=fifty_one_health_vision_mask)

one_health_vision_mask = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\1_hp_vision_mask.png', cv.IMREAD_COLOR)
one_health_vision= Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\1_hp.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask=one_health_vision_mask)


#initialize the action class
rapid_heal_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\rapid_heal.png')
protect_melee_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\protect_melee.png')


sorb_one_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_one.png') #these could all have been the same, or even been an ranging. all the potiosn have the same size hitbox
sorb_two_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_two.png')
sorb_three_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_three.png')
sorb_four_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\sorb_four.png')

next_ranging_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz range\\image library\\ranging_one.png')#put any ranging potion picture here, provided they are all the same size. They must be all the same size for this to work. 



PRAYER_THRESHOLD = .93
POTION_THRESHOLD = .93
FIFTY_ONE_HEALTH_THRESHOLD = .85
ZERO_PRAYER_THRESHOLD = .96 
RANGING_OFF_THRESHOLD = .9
MAX_SORB_THRESHOLD = .9
PRAYER_OPEN_THRESHOLD = .8
WAKE_UP_THRESHOLD = .9

#set a new one each time
KNOWN_OFFSCREEN_POINT = [1300,300]

def speed():
    speed = np.random.normal(.7,.3)
    while speed > .85 or speed < .6:
        speed = np.random.normal(.75,.08)
    return speed


def tick_dropper(odds=20):
    if np.random.randint(0,odds) == 1:
        
        drop = np.random.uniform(.6,2)
        print('tick dropper! sleeping %s' %drop)
        time.sleep(drop)
    return

def wait():
    wait = (.1 + abs(np.random.normal(0,.05)))
    return wait

#need to define sorb confidence so they don't get referenced before assignment. I'm pretty sure the value doesn't matter because the reference only matters in cases where they've been redefined
sorb_one_confidence = 0
sorb_two_confidence = 0
sorb_three_confidence = 0
sorb_four_confidence =0

#determine the session parameters for how early to turn on protect melee
protect_melee_early_time_mean = np.random.uniform(.3,3)
protect_melee_early_time_stdDev = protect_melee_early_time_mean/6


#determine the session parameters for how late to turn off protect melee
protect_melee_late_time_mean = np.random.uniform(0,20)
protect_melee_late_time_stdDev = protect_melee_early_time_mean/6

#determine the session parameters for how late to repot 
repot_late_time_mean = np.random.uniform(.1,.6)
repot_late_time_stdDev = repot_late_time_mean/5

#session parameters for rapid heal flicking
flick_early_time_mean = np.random.uniform(20,40)
flick_early_time_stdDev = np.random.uniform(1,3)

print('session figures:')
print('protect_melee_early_time_mean %s' %protect_melee_early_time_mean)
print('protect_melee_early_time_stdDev %s'%protect_melee_early_time_stdDev)
print('protect_melee_late_time_mean %s' %protect_melee_late_time_mean)
print('protect_melee_late_time_stdDev %s' %protect_melee_late_time_stdDev)
print('repot_late_time_mean %s' %repot_late_time_mean)
print('repot_late_time_stdDev %s' %repot_late_time_stdDev)
print('flick_early_time_mean %s'%flick_early_time_mean)
print('flick_early_time_stdDev %s' %flick_early_time_stdDev)

#find your ranging potion locations (GRAYSCALE) before starting the loop
print('opening inventory (f1) to find rangings...')
pyautogui.keyDown('f1')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
pyautogui.keyUp('f1')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
current_tab = 'f1'

print('finding ranging_ones')
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_one_allPoints, ranging_one_bestPoint, ranging_one_confidence = ranging_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

print('finding ranging_twos')
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_two_allPoints, ranging_two_bestPoint, ranging_two_confidence = ranging_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()
    
print('finding ranging_threes')
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_three_allPoints, ranging_three_bestPoint, ranging_three_confidence = ranging_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

print('finding ranging_fours')
screenshot = wincap.get_screenshot() 
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_four_allPoints, ranging_four_bestPoint, ranging_four_confidence = ranging_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()
    

#define the next ranging for use in coming loop
print('looking for rangings...')
if ranging_one_confidence > POTION_THRESHOLD:
    next_ranging = ranging_one_bestPoint
    print('determined next_ranging = ranging_one | confidence %s' % ranging_one_confidence)
elif ranging_two_confidence > POTION_THRESHOLD:
    next_ranging = ranging_two_bestPoint
    print('determined next_ranging = ranging_two | confidence %s' % ranging_two_confidence)
elif ranging_three_confidence > POTION_THRESHOLD:
    next_ranging = ranging_three_bestPoint
    print('determined next_ranging = ranging_three | confidence %s' % ranging_three_confidence)
elif ranging_four_confidence > POTION_THRESHOLD:
    next_ranging = ranging_four_bestPoint
    print('determined next_ranging = ranging_four | confidence %s' % ranging_four_confidence)
else:
    print('problem: no rangings found on startup. exitting...')
    exit()

ranging_total = len(ranging_one_allPoints) + (len(ranging_two_allPoints)*2) + (len(ranging_three_allPoints)*3) + (len(ranging_four_allPoints)*4)

print('found %s ranging_ones | %s ranging_twos | %s ranging_threes | %s ranging_fours | enough rangings for %s minutes' % (len(ranging_one_allPoints), len(ranging_two_allPoints), len(ranging_three_allPoints), len(ranging_four_allPoints), ranging_total*5))

#find the protect melee for use in the coming loop
print('opening prayer tab w. f5')
pyautogui.keyDown('f5')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
pyautogui.keyUp('f5')
current_tab = 'f5'

print('moving mouse to %s to clear out any covered objects' % (KNOWN_OFFSCREEN_POINT))
protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

print('looking for protect melee...') 
screenshot = wincap.get_screenshot() #color
protect_melee_allPoints, protect_melee_bestPoint, protect_melee_confidence = protect_melee_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

if protect_melee_confidence > PRAYER_THRESHOLD:
    print('found protect_melee at %s | confidence %s' % (protect_melee_bestPoint, round(protect_melee_confidence,3)))
else:
    print('no protect_melee found | confidence %s' % round(protect_melee_confidence))

input('press enter to begin botting...')
#note: you should turn protect melee on shortly before running out of ranging, probably using a timer. I'm going to time an ranging now. the time from ranging click to return to 51 hp is exactly 5:00.
print('Click into game. you have 10 seconds...')
time.sleep(2)
print('Click into game. you have 8 seconds...')
time.sleep(2)
print('Click into game. you have 6 seconds...')
time.sleep(2)
print('Click into game. you have 4 seconds...')
time.sleep(2)
print('Click into game. you have 2 seconds...')
time.sleep(2)
print('we are now behaving as if in game...')
time.sleep(2)

#these are things that need to be defined before entering the loop, or indeed before doing some pre-loop shit below
protect_melee_early_time = np.random.normal(protect_melee_early_time_mean, protect_melee_early_time_stdDev)
protect_melee_late_time = np.random.normal(protect_melee_late_time_mean, protect_melee_late_time_stdDev)
flick_early_time = np.random.normal(flick_early_time_mean,flick_early_time_stdDev)
protect_melee_click_time = time.time()
last_praypot_time = time.time()
nothing_since_last_flick = True
loop_time = time.time()
protect_melee_disabled = False
out_of_praypots = False
protect_melee_off_failed = False

#I'm pretty sure I don't need to do this
''' 
print('setting tab to prayer (f5)')
pyautogui.keyDown('f5')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
pyautogui.keyUp('f5')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
current_tab = 'f5'
'''
#we do a prayer flick before entering loop to prevent missed flick
if current_tab != 'f5':
    print('opening prayer tab w. f5')
    pyautogui.keyDown('f5')
    time.sleep(.15 + abs(np.random.normal(.1,.05)))
    tick_dropper()
    pyautogui.keyUp('f5')
    time.sleep(.15 + abs(np.random.normal(.1,.05)))
    tick_dropper()
    current_tab = 'f5'
else:
    print('we are already in the prayer tab')

     
print('moving mouse to %s to clear out any covered objects' % (KNOWN_OFFSCREEN_POINT))
protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

screenshot = wincap.get_screenshot()
rapid_heal_allPoints, rapid_heal_bestPoint, rapid_heal_confidence = rapid_heal_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode= 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

if rapid_heal_confidence > PRAYER_THRESHOLD:
    rapid_heal_screenpoint = wincap.get_screen_position(rapid_heal_bestPoint)
    rapid_heal_clickpoint = rapid_heal_action.click(rapid_heal_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
    print('clicked rapid_heal on')
    time.sleep(wait())
    pyautogui.click()
    print('clicked rapid_heal off')
else: 
    print('could not find rapid heal, not in loop yet. giving up...')
    exit()

last_flick_time = time.time()
flick_early_time = np.random.normal(flick_early_time_mean,flick_early_time_stdDev)
nothing_since_last_flick = True

# then we sorb up 

#the way this works is it looks for the least-filled sorb bottle, hits it, then checks for a max sorb message. it stops when it sees a max sorb message
        #this loop takes so long that we have to include a flicking loop in it too
print('sorbing up before entering main loop')
start_time = time.time()
while True:
    #prayer flicking loop here. required because the resorb loop takes so god damn long.
    if time.time() - last_flick_time > 60 -  flick_early_time:
        print('time to flick! | time since last flick %s | flick_early_time %s' %(time.time()-last_flick_time, flick_early_time))
        
        if current_tab != 'f5':
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'
        else:
            print('we are already in the prayer tab')

        
        screenshot = wincap.get_screenshot()
        rapid_heal_allPoints, rapid_heal_bestPoint, rapid_heal_confidence = rapid_heal_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode= 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()

        if rapid_heal_confidence > PRAYER_THRESHOLD:
            rapid_heal_screenpoint = wincap.get_screen_position(rapid_heal_bestPoint)
            rapid_heal_clickpoint = rapid_heal_action.click(rapid_heal_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
            print('clicked rapid_heal on')
            time.sleep(wait())
            pyautogui.click()
            print('clicked rapid_heal off')
            last_flick_time = time.time()
        else: 
            print('could not find rapid heal, attempting to reopen prayer tab. and moving mouse offscreen to reveal obscured objects. this should fix the issue next loop around...')
            protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'
            #exit()
        #generating new flick values
        flick_early_time = np.random.normal(flick_early_time_mean,flick_early_time_stdDev)
        nothing_since_last_flick = True

    if current_tab != 'f1':
        print('opening inventory tab w. f1')
        pyautogui.keyDown('f1')
        time.sleep(.15 + abs(np.random.normal(.1,.05)))
        pyautogui.keyUp('f1')
        time.sleep(.15 + abs(np.random.normal(.1,.05)))
        tick_dropper()
        current_tab = 'f1'
    else:
        print('we are already in the inv tab')
    #find sorb_ones
    screenshot = wincap.get_screenshot() 
    sorb_one_allPoints, sorb_one_bestPoint, sorb_one_confidence = sorb_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        exit()

    #if we see a sorb one, hit it
    if sorb_one_confidence > POTION_THRESHOLD:
        sorb_one_screenpoint = wincap.get_screen_position(sorb_one_bestPoint)
        next_ranging_clickpoint = next_ranging_action.click(sorb_one_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
        print('clicked sorb_one | confidence %s' % round(sorb_one_confidence,3))

    #if we dont' see a sorb_one, we look for sorb_two
    if sorb_one_confidence < POTION_THRESHOLD:
        screenshot = wincap.get_screenshot() 
        sorb_two_allPoints, sorb_two_bestPoint, sorb_two_confidence = sorb_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()         

        #if we see a sorb_two, hit it
        if sorb_two_confidence > POTION_THRESHOLD:
            sorb_two_screenpoint = wincap.get_screen_position(sorb_two_bestPoint)
            next_ranging_clickpoint = next_ranging_action.click(sorb_two_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
            print('clicked sorb_two |  confidence %s' %round(sorb_two_confidence,3))

    #if we don't see a sorb_one and we don't see a sorb_two, we look for a sorb_three
    if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD:
        screenshot = wincap.get_screenshot() 
        sorb_three_allPoints, sorb_three_bestPoint, sorb_three_confidence = sorb_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
        #if we see a sorb_three, hit it
        if sorb_three_confidence > POTION_THRESHOLD:
            sorb_three_screenpoint = wincap.get_screen_position(sorb_three_bestPoint)
            next_ranging_clickpoint = next_ranging_action.click(sorb_three_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
            print('clicked sorb_three | confidence %s' %round(sorb_three_confidence,3))
    
    #if we don't see a sorb_one, sorb_two, or sorb_three, we look for a sorb_four
    if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD and sorb_three_confidence < POTION_THRESHOLD:
        screenshot = wincap.get_screenshot() 
        sorb_four_allPoints, sorb_four_bestPoint, sorb_four_confidence = sorb_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()

        #if we see a sorb_four, hit it
        if sorb_four_confidence > POTION_THRESHOLD:
            sorb_four_screenpoint = wincap.get_screen_position(sorb_four_bestPoint)
            next_ranging_clickpoint = next_ranging_action.click(sorb_four_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
            print('clicked sorb_four | confidence %s' %round(sorb_four_confidence,3))

    #if we don't see a sorb_one,two,three OR four, then we break the loop
    if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD and sorb_three_confidence < POTION_THRESHOLD and sorb_four_confidence < POTION_THRESHOLD:
        print('I see no sorb_one(%s), no sorb_two(%s), no sorb_three(%s), and no sorb_four(%s). breaking re-sorb loop but not exiting' %(round(sorb_one_confidence,3),round(sorb_two_confidence,3),round(sorb_three_confidence,3),round(sorb_four_confidence,3)))
        break

    #if we run for more than 60 seconds, stop
    if time.time() - start_time > 60:
        print('resorbing for %ss (>60), I think you should have been done by now. Quitting')
        exit()

    #check for max sorb message. If we see it, break the loop
    screenshot = wincap.get_screenshot() 
    max_sorb_allPoints, max_sorb_bestPoint, max_sorb_confidence = max_sorb_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        exit()

    if max_sorb_confidence > MAX_SORB_THRESHOLD:
        print('I see max_sorb message, breaking re-sorb loop')
        break





# in order to correctly time rangings and melee prayers, you have to ranging and set ranging time before entering main loop
#first we get into inv. tab
print('opening inv tab w. f1')
pyautogui.keyDown('f1')
time.sleep(.15 + abs(np.random.normal(.1,.05)))
tick_dropper()
pyautogui.keyUp('f1')
current_tab = 'f1'

#then we click next ranging
next_ranging_screenpoint = wincap.get_screen_position(next_ranging)
next_ranging_clickpoint = next_ranging_action.click(next_ranging_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
nothing_since_last_flick = False #ie we have to move the mouse back to rapid heal
last_ranging_time = time.time() #the next ranging becomes the last ranging
print('clicked ranging, sleeping 5s to ensure sprites updated...')
time.sleep(5)
print('moving mouse to %s to clear out any covered objects' % (KNOWN_OFFSCREEN_POINT))
protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

print('finding next ranging...')
#print ranging_ones
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_one_allPoints, ranging_one_bestPoint, ranging_one_confidence = ranging_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

#print('finding ranging_twos')
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_two_allPoints, ranging_two_bestPoint, ranging_two_confidence = ranging_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

#print('finding ranging_threes')
screenshot = wincap.get_screenshot()
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_three_allPoints, ranging_three_bestPoint, ranging_three_confidence = ranging_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()

#print('finding ranging_fours')
screenshot = wincap.get_screenshot() 
screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
ranging_four_allPoints, ranging_four_bestPoint, ranging_four_confidence = ranging_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
if cv.waitKey(1) == ord('q'):
    cv.destroyAllWindows()
    exit()


#define the next ranging for use in coming loop
#print('looking for rangings...')
if ranging_one_confidence > POTION_THRESHOLD:
    next_ranging = ranging_one_bestPoint
    print('found next_ranging = ranging_one | confidence %s'% ranging_one_confidence)
elif ranging_two_confidence > POTION_THRESHOLD:
    next_ranging = ranging_two_bestPoint
    print('found next_ranging = ranging_two | confidence %s'% ranging_two_confidence)
elif ranging_three_confidence > POTION_THRESHOLD:
    next_ranging = ranging_three_bestPoint
    print('found next_ranging = ranging_three | confidence %s'% ranging_three_confidence)
elif ranging_four_confidence > POTION_THRESHOLD:
    next_ranging = ranging_four_bestPoint
    print('found next_ranging = ranging_four | confidence %s'% ranging_four_confidence)
else:
    print('problem: Not yet in the loop and no more rangings found. something is up, exitting...')
    exit()





#this is start of main loop   
#main loop run until it's out of one type of potion(?)
main_loop_start_time = time.time()
print('entering main loop...')
while True:
    #see if it's time to flick
    if time.time() - last_flick_time > 60 -  flick_early_time:
        print('time to flick! | time since last flick %s | flick_early_time %s' %(time.time()-last_flick_time, flick_early_time))
        #get in the right tab
        if current_tab != 'f5':
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'
        else:
            print('we are already in the prayer tab')
        
        screenshot = wincap.get_screenshot()
        rapid_heal_allPoints, rapid_heal_bestPoint, rapid_heal_confidence = rapid_heal_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode= 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
    
        if rapid_heal_confidence > PRAYER_THRESHOLD:
            rapid_heal_screenpoint = wincap.get_screen_position(rapid_heal_bestPoint)
            rapid_heal_clickpoint = rapid_heal_action.click(rapid_heal_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
            print('clicked rapid_heal on')
            time.sleep(wait())
            pyautogui.click()
            print('clicked rapid_heal off | moving mouse offscreen (%s) to prevent obscured objects' % (KNOWN_OFFSCREEN_POINT))
            last_flick_time = time.time()
            protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        else: 
            print('could not find rapid heal. attempting to reopen prayer tab and moving mouse offscreen to reveal obscured objects. It should reattempt flick next cycle')
            protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'



        #generating new values
        flick_early_time = np.random.normal(flick_early_time_mean,flick_early_time_stdDev)
        nothing_since_last_flick = True


    #determine if we should protect melee on, which should happen shortly before ranging runs out. this is run on timing with a computer vision backup
        
    
    #if the ranging has run out, repot, wait 7 seconds (plus some random time) to hit 1hp, turn off protect from melee, resorb
    if time.time() - last_ranging_time > 305 + protect_melee_late_time:
        print('it has been about 5m, time to repot')
        time.sleep(2 + np.random.normal(0,.3))
        #this line above is new as of 8.28.22 and untested. if you get timing problems, remove it. 
        #hit the next potion
        if current_tab != 'f1':
            print('opening inv tab w. f1')
            pyautogui.keyDown('f1')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f1')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f1'
        else:
            print('we are already in the inventory tab (f1)')
    
        next_ranging_screenpoint = wincap.get_screen_position(next_ranging)
        next_ranging_clickpoint = next_ranging_action.click(next_ranging_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
        nothing_since_last_flick = False #ie we have to move the mouse back to rapid heal
        last_ranging_time = time.time() #the next ranging becomes the last ranging
        print('clicked ranging...')

        
        #here we wait for 7 seconds + protect_melee_late_time to have elapsed, then turn off protect from melee. because this takes so long, we also check whether it's time to flick 
       
        #calculate new next_ranging
        print('switching to inventory tab (f1)')
        pyautogui.keyDown('f1')
        time.sleep(.15 + abs(np.random.normal(.1,.05)))
        tick_dropper()
        pyautogui.keyUp('f1')
        time.sleep(.15 + abs(np.random.normal(.1,.05)))
        tick_dropper()
        current_tab = 'f1'
        print('finding next_ranging...')

        #print ranging_ones
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
        ranging_one_allPoints, ranging_one_bestPoint, ranging_one_confidence = ranging_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
    
        #print('finding ranging_twos')
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
        ranging_two_allPoints, ranging_two_bestPoint, ranging_two_confidence = ranging_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
    
        #print('finding ranging_threes')
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
        ranging_three_allPoints, ranging_three_bestPoint, ranging_three_confidence = ranging_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
    
        #print('finding ranging_fours')
        screenshot = wincap.get_screenshot() 
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY) #grayscale
        ranging_four_allPoints, ranging_four_bestPoint, ranging_four_confidence = ranging_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
    

        #define the next ranging for use in coming loop
        #print('looking for rangings...')
        if ranging_one_confidence > POTION_THRESHOLD:
            next_ranging = ranging_one_bestPoint
            print('found next_ranging = ranging_one | confidence %s'% ranging_one_confidence)
        elif ranging_two_confidence > POTION_THRESHOLD:
            next_ranging = ranging_two_bestPoint
            print('found next_ranging = ranging_two | confidence %s'% ranging_two_confidence)
        elif ranging_three_confidence > POTION_THRESHOLD:
            next_ranging = ranging_three_bestPoint
            print('found next_ranging = ranging_three | confidence %s'% ranging_three_confidence)
        elif ranging_four_confidence > POTION_THRESHOLD:
            next_ranging = ranging_four_bestPoint
            print('found next_ranging = ranging_four | confidence %s'% ranging_four_confidence)
        else:
            print('problem: no rangings found for next click. Keep running anyway but disable protect melee...')
            protect_melee_disabled = True
            #exit()

        #this loop resorbs until it sees the no more resorb message
        print('we will now resorb. hitting sorbs until I see a sorb full message..')
        #the way this works is it looks for the least-filled sorb bottle, hits it, then checks for a max sorb message. it stops when it sees a max sorb message
        #this loop takes so long that we have to include a flicking loop in it too
        start_time = time.time()
        while True:
            #prayer flicking loop here. required because the resorb loop takes so god damn long.
            if time.time() - last_flick_time > 60 -  flick_early_time:
                print('time to flick! | time since last flick %s | flick_early_time %s' %(time.time()-last_flick_time, flick_early_time))
                
                if current_tab != 'f5':
                    print('opening prayer tab w. f5')
                    pyautogui.keyDown('f5')
                    time.sleep(.15 + abs(np.random.normal(.1,.05)))
                    tick_dropper()
                    pyautogui.keyUp('f5')
                    time.sleep(.15 + abs(np.random.normal(.1,.05)))
                    tick_dropper()
                    current_tab = 'f5'
                else:
                    print('we are already in the prayer tab')
                
                
                screenshot = wincap.get_screenshot()
                rapid_heal_allPoints, rapid_heal_bestPoint, rapid_heal_confidence = rapid_heal_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode= 'allPoints + bestPoint + confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()
    
                if rapid_heal_confidence > PRAYER_THRESHOLD:
                    rapid_heal_screenpoint = wincap.get_screen_position(rapid_heal_bestPoint)
                    rapid_heal_clickpoint = rapid_heal_action.click(rapid_heal_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
                    print('clicked rapid_heal on')
                    time.sleep(wait())
                    pyautogui.click()
                    print('clicked rapid_heal off | moving mouse offscreen (%s) to prevent obscured objects' %(KNOWN_OFFSCREEN_POINT))
                    protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
                    last_flick_time = time.time()
                else: 
                    print('could not find rapid heal, attempting to reopen prayer tab and moving mouse offscreen (%s) to prevent obscured objects. should fix the issue next loop around...' %KNOWN_OFFSCREEN_POINT)
                    protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
                    print('opening prayer tab w. f5')
                    pyautogui.keyDown('f5')
                    time.sleep(.15 + abs(np.random.normal(.1,.05)))
                    tick_dropper()
                    pyautogui.keyUp('f5')
                    time.sleep(.15 + abs(np.random.normal(.1,.05)))
                    tick_dropper()
                    current_tab = 'f5'
                    #exit()
                #generating new flick values
                
                flick_early_time = np.random.normal(flick_early_time_mean,flick_early_time_stdDev)
                nothing_since_last_flick = True

            #find sorb_ones
            screenshot = wincap.get_screenshot() 
            sorb_one_allPoints, sorb_one_bestPoint, sorb_one_confidence = sorb_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()

            #if we see a sorb one, hit it
            if sorb_one_confidence > POTION_THRESHOLD:
                sorb_one_screenpoint = wincap.get_screen_position(sorb_one_bestPoint)
                next_ranging_clickpoint = next_ranging_action.click(sorb_one_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
                print('clicked sorb_one | confidence %s' % round(sorb_one_confidence,3))

            #if we dont' see a sorb_one, we look for sorb_two
            if sorb_one_confidence < POTION_THRESHOLD:
                screenshot = wincap.get_screenshot() 
                sorb_two_allPoints, sorb_two_bestPoint, sorb_two_confidence = sorb_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()         

                #if we see a sorb_two, hit it
                if sorb_two_confidence > POTION_THRESHOLD:
                    sorb_two_screenpoint = wincap.get_screen_position(sorb_two_bestPoint)
                    next_ranging_clickpoint = next_ranging_action.click(sorb_two_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
                    print('clicked sorb_two |  confidence %s' %round(sorb_two_confidence,3))

            #if we don't see a sorb_one and we don't see a sorb_two, we look for a sorb_three
            if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD:
                screenshot = wincap.get_screenshot() 
                sorb_three_allPoints, sorb_three_bestPoint, sorb_three_confidence = sorb_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()
                #if we see a sorb_three, hit it
                if sorb_three_confidence > POTION_THRESHOLD:
                    sorb_three_screenpoint = wincap.get_screen_position(sorb_three_bestPoint)
                    next_ranging_clickpoint = next_ranging_action.click(sorb_three_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
                    print('clicked sorb_three | confidence %s' %round(sorb_three_confidence,3))
            
            #if we don't see a sorb_one, sorb_two, or sorb_three, we look for a sorb_four
            if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD and sorb_three_confidence < POTION_THRESHOLD:
                screenshot = wincap.get_screenshot() 
                sorb_four_allPoints, sorb_four_bestPoint, sorb_four_confidence = sorb_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()

                #if we see a sorb_four, hit it
                if sorb_four_confidence > POTION_THRESHOLD:
                    sorb_four_screenpoint = wincap.get_screen_position(sorb_four_bestPoint)
                    next_ranging_clickpoint = next_ranging_action.click(sorb_four_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)
                    print('clicked sorb_four | confidence %s' %round(sorb_four_confidence,3))

            #if we don't see a sorb_one,two,three OR four, then we break the loop
            if sorb_one_confidence < POTION_THRESHOLD and sorb_two_confidence < POTION_THRESHOLD and sorb_three_confidence < POTION_THRESHOLD and sorb_four_confidence < POTION_THRESHOLD:
                print('I see no sorb_one(%s), no sorb_two(%s), no sorb_three(%s), and no sorb_four(%s). breaking re-sorb loop and moving mouse offscreen but not exiting' %(round(sorb_one_confidence,3),round(sorb_two_confidence,3),round(sorb_three_confidence,3),round(sorb_four_confidence,3)))
                protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
                break

            #if we run for more than 60 seconds, stop
            if time.time() - start_time > 60:
                print('resorbing for %ss (>60), I think you should have been done by now. Quitting')
                exit()

            #check for max sorb message. If we see it, break the loop
            screenshot = wincap.get_screenshot() 
            max_sorb_allPoints, max_sorb_bestPoint, max_sorb_confidence = max_sorb_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()

            if max_sorb_confidence > MAX_SORB_THRESHOLD:
                print('I see max_sorb message, moving mouse offscreen (%s) and breaking re-sorb loop' % KNOWN_OFFSCREEN_POINT)
                protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
                break
    
    #see if we should prayer pot up
    screenshot = wincap.get_screenshot() 
    zero_prayer_allPoints, zero_prayer_bestPoint, zero_prayer_confidence = zero_prayer_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        exit()
    #print('debugging! zero prayer confidence %s' %zero_prayer_confidence)

    #if we're confidence there's no prayer left and we havent repotted in the last 5 seconds, look for a praypot to hit
    if zero_prayer_confidence > ZERO_PRAYER_THRESHOLD and last_praypot_time > 10 and out_of_praypots == False:
        print('\'zero\' prayer detected | confidence of .9-.98 usually means prayer is between 1-15| confidence %s' %zero_prayer_confidence)
        
        if current_tab != 'f1':
            print('opening inv tab w. f1')
            pyautogui.keyDown('f1')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f1')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f1'
        else:
            print('we are already in the inventory tab (f1)')
        
        print('moving mouse offscreen %s to prevent obscured praypots' % KNOWN_OFFSCREEN_POINT)
        protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        #find praypot_ones
        screenshot = wincap.get_screenshot() 
        praypot_one_allPoints, praypot_one_bestPoint, praypot_one_confidence = praypot_one_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()

        #if we see a praypot one, hit it
        if praypot_one_confidence > POTION_THRESHOLD:
            praypot_one_screenpoint = wincap.get_screen_position(praypot_one_bestPoint)
            next_ranging_clickpoint = next_ranging_action.click(praypot_one_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)#this is ok because next_ranging and next_pray_pot and absorbtions all ahve the same hitbox size. 
            last_praypot_time = time.time()
            print('clicked praypot_one | confidence %s | moving mouse offscreen' % round(praypot_one_confidence,3))
            protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        #if we dont' see a praypot_one, we look for praypot_two
        if praypot_one_confidence < POTION_THRESHOLD:
            screenshot = wincap.get_screenshot() 
            praypot_two_allPoints, praypot_two_bestPoint, praypot_two_confidence = praypot_two_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()         

            #if we see a praypot_two, hit it
            if praypot_two_confidence > POTION_THRESHOLD:
                praypot_two_screenpoint = wincap.get_screen_position(praypot_two_bestPoint)
                next_ranging_clickpoint = next_ranging_action.click(praypot_two_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100) #this is ok because next_ranging and next_pray_pot and absorbtions all ahve the same hitbox size. 
                last_praypot_time = time.time()
                print('clicked praypot_two |  confidence %s | moving mouse offscreen' %round(praypot_two_confidence,3))
                protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        #if we don't see a praypot_one and we don't see a praypot_two, we look for a praypot_three
        if praypot_one_confidence < POTION_THRESHOLD and praypot_two_confidence < POTION_THRESHOLD:
            screenshot = wincap.get_screenshot() 
            praypot_three_allPoints, praypot_three_bestPoint, praypot_three_confidence = praypot_three_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()
            #if we see a praypot_three, hit it
            if praypot_three_confidence > POTION_THRESHOLD:
                praypot_three_screenpoint = wincap.get_screen_position(praypot_three_bestPoint)
                next_ranging_clickpoint = next_ranging_action.click(praypot_three_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100) #this is ok because next_ranging and next_pray_pot and absorbtions all ahve the same hitbox size. 
                last_praypot_time = time.time()
                print('clicked praypot_three | confidence %s | moving mouse offscreen' %round(praypot_three_confidence,3))
                protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        #if we don't see a praypot_one, praypot_two, or praypot_three, we look for a praypot_four
        if praypot_one_confidence < POTION_THRESHOLD and praypot_two_confidence < POTION_THRESHOLD and praypot_three_confidence < POTION_THRESHOLD:
            screenshot = wincap.get_screenshot() 
            praypot_four_allPoints, praypot_four_bestPoint, praypot_four_confidence = praypot_four_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()

            #if we see a praypot_four, hit it
            if praypot_four_confidence > POTION_THRESHOLD:
                praypot_four_screenpoint = wincap.get_screen_position(praypot_four_bestPoint)
                next_ranging_clickpoint = next_ranging_action.click(praypot_four_screenpoint, speed = speed()-.15, wait=wait(), tick_dropper_odds= 100)#this is ok because next_ranging and next_pray_pot and absorbtions all ahve the same hitbox size. 
                last_praypot_time = time.time()
                print('clicked praypot_four | confidence %s | moving mouse offscreen' %round(praypot_four_confidence,3))
                protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())

        #if we don't see a praypot_one,two,three OR four, then we click nothing
        if praypot_one_confidence < POTION_THRESHOLD and praypot_two_confidence < POTION_THRESHOLD and praypot_three_confidence < POTION_THRESHOLD and praypot_four_confidence < POTION_THRESHOLD:
            last_praypot_time = time.time()
            print('I see no praypot_one(%s), no praypot_two(%s), no praypot_three(%s), and no praypot_four(%s). clicking nothing but also not exiting' %(round(praypot_one_confidence,3),round(praypot_two_confidence,3),round(praypot_three_confidence,3),round(praypot_four_confidence,3)))
            print('prayer is low and I see no more prayer pots. disabling protect melee to preserve remaining prayer')
            protect_melee_disabled = True
            out_of_praypots = True

        #if we ran out of prayer, that means we may have missed a flick. we should sleep for a second to wait for prayer to kick in, then flick
        time.sleep(np.random.uniform(.6,1))
        if current_tab != 'f5':
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'
        else:
            print('we are already in the prayer tab')

        #wind_mouse(pyautogui.)        

        screenshot = wincap.get_screenshot()
        rapid_heal_allPoints, rapid_heal_bestPoint, rapid_heal_confidence = rapid_heal_vision.find(screenshot, threshold = PRAYER_THRESHOLD, debug_mode= 'rectangles', return_mode= 'allPoints + bestPoint + confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()

        if rapid_heal_confidence > PRAYER_THRESHOLD:
            rapid_heal_screenpoint = wincap.get_screen_position(rapid_heal_bestPoint)
            rapid_heal_clickpoint = rapid_heal_action.click(rapid_heal_screenpoint, speed = speed(), wait=wait(), tick_dropper_odds= 100)
            print('clicked rapid_heal on')
            time.sleep(wait())
            pyautogui.click()
            print('clicked rapid_heal off | moving mouse offscreen (%s) to prevent obscured objects ' % KNOWN_OFFSCREEN_POINT)
            protect_melee_action.moveTo(KNOWN_OFFSCREEN_POINT, speed = speed(), wait= wait())
            last_flick_time = time.time()
        else: 
            print('could not find rapid heal, attempting to reopen prayer tab. this should fix the issue next go around...')
            print('opening prayer tab w. f5')
            pyautogui.keyDown('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            pyautogui.keyUp('f5')
            time.sleep(.15 + abs(np.random.normal(.1,.05)))
            tick_dropper()
            current_tab = 'f5'

    screenshot = wincap.get_screenshot() 
    wake_up_allPoints, wake_up_bestPoint, wake_up_confidence = wake_up_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        exit()
    
    if wake_up_confidence > WAKE_UP_THRESHOLD:
        print('I see wakeup message | confidence %s | ran for %ss | dream over, exitting...' % (wake_up_confidence, time.time() - main_loop_start_time))
        exit()


    if out_of_praypots == True:
        print ('debugging | out_of_praypots == True')
    if protect_melee_disabled == True:
        print('debugging | protect_melee_disabled == True')       
    
    #print('debugging | main loop complete | loop time %s' %(time.time()-loop_time))
    loop_time = time.time()

