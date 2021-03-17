from flask import request
from config import Config
import time, os, logging

def audit_log(message, session, request):

    timestamp = time.strftime("%d.%m.%Y %H:%M:%S")
    path = Config.log_path
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) if Config.use_reverse_proxy else request.remote_addr
    username = session['username']
    logname = path + 'audit_' + time.strftime("%Y-%m-%d")
    logline = '[ {} ] {} {} | '.format(timestamp, user_ip, username) + message

    if(Config.do_audit_log):

        if path:
            if not (os.access(path, os.W_OK)):
                try:
                    print("no folder named " + path + ", making a new one.")
                    os.makedirs(path)
                except PermissionError:
                    print("No access to " + path)

        if not (os.access(logname, os.W_OK)):
            try:
                filelog = open(logname, 'w')
                filelog.write(logline + os.linesep)
                filelog.close()
            except PermissionError:
                print('No access to ' + logname)
        else:
            filelog = open (logname, 'a')
            filelog.write(logline + os.linesep)
            filelog.close()
			

    print(logline)
