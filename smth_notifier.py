#-------------------------------------------------------------------------------
# Name:    smth_notifier 
# Purpose: continuously monitor newsmth borad and notify user by email when desired post published.
#
# Author:      Hao Wei
#
# Created:     13-01-2014
# Copyright:   (c) whao 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#!/usr/bin/python
# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
from time import sleep
import urllib2
import sys
import re
import signal
import httplib
import time
import smtplib
import os
from email.mime import text

smth_prot = "http"
smth_host = "www.newsmth.net"
smth_ip   = "42.62.43.22"
latest_page_uri = "bbsdoc.php?board=ITjob&ftype=6"

def log(cont):
    #f = open("smth.log","a")
    #f.write(cont)
    #f.write("\n")
    #f.close()
    print cont.encode("utf-8")

def parse_post(post_list):
    notifiers = {}
    #if True:
    try:
        fo = urllib2.urlopen(urllib2.Request("%s://%s/%s" % (smth_prot,smth_ip,latest_page_uri), None, {"HOST": smth_host}, smth_host))
        rd = fo.read()
        rd = rd.decode('gbk')
        fo.close()
        lst = rd.split('\n')
        regstr  = r"""c\.o\((\d+),\d+,'([\d\w]+)','([a-z\@\s]+)',\d+,'(.+)',\d+,\d+,\d+\)"""
        regstr_c  =  re.compile(regstr,re.M)
        cnt = 0
        for tr in lst:
            regstr_m = regstr_c.search(tr)
            if regstr_m:
                cnt += 1
                post_id =  int(regstr_m.group(1))
                post_author =  regstr_m.group(2)
                post_flag =  regstr_m.group(3)
                post_title =  regstr_m.group(4)
                #print("[%10d][%15s]%s" % (int(post_id),post_author,post_title))
                if not post_list.has_key(post_id) or post_list[post_id].title != post_title:
                    if not u"实习" in post_title and not u"招聘" in post_title:
                        post = Post(post_id,post_author,post_flag,post_title)
                        notifiers[post_id] = post

    except:
        print "Meet error"
        return None
    for k in notifiers.keys():
        post_list[k] = notifiers[k]
    return notifiers
    #print "process %d finished!" % id

def build_message(notifiers):
    subject = u"水木兼职版新主题"
    toaddrs = ["haow05@126.com"]
    content = u""
    for k in notifiers:
        p = notifiers[k]
        content += u"""<p><a href="%s">%s:%s</a></p>\n""" % (p.get_url(),p.author,p.title)
    return (toaddrs,subject,content)

class Post:
    board = "ITjob"
    author= None
    id = None
    title = None
    flag = None
    content = None
    def get_url(self):
        return "%s://%s/nForum/article/%s/%d" % (smth_prot,smth_host,self.board,self.id)
    def __init__(self,id,author,flag,title):
        self.id = id
        self.title = title
        self.flag = flag
        self.author = author


# Specifying the from and to addresses
def send_mail(toaddrs  = ['haow05@126.com'],subject = "Mail test",content="test mail"):
    from_txt = 'NewSmth Notifier <notifier.apptest@gmail.com>'
    from_addr = 'notifier.apptest@gmail.com'

    # Writing the message (this message will appear in the email)
    msg = text.MIMEText(content,'html','utf-8')
    msg['From'] = from_txt
    msg['To']   = ";".join(toaddrs)
    msg['Subject']= subject

    # Gmail Login
    #Fill in your username of gmail
    mail_username = 'user'
    #then password
    mail_password = '123456'

    # Sending the mail
    try:
        #server = smtplib.SMTP('smtp.gmail.com', 25)
        server = smtplib.SMTP('173.194.72.108', 25)

        server.ehlo()
        server.starttls()
        server.ehlo()
    except:
        log( 'Cannot Connect')
        # login with username & password
        # print 'loginning ...'
    try:
        server.login(mail_username,mail_password)
    except:
        log( 'Cannot Login')
    try:
        server.sendmail(from_addr, toaddrs, msg.as_string() )
        server.quit()
    except:
        log( 'Cannot Send Mail')


if __name__ == '__main__':
    post_list = {}
    try:
        if os.fork() > 0:
            os._exit(0) # exit father…
    except OSError, error:
        print 'fork #1 failed: %d (%s) '%  (error.errno, error.strerror)
        os._exit(1)
    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    os.chdir("/")
    os.setsid()
    os.umask(0)

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    si = file("/dev/null", 'r')
    so = file("/tmp/tmp_1234.log", 'a+', 0)
    #se = file("/tmp/tmp_1234.log", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(so.fileno(), sys.stderr.fileno())
    cnt =0
    while 1:
        #if True:
        try:
            notifiers = parse_post(post_list)
            if(notifiers):
                (toaddrs ,subject, content  ) = build_message(notifiers)
                log(  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) )
                log(  content)
                send_mail(toaddrs ,subject, content  )
                #send_notifer(notifiers)
        except:
            log(  "Get a error when get notifiers ")
            sleep(5)
            continue
        log(  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))
        log(  "Loop %d end, begin to sleep" % cnt)
        cnt +=1
        sleep(10)
