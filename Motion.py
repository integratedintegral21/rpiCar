from HBridges import HBridges
from PinMaps import confFiles
import RPi.GPIO as GPIO
import json
import os
import subprocess

class Motion:
    HIGH = 1
    LOW = 0

    def __init__(self, chip):
        filename = confFiles[chip]
        with open(filename) as f:
            pinMap = json.load(f)
        LForwardPin = pinMap["input1"]
        LBackwardPin = pinMap["input2"]
        LSpeedPin = pinMap["enable1"]

        RForwardPin = pinMap["input3"]
        RBackwardPin = pinMap["input4"]
        RSpeedPin = pinMap["enable2"]

        self.motorTable = [
            {
                "forPin" : LForwardPin,
                "backPin" : LBackwardPin,
                "speedPin" : LSpeedPin
            },
            {
                "forPin" : RForwardPin,
                "backPin" : RBackwardPin,
                "speedPin" : RSpeedPin
            }
        ]

        self.setupPinModes()
        self.setSpeed(0,0)
        self.setSpeed(1,0)
    
    def setPinMode(self, pin, mode):
        cmd = "gpio mode " + str(pin) + " " + mode
        print(cmd)
        subprocess.run(cmd, shell=True)

    def writePinValue(self, pin, value):
        cmd = "gpio write " + str(pin) + " " + str(value)
        print(cmd)
        subprocess.run(cmd, shell=True)
    
    def setPwmValue(self, pin, value):
        cmd = "gpio pwm " + str(pin) + " " + str(value)
        print(cmd)
        subprocess.run(cmd, shell=True)

    def setupPinModes(self):
        inputs_mode = "out"
        enable_mode = "pwm"

        self.setPinMode(self.motorTable[0]["forPin"], inputs_mode)
        self.setPinMode(self.motorTable[0]["backPin"], inputs_mode)
        self.setPinMode(self.motorTable[1]["forPin"], inputs_mode)
        self.setPinMode(self.motorTable[1]["backPin"], inputs_mode)

        self.setPinMode(self.motorTable[0]["speedPin"], enable_mode)
        self.setPinMode(self.motorTable[1]["speedPin"], enable_mode)

    def resetPinModes(self):
        self.stopDriving()
        in_mode = "in"
        self.setPinMode(self.motorTable[0]["forPin"], in_mode)
        self.setPinMode(self.motorTable[0]["backPin"], in_mode)
        self.setPinMode(self.motorTable[1]["forPin"], in_mode)
        self.setPinMode(self.motorTable[1]["backPin"], in_mode)

        self.setPinMode(self.motorTable[0]["speedPin"], in_mode)
        self.setPinMode(self.motorTable[1]["speedPin"], in_mode)
    
    def setMotorDirection(self, motor, dir): # motor: 0 = left, 1 = right; dir: 1 = forward, 0 = backward
        if dir == 0:
            self.writePinValue(self.motorTable[motor]["forPin"], self.LOW)
            self.writePinValue(self.motorTable[motor]["backPin"], self.HIGH)
        else:
            self.writePinValue(self.motorTable[motor]["forPin"], self.HIGH)
            self.writePinValue(self.motorTable[motor]["backPin"], self.LOW)

    def resetMotorDirection(self, motor):
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

        

