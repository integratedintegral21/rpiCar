from HBridges import HBridges
from PinMaps import confFiles
import RPi.GPIO as GPIO
import json
import time
import threading
import logging
import os

class Motion:
    LForwardPin = None
    LBackwardPin = None
    LSpeedPin = None

    RForwardPin = None
    RBackwardPin = None
    RSpeedPin = None

    HIGH = 1
    LOW = 0

    def __init__(self, chip):
        filename = confFiles[chip]
        with open(filename) as f:
            pinMap = json.load(f)
        self.LForwardPin = pinMap["input1"]
        self.LBackwardPin = pinMap["input2"]
        self.LSpeedPin = pinMap["enable1"]

        self.RForwardPin = pinMap["input3"]
        self.RBackwardPin = pinMap["input4"]
        self.RSpeedPin = pinMap["enable2"]

        gpio_mode_cmd = "gpio mode "
        inputs_mode = "out"
        enable_mode = "pwm"

        self.setPinMode(self.LForwardPin, inputs_mode)
        self.setPinMode(self.LBackwardPin, inputs_mode)
        self.setPinMode(self.RForwardPin, inputs_mode)
        self.setPinMode(self.RBackwardPin, inputs_mode)

        self.setPinMode(self.LSpeedPin, enable_mode)
        self.setPinMode(self.RSpeedPin, enable_mode)

        self.motorTable = [
            {
                "forPin" : self.LForwardPin,
                "backPin" : self.LBackwardPin,
                "speedPin" : self.LSpeedPin
            },
            {
                "forPin" : self.RForwardPin,
                "backPin" : self.RBackwardPin,
                "speedPin" : self.RSpeedPin
            }
        ]
    
    def setPinMode(self, pin, mode):
        cmd = "gpio mode " + str(pin) + " " + mode
        print(cmd)
        os.system(cmd)

    def writePinValue(self, pin, value):
        cmd = "gpio write " + str(pin) + " " + str(value)
        print(cmd)
        os.system(cmd)
    
    def setPwmValue(self, pin, value):
        cmd = "gpio pwm " + str(pin) + " " + str(value)
        print(cmd)
        os.system(cmd)

    def resetPinModes(self):
        in_mode = "in"
        self.setPinMode(self.LForwardPin, in_mode)
        self.setPinMode(self.LBackwardPin, in_mode)
        self.setPinMode(self.RForwardPin, in_mode)
        self.setPinMode(self.RBackwardPin, in_mode)

        self.setPinMode(self.LSpeedPin, in_mode)
        self.setPinMode(self.RSpeedPin, in_mode)
    
    def setMotorDirection(self, motor, dir): # motor: 0 = left, 1 = right; dir: 1 = forward, 0 = backward
        if dir == 0:
            self.writePinValue(self.motorTable[motor]["forPin"], self.LOW)
            self.writePinValue(self.motorTable[motor]["backPin"], self.HIGH)
        else:
            self.writePinValue(self.motorTable[motor]["forPin"], self.HIGH)
            self.writePinValue(self.motorTable[motor]["backPin"], self.LOW)

    def resetMotorDirection(self, motor):
        if motor == 0:
            self.writePinValue(self.motorTable[motor]["forPin"], self.LOW)
            self.writePinValue(self.motorTable[motor]["backPin"], self.LOW)
        else:
            self.writePinValue(self.motorTable[motor]["forPin"], self.LOW)
            self.writePinValue(self.motorTable[motor]["backPin"], self.LOW)
    
    def setSpeed(self, motor, speed): # motor: 0 = left, 1 = right
        self.setPwmValue(self.motorTable[motor]["speedPin"], speed)

    def stopRotateMotor(self, motor):
        self.resetMotorDirection(motor)
        self.setSpeed(motor, 0)
    
    def startRotating(self, speed, dir): # 0 - left 1 - right
        self.setMotorDirection(1, not(dir))
        self.setMotorDirection(0, dir)

        self.setSpeed(1, speed)
        self.setSpeed(0, speed)
    def startDriving(self, speed, dir):
        self.setMotorDirection(1, dir)
        self.setMotorDirection(0, dir)

        self.setSpeed(1, speed)
        self.setSpeed(0, speed)
    
    def stopDriving(self):
        self.setSpeed(0,0)
        self.setSpeed(0,1)

        self.resetMotorDirection(0)
        self.resetMotorDirection(1)
    
    def stopRotating(self):
        self.stopRotateMotor(1)
        self.stopRotateMotor(0)

        

