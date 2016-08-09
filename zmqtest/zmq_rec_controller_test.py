
import zmq
import platform
import time
from random import randint

#if platform.system == 'Windows':
import msvcrt 

def kbfunc(): 
   x = msvcrt.kbhit()
   if x: 
      ret = ord(msvcrt.getch()) 
   else: 
      ret = 0 
   return ret
        
#initialize zmq
context = zmq.Context()
socketOut = context.socket(zmq.PAIR)
portOut = "5556"
socketOut.bind("tcp://127.0.0.1:%s" % portOut)

#msgs = ("ZT", "TQB", "TQE", "IB", "IE", "MQQ0A1B2", "MKW0B2C2")

keepRunning = True
zerotime = time.time()

recording = False
videonum = 0;

msg_start = "TQB"
msg_stop = "TQE"

while keepRunning:
    key = kbfunc()
    if key == 27:
        print "quitting"
        keepRunning = False;
    elif key <> 0:
        recording = not recording
        if recording:
            videonum += 1
            print "start recording %s" % videonum
            socketOut.send("%s" % msg_start)
            #socket
        else:
            print "stop recording %s" % videonum
            socketOut.send("%s" % msg_stop)
        
