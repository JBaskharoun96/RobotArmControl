import GUIPanel
import os
import random
import sched
import threading
import time


def coordsUpdate():

    dataFile = open('data.txt', 'w')

    dataFile.write("%s %s\n" % (joystick.xz_coordinates[0], joystick.xz_coordinates[1]))
    dataFile.write("extendclaw=%d\n" % random.randint(0,1))
    dataFile.write("gripclaw=%d\n" % random.randint(0,1))

    dataFile.close()

    print("Sending data.txt:")
    print(joystick.xz_coordinates)

    os.system('scp "%s" "%s:%s"' % ("data.txt", "volcane@192.168.0.17", "~/Code/RobotArm/data.txt"))
    
    print("Data sent")


def periodicEvent(scheduler, interval, action):

    if joystick.close:
        exit()

    scheduler.enter(interval, 1, periodicEvent,
                    (scheduler, interval, action))
    action()


def main():

    scheduler = sched.scheduler(time.time, time.sleep)

    periodicEvent(scheduler, 0.6, coordsUpdate)

    schedulerThread = threading.Thread(target=scheduler.run)
    schedulerThread.start()

    joystick.run()


joystick = GUIPanel.JoyStick()
main()
