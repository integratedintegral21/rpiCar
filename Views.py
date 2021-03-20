import subprocess
import tkinter as tk
from threading import Thread, Lock
from tkinter import messagebox
import re
import time

class MainWindow(tk.Tk):
    pass


class View(Thread):
    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 480

    BUTTON_WIDTH = 15
    BUTTON_HEIGHT = 2

    targetUdpIp = "192.168.0.52"
    targetUdpPort = 5000

    closed = 0
    cmd = None

    forwardKey = 'w'
    backwardKey = 's'
    leftKey = 'a'
    rightKey = 'd'
    stopKey = 'x'
    stopRotKey = 'z'
    stopAllKey = 'c'

    linearSpeed = 0
    rotSpeed = 0
    
    lock = Lock()

    def __init__(self):
        Thread.__init__(self)
        self.interrupts = {
            "main": 0,
            "connect_camera": 0,
            "abort_connection": 0,
            "set_speed" : 0,
        }
    
    def verifySocket(self):
        sck = self.targetSocketEntry.get()
        verified = re.match('^[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+$', sck)
        if verified:
            sck = sck.split(':')
            if len(sck) == 2:
                return sck
        else:
            return None
    def controllerStartMessage(self):
        print("Controller is now running...")

    def askForStreamingAttempt(self, code):
        answer = messagebox.askquestion('Stream failed [Exit code {0}]', 'Do you want to retry?'.format(code))
        if answer == 'yes':
            return True
        return False

    def askForCommand(self):
        return input("Enter a command: ")

    def connectButtonClick(self):
        self.lock.acquire()
        socket = self.verifySocket()
        if socket is not None:
            self.targetUdpIp = socket[0]
            self.targetUdpPort = socket[1]
            self.interrupts["main"] = 1
            self.interrupts["connect_camera"] = 1
        else:
            pass
        self.lock.release()
    def abortButtonClick(self):
        self.lock.acquire()
        self.interrupts["main"] = 1
        self.interrupts["abort_connection"] = 1
        self.lock.release()
    def exitButtonClick(self):
        self.lock.acquire()
        self.window.quit()
        self.interrupts["main"] = 1
        self.closed = 1
        self.lock.release()
    def steeringKeyPressed(self,event):
        self.lock.acquire()
        if event.char == self.forwardKey:
            print("Linear speed set to +max")
            self.linearSpeed = 100
        if event.char == self.backwardKey:
            print("Linear speed set to -max")
            self.linearSpeed = -100
        if event.char == self.stopKey or event.char == self.stopAllKey:
            print("Linear speed set to 0")
            self.linearSpeed = 0        
        if event.char == self.stopRotKey or event.char == self.stopAllKey:
            print("Angular speed set to 0")
            self.rotSpeed = 0        
        if event.char == self.leftKey :
            print("Angular speed set to 100")
            self.rotSpeed = 100
        if event.char == self.rightKey:
            print("Angular speed set to -100")
            self.rotSpeed = -100
        self.interrupts["main"] = 1
        self.interrupts["set_speed"] = 1
        self.lock.release()
    
    def steeringKeyRelease(self, event):
        self.lock.acquire()
        if event.char == self.forwardKey:
            print("Linear speed set to 0")
            self.linearSpeed = 0
            self.interrupts["main"] = 1
            self.interrupts["set_speed"] = 1
        if event.char == self.backwardKey:
            print("Linear speed set to 0")
            self.linearSpeed = 0
            self.interrupts["main"] = 1
            self.interrupts["set_speed"] = 1
        
        self.lock.release()

    def getForSpeed(self):
        return self.linearSpeed
    def getRotSpeed(self):
        return self.rotSpeed
    def run(self):
        self.window = MainWindow()
        self.window.geometry('{0}x{1}'.format(self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.window.title("rpiCar Controller Main Window")
        self.window.resizable(0, 0)

        self.cameraFrame = tk.Frame(self.window, relief=tk.RAISED, borderwidth=1)
        self.cameraFrame.pack(side=tk.LEFT)

        self.motionFrame = tk.Frame(self.window, relief=tk.RAISED, borderwidth=1)
        self.motionFrame.pack(side=tk.LEFT)
        
        # camera
        self.cameraFrameTitleLabel = tk.Label(self.cameraFrame, text="Camera")
        self.targetSocketEntryLabel = tk.Label(self.cameraFrame, text="Target UDP socket:")
        self.targetSocketEntry = tk.Entry(self.cameraFrame,textvariable=(self.targetUdpIp + str(self.targetUdpPort)))
        self.connectButton = tk.Button(self.cameraFrame, text="Connect camera", bg='gray', command=self.connectButtonClick, height=self.BUTTON_HEIGHT, width=self.BUTTON_WIDTH)
        self.abortConnection = tk.Button(self.cameraFrame, text="Abort connection", bg='gray', command=self.abortButtonClick, height=self.BUTTON_HEIGHT, width=self.BUTTON_WIDTH)
        self.exitProgramButtion = tk.Button(self.cameraFrame, text="Exit", bg='gray', command=self.exitButtonClick, height=self.BUTTON_HEIGHT, width=self.BUTTON_WIDTH)

        self.cameraFrameTitleLabel.pack()
        self.targetSocketEntryLabel.pack()
        self.targetSocketEntry.pack()
        self.connectButton.pack()
        self.abortConnection.pack()
        self.exitProgramButtion.pack()

        # motion
        self.motionFrameTitleLabel = tk.Label(self.motionFrame, text="Motion")
        #self.forSpeedSlider = tk.Scale(self.motionFrame,from_=100, to=-100,length=150)
        #self.rotSpeedSlider = tk.Scale(self.motionFrame,from_=100, to=-100,length=150, orient=tk.HORIZONTAL)
        
        self.motionFrameTitleLabel.pack()
        #self.forSpeedSlider.pack()
        #self.rotSpeedSlider.pack()
        
        self.window.bind('<KeyPress-' + self.forwardKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.backwardKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.stopKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.stopRotKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.leftKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.rightKey + '>', self.steeringKeyPressed)
        self.window.bind('<KeyPress-' + self.stopAllKey + '>', self.steeringKeyPressed)

        #self.window.bind('<KeyRelease-' + self.forwardKey + '>', self.steeringKeyRelease)
        #self.window.bind('<KeyRelease-' + self.backwardKey + '>', self.steeringKeyRelease)
        self.window.mainloop()

