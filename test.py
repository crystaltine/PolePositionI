from multiprocessing import Process
from time import sleep


def looper(printstr):
    while 1:
        sleep(1)
        print(printstr)

if __name__ == '__main__':
    for i in range(2):
        Process(target=looper, args=(f"thing {i}",)).start()


