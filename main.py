import sys
import socket
import time

reload(sys)
sys.setdefaultencoding("utf-8")

HOST='irc.freenode.net' #The server we want to connect to
PORT=6667 #The connection port which is usually 6667
NICK='MariaBot' #The bot's nickname
IDENT='Maria'
REALNAME='what u talkin about'
channel_list='#elweb' #The default channel for the bot

MODULES_LOAD='urldb'

modules = {}

irc_socket = None

def connectAndProcess():
    global irc_socket
    
    irc_buffer = ""
    irc_socket=socket.socket( ) #Create the socket
    irc_socket.connect((HOST, PORT)) #Connect to server
    irc_socket.send('NICK '+NICK+'\r\n') #Send the nick to server
    irc_socket.send('USER '+IDENT+' '+HOST+' bla :'+REALNAME+'\r\n') #Identify to server

    while 1:
        irc_buffer=irc_buffer+irc_socket.recv(1024) #recieve server messages
        
        irc_lines = irc_buffer.split('\n')
        irc_buffer = irc_lines.pop()
        
        for line in irc_lines:
            processLine(line)

def processLine(line):
    print line #server message is output
    
    if line.find('End of /MOTD command.')!=-1: 
        for channel in channel_list.split():
            joinChannel(channel)
        initModules()
        
    # if line.find('NickServ!NickServ@services. NOTICE')!=-1:
    #     print 'Identifying...'
        # irc_socket.send('PRIVMSG NickServ :identify 12345\r\n')
    
    if line.find(' PRIVMSG ')!=-1: #Call a parsing function
        line_info = getLineInformation(line)
    
        parseMessage(line, line_info)
        
        for module in modules:
            print 'Sending to module: %s' % module
            modules[module].parseMessage(line, line_info)
            try:
                # modules[module].parseMessage(line, line_info)
                pass
            except Exception, e:
                print 'Error in module: %s' % module
                print e
                raise e
                
    line=line.rstrip() #remove trailing 'rn'
    line=line.split()
    if(line[0]=='PING'): #If server pings then pong
        print 'PONG'
        irc_socket.send('PONG '+line[1]+'\r\n')

def joinChannel(channel):
    irc_socket.send('JOIN '+channel+'\r\n') #Join a channel
    
def parseMessage(line, line_info):
    print 'Got a line i should parse...'
    
    line_txt = line_info[2]
    
    # print 'Line Info: %s' % str(line_info)
    # print line_txt
    
    if line_txt[0] == '@': #This is a command do something about it
        print 'Got a command!'
        command = line_txt.split(' ', 1)
        
        command[0] = command[0][1:]
        
        if len(command) == 1:
            return
        
        if command[0] == 'reload':
            if len(command) > 1:
                if command[1] == 'all':
                    for module in modules:
                        sendMessageToChannel(line_info[1], line_info[0], 'Relaoding module: %s' % module)
                        reload(modules[module])
                else:
                    if modules.has_key(command[1]):
                        sendMessageToChannel(line_info[1], line_info[0], 'Relaoding module: %s' % command[1])
                        reload(modules[command[1]])
                    else:
                        sendMessageToChannel(line_info[1], line_info[0], 'No module named %s' % command[1])

                initModules()
        elif command[0] == 'load':
            if len(command) > 1:
                try:
                    loadModule(command[1])
                    initModules()
                    sendMessageToChannel(line_info[1], line_info[0], 'Succesfully loaded module %s' % command[1])
                except Exception, e:
                    sendMessageToChannel(line_info[1], line_info[0], 'Could not load module named %s' % command[1])
                            
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
            # sendMessageToChannel(line_info[1], line_info[0], 'Unknown command %s' % command[0])

def getLineInformation(line):
    line_items = line.split(' ', 3) # USERNAME COMMAND CHANNEL :TEXT
    
    username_mask = line_items[0].split('!', 1)
    command = line_items[1]
    channel = line_items[2]
    line_text = line_items[3][1:].rstrip()
    username = username_mask[0][1:]
    mask = username_mask[1]
    
    return ( username, channel, line_text, command, mask )

def sendMessageToChannel(channel, user, message):
    print 'In main.py'
    if channel == NICK:
        # print 'PRIVMSG %s :%s\r\n' % (user, message)
        irc_socket.send('PRIVMSG %s :%s\r\n' % (user, message))
    else:
        # print 'PRIVMSG %s :%s\r\n' % (channel, message)
        irc_socket.send('PRIVMSG %s :%s\r\n' % (channel, message))
    
    time.sleep(.75)

def loadModule(module_name):
    global modules
    
    print 'Loading: %s' % module_name
    modules[module_name] = __import__('modules.%s' % module_name, None, None, ['*'])

def initModules():
    for module in modules:
        print 'Initializing module: %s' % module
        modules[module].sendMessageToChannel = sendMessageToChannel

def loadDefaultModules():
    global modules
    
    for module in MODULES_LOAD.split():
        loadModule(module)
        
loadDefaultModules()
connectAndProcess()