#-------------------------------------------------------------------------------
# Name:    2.newsmth.net user status monitor
# Purpose:  monitor status of all users at 2.newsmth.net, record possiable publishing action of each user.
#
# Author:      Hao Wei
#
# Created:     13-01-2014
# Copyright:   (c) whao 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#!/usr/bin/python
# -*- coding: utf-8 -*-
import  multiprocessing
from multiprocessing import Process , Queue
import threading
from threading import Thread
#from Queue import Queue
from time import sleep
import urllib2
import sys
import re
import signal
import httplib
import time
import types
#local time and server time
time_delay = 8*3600
#time_delay = 12*3600 - 4

result_q = Queue()

def parse_page_num(cont):
    cont = cont.decode("gbk")
    m1 = re.match(r'^.*\[(\d+)\]',cont,re.S)
    return int(m1.group(1))


def fetch_user(rd):
    rd = rd.decode("gbk")
    st = 0
    if u"目前在站上" in rd:
        st = 1
        if u"发表文章" in rd:
            st = 2
    else:
        st = 0

    return st




def poll_user(userid,result_q):
    #if(userid == "windhw"): print "focus: %s" % userid

    state = 1
    state_time = 0
    conn = httplib.HTTPConnection("www.2.newsmth.net")
    while (1):
        rd = ""
        try:
            conn.request("GET", "/bbsqry.php?userid=%s" % userid)
            r1 = conn.getresponse()
            rd = r1.read()
        except:
            conn = httplib.HTTPConnection("www.2.newsmth.net")
            continue

        parse_st = fetch_user(rd);
        if parse_st != state :
            state_time = 0

        if parse_st == 1:
            if(state == 2):
                str_time = time.strftime('[%Y-%m-%d]%H:%M:%S',time.localtime(time.time()+ time_delay))
                result_q.put( "%s | %s" % (str_time,userid) )
                state_time =  0
            sleep(5)
            state_time += 5

        if parse_st == 2:
            sleep(1+state_time/200)
            state_time += (1+state_time/200)
        if parse_st == 0:
            sleep(5)
            state_time += 5

        if(state_time > 1200):
            break
        state = parse_st
    conn.close()

class User:
    id = "" 
    # offline: 0
    # online:  1
    # edit:    2
    stat = {}
    ip = ""
    idletime = 0
    timer = 0
    proc = None

    def __init__(self, userid):
        self.id = userid
        self.stat = {u"阅读文章"   : 0, 
                     u"主菜单"     : 0,
                     u"选择讨论区" : 0,
                     u"Web浏览"    : 0,
                     u"发表文章"   : 0 }

    def update_by_main(self,userip, stat_str):
        self.ip   = userip
        self.stat[stat_str] = 1
        #hw
        #return

        if u"发表文章" in stat_str:
            #pass
            #trigger new process for this user
            if  not self.proc :
                self.proc = Process(target = poll_user , args=(self.id,result_q))
                #self.proc.daemon = True
                self.proc.start()
            elif (not self.proc.is_alive() ):
                self.proc.terminate()
                self.proc.join()
                self.proc = Process(target = poll_user , args=(self.id,result_q))
                self.proc.start()
            else:
                pass
        else:
            pass

    def print_info(self,vb=False):
        rt = "id:%s,ip:%s\n" %(self.id,self.ip)
        if(vb):
            print rt
        return rt


def fetch_page(id,q_i,q_o):
    #print "Threading %d is started" % id
    conn = httplib.HTTPConnection("www.2.newsmth.net")
    while True:
        rt = []
        #print "[%d] wait for uri" % id
        uri = q_i.get()
        #print "[%d] get uri %s" % (id,uri)
        try:
            conn.request("GET", uri,"",{"Connection":"keep-alive"})
            r1 = conn.getresponse()
            rd = r1.read()
            #fo = urllib2.urlopen("http://www.2.newsmth.net" + uri)
            #rd = fo.read()
            #rd = rd.decode('gbk')
        except:
            print "Request error!"
            rd = ""
            conn.close()
            conn = httplib.HTTPConnection("www.2.newsmth.net")
        id_str=r"""^<tr><td>\d+</td><td>  </td><td><a href="bbsqry.php\?userid=(\w+)">.+$"""
        stat_str=r"""^--></script></a></td><td>(\d+\.\d+\.\d+\.[\d\*]+)</td><td>(.+)</td><td>([ \d]+)</td>$"""
        search_id = re.compile(id_str,re.M)
        search_stat  =  re.compile(stat_str,re.M)
        lst = rd.split('</tr>\n')
        cnt = 0
        for tr in lst:
            id_m = search_id.search(tr)
            stat_m = search_stat.search(tr)
            if id_m and stat_m :
                cnt += 1
                userid =  id_m.group(1).lower()
                userip =  stat_m.group(1)
                stat_str =  stat_m.group(2)
                useridletime =  stat_m.group(3)
                #print userid
                rt.append((userid,userip,stat_str,useridletime))
        q_o.put(rt)
        #q_i.task_done()
        #print "[%d] %s is done!" % (id ,uri)

def write_result(log_name,result_q):
    while(1):
        rt = result_q.get()
        print rt
        fd = open(log_name,"a")
        fd.write(rt)
        fd.write("\n")
        fd.close()


if __name__ == '__main__':
    pages_lst = []
    users_dict = {}
    pages_q = Queue()
    uri_q   = Queue()
    #base_url = "http://www.2.newsmth.net/"
    #foot_url = base_url + "bbsfoot.php"
    #online_url = base_url + "bbsuser.php?start=%d"

    host = "www.2.newsmth.net"
    foot_uri = "/bbsfoot.php"
    online_uri = "/bbsuser.php?start=%d"

    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    log_name = "smth.log"
    p = Process(target = write_result , args=(log_name,result_q))
    p.daemon = True
    p.start()
    proc_num = 20
    workers=[]
    for i in range(20):
        p = Process(target = fetch_page , args=(i,uri_q,pages_q))
        p.start()
        workers.append(p)
    conn_foot = httplib.HTTPConnection("www.2.newsmth.net")
    while 1:
        #print "============Main loop begein=============="
        #print "URI_Q:", uri_q.empty()
        #print "PAGE_Q:", pages_q.empty()
        try:
            conn_foot.request("GET", foot_uri)
            r_foot = conn_foot.getresponse()
            rd_foot = r_foot.read()
            page_num = parse_page_num(rd_foot)
            #print "page_num : %d" % page_num
        except:
            print "Get a error when get page_num"
            sleep(1)
            conn_foot = httplib.HTTPConnection("www.2.newsmth.net")
            continue
        proc_num = (page_num + 19)/20
        #print "proc_num: %d " % proc_num
        timer = time.time()
        for i in range(proc_num):
            page_uri = online_uri % (i*20 +1)
            uri_q.put(page_uri)
        #print " ==> wait for join"
        #uri_q.join()
        cnt = 0
        for i in range(proc_num):
            rt = pages_q.get()
            for item in rt:
                #print "userid : %s" % item[0]
                cnt += 1
                userid = item[0]
                userip = item[1]
                stat_str = item[2].decode("gbk")
                useridletime = item[3]
                if users_dict.has_key(userid):
                    user = users_dict[userid]
                else:
                    user = User(userid)
                    users_dict[userid] = user
                user.update_by_main(userip,stat_str)
        print " --------------------------------get %4d users, %3.3f  s" %( cnt,   (time.time()-timer) )
        sleep(3)
