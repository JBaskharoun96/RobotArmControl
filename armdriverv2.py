import RPi.GPIO as GPIO
import os
import sched
import time
import threading


class ArmDriver:

    def __init__(self):

        if True:  # GPIO Output Pinout  
            self.pullMainPin = 2
            self.pushMainPin = 3
            self.turnLeftPin = 4
            self.turnRightPin = 17
            self.extendClawPin = 22
            self.retractClawPin = 27
            self.closeClawPin = 9
            self.openClawPin = 10

        # Initializing position of arm at center of close wall and joystick coords to 0
        self.currentPosition = [0, -20]
        self.xyCoords = [0, 0]
        self.extendClaw = 0
        self.gripClaw = 0

        if True:  # Input Signal Setup
            self.pushMainInput    = False
            self.pullMainInput    = False
            self.turnLeftInput    = False
            self.turnRightInput   = False
            self.extendClawInput  = False
            self.retractClawInput = False
            self.closeClawInput   = False
            self.openClawInput    = False

        # Board Setup
        GPIO.setmode(GPIO.BCM)

        if True:  # Relay Outputs Setup
            GPIO.setup(self.pushMainPin,    GPIO.OUT)
            GPIO.setup(self.pullMainPin,    GPIO.OUT)
            GPIO.setup(self.turnLeftPin,    GPIO.OUT)
            GPIO.setup(self.turnRightPin,   GPIO.OUT)
            GPIO.setup(self.extendClawPin,  GPIO.OUT)
            GPIO.setup(self.retractClawPin, GPIO.OUT)
            GPIO.setup(self.closeClawPin,   GPIO.OUT)
            GPIO.setup(self.openClawPin,    GPIO.OUT)


    def dataUpdate(self):
        """Opens data file which will be written into by armfirmware to get joystick coordinates and claw flags"""

        dataFile = open('data.txt', 'r')

        self.xyCoords = [int(x) for x in dataFile.readline().split(' ')]
        self.extendClaw = int(dataFile.readline()[-2])
        self.gripClaw = int(dataFile.readline()[-2])

        print("\nCurrent position (x,y): [%d, %d]" % (self.currentPosition[0], self.currentPosition[1]) )
        print("XY Coordinates of joystick: %d %d" % (self.xyCoords[0], self.xyCoords[1]) )
        # print("Extend claw input: %d" % self.extendClaw)
        print("Grip claw input: %d" % self.gripClaw)

        dataFile.close()


    def sendOutputs(self):
        """Based on inputs determined from joystick data, send output activation to proper GPIO pins"""

        # First check if arm is limited by physical constraints, and if so disable movement and return
        if not self.checkLimit():
            GPIO.output(self.pushMainPin, False)
            GPIO.output(self.pullMainPin, False)
            GPIO.output(self.turnLeftPin, False)
            GPIO.output(self.turnRightPin, False)
            return

        if self.pushMainInput:
            GPIO.output(self.pushMainPin, True); GPIO.output(self.pullMainPin, False)
            self.currentPosition[1] = 80

        elif self.pullMainInput:
            GPIO.output(self.pushMainPin, False); GPIO.output(self.pullMainPin, True)
            self.currentPosition[1] = -20

        else:
            GPIO.output(self.pushMainPin, False); GPIO.output(self.pullMainPin, False)
            self.currentPosition[1] = 0

        if self.turnLeftInput:
            GPIO.output(self.turnLeftPin, True); GPIO.output(self.turnRightPin, False)
            self.currentPosition[0] = -100

        elif self.turnRightInput:
            GPIO.output(self.turnLeftPin, False); GPIO.output(self.turnRightPin, True)
            self.currentPosition[0] = 100

        else:
            GPIO.output(self.turnLeftPin, False); GPIO.output(self.turnRightPin, False)
            self.currentPosition[0] = 0

        if self.extendClawInput:
            GPIO.output(self.extendClawPin, True); GPIO.output(self.retractClawPin, False)
        elif self.retractClawInput:
            GPIO.output(self.extendClawPin, False); GPIO.output(self.retractClawPin, True)
        else:
            GPIO.output(self.extendClawPin, False); GPIO.output(self.retractClawPin, False)

        if self.closeClawInput:
            GPIO.output(self.closeClawPin, True); GPIO.output(self.openClawPin, False)
        elif self.openClawInput:
            GPIO.output(self.closeClawPin, False); GPIO.output(self.openClawPin, True)
        else:
            GPIO.output(self.closeClawPin, False); GPIO.output(self.openClawPin, False)


    def convertJoystick(self):
        """Converts the xy coordinates from the joystick into the appropriate set of GPIO output flags"""
        # Using a deadzone of +- 8 to make it easier to hit cardinal direction outputs instead of diagonals

        if    self.xyCoords[0] < -8:  self.turnLeftInput   = True;   self.turnRightInput   = False
        elif  self.xyCoords[0] > 8:   self.turnLeftInput   = False;  self.turnRightInput   = True
        else:                         self.turnLeftInput   = False;  self.turnRightInput   = False

        if    self.xyCoords[1] > 8:   self.pushMainInput   = True;   self.pullMainInput    = False; \
                                      self.extendClawInput = True;   self.retractClawInput = False
        elif  self.xyCoords[1] < -8:  self.pushMainInput   = False;  self.pullMainInput    = True; \
                                      self.extendClawInput = False;  self.retractClawInput = True
        else:                         self.pushMainInput   = False;  self.pullMainInput    = False; \
                                      self.extendClawInput = False;  self.retractClawInput = False

        if self.gripClaw: self.closeClawInput = True; self.openClawInput = False
        else:             self.closeClawInput = False; self.openClawInput = True

    def checkLimit(self):
        """Returns True if the attempted move is safe, and False if the attempted move is unsafe"""

        return True

        # If not yet at a wall, any move will be safe
        if self.currentPosition[0] not in {100, -100} and self.currentPosition[1] not in {100, -100}:
            return True

        # If attempting to extend and the tip position is at the far walls, unsafe move
        if self.pushMainInput and self.currentPosition[1] == 100:
            return False

        # If retracting, don't retract further than back wall
        if self.pullMainInput and self.currentPosition[1] == -100:
            return False

        # For moves which turn left, unsafe if x position is on left wall
        if self.turnLeftInput and self.currentPosition[0] == -100:
            return False

        # For moves which turn right, unsafe if x position is on right wall 
        if self.turnRightInput and self.currentPosition[0] == 100:
            return False

        return True


    def programTicker(self, scheduler, interval):
        """Function which re-schedules a new version of itself before carrying out tick functions"""
        
        scheduler.enter(interval, 1, self.programTicker,
                        (scheduler, interval))

        self.dataUpdate()
        self.convertJoystick()
        self.sendOutputs()


def main():

    # Initialize ArmDriver object and scheduler
    armControl = ArmDriver()
    scheduler = sched.scheduler(time.time, time.sleep)

    # Establish program tick loop and start scheduler running in separate thread
    armControl.programTicker(scheduler, 0.002)
    schedulerThread = threading.Thread(target=scheduler.run)
    schedulerThread.start()

    # Try block used here for the finally clause which we need to run when the program closes
    try:

        # Repeatedly sleep while the other thread carries out the ArmDriver tick scheduler
        while True:
            time.sleep(8)

    # Finally block runs at end of program, cleans up GPIO and uses os._exit(1) to make all threads exit cleanly
    finally:
        GPIO.cleanup()
        os._exit(1)


if __name__ == "__main__":
    
    main()