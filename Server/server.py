import socket
import sys
import time
import os
import struct
import math
import random
import platform
import shutil

BUFFER_SIZE = 4096  # BUFFER SIZE
TCP_IP = "127.0.1.1"
TCP_PORT = 21  # PORT
dataPort = 20
Line_terminator = '\r\n'
loggedIn = False

class FTP_SERVER :
    def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE, conn, clientControlAddress) :
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.conn = conn
        self.serverSocket = None
        self.serverDataSocket = None
        self.clientControlAddress = clientControlAddress
        self.currentUser = None
        self.dataType = None

    def makeDatabase(self) :
        d = {}  # use dictionary to store username and passwords for fast access
        myFile = open ( 'user.txt', 'r' )
        for line in myFile :
            inf = line.split ( ',' )
            user = inf[0]
            passwd = inf[1]
            passwd = passwd[0 :len ( passwd ) - 1]
            d[user] = passwd
        myFile.close ( )
        return d

    def validUser(self, userNameINput, database) :
        passWd = database.get ( userNameINput ) # the user name is valid

        # if user doesnt exist
        if passWd == None :
            return False

        return True

    def ValidUserPasswd(self, UserNameInput, passwordInput, database) :
        passWd = database.get ( UserNameInput )

        # if password corresponding to user is incorrect
        if passWd != passwordInput :
            return False

        return True

    def loggIn(self) :
        global loggedIn

        database = self.makeDatabase ( )

        userNameINput = self.conn.recv ( BUFFER_SIZE )

        if self.validUser ( userNameINput, database ) :
            serverResponse = '331 ' + 'User name okay, need password' + Line_terminator
            self.conn.send ( serverResponse.encode ( ) )
            passwordInput = self.conn.recv ( BUFFER_SIZE )

            if self.ValidUserPasswd ( userNameINput, passwordInput, database ) :
                serverResponse = '230 ' + 'User ' + userNameINput + ' logged in' + Line_terminator
                self.conn.send ( serverResponse.encode ( ) )
                loggedIn = True # change logged in status
                path = os.getcwd ( ) + '/' + userNameINput
                os.chdir ( path )
                self.currentUser = userNameINput
            else :
                serverResponse = '530 ' + 'could not log in' + Line_terminator
                self.conn.send ( serverResponse.encode ( ) )

        else :
            serverResponse = '530 ' + 'could not log in' + Line_terminator
            self.conn.send ( serverResponse.encode ( ) )

    def STOR(self):

        # Recieve file name length, then file name
        file_name_size = struct.unpack("h", self.conn.recv(2))[0]
        file_name = self.conn.recv(file_name_size)

        # get file size corresponding to
        file_size = struct.unpack("i", self.conn.recv(4))[0]
        # Initialise and enter loop to recive file content
        start_time = time.time()
        output_file = open(file_name.decode(), "wb")

        bytes_recieved = 0

        while bytes_recieved < file_size:
            l = self.conn.recv(self.BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += self.BUFFER_SIZE
        output_file.close()

        # Send upload performance details
        self.conn.send(struct.pack("f", time.time() - start_time))
        self.conn.send(str(file_size)+Line_terminator)
        self.conn.send("150 file received")
        return

    def LIST(self) :

        # Get list of files in directory
        listing = os.listdir ( os.getcwd ( ) )
        # Send over the number of files, so the client knows what to expect (and avoid some errors)
        self.conn.send ( struct.pack ( "i", len ( listing ) ) )
        total_directory_size = 0
        # Send over the file names and sizes whilst totaling the directory size

        for i in listing :

            self.conn.send ( i.encode() )

        # Final check
        self.conn.send ( "125 list of files in current directory")
        return

    def MKD(self) :

        newDir = self.conn.recv ( BUFFER_SIZE )

        newDir = os.getcwd ( ) + '/' + newDir.encode ( )
        if os.path.isdir ( newDir ) :
            self.conn.send ( "521 directory already exists" + Line_terminator )
        else :
            os.makedirs ( newDir )
            self.conn.send ( "257 new directory created" + Line_terminator )

    def pwd(self) :
        workingDir = os.getcwd ( )
        respose = workingDir[workingDir.find ( self.currentUser ) :]
        self.conn.send ( "257 " + respose + " is the working the directory" )

    def cwd(self) :

        cdDir = self.conn.recv ( BUFFER_SIZE )

        cdDir = os.getcwd ( ) + '/' + cdDir.encode ( )
        if os.path.isdir ( cdDir ) :
            os.chdir ( cdDir )
            self.conn.send ( "200 directory changed to" + cdDir)
        else :
            self.conn.send ( "521 directory does not exist" )


    def SYST(self) :
        systMessage = '215 ' + platform.platform ( aliased=1 ) + Line_terminator
        self.conn.send ( systMessage.encode ( ) )

    def PASV(self) :

        serverIP = TCP_IP.replace ( '.', ',' )
        random.seed ( a=None )
        randomServerPort = random.randint ( 1024, 2000 )
        p1, p2 = divmod ( randomServerPort, 256 )
        serverIP = serverIP + str ( math.floor ( p1 ) ) + ',' + str (
            p2 )  # Storing server port number: serverDataSocketAddress= h1,h2,h3,h4,p1,p2

        # Creating server data port for client to connect to
        self.serverDataSocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.serverDataSocket.setsockopt ( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.serverDataSocket.bind ( (TCP_IP, randomServerPort) )
        self.serverDataSocket.listen ( 1 )

        # Sending client information of server data port and IP address
        passiveModeMessage = '227 ' + 'Entering Passive Mode (' + serverIP + ')' + Line_terminator
        self.conn.send (passiveModeMessage)
        # self.connectionControlSocket.send(passiveModeMessage.encode())

        self.clientDataSocket, self.clientDataAddress = self.serverDataSocket.accept ( )


    def PORT(self) :
        self.clientDataIP = clientControlAddress.replace ( '.', ',' )
        self.clientDataPort = self.conn[4] * 256 + self.conn[5]  # Converting 16-bit TCP port address, to a port number

        self.serverDataSocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.serverDataSocket = socket.setsockopt ( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )  # Setting up socket to be reused, after it is closed.
        self.serverDataSocket.bind ( (TCP_IP, dataPort) )
        self.serverDataSocket.connect ( self.clientDataIP, self.clientDataPort )  # Connecting to client's data port

        activeDataConnectionMessage = '225 ' + 'Data connection open; no transfer in progress.' + Line_terminator

        self.conn.send ( activeDataConnectionMessage )

    def RETR(self) :
        self.conn.send ( "1" )
        file_name_length = struct.unpack ( "h", self.conn.recv ( 2 ) )[0]

        file_name = self.conn.recv ( file_name_length )
        file_name = file_name.decode()

        if os.path.isfile ( file_name ) :
            # Then the file exists, and send file size

            self.conn.send ( struct.pack ( "i", os.path.getsize ( file_name ) ) )
        else :
            # Then the file doesn't exist, and send error code

            self.conn.send ( struct.pack ( "i", -1 ) )
            return

        start_time = time.time ( )

        file_ = open ( file_name, "rb" )
        # Again, break into chunks defined by BUFFER_SIZE
        data = file_.read ( BUFFER_SIZE )
        while data :
            self.conn.sendall ( data )
            data = file_.read ( BUFFER_SIZE )
        file_.close ( )
        # Get client go-ahead, then send download details
        self.conn.recv ( BUFFER_SIZE )
        self.conn.send ( struct.pack ( "f", time.time ( ) - start_time ) )
        return

    def delf(self) :
        # Send go-ahead
        self.conn.send ( "1" )
        # Get file details
        file_name_length = struct.unpack ( "h", self.conn.recv ( 2 ) )[0]
        file_name = self.conn.recv ( file_name_length ).decode ( )

        if os.path.isfile ( file_name ) :
            self.conn.send ( struct.pack ( "i", 1 ) )
        else :
            self.conn.send ( struct.pack ( "i", -1 ) )

        try :
            # Delete file

            os.remove ( file_name )
            self.conn.send ( struct.pack ( "i", 1 ) )
        except :
            # Unable to delete file

            self.conn.send ( struct.pack ( "i", -1 ) )
            return

    def RMD(self) :
        # Send go-ahead
        self.conn.send ( "1" )
        # Get file details
        file_name_length = struct.unpack ( "h", self.conn.recv ( 2 ) )[0]
        file_name = self.conn.recv ( file_name_length )
        # Check file exists

        if os.path.isdir ( file_name ) :
            self.conn.send ( struct.pack ( "i", 1 ) )
        else :
            self.conn.send ( struct.pack ( "i", -1 ) )

        try :
            # Delete folder
            shutil.rmtree ( file_name )
            self.conn.send ( struct.pack ( "i", 1 ) )
        except :
            # Unable to delete file

            self.conn.send ( struct.pack ( "i", -1 ) )


    def quit(self) :
        # Send quit conformation
        global loggedIn
        self.conn.send ( "1" )
        # Close and restart the server
        loggedIn = False

    def start(self) :
        global loggedIn

        while loggedIn == False:
            self.loggIn ()
            while True and loggedIn == True:
                # Enter into a while loop to recieve commands from client

                data = self.conn.recv ( BUFFER_SIZE )

                # Check the command and respond correctly
                if data == "STOR" :
                    self.STOR ()
                elif data == "LIST" :
                    self.LIST ( )
                elif data == "CWD" :
                    self.cwd ( )
                elif data == "RETR" :
                    self.RETR ( )
                elif data == "DELE" :
                    self.delf ( )
                elif data == "QUIT" :
                    self.quit ( )
                elif data == "MKD" :
                    self.MKD ( )
                elif data == "TYPE" :
                    self.TYPE ( )
                elif data == "SYST" :
                    self.SYST ( )
                elif data == "PWD" :
                    self.pwd ( )
                elif data == "PASV" :
                    self.PASV ( )
                elif data == "PORT" :
                    self.PORT ( )
                elif data == "RMD" :
                    self.RMD( )
                # Reset the data to loop
                data = None


# main program
commandSocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
commandSocket.bind ( (TCP_IP, TCP_PORT) )
commandSocket.listen ( 1 )
CONN, clientControlAddress = commandSocket.accept ( )
print ( "\nConnected to by address: {}".format ( clientControlAddress ) )
res = "\n220 server " + str ( TCP_IP ) + " is ready"
CONN.send ( res.encode ( ) )
client = FTP_SERVER ( TCP_IP, TCP_PORT, BUFFER_SIZE, CONN, clientControlAddress )


client.start ( )
