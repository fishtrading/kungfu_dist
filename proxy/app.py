import os
import sys
import websocketManager
from ProcessClient import watchStart


def child_process():
    print('child process is running')
    watchStart()
    sys.exit(0)

def parent_process():
    print('parent process is running')
    websocketManager.ProcessStart()
    exit_stat = os.wait()
    print("waited child process's PID = %d" % (exit_stat[0]))
    sys.exit(0)
    
def main():
    '''main function'''
    try:
        pid = os.fork()
        if pid > 0:
            '''parent process'''
            parent_process()
        else:
            child_process()
    except OSError:
        print(os.strerror(OSError.errno))

if __name__ == '__main__':
    main()