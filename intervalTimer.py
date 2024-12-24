import threading
import time

class intervalTimer:
    def __init__(self,
                 interval,
                 callback):
        self._interval    = interval
        self._callback    = callback
        self._timerActive = True
        
        self._t = threading.Thread(target=self._expiredFunc)
        
    def join(self):
        self._t.join()        
        
    def _expiredFunc(self):
        while(self._timerActive):
            time.sleep(self._interval)
            self._callback()
        
    def START(self):
        self._t.start()
        
    def stop(self):
        self._timerActive = False