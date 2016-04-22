import os
import sys

if __name__ == "__main__":
    curpath = os.path.split(os.path.realpath(sys.argv[0]))[0]
    os.chdir(curpath)

    from redis_live import redis_live
    live = redis_live()
    live.start_daemon()
