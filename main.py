import sys
import socket
import config
import select

reload(sys)
sys.setdefaultencoding("utf-8")


modules = {}

irc_socket = None
send_queue = []

def connectAndProcess():
    global irc_socket
    
    irc_buffer = ""
    
    
    irc_socket=socket.socket( ) #Create the socket
    irc_socket.connect((config.HOST, config.PORT)) #Connect to server
    
    irc_socket_fd = irc_socket.fileno()
    
    sendMessageRaw('NICK '+config.NICK+'\r\n') #Send the nick to server
    sendMessageRaw('USER '+config.IDENT+' '+config.HOST+' bla :'+config.REALNAME+'\r\n') #Identify to server
    
    processSendQueue()
    
    while 1:
        if len(select.select([irc_socket_fd],[],[], 1)[0]) > 0:
            irc_buffer=irc_buffer+irc_socket.recv(1024) #recieve server messages
        
            irc_lines = irc_buffer.split('\n')
            irc_buffer = irc_lines.pop()
        
            for line in irc_lines:
                processLine(line)
        else:
            processSendQueue()
            
def processSendQueue():
    if len(send_queue) > 0:
        line = send_queue.pop(0)
        irc_socket.send(line)

def processLine(line):
    print line #server message is output
    
    line=line.rstrip() #remove trailing 'rn'

    line_parts = line.split(' ', 3)
    
    if len(line_parts) >= 2:
        
        if(line_parts[0] == 'PING'): #If server pings then pong
            print 'PONG'
            sendMessageRaw('PONG '+line[1]+'\r\n')
            return
        
        srv_command = line_parts[1]

        # end of MOTD, we can continue with connection
        if srv_command == '376': 
            for channel in config.channel_list.split():
                joinChannel(channel)
            for module in modules:
                initModule(module)
        
        # if line.find('NickServ!NickServ@services. NOTICE')!=-1:
        #     print 'Identifying...'
        # sendMessage(config.NICK, 'NickServ', 'identify 12345')
    
        if srv_command == 'PRIVMSG': #Call a parsing function
            line_info = getLineInformation(line)
    
            parseMessage(line, line_info)



def joinChannel(channel):
    sendMessageRaw('JOIN '+channel+'\r\n') #Join a channel
    
def parseMessage(line, line_info):
    print '- Got a PRIVMSG'

    if line_info[2][0] == '@': #This is a command do something about it
        processCommand(line, line_info)
    else: # Not a command so send to modules
        for module in modules:
            print 'Sending to module: %s' % module
            try:
                modules[module].parseMessage(line, line_info)
                pass
            except Exception, e:
                print 'Error in module: %s' % module
                print e
                raise e
        
def processCommand(line, line_info):
    print 'Got a command!'

    command = line_info[2].split(' ', 1)
    
    command[0] = command[0][1:]
    
    if len(command) == 1:
        return
    
    if command[0] == 'reload':
        if len(command) > 1:
            module_name = command[1]
            
            if module_name == 'all':
                for module in modules:
                    sendMessage(line_info[1], line_info[0], 'Reloading module: %s' % module)
                    reload(modules[module])
            else:
                if modules.has_key(module_name):
                    sendMessage(line_info[1], line_info[0], 'Reloading module: %s' % module_name)
                    reload(modules[module_name])
                    initModule(module_name)
                else:
                    sendMessage(line_info[1], line_info[0], 'No module named %s' % module_name)
                
                
            
    elif command[0] == 'load':
        if len(command) > 1:
            module_name = command[1]

            try:
                loadModule(module_name)
                initModule(module_name)
                sendMessage(line_info[1], line_info[0], 'Succesfully loaded module %s' % module_name)
            except Exception, e:
                sendMessage(line_info[1], line_info[0], 'Could not load module named %s' % module_name)
                        
    elif modules.has_key(command[0]):
        try:
            if len(command) > 1:
                modules[command[0]].processCommand(command[1], line, line_info)
            else:
                modules[command[0]].processCommand('', line, line_info)
        except Exception, e:
            print 'Error sending processCommand to %s' % command[0]
            print e
    else:
        pass

def getLineInformation(line):
    line_items = line.split(' ', 3) # USERNAME COMMAND CHANNEL :TEXT
    
    username_mask = line_items[0].split('!', 1)
    command = line_items[1]
    channel = line_items[2]
    line_text = line_items[3][1:].rstrip()
    username = username_mask[0][1:]
    mask = username_mask[1]
    
    return ( username, channel, line_text, command, mask )

def sendMessageRaw(message, no_delay = False):
    if no_delay == True:
        irc_socket.send(message)
    else:
        send_queue.append(message)

def sendNotice(user, message, no_delay = False):
    if no_delay == True:
        irc_socket.send('NOTICE %s :%s\r\n' % (user, message) )
    else:
        send_queue.append('NOTICE %s :%s\r\n' % (user, message) )
    
def sendMessage(channel, user, message):
    if channel == config.NICK:
        send_queue.append('PRIVMSG %s :%s\r\n' % (user, message))
    else:
        send_queue.append('PRIVMSG %s :%s\r\n' % (channel, message))

def loadModule(module_name):
    global modules
    
    print 'Loading: %s' % module_name
    modules[module_name] = __import__('modules.%s' % module_name, None, None, ['*'])

def initModule(module):
    if modules.has_key(module):
        print 'Initializing module: %s' % module
        modules[module].sendMessage = sendMessage
        modules[module].sendMessageRaw = sendMessageRaw
        modules[module].sendNotice = sendNotice

def loadDefaultModules():
    global modules
    
    for module in config.MODULES_LOAD.split():
        loadModule(module)
        
loadDefaultModules()
connectAndProcess()