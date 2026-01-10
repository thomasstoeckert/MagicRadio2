import MRGlobals
import logging
import time
import os

def deleteAgedLogs():

    try:
        logs = [file for file in os.listdir("logs")]
    except (OSError):
        logging.info("Tried to delete logs, but couldn't find the logs folder")
        return
    
    now = time.time()
    # One day in seconds
    max_time = MRGlobals.logDeathInDays * 86400

    for log in logs:
        stripped_log = log[:-4]
        log_date = time.strptime(stripped_log, "%Y-%m-%d-%H:%M:%S")
        elapsed = abs(time.mktime(log_date) - now)
        if elapsed > max_time:
            logging.debug("Removing outdated log %s" % log)
            os.remove("logs/" + log)
        else:
            logging.debug("Log %s is still in good standing" % log)