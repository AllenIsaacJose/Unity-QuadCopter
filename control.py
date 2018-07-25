import socket
import time
import threading
import itertools

actions = list(itertools.product([-1,0,1], repeat = 4))
step = 1
class Drone_Control:

    def __init__(self,PORT,delta_w):
        self.port = PORT
        self.listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.listener.connect(("localhost",PORT+1))
        self.delta_w = delta_w
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect(("localhost",PORT))
        self.thrusts = [0,0,0,0]
        self.rotation = [0,0,0]
        self.velocity = [0,0,0]
        self.crashed = False
        self.listena = True;
        self.lock = threading.Lock()
        self.listen = threading.Thread(target = self.listener_thread)
        self.listen.start()

    def listener_thread(self):
        while self.listena:
            crashed = self.listener.recv(1024).decode("UTF-8")
            if crashed == "CRASHED":
                with self.lock:
                    self.crashed = True
                    #since you have crashed you need to recreate the pots and reset the velocities


    def transmit(self):
        sent = ",".join(map(str,self.thrusts))
        self.s.sendall(sent.encode("UTF-8"))
        returned = self.s.recv(1024).decode("utf-8")

    def pollRotation(self):
        self.s.sendall("GET ROTATION".encode("UTF-8"))
        returned = self.s.recv(1024).decode("UTF-8")
        self.rotation = list(map(float,returned.split(",")))
        return self.rotation

    def pollVelocity(self):
        self.s.sendall("GET VELOCITY".encode("UTF-8"))
        returned = self.s.recv(1024).decode("UTF-8")
        self.velocity = list(map(float,returned.split(",")))
        return self.velocity

    def reset(self):
        self.s.sendall("RESET".encode("utf-8"))
        data = self.s.recv(1024).decode("utf-8")
        self.thrusts = [0,0,0,0]

    def eval_action(self,actionId):
        action = actions[actionId]
        for i,thruster in enumerate(action):
            if thruster == 1 and self.thrusts[i] < (1 - self.delta_w): self.thrusts[i] += self.delta_w 
            if thruster == -1 and self.thrusts[i] > self.delta_w: self.thrusts[i] -= self.delta_w
        self.transmit()

if __name__ == "__main__":
    d = Drone_Control(25000,0.01)
    print("CONNECTED")
    d.transmit()
    time.sleep(1)
    d.transmit()
    time.sleep(1)
    print(d.pollRotation())
    time.sleep(1)
    print(d.pollVelocity())
    time.sleep(1)
    d.reset()
    print(d.pollRotation())
    print(d.pollVelocity())
    d.transmit()
