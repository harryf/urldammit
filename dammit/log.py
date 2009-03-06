import sys, logging
from wsgilog import WsgiLog, LogIO
import config

class Log(WsgiLog):
    def __init__(self, application):
        WsgiLog.__init__(
            self,
            application,
            tofile = True,
            file = config.log_file,
            interval = config.log_interval,
            backups = config.log_backups
            )
        sys.stdout = LogIO(self.logger, logging.INFO)
        sys.stderr = LogIO(self.logger, logging.ERROR)
