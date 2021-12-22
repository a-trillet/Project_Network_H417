from hashlib import algorithms_available
import sys
import socket
#import colorama
import datetime
import threading
import random
from cryptography.fernet import Fernet
import cryptography
import base64
from Classes import *
import pyDH
import base64

#definition of variables that will be used accross the code
global current_room
current_room = "0"
global allsymkey
allsymkey = {} 

def currentTime():
    # Retrieves local time formatted as HH:MM:SS
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M:%S")
    return formattedTime

def deleteLastLine():
    #function that clears the terminal to get a better view after sending messages
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def sendto(sock):
    global current_room
    global allsymkey
    # start sending messages from the client input to the server
    while threadFlag:
        try:
            message = input()
            deleteLastLine()
            if message[0] != "/":
                print("idroom:"+current_room)
                if current_room in allsymkey:
                    #print("encryption start ")
                    message = encrypt_mess(message)
                    
                    sock.send(message)
                    #print("encryption finished")
                else: 
                    sock.send(str(message).encode("utf8"))
            else: 
                sock.send(str(message).encode("utf8"))
        except Exception as e:
            print("An error occured while trying to send a message!")
            print(e)
            break

def receive(sock):
    # start receiving messages from the server
    global allsymkey
    global current_room
    while threadFlag:
        try:
            message = sock.recv(2048).decode()
            messageSplit = message.split()[0]
            if  messageSplit in ['/Key', '/room', 'Room']:
                if messageSplit == "/Key":
                    sharedkey = key_exchange(sock)
                    symkey =   generate_encryption_key(sharedkey) 
                    save_key(message.split()[1], symkey)

                elif messageSplit == "/room":
                    current_room = message.split()[1]

                elif messageSplit == "Room":
                    idroom = message.split()[1]
                    name = message.split()[3]
                    real_message = sock.recv(2048)   
                    if idroom in allsymkey:      
                        real_message = decrypt_mess(real_message, idroom) #decrypt message if encrypted
                    print("[{}] Room {} > {} : {}".format(currentTime(), idroom, name, real_message.decode()))
            elif message:
                print("[{}] {}".format(currentTime(), message))
            else:
                # When the server closes the socket, the received messages are empty
                break
        except Exception as e:
            print("Error while trying to reach the server.")
            print(e)
            break

def save_key(id, symkey):
    allsymkey[id] = symkey   #TODO Save key
    print(allsymkey)

def load_keys():
    pass

def key_exchange(sock):
    #generation of the Diffie Hellmann secret shared key
    try: 
        d1 = pyDH.DiffieHellman()
        d1_pubkey = d1.gen_public_key()
        sock.send(str(d1_pubkey).encode("utf8"))
        d2_pubkey = sock.recv(2048).decode("utf8")
        print(d2_pubkey)
        sharedkey = d1.gen_shared_key(int(d2_pubkey))
        print(sharedkey)
    except Exception as e: 
        print('Problem happened when exchanging keys')
        print(e)
    return sharedkey

def generate_encryption_key(DH_shared_key):
    #generation of the Fernet symmetric key based on the DH key
    temp = int(DH_shared_key, base=16)
    key = temp.to_bytes(32, 'big')
    key = base64.urlsafe_b64encode(key)
    print("key : " + str(key))
    sym_key = Fernet(key)
    return sym_key

def decrypt_mess(mess, idroom):
    global allsymkey
    f = allsymkey[idroom]
    try: 
        #print("start decrypting")
        decrypted_token = f.decrypt(mess, None)
        #print("decryption finished")
    except Exception as e:
        print('Problem while decrypting the message')
        print(e)
    return decrypted_token

def encrypt_mess(mess):
    global allsymkey
    global current_room
    f = allsymkey[current_room]
    encrypted_token = f.encrypt(mess.encode())
    return encrypted_token

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