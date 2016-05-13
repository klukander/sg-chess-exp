 # -*- coding: utf-8 -*-

"""
WCST experiment / ReKnow

"""
import sys
import math

global USE_ZMQ; USE_ZMQ = False
if USE_ZMQ:
    import zmq


"""
global USE_LSL; USE_LSL = False
# Create LSL outlet
if USE_LSL:
    sys.path.append('C:\Program Files (x86)\PsychoPy2\Lib\pylsl')
    from pylsl import StreamInfo, StreamOutlet, resolve_streams, StreamInlet, IRREGULAR_RATE, cf_int32
    global outlet
    info = StreamInfo('markerstream', 'markers', 1, 10, 'float32', 'streasdfsaamid002')
    outlet = StreamOutlet(info)
"""

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
global s; s=os.sep

global startTime; startTime = datetime.utcnow()

"""
ZMQ messaging protocol
Send strings consisting of character codes in distinct positions

for instance 
    TQB = Task: Queen's Begin
    MQQA1B2 = Move Queen from A1 to B2
    ...

ZT  Zero Time -> set zerotime, respond with ZR
ZR  Zero Response (for calculating pingback time)

T   Task [Tx]
    Q   Queen's Quadrille
    M   Model copying
    C   Color sort
    V   Visual Search
    P   Puzzle

E   Event
    Types?

I   Instruction

G   Gaze target
    See pieces in "Move"

xB  Begin
xE  End

M   Move
    QQ0  Queen (there's only 1)
    KW0  White King
    KB0  Black King
    B[B/W][1/2] Bishop, two of each color, BW1 = white bishop 1
    T-"-        Tower
    H-"-        Knight (Horseface)

"""

def ShowInstructionSequence( instrSequence ):
    for item in instrSequence['pages']:
        ShowPicInstruction( unicode(item['text']),int(item['duration']), item['pic'], 1)

def ShowPicInstruction( txt, duration, picFile, location, col=(0.0, 0.0, 0.0), flip=False ):

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

    if flip:
        instr.setOri(-90)

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

def DrawFrames(duration=-1, flip=False):

    uprect = visual.Rect( win, .8*winW, .4*winH, fillColor='red', lineColor='red')
#    if flip:
#        uprect.setSize((0.4*w, 0.8*h))
#    uprect.setPos((-.25*h,0))
#    else:
#        uprect.setSize((0.8*w, 0.4*h))
    uprect.setPos((0,.25*winH))
    uprect.draw(win)

    dnrect = visual.Rect( win, .4*winW, .8*winH, fillColor='blue', lineColor='blue')
    #if flip:
    #    dnrect.setSize((0.4*w, 0.8*h))
    #    dnrect.setPos((.25*h,0))
    #else:
    dnrect.setPos((0,-.25*winW))
    dnrect.draw(win)

    win.flip()

    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)

def DrawChessBoard(left, top, width, height, squares, flip=False, duration=-1):

    sqz = width / squares
    sqzh = height/ squares
    
    #sqz = 0.6*winW/CHESS_SQUARES
    #sqzh = 0.6*winH/CHESS_SQUARES
    boardcoords = []
    colors = []
    for i in range(squares):
        for j in range(squares):
            tmp=[left+(i-1)*sqz, top+(j-1)*sqzh] 
            colval = .5*((i+j)%2)
            tmpcol=[colval, colval, colval]
            boardcoords.append(tmp)
            colors.append(tmpcol)

    for sq in range(len(boardcoords)):
        tmp = visual.Rect( win, sqz, sqzh)#(0.8*(1-(sq % 2)), 0.8*(1-(sq % 2)),0.8*(1-(sq % 2))))
        tmp.fillColor = colors[sq]; tmp.colorSpace='rgb'
        tmp.setPos(boardcoords[sq])
        tmp.draw(win)
        
    win.flip()

    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)

def DrawSideBins(left, top, width, height, flip=False, duration=-1):
    bin1 = visual.Rect(win, width, height)
    bin1.setPos((left, int(round(top+height/2))))
    bin1.fillColor = (1.0, 0.0, 0.0)
    
    bin2 = visual.Rect(win, width, height)
    bin2.setPos((left, int(round(-1*top-height/2))))
    bin2.fillColor = (0.0, 1.0, 0.0)
    
    bin1.draw(win)
    bin2.draw(win)
    
    win.flip()

    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)

def zmqSend(msg):
    if USE_ZMQ:
        print "sending %s" % msg
        socketOut.send("%s %s" % ("psychopy", msg))
        socketOut.send("%s %s" % ("you_will_never_see_me", "crapperjack"))

def zmqListen():
    msg = socketIn.recv()
    return msg

def logThis( msg ):
    logging.log( msg, level=myLogLevel )

# -------------------------------------------------------------------------------------------------#
# - MAIN PROG -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------#

if USE_ZMQ:
    #initialize zmq
    context = zmq.Context()
    #socketIn = context.socket(zmq.SUB)
    socketOut = context.socket(zmq.PUB)
    #portIn = "5557"
    portOut = "5557"
    #socketIn.connect("tcp://127.0.0.1:%s" % portIn)
    socketOut.connect("tcp://127.0.0.1:%s" % portOut)

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
#the distance doesn't apply! 
#w=69, h=149
mntrs.append( monitors.Monitor('PROJECTOR', width=69.0, distance=50) ); monW.append(1400); monH.append(1050)

midx=1
myMon=mntrs[midx]
myMon.setSizePix((monW[midx], monH[midx]))

#screen index now hardcoded to 0, was
#int(confInfo[7])
flip=True

winOrientation = 0.0

if flip:
    winOrienation=-90.0
else:
    winOrientation = 0.0
    
win=visual.Window(winType='pyglet', size=(monW[midx], monH[midx]), units='pix', fullscr=False, monitor=myMon,\
                screen=1, rgb=(1,1,1), viewOri=winOrientation)


global winW; winW = win.size[0]
global winH; winH = win.size[1]

#load config
#TODO: ADD ERROR CHECKING! Here we trust the json files to be correctly formed and valid
confFile = open( '.'+s+'configs'+s+'testconfig'+'.json' )
config = json.loads( confFile.read() )
confFile.close()

zmqSend("ZT") #zerotime
#todo set zero time

#run sets according to config loaded
for item in config['sets']:

    if( item['type'] == 'instruction'):
        temp=string.replace( item['file'], '\\', s )
        instrFile = open( temp )
        instrSequence = json.loads( instrFile.read() )
        instrFile.close()
        zmqSend('IB')
        ShowInstructionSequence( instrSequence )
        zmqSend('IE')

    elif( item['type'] == 'quadrille'):
        zmqSend('TQB')
        DrawChessBoard(250, -100, 500, 500, 4, flip=True)
        zmqSend('TQE')

    elif( item['type'] == 'colorsort'):
        zmqSend('TCB')
        DrawSideBins(300, 300, 500, 250, flip=True)
        zmqSend('TCE')

    else:
        print 'unidentified item type in config: ' + item['type']

"""
zmqSend("IB")
ShowPicInstruction("Tehtavasi on pelata allaolevalla shakkilaudalla\nKuningattaren kvadrillia.\nSiirra kuningatar shakkisiirroilla pelaamalla\nPelilaudan oikeaan alakulmaan.", -1, "", "nolocus", (1.0, 0.0, 0.0), flip=True)
zmqSend("IE")

zmqSend("TB")
DrawChessBoard(250, -100, 500, 500, 4, flip=True)
zmqSend("TE")

zmqSend("IB")
ShowPicInstruction("Lajittele mustat oikealle ja valkoiset vasemmalle.", -1, "", "nolocus", (1.0, 0.0, 0.0), flip=True)
zmqSend("IE")

zmqSend("TB")
DrawSideBins(300, 300, 500, 250, flip=True)
zmqSend("TE")
"""

event.clearEvents()
zmqSend("EQ")


#cleanup
win.close()
core.quit()


