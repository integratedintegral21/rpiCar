import os
import time
import subprocess

class PiCameraStreamer:
    UDP_SCRIPT_PATH = "scripts/udpCameraRun.sh"
    
    width = 1280
    height = 720
    fps = 24

    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
    
    def udpStream(self,target_ip, target_port):
        udpCommand = ["./{0}".format(self.UDP_SCRIPT_PATH),"udp://" + target_ip + ":" + str(target_port), str(self.width), str(self.height)]
        result = subprocess.run(udpCommand)
        return result.returncode
    
    def udpStreamForever(self,target_ip, target_port):
        while True:
            self.udpStream(target_ip, target_port)
        print("Ending streaming")
