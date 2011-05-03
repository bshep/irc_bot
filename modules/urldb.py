import sqlite3
import re
import time
import datetime

urlRegEx = re.compile(r"https?://([^ ]+)")

socket = None
nickname = None

def parseMessage(line):
    
    line = line.rstrip()
    for url in urlRegEx.finditer(line):
        line_items = line.split(' ', 3)
        
        username = line_items[0].split('!')[0][1:]
        now = time.time()
        channel = line_items[2]
        
        checkURL(url.group(0), channel, username, now)

def checkURL(url, spoken_where, spoken_by, on_date):
    row = runQuery('SELECT url, spoken_where, spoken_by, on_date, count FROM urls WHERE spoken_where = ? AND url = ?', [spoken_where, url] )
    
    print row
    
    if row:
        timestamp = datetime.datetime.isoformat(datetime.datetime.fromtimestamp(float(row[3])))
        if row[4] == 1:
            sendMessageToChannel(spoken_where, spoken_by, '%s already shared %s on %s' % (row[2], url, timestamp))
        else:
            # pass
            sendMessageToChannel(spoken_where, spoken_by, '%s already shared %s on %s and has been repeated %i times' % (row[2], url, timestamp, row[4]+1))
        
        runQuery('UPDATE urls SET count=count+1 WHERE spoken_where = ? AND url = ?', [spoken_where, url])
    else:
        runQuery('INSERT INTO urls (url, spoken_where, spoken_by, on_date) VALUES (?, ?, ?, ?)', [url, spoken_where, spoken_by, on_date])

def sendMessageToChannel(channel, user, message):
    if channel == nickname:
        # print 'PRIVMSG %s :%s\r\n' % (user, message)
        socket.send('PRIVMSG %s :%s\r\n' % (user, message))
    else:
        # print 'PRIVMSG %s :%s\r\n' % (channel, message)
        socket.send('PRIVMSG %s :%s\r\n' % (channel, message))

def runQuery(query, args):
    conn = sqlite3.connect('dbs/urldb.db')
    cursor = conn.cursor()
    
    cursor.execute(query, args)
    
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    return row
    
def initModule():
    runQuery('CREATE TABLE IF NOT EXISTS urls (url text, spoken_where text, spoken_by text, on_date text, count int)',[])

initModule()

if __name__ == '__main__':
    parseMessage('bshep http://cnn.com')