#-------------------------------------------------------------------------------
# Name:        Telnet into Smth  using python
# Purpose:
#
# Author:      Hao Wei
#
# Created:     13-01-2014
# Copyright:   (c) whao 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import telnetlib
import time

down_key  = chr(27)+'[A'
down_key  = chr(27)+'[B'
right_key = chr(27)+'[C'
left_key  = chr(27)+'[D'

def main():
    tn = telnetlib.Telnet("bbs.2.newsmth.net")
    time.sleep(2)
    rd =  tn.read_very_eager();
    f = open("telnet_prelogin.txt","w")
    f.write(rd)
    f.close()
    time.sleep(0.05)
    tn.write("guest\n");
    time.sleep(0.2)
    rd =  tn.read_very_eager();
    f = open("telnet_login.txt","w")
    f.write(rd)
    f.close()
    for i in range(12):
        time.sleep(0.2)
        tn.write(left_key);
        rd = tn.read_very_eager();
	print "====================%d===========" % i
	#print rd
	f = open("telnet_%d.txt"%i,"w")
	f.write(rd)
	f.close()
    time.sleep(2)
    tn.write("T");
    time.sleep(0.2)
    rd =  tn.read_very_eager(); 
    time.sleep(0.2)
    tn.write("\n");
    time.sleep(0.2)
    rd =  tn.read_very_eager();
    #print rd
    time.sleep(3)
    tn.write("U")
    time.sleep(0.5)
    print tn.read_very_eager();
    time.sleep(0.5)
    tn.write("\n");
    time.sleep(0.5)
    rd = tn.read_very_eager();
    f = open("telnet_8976.txt","wb")
    f.write(rd)
    f.close()
if __name__ == '__main__':
    main()
