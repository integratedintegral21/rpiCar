from re import S
from CameraStreamer import PiCameraStreamer
from Motion import Motion
from HBridges import HBridges
from Views import View
from threading import Thread, Lock
import time
from threading import Lock
import RPi.GPIO as GPIO
import os
import logging

class StreamThread(Thread):
    udpStreaming = 0
    targetIp = "192.168.0.52"
    targetPort = 5000

    stop = 0
    log = logging.Logger(name="log",level=0)

    lock = Lock()

    def __init__(self, view):
        Thread.__init__(self)
        self.streamer = PiCameraStreamer(640, 480, 15)
        self.view = view
    
    def run(self):
        while True:
            if self.stop == 1:
                break
            if self.udpStreaming == 1:
                code = self.streamer.udpStream(self.targetIp, self.targetPort)
                if self.view.askForStreamingAttempt(code) is False:
                    self.stopUdp()

    
    def stopUdp(self):
        self.udpStreaming = 0
    
    def startUdp(self):
        self.udpStreaming = 1
    
    def stop(self):
        self.lock.acquire()
        self.udpStreaming = 0
        self.stop = 1
        self.lock.release()

class MotionThread(Thread):
    forSpeed = 0
    intForSpeed = 0

    def __init__(self, view):
        Thread.__init__(self)
        self.motion = Motion(HBridges().TB6612FNG)
        self.view = view
    
    def run(self):
        while True:
            pass
    
    def setForSpeed():
        pass



class Controller(Thread):
    view = None
    streamer = None
    maxSpeed = 1000
    maxRotSpeed = 500

    streamThread = None

    def __init__(self):
        Thread.__init__(self)
        self.view = View()
        self.view.start() 
        
        self.motion = Motion(HBridges().TB6612FNG)    
        '''    
        self.motion.startDriving(1000, 1)
        time.sleep(1)
        self.motion.startDriving(1000, 0)
        time.sleep(2)
        self.motion.startRotating(1000, 1)
        time.sleep(2)
        self.motion.stopRotating()
        self.motion.startRotating(1000, 0)
        time.sleep(2)
        self.motion.stopRotating()'''
        
        self.streamThread = StreamThread(self.view)
        #self.motionThread = MotionThread(self.view)

        self.streamThread.start()
        #self.motionThread.start()

    def run(self):
        try:      
            while True:
                if self.view.interrupts["main"] == 1:
                    if self.view.interrupts["connect_camera"] == 1:
                        self.streamThread.targetIp = self.view.targetUdpIp
                        self.streamThread.targetPort = self.view.targetUdpPort
                        self.streamThread.startUdp()
                        self.view.interrupts["connect_camera"] = 0
                        self.view.interrupts["main"] = 0
                    if self.view.interrupts["abort_connection"] == 1:
                        self.streamThread.stopUdp()
                        self.view.interrupts["abort_connection"] = 0
                        self.view.interrupts["main"] = 0
                    if self.view.closed == 1:
                        print("Closing")
                        self.streamThread.stop()
                        self.view.interrupts["main"] = 0
                        break
                    if self.view.interrupts["set_speed"] == 1:
                        speed = self.view.getForSpeed()
                        rotSpeed = self.view.getRotSpeed() * self.maxRotSpeed / self.maxSpeed
                        if speed < 0:
                            rotSpeed = -rotSpeed
                        speeds = [speed - rotSpeed, speed + rotSpeed]
                        for motorNr, sp in enumerate(speeds):
                            dir = 0
                            if sp > 0:
                                dir = 1
                            self.motion.setMotorDirection(motorNr,dir)
                            motorSpeed = min(self.maxSpeed, self.maxSpeed*abs(sp) / 100)
                            print(motorSpeed)
                            self.motion.setSpeed(motorNr, motorSpeed)
                        self.view.interrupts["set_speed"] = 0
                        self.view.interrupts["main"] = 0
                
                    
        finally:
            self.motion.resetPinModes()
            pass
 