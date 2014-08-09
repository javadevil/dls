import socket
import logging
from threading import Thread
from django.conf import settings

def watcher(handler,port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((settings.GPS_HOST,port))
    s.listen(1)
    print('GPS Watcher[{}] {}'.format(handler.NAME,port))
    while 1:
        conn,addr = s.accept()
        p = handler(conn,addr)
        Thread(target=p.run).start()

def start():
    print('Receiver Start')
    for w in settings.GPS_PROTOCOLS:
        Thread(target=watcher,args=(w[0],w[1])).start()