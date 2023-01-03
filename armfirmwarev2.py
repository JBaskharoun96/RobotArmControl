import GUIPanel
import os
import sched
import threading
import time


def coordsUpdate():

    dataFile = open('data.txt', 'w')

    dataFile.write("%s %s\n" % (joystick.xz_coordinates[0], joystick.xz_coordinates[1]))
    dataFile.write("extendclaw=%s\n" % (1 if not joystick.ExtendDown else 0) )
    dataFile.write("gripclaw=%s\n" % (1 if not joystick.GrabDown else 0) )

    dataFile.close()

    print("Sending data.txt:")
    print(joystick.xz_coordinates)

    os.system('scp "%s" "%s:%s"' % ("data.txt", "volcane@192.168.0.13", "~/Code/RobotArm/data.txt"))

    print("Data sent")


def periodicEvent(scheduler, interval, action):

    if joystick.close:
        exit()

    scheduler.enter(interval, 1, periodicEvent,
                    (scheduler, interval, action))
    action()


def main():

    scheduler = sched.scheduler(time.time, time.sleep)

    periodicEvent(scheduler, 0.003, coordsUpdate)

    schedulerThread = threading.Thread(target=scheduler.run)
    schedulerThread.start()

    joystick.run()


if __name__ == "__main__":

    joystick = GUIPanel.JoyStick()
    main()
