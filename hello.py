import time
import sys

if __name__ == "__main__":
    print("Hello Container :D")
    args = sys.argv
    if len(args) > 1:
        counter = int(args[1])
    else:
        counter = 10
    for i in range(counter):
        print("this is a number: ", i)
        sys.stdout.flush()
        time.sleep(1)
        # if i == 2:
        #     raise Exception("this is an exception")