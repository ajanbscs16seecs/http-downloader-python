# Socket client example in python

import socket
import sys
import re
import os
import io

CHUNK_SIZE = 4096


'''
FUNCTIONS
'''


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(now,total):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    progress = now/total
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2} bytes of {3} {4}".format( ">"*block + "-"*(barLength-block), progress*100,now,total, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def receive_all(sock, chunk_size=CHUNK_SIZE ,temp=0, total =0):
    '''
    Gather all the data from a request.
    '''
    chunks = []
    
    while True:
        chunk = sock.recv(int(chunk_size))
        if chunk:
            chunks.append(chunk)
            
            temp+=len(chunk)
            update_progress(temp,total)

        else:
            break


    return b''.join(chunks)



print(sys.argv)



ARG_NO_OF_CONNECTIONS =  sys.argv[1] if sys.argv[1] else "1"
ARG_INTERVAL = sys.argv[2] if sys.argv[2] else "1"
ARG_CON_TYPE = sys.argv[3] if sys.argv[3] else  "tcp"
ARG_URL = sys.argv[4] if sys.argv[4] else "https://s.aolcdn.com/hss/storage/midas/9177f1bff2326923725e0ed737583830/201851840/putinmeme02.jpg"
ARG_SAVE_AT = sys.argv[5] if sys.argv[5] else  "output/.default"
ARG_RESUME = sys.argv[6] if sys.argv[6] else  "1"

    
ARG_URL = "http://localhost/add_item.png"
ARG_URL = "http://www.gsfdcy.com/data/img1/60/1826675-natur-wallpaper.jpg" 


host = 'localhost'
port = 80  # web

p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
p = '(https?://)([^:^/]*)(:\\d*)?(.*)?'

m = re.search(p,ARG_URL)
host = m.group(2) if m.group(2) else 'localhost'
port = int(m.group(3)) if m.group(3) else 80
uri =  m.group(4) if m.group(4) else ''
print(host)
print(port)
print(uri)

# create socket
print('# Creating socket')
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

print('# Getting remote IP address') 
try:
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    print('Hostname could not be resolved. Exiting')
    sys.exit()

# Connect to remote server
print('# Connecting to server, ' + host + ' (' + remote_ip + ')') 
s.connect((remote_ip , port))

# Send data to remote server
print('# Sending data to server')
# FILE_TO_DOWNLOAD = "test.txt"

request = "GET "+uri+" HTTP/1.0\r\nHost: "+ host+"\r\n\r\n"


print(request)
try:
    s.sendall(request.encode())
except socket.error:
    print('Send failed')
    sys.exit()

# Receive data
print('# Receive data from server')



data = s.recv(int(CHUNK_SIZE))


'''
    Parse Raw Response
'''
CRLF = b"\r\n\r\n"
splitted = data.split(CRLF, 1)
headers = splitted[0].decode()
request_line = headers.split('\n')[0]
response_code = request_line.split()[1]
headers = headers.replace(request_line, '')
# print
print(response_code+"\n")
print(request_line+"\n")
print(headers+"\n")

p = "Content-Length: (\d+)"
m = re.search(p,headers)
total = int(m.group(1))


data = data+receive_all(s,4096,len(data),total)
#separate body now
body = data.replace(headers.encode(), b'').replace(request_line.encode(), b'').replace(CRLF,b'')







# save
f = open('output/'+ARG_SAVE_AT, 'wb+')
f.write(body)
f.close()


# open
adsPath = os.path.abspath('output/'+ARG_SAVE_AT)
os.startfile(adsPath)
print("The file is downloaded as: "+adsPath)
