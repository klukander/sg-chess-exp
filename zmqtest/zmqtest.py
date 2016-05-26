
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
"""
elif platform.system == 'Linux':
    import sys
    import select

    def heardEnter():
        i,o,e = select.select([sys.stdin],[],[],0.0001)
        for s in i:
            if s == sys.stdin:
                input = sys.stdin.readline()
                return True
        return False
"""
        
#initialize zmq
context = zmq.Context()
#socketIn = context.socket(zmq.SUB)
socketOut = context.socket(zmq.PAIR)
#portIn = "5557"
portOut = "5555"
#socketIn.connect("tcp://127.0.0.1:%s" % portIn)
#socketOut.bind("tcp://127.0.0.1:%s" % portOut)
socketOut.bind("tcp://192.168.2.245:%s" % portOut)

msgs = ("ZT", "TQB", "TQE", "IB", "IE", "MQQ0A1B2", "MKW0B2C2")

keepRunning = True
zerotime = time.time()

while keepRunning:
    msg = msgs[randint(0, len(msgs)-1)]
    if msg == "ZT":
        zerotime = time.time()
    socketOut.send("%s" % msg)#("p", msg))
    print "sending %s, time: %s" % (msg, time.time()-zerotime)
    #socketOut.send("%s %s" % ("you_will_never_see_me", "crapperjack"))
    time.sleep(0.25)
    if kbfunc() != 0:
        keepRunning = False
        
