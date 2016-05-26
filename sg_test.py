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

from random import randint, random, seed, sample
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
        ShowPicInstruction( unicode(item['text']),int(item['duration']), item['pic'], location=1, flip=True)

def ShowPicInstruction( txt, duration, picFile, col=(0.0, 0.0, 0.0), location=0, flip=False ):

    hasPic = False; hasTxt = False; logTxt=False
    h = 0;

    pic = visual.ImageStim( win );


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
        pic.setImage( picFile );
        h = pic.size

    if flip:
        instr.setOri(-90)
        pic.setOri(-90)

    if location == 1:
        offset = (-100, 0)
        offset = (-100, 0)
    elif location==2:
        offset = (150, 0)
    else:
        offset = (0,0)

    if hasTxt:
        if hasPic:
            if flip:
                textpos = ( offset[0] -1* instr.height/2 - 10, offset[1] )
                picpos = ( offset[0] + h[1]/2 -350, offset[1] )
            else:
                textpos = ( offset[0] + 0, offset[1] -1* instr.height/2 - 10)
                picpos = ( offset[0] + 0, offset[1] + h[1]/2 + 20 )
        else:
            textpos = offset#( 0, 0 )
            picpos = ( -2000, -2000 )
    else:
        picpos = offset#(0, 0)
        textpos = ( -2000, -2000 )

    if hasPic:
        pic.setPos( (offset[0]+picpos[0], offset[1]+picpos[1]) )
        pic.draw( win );

    if hasTxt:
        instr.setPos( (offset[0] + textpos[0], offset[1] + textpos[1]) )
        instr.draw(win)

    win.flip()
    if duration < 0:
        if logTxt:
            #triggerAndLog(portCodes['tlx'] + portCodes['segStart'] , "{:02d}".format(currentSet) + '.0_' + txt_to_log + " TLX start")
            keys = event.waitKeys(keys=['space'])
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
"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""

def DrawChessBoard(xpos, ypos, width, height, squares, flip=False, duration=-1):

    sqz = width / squares
    sqzh = height/ squares
    
    #sqz = 0.6*winW/CHESS_SQUARES
    #sqzh = 0.6*winH/CHESS_SQUARES
    boardcoords = []
    colors = []
    for i in range(squares):
        for j in range(squares):
            #tmp=[left+(i-1)*sqz, top+(j-1)*sqzh] 
            tmp=[xpos-(width/2)+i*sqz+sqz/2, ypos-(height/2)+j*sqzh+sqzh/2] 
            colval = 0.9-.5*((i+j)%2)
            tmpcol=[colval, colval, colval]
            boardcoords.append(tmp)
            colors.append(tmpcol)

    for sq in range(len(boardcoords)):
        tmp = visual.Rect( win, sqz, sqzh)#(0.8*(1-(sq % 2)), 0.8*(1-(sq % 2)),0.8*(1-(sq % 2))))
        tmp.fillColor = colors[sq]; tmp.colorSpace='rgb'
        tmp.setPos(boardcoords[sq])
        tmp.draw(win)
        
    win.flip()

"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""
def DrawCalibTargets(xpos, ypos, width, height, flip=False, duration=-1):

    tmp = visual.Rect( win, width, height )
    tmp.fillColor = (-1, -1, -1); tmp.colorSpace = 'RGB'
    tmp.setPos((xpos, ypos))
    tmp.draw(win)
    
"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""

def DrawVisSearch(left, top, width, height, itemnum, targetVisible=True, tgt=10, duration=-1, ):

    #load images
    """    names={
        1: 'bishop_b.bmp', \
        2: 'bishop_b2.bmp', \
        3: 'bishop_w.bmp', \
        4: 'bishop_w2.bmp', \
        5: 'king_b.bmp', \
        6: 'king_w.bmp', \
        7: 'knight_b.bmp', \
        8: 'knight_b2.bmp', \
        9: 'knight_w.bmp', \
        10: 'knight_w2.bmp', \
        11: 'queen_w.bmp', \
        12: 'tower_b.bmp', \
        13: 'tower_b2.bmp', \
        14: 'tower_w.bmp', \
        15: 'tower_w2.bmp'}
    """

    names=(
        'bishop_b.jpg', \
        'bishop_b2.jpg', \
        'bishop_w.jpg', \
        'bishop_w2.jpg', \
        'king_b.jpg', \
        'king_w.jpg', \
        'knight_b.jpg', \
        'knight_b2.jpg', \
        'knight_w.jpg', \
        'knight_w2.jpg', \
        'queen_w.jpg', \
        'tower_b.jpg', \
        'tower_b2.jpg', \
        'tower_w.jpg', \
        'tower_w2.jpg')

    gridpoints=[]
    ptn = int(math.ceil( math.sqrt(itemnum) ))
    for i in range( ptn ):
        for j in range( ptn ):
            jx = randint(0,40)-20; jy = randint(-15,15)
            pt = (left+(i-.5)*width/ptn + jx-(width/2), top+(j)*height/ptn + jy-(height/2))
            gridpoints.append(pt)

    #shuffle locations
    gridpoints = sample( gridpoints, len(gridpoints))
    itemlist=[]

    dstrs = range(1, 15)
    dstrs.remove(tgt) # this has to be removed anyway to not show up :)

    if targetVisible: # if tgt < 0, no target, and no removals
        
        target = visual.ImageStim( win );
        target.setImage( "pics\\" + names[tgt] )

        target.setPos( gridpoints[tgt] )
        del gridpoints[tgt] #avoid overlapping location
        target.setSize(75)
        target.setOri( randint(-90,90) )


    count = len( dstrs )

    for i in dstrs: #dstrs: #range(15-1): #removed one
        picFile = "pics\\" + names[i]
        picFile = string.replace( picFile, '\\', s )
        pic = visual.ImageStim( win );
        pic.setImage( picFile );
        pic.setSize(75)
        
        itemlist.append( pic )

    """for i in range(15):
        #itemlist[i].setPos( (randint(left, width), randint(top, height) ) )
        itemlist[i].setPos( gridpoints[i])
        itemlist[i].setOri( randint(0,180)-90 )
        itemlist[i].draw(win)
    """
    for i in range( itemnum-1 ):
        #pic = visual.ImageStim( win )
        #pic.setImage( itemlist[i%15] )
        itemlist[i%count].setPos( gridpoints[i] )
        itemlist[i%count].setOri( randint(0,360) )
        itemlist[i%count].draw(win)

    if targetVisible:
        target.draw(win)
    
    win.flip()

"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""

def DrawModelCopy(left, top, width, height, itemnum, duration=-1):

    names=(
        'bishop_b.jpg', \
        'bishop_b2.jpg', \
        'bishop_w.jpg', \
        'bishop_w2.jpg', \
        'king_b.jpg', \
        'king_w.jpg', \
        'knight_b.jpg', \
        'knight_b2.jpg', \
        'knight_w.jpg', \
        'knight_w2.jpg', \
        'queen_w.jpg', \
        'tower_b.jpg', \
        'tower_b2.jpg', \
        'tower_w.jpg', \
        'tower_w2.jpg')

    gridpoints=[]
    ptn = int(math.ceil( math.sqrt(itemnum) ))
    #regular grid, no jitter
    for i in range( ptn ):
        for j in range( ptn ):
            #jx = randint(0,40)-20; jy = randint(-15,15)
            pt = (left+i*width/ptn -(width/2), top+j*height/ptn -(height/2))
            gridpoints.append(pt)

    #pick random locations
    gridpoints = sample( gridpoints, itemnum) #len(gridpoints))

    itemlist=[]
    for i in range(15):
        picFile = "pics\\" + names[i]
        picFile = string.replace( picFile, '\\', s )
        pic = visual.ImageStim( win );
        pic.setImage( picFile );
        itemlist.append( pic )

    """for i in range(15):
        #itemlist[i].setPos( (randint(left, width), randint(top, height) ) )
        itemlist[i].setPos( gridpoints[i])
        itemlist[i].setOri( randint(0,180)-90 )
        itemlist[i].draw(win)
        """
    
    picked = range(1, itemnum) #should be shorter than n of cards
    
    for i in range( itemnum ):
        #pic = visual.ImageStim( win )
        #pic.setImage( itemlist[i%15] )
        itemlist[i%15].setPos( gridpoints[i] )
        itemlist[i%15].setOri( -90)
        itemlist[i%15].draw(win)
        
    win.flip()

"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""

def DrawModelCopyFromPic(xpos, ypos, filename, chessboard=True, duration=-1):

    picFile = filename
    picFile = string.replace( picFile, '\\', s)
    pic = visual.ImageStim( win )
    pic.setImage( picFile )
    pic.setPos( (xpos, ypos))
    pic.setOri( -90 )
    pic.setSize( 512)
    pic.draw( win )
    
    if chessboard:
        DrawChessBoard(350, 0, 500, 500, 4, flip=True, duration = duration) # has its own wait

    else: #
        win.flip()
"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""

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

"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""
def zmqSend(msg):
    if USE_ZMQ:
        print "sending %s" % msg
        socketOut.send("%s" % (msg))
        #socketOut.send("%s %s" % ("you_will_never_see_me", "crapperjack"))

def zmqListen():
    tmp = 0
    #if USE_ZMQ:
    #    socketIn.listen()
        
def logThis( msg ):
    logging.log( msg, level=myLogLevel )

def Sync():
    repeats = 5
    for i in range(repeats):
        t1 = datetime.utcnow()
        zmqSend("ZT") #zerotime
        if(zmqListen() == 'ZR' ):
            t2 = datetime.utcnow()
            print t2-t1
        
    #todo set zero time

def WaitForIt( keys=['x'], duration=-1 ):
    if duration < 0:
        keys = event.waitKeys(keys)
    else:
        core.wait(duration)

def DrawNumOrder( xpos, ypos, number, duration=-1):
    wsq = 75
    wsep = 4
    wtot = number*wsq+(number-1)*wsep
    
    for i in range(number):
        #stimpos = (xpos-0.5*wsq, ypos-wtot/2+i*(wsq+wsep)+wsq/2)
        stimpos = (xpos-wtot/2+i*(wsq+wsep)-wsq/2, ypos-0.5*wsq)

        tmp = visual.Rect( win, wsq, wsq, lineColor='black')
        txt = visual.TextStim( win, text=str(i+1), color='red', colorSpace='rgb', height=25, wrapWidth=100, alignHoriz='center')
        tmp.setPos(stimpos)
        txt.setPos(stimpos)
        txt.setOri(-90)
        tmp.draw(win)
        txt.draw(win)

    win.flip()

"""
    if duration < 0:
        keys = event.waitKeys()#keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    else:
        core.wait(duration)
"""
# -------------------------------------------------------------------------------------------------#
# - MAIN PROG -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------#

"""
g = m
r = x
b = space
"""

if USE_ZMQ:
    #initialize zmq
    context = zmq.Context()
    #socketIn = context.socket(zmq.SUB)
    socketOut = context.socket(zmq.PAIR)
    #portIn = "5557"
    portOut = "5555"
    #socketIn.connect("tcp://127.0.0.1:%s" % portIn)
#socketOut.connect("tcp://127.0.0.1:%s" % portOut)
    socketOut.bind("tcp://192.168.2.183:%s" % portOut)

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
logThis('timestamp [event type] [event info]')
"""logThis('timestamp [block].[trial]_STM [state for each rule G1 G2 L1 L2 : 0,1,2,3] RULE [current rule]')
logThis('timestamp [block].[trial]_TGT [states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...]') 
logThis('timestamp [block].[trial]_RSP [correct: 1/0] [current rule: G1, G2, L1, L2] ANSWER [card selected: 1(up), 2(right), 3(down), 4(left)]')
logThis('timestamp [block].[trial]_FDB [correct/fail] [correct answers] of [series length]')"""
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

Sync()

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

    elif( item['type'] == 'numberorder'):
        zmqSend('TNB')
        DrawNumOrder( 110, -425, 15)
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('TNE')

    elif( item['type'] == 'vissearch'):

        targetVisible = True
        if item['target'] == 'false':
            targetVisible = False
            
        zmqSend('TSB')
        DrawVisSearch( 300, 100, 950, 950, 64, targetVisible, tgt=10, duration=-1)
        WaitForIt( keys=['x', 'b'], duration=-1 ) #only red&green buttons (x, m)
        zmqSend('TSE')

    elif( item['type'] == 'modelcopy'):
        zmqSend('TMB')
        DrawModelCopy( -300, 0, 512, 512, 7)
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('TME')
        
    elif( item['type'] == 'modelcopy2'):
        zmqSend('TMB')
        DrawModelCopyFromPic( -300, 0, item['file'])
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('TME')

    elif( item['type'] == 'quadrille'):
        zmqSend('TQB')
        #DrawChessBoard(250, -100, 500, 500, 4, flip=True)
        DrawChessBoard(350, 0, 500, 500, 4, flip=True)
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('TQE')

    elif( item['type'] == 'colorsort'):
        zmqSend('TCB')
        DrawSideBins(300, 300, 500, 250, flip=True)
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('TCE')

    elif( item['type'] == 'calib'):
        zmqSend('ECB')
        DrawCalibTargets(350, 0, 500, 500)
        WaitForIt( keys=['space'], duration=-1 ) 
        zmqSend('ECE')

    else:
        print 'unidentified item type in config: ' + item['type']


event.clearEvents()
zmqSend("EQ")

#cleanup
win.close()
core.quit()


