import os
import sys

class daemonized(object):
    def __init__(self):
        pass
   
    def daemonize(self):
        pass
    
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.stderr.write("Fork 1 has failed --> %d--[%s]\n" \
                             % (e.errno,e.strerror))
            sys.exit(1)
 
        #os.chdir('/')
        #detach from terminal
        os.setsid()
        #file to be created?
        os.umask(0)
 
        try:
            pid = os.fork()
            if pid > 0:
                print "Daemon process pid %d" % pid
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("Fork 2 has failed --> %d--[%s]" \
                             % (e.errno, e.strerror))
            sys.exit(1)
 
        sys.stdout.flush()
        sys.stderr.flush()
        if sys.platform != 'darwin': # This block breaks on OS X
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            si = file( os.devnull, 'r')
            so = file( os.devnull, 'a+')
            se = file( os.devnull, 'a+', 0)
            
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

    def start_daemon(self):
        self.daemonize()
      
        self.run_daemon()
        
    def start(self):
        self.run_daemon()    

    def run_daemon(self):
        '''override'''
        pass
    
