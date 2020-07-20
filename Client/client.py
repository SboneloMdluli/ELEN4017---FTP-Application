import socket
import sys
import os
import struct

SERVER_TCP_IP = "127.0.1.1" # local server
SERVER_TCP_PORT = 21 #
dataPort = 20
BUFFER_SIZE = 4096 #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
loogedIn = False
Line_terminator = '\r\n'
message = "530 Not logged In"
response =""

def getReponse():
    return response

def login(userName):
    global response
    try:
        if userName == '':
            userName = 'anonymous'  # setting up the anonymous user

        s.sendall(userName.encode())
        serverResponse = s.recv(BUFFER_SIZE)
        response = serverResponse.decode()
        return True
    except:
        response = message
        return False


def userPass(password):
    global response
    try:
        if password == '':
            password = 'anonymous@'

        s.sendall(password.encode())
        serverResponse = s.recv(BUFFER_SIZE)
        response = serverResponse.decode()
        loogedIn = True
    except:
        response = "Could not send command"

def conn():
    # Connect to the server
    global response
    try:
        s.connect((SERVER_TCP_IP, SERVER_TCP_PORT))
        response = s.recv(BUFFER_SIZE).decode()
    except:
        response = "425 cant open data connection"

def mkdir(dir_name):
    global response
    try:
       msg = "MKD"
       s.send(msg.encode())
    except:
       response = message
       return

    try:
       s.send(dir_name.encode())
    except:
       response = "directory could not be created"
       return


def pwd ():
    global response
    try:
        msg = "PWD"
        s.send(msg.encode())
    except:
        response =message
        return

    try:
        workingDir = s.recv(BUFFER_SIZE).decode()
        response = workingDir
    except:
        response ="ERROR printing directory"
        return

def syst ():
    global response
    try:
        msg = "SYST"
        s.send(msg.encode())
    except:
        response = message
        return

    try:
        systMessage = s.recv(BUFFER_SIZE)
        response = systMessage.decode()
    except:
        response = "ERROR printing directory"
        return


def cwdir(dir_name):
    global response
    try:
       msg = "CWD"
       s.send(msg.encode())
    except:
       response ="425 cant open data connection"
       return

    try:
       s.send(dir_name.encode())
       response = s.recv ( BUFFER_SIZE ).decode()
    except:
       response = s.recv ( BUFFER_SIZE )
       return

def STOR(file_name):
    # Upload a file
    global response
   # file_name = file_name.encode()
    try:
        # Check the file exists
        content = open(file_name, "rb")
    except:
        response = "431 cant find file"
        return
    try:
        # Make upload request
        msg = "STOR"
        s.send(msg.encode())
    except:
        response = "521 cant send command."
        return
    try:
        # Wait for server acknowledgement then send file details
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
        s.send(struct.pack("i", os.path.getsize(file_name)))
    except:
        response = "431 Error sending file details"
    try:
        # Send the file in chunks defined by BUFFER_SIZE
        # Doing it this way allows for unlimited potential file sizes to be sent
        l = content.read(BUFFER_SIZE)
        response = "\nSending..."
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        # Get upload performance details
        upload_time = struct.unpack("f", s.recv(4))[0]
        upload_size = struct.unpack("i", s.recv(4))[0]
        response = "\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_name, upload_time, upload_size)
        response = s.recv(BUFFER_SIZE)
    except:
        response = "Error sending file"
        return
    return



def LIST():

    global response
    try:
        # Send list request
        msg = "LIST"
        s.send(msg.encode())
    except:
        response = "425 cant open data connection"
        return

    try:
        # First get the number of files in the directory
        number_of_files = struct.unpack("i", s.recv(4))[0]
        # Then enter into a loop to recieve details of each, one by one
        for i in range(int(number_of_files)):

            # Get the file name size first to slightly lessen amount transferred over socket

            file_name = s.recv(BUFFER_SIZE).decode()
            # Also get the file size for each item in the server

            response = "\n{}".format(file_name)
            # Make sure that the client and server are syncronised

        # Get total size of directory

    except:
        response = "Couldn't retrieve listing"
        return

    s.recv ( BUFFER_SIZE )

def RETR(file_name):
    # Download given file
    file_name = file_name.encode()
    global response
    try:
        # Send server request
        msg = "RETR"
        s.send(msg.encode())
    except:
        response = "425 cant open data connection"
        return

    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        t = s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        # Get file size (if exists)
        response = "150 file sent"
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size is None:
            # If file size is -1, the file does not exist
            response = "File does not exist. Make sure the name was entered correctly"
            return
    except:
        response = "Error checking file"

    try:
        # Enter loop to recieve file
        output_file = open(file_name, "wb")
        bytes_recieved = 0

        while bytes_recieved < file_size:
            # Again, file broken into chunks defined by the BUFFER_SIZE variable
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        response = "Successfully downloaded {}".format(file_name)
        # Tell the server that the client is ready to recieve the download performance details
        s.send("1")
        # Get performance details
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        response = "Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size)
    except:
        response = "150 file sent"
        return

    return



def delr(file_name,msg):
    # Delete specified file from file server

    global response
    try:
        # Send resquest, then wait for go-ahead
        s.send(msg.encode())
        s.recv(BUFFER_SIZE)
    except:
        response = "425 cant open data connection"
        return

    try:
        # Send file name length, then file name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
    except:
        response = "\n 450 Couldn't send file details"
        return

    try:
        # Get conformation that file does/doesn't exist
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            response = "The file does not exist on server"
            return
    except:
        response = "Couldn't determine file existance"
        return

def quit():
    msg = "QUIT"
    s.send(msg.encode())
    # Wait for server go-ahead
    s.recv(BUFFER_SIZE)
    s.close()
    global response
    response = "\nServer connection ended"
    return


def port():
    msg = "PORT"
    s.send(msg.encode())
    return

def pasv():
    global response
    msg = "PASV"
    s.send(msg.encode())
    response = s.recv(BUFFER_SIZE)
    return

def help():
    global response
    response = "\n\nFTP server commands:" \
               "\nFTP            : Connect to server" \
               "\nUSER           : User name" \
               "\nPASS           : password" \
               "\nMKD            : Make directory" \
               "\nCWD            : Change working directory" \
               "\nPWD            : Print working directory" \
               "\nSTOR      file : Upload file" \
               "\nLIST           : List files" \
               "\nRETR file        : Download file" \
               "\nDELE file      : Delete file" \
               "\nSYST           : Server operating system" \
               "\nRMD file_path  : Delete directory" \
               "\nQUIT           : logout"


def processedCommand(prompt):
    # Listen for a command
    global response

    if prompt[:4].upper() == "FTP":
        conn()
    elif prompt[:4].upper() == "USER":
        login(prompt[5:])
        # prompt = raw_input("\nEnter a command: ")
    elif prompt[:4].upper() == "PASS":
        userPass(prompt[5:])
    elif prompt[:4].upper() == "STOR":
        STOR(prompt[5:])
    elif prompt[:4].upper() == "LIST":
        LIST()
    elif prompt[:4].upper() == "RETR":
        RETR(prompt[5:])
    elif prompt[:3].upper() == "CWD":
        cwdir(prompt[4:])
    elif prompt[:4].upper() == "DELE":
        delr(prompt[5:],"DELE")
    elif prompt[:3].upper() == "MKD":
        mkdir(prompt[4:])
    elif prompt[:4].upper() == "QUIT":
        quit()
    elif prompt[:3].upper() == "PWD":
        pwd()
    elif prompt[:4].upper() == "SYST":
        syst()
    elif prompt[:3].upper() == "RMD":
        delr(prompt[4:],"RMD")
    elif prompt[:4].upper() == "PORT":
        port()
    elif prompt[:4].upper() == "PASV":
        pasv()
    elif prompt[:4].upper() == "HELP":
        help()
    else:
        response = "202 Command not implemented"
