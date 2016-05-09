 # -*- coding: utf-8 -*-

"""
WCST experiment / ReKnow

"""
import sys

global USE_LSL; USE_LSL = False
# Create LSL outlet
if USE_LSL:
    sys.path.append('C:\Program Files (x86)\PsychoPy2\Lib\pylsl')
    from pylsl import StreamInfo, StreamOutlet, resolve_streams, StreamInlet, IRREGULAR_RATE, cf_int32
    global outlet
    info = StreamInfo('markerstream', 'markers', 1, 10, 'float32', 'streasdfsaamid002')
    outlet = StreamOutlet(info)


from random import randint, random, seed
from psychopy import visual,core,monitors,event,gui,logging#,parallel
from copy import deepcopy
import csv
from datetime import datetime
import json

import os       # to get path separator for platform independence
import string   # to find test type from pathstrings (noise, patch)

if sys.platform.startswith('win'):
    from ctypes import windll
   
# - GLOBALS -------------------------------------------------------------------------------------------
global DEBUG; DEBUG = False
global portCodes;
global s; s=os.sep

global paraport; paraport=0xEC00    # or 0xEC00, 0xE880

global startTime; startTime = datetime.utcnow()

"""
Additive port code scheme allows unique decoding with sparse set. 

'clear'     : 0     triggers the parallel port

'task1'     : 1    = global 1 rule, FACES or LETTERS
'task2'     : 2    = global 2 rule, colour
'task3'     : 3    = local 1 rule, shape or letter
'task4'     : 4    = local 2 rule, orientation

'segStart' : 8    = marks the start of a segment when combined with [baseline, instr, tlx, set]
'segStop'  : 9    = marks the end of a segment when combined with -"-

'cue'       : 10   = fixation cross before target stimulus
'stimOn'    : 20   = target stimulus is shown
'refsOn'    : 30   = four reference stimuli are shown
'respRight' : 40   = correct response is received
'respWrong' : 50   = wrong response is received
'feedback'  : 60   = red/wrong or green/correct visual feedback to a response
'baseline'  : 70   = baseline start
'instr'     : 80   = marks the display of an instruction
'tlx'       : 90   = marks the display of a questionnaire

'set'       : 100   marks the beginning of a test/practice set
'start'     : 254   marks the start of the experiment
'stop'      : 255   marks the end of the experiment

use: 
    writePort( stimOn + rule1 ) -> 21
    writePort( respRight + rul4 ) -> 44
    writePort( baseline + segStart ) -> 78

"""
portCodes = {'clear' : 0,\
             'rule1' : 1,\
             'rule2' : 2,\
             'rule3' : 3,\
             'rule4' : 4,\
             'segStart' : 8,\
             'segStop' : 9,\
             'cue'   : 10,\
             'stimOn' : 20,\
             'refsOn' : 30,\
             'respRight' : 40,\
             'respWrong' : 50,\
             'feedback' : 60,\
             'base' : 70,\
             'instr': 80,\
             'tlx'  : 90,\
             'set'  : 100,\
             'start': 254,\
             'stop' : 255}


def ShowPicInstruction( txt, duration, picFile, location, col=(0.0, 0.0, 0.0) ):

    hasPic = False; hasTxt = False; logTxt=False
    h = 0;

    if txt != "":
        hasTxt=True
        logTxt=True
        if txt[0]=='*': # 'text' field in a NasaTLX instruction should start with asterix
            symbol='*'
        elif txt[0]=='£': # 'text' field in a baseline instruction should start with plus
            symbol='£'
            hasTxt=False
        else:
            logTxt=False
        if logTxt:
            offset=txt.find(symbol,1)
            txt_to_log=txt[1:offset]
            txt=string.replace(txt, symbol, '')
        instr = visual.TextStim( win, text=txt, pos=(0,-50), color=col, colorSpace='rgb', height=25, wrapWidth=800, alignHoriz='center')

    if picFile != "":
        picFile = string.replace( picFile, '\\', s )
        hasPic = True
        pic = visual.ImageStim( win );
        pic.setImage( picFile );
        h = pic.size

    if hasTxt:
        if hasPic:
            textpos = ( 0, -1* instr.height/2 - 10)
            picpos = ( 0, h[1]/2 + 20 )
        else:
            textpos = ( 0, 0 )
            picpos = ( -2000, -2000 )
    else:
        picpos = (0, 0)
        textpos = ( -2000, -2000 )

    if hasPic:
        pic.setPos( picpos );
        pic.draw( win );

    if hasTxt:
        instr.setPos( textpos )
        instr.draw(win)

    win.flip()
    if duration < 0:
        if logTxt:
            #triggerAndLog(portCodes['tlx'] + portCodes['segStart'] , "{:02d}".format(currentSet) + '.0_' + txt_to_log + " TLX start")
            keys = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
            #triggerAndLog(portcodes['tlx'] + portCodes['segStop'], "{:02d}".format(currentSet) + '.0_' + txt_to_log + ' TLX : ' + str(keys[0]))
        else:
            event.waitKeys()
    else:
        #if logTxt:
            #Ben, I'm not quite sure of how the portcodes (segStart, segStop) for a baseline section should be played?
            #triggerAndLog(portcodes['base'] , txt_to_log )
        core.wait( duration )

    win.flip() #clear screen

def DrawFrames(duration=-1):

    uprect = visual.Rect( win, 0.8*winW, 0.4*winH, fillColor='red', lineColor='red')
    uprect.setPos((0,.25*winH))
    uprect.draw(win)

    dnrect = visual.Rect( win, 0.8*winW, 0.4*winH, fillColor='blue', lineColor='blue')
    dnrect.setPos((0,-.25*winH))
    dnrect.draw(win)

    win.flip()



    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)


def logThis( msg ):
    logging.log( msg, level=myLogLevel )

# -------------------------------------------------------------------------------------------------#
# - MAIN PROG -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------#

#init random seed
seed()

# SETUP LOGGING & CLOCKING
testClock = core.Clock()
logging.setDefaultClock( testClock )

myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
#replace test with subj
myLog = logging.LogFile( '.'+s+'logs'+s+'' + 'test' + '.log', filemode='w', level = myLogLevel, encoding='utf8') #= myLogLevel )

logThis('--------------------------------------------------------')
logThis('INFO')
logThis('timestamp [block].[trial]_CUE')
logThis('timestamp [block].[trial]_STM [state for each rule G1 G2 L1 L2 : 0,1,2,3] RULE [current rule]')
logThis('timestamp [block].[trial]_TGT [states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...]') 
logThis('timestamp [block].[trial]_RSP [correct: 1/0] [current rule: G1, G2, L1, L2] ANSWER [card selected: 1(up), 2(right), 3(down), 4(left)]')
logThis('timestamp [block].[trial]_FDB [correct/fail] [correct answers] of [series length]')
logThis('--------------------------------------------------------')

#rendering window setup
mntrs=[]
monW=[]
monH=[]
# desktop
mntrs.append( monitors.Monitor('DESKTOP', width=51.4, distance=50) ); monW.append(1920); monH.append(1200)
#projector setup
#the distance doesn't apply! 
#w=69, h=149
mntrs.append( monitors.Monitor('PROJECTOR', width=69.0, distance=50) ); monW.append(1050); monH.append(1400)

midx=0
myMon=mntrs[midx]
myMon.setSizePix((monW[midx], monH[midx]))

#screen index now hardcoded to 0, was
#int(confInfo[7])
win=visual.Window(winType='pyglet', size=(monW[midx], monH[midx]), units='pix', fullscr=False, monitor=myMon,\
                screen=0, rgb=(1,1,1))


global winW; winW = win.size[0]
global winH; winH = win.size[1]


ShowPicInstruction("fickus", -1, "", "nolocus", (1.0, 0.0, 0.0))

DrawFrames()

event.clearEvents()


#cleanup
win.close()
core.quit()


