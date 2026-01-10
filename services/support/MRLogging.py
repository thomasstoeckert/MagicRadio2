import logging
import time
import sys

# Logging of uncaught crashes to the log file.
def uncaught_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# This guy sets up logging for the whole program, just moved here from MagicRadio.py for cleanliness
def init_logging():
    logTimeString = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    logFileString = "logs/" + logTimeString + ".log"

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s]%(filename)s: %(message)s",
                        filename=logFileString)
    
    # Duplicate the logging stream between console and file
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    logging.getLogger('').addHandler(consoleHandler)
    # Setup crash handler
    sys.excepthook = uncaught_handler

    logging.info("Logging has begun")