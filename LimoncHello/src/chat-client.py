import sys
import socket
import datetime
import threading
from Classes import *

def currentTime():
    # Retrieves local time formatted as HH:MM:SS
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M:%S")
    return formattedTime

def deleteLastLine():
    # Writes ANSI codes to perform cursor movement and current line clear
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def sendto(sock):
    # start sending messages from the client input to the server
    while threadFlag:
        try:
            message = input()
            deleteLastLine()
            sock.send(message.encode("utf8"))
        except:
            print("An error occured while trying to send a message!")
            break

def receive(sock):
    # start receiving messages from the server
    while threadFlag:
        try:
            message = sock.recv(2048).decode()
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                # When the server closes the socket, messages received are empty
                break
        except Exception as e:
            print("An error occured while trying to reach the server!")
            print(e)
            break

def main():
    # a flag to exit the thread loops at the end of the code. 
    global threadFlag
    # host and port of the server
    host = "localhost"
    port = 25000
    # Creates the socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connects to the server
    clientSocket.connect((host, port))
    # Threads for receiving and sending messages 
    sendingThread = threading.Thread(target=sendto, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    # Start the threads
    receivingThread.start()
    sendingThread.start()
    # ensure that the threads are still alive
    while receivingThread.is_alive() and sendingThread.is_alive():
        continue
    threadFlag = False
    # Closes the connection to the socket in the end
    clientSocket.close()
    print("\nYou can now close the application.")

threadFlag = True

if __name__ == "__main__":
    main()
    pass