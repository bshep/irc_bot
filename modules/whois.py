sendMessage = None # This will be set to a function by main.py
sendMessageRaw = None
sendNotice = None

def processCommand(command, line, line_info):
    print __name__+': processCommand'
    pass
    
def parseMessage(line, line_info):
    if line_info[2] == '\x01PING\x01':
        sendNotice(line_info[0], '\x01PING\x01', True)
    elif line_info[2] == '\x01VERSION\x01':
        sendNotice(line_info[0],'\x01VERSION Version what version\x01\r\n', True)
    elif line_info[2] == '\x01TIME\x01':
        sendNotice(line_info[0],'\x01TIME now\x01\r\n', True)
    else:
        pass
