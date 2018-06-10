# -*- coding: utf-8 -*-

"""
    Code based on:

https://github.com/mvillalba/python-ant/blob/develop/demos/ant.core/03-basicchannel.py

    in the python-ant repository and

https://github.com/tomwardill/developerhealth

    by Tom Wardill and

https://www.johannesbader.ch/2014/06/track-your-heartrate-on-raspberry-pi-with-ant/

    by Johannes Bader
"""
import sys
import time
from ant.core import driver, node, event, message, log
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER

import json

class HeartRateMonitor(event.EventCallback):

    DEFAULT_SERIAL = "/dev/ttyUSB0"
    DEFAULT_NETKEY = 'B9A521FBBD72C345'.decode('hex')

    def __init__(self, call_func, serial = None, netkey = None):
        self.call_func = call_func
        self.serial = serial or HeartRateMonitor.DEFAULT_SERIAL
        self.netkey = netkey or HeartRateMonitor.DEFAULT_NETKEY
        self.antnode = None
        self.channel = None

    def start(self):
        #print("starting node")
        self._start_antnode()
        self._setup_channel()
        self.channel.registerCallback(self)
        #print("start listening for hr events")

    def stop(self):
        if self.channel:
            self.channel.close()
            self.channel.unassign()
        if self.antnode:
            self.antnode.stop()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.stop()

    def _start_antnode(self):
        stick = driver.USB2Driver(self.serial)
        self.antnode = node.Node(stick)
        self.antnode.start()

    def _setup_channel(self):
        key = node.NetworkKey('N:ANT+', self.netkey)
        self.antnode.setNetworkKey(0, key)
        self.channel = self.antnode.getFreeChannel()
        self.channel.name = 'C:HRM'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(120, 0, 0)
        self.channel.setSearchTimeout(TIMEOUT_NEVER)
        self.channel.setPeriod(8070)
        self.channel.setFrequency(57)
        self.channel.open()

    def process(self, msg):
        time.sleep(5)  # 5秒の停止
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            #print("heart rate is {}".format(ord(msg.payload[-1])))
            heart_rate = int(ord(msg.payload[-1]))
            self.call_func(heart_rate)

def my_print(data):
    print("heart rate is {}".format(data))

    # 心拍数をJSONファイルに書き込む    
    data_json = {"heart_rate": data}
    file = open("heart_rate.json", "w")
    json.dump(data_json , file)
    

if __name__ == '__main__':
    hrm = HeartRateMonitor(my_print)
    print("monitor start")
    hrm.start()
    print("monitor start listening")
    print("press Ctrl-C to stop this script")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("monitor stop")
            hrm.stop()
            sys.exit(0)

