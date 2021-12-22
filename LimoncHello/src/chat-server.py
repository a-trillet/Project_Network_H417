import socket
import threading
from Classes.User import User
from Classes.Conversation import Conversation
from Classes.Message import Message

# list of existing user that have an account already created
list_users = []

# list of existing conversations that have been created
list_conv = []

global searching_key
searching_key = False
global key_ex
key_ex = ""
def connectionThread(sock):

    # Initialisation of the General conversation with everyone
    list_users.append(User("admin", "admin"))    
    
    list_conv.append(Conversation(0))
    list_conv[0].add_users(list_users)

    # Accepts a connection request and stores both a socket object and its IP address
    while True:
        try:
            client, address = sock.accept()
        except:
            print("Error while accepting incoming connections.")
            break
        print("{} is now connected.".format(address[0]))
        
        threading.Thread(target=clientThread, args=(client,address,)).start()

def clientThread(client, adrs):
    global searching_key
    global key_ex
    # Handles the client
    address = adrs[0]
    
    #Connexion steps
    try:
        user = login(client)
        user.connect(client)
    except:
        print("Error while setting the username for {}.".format(address))
       
        client.close()
        return    
    print("{} is now logged in as {}".format(address ,user.name))

    try:
        client.send("Dear individual {}, You are now connected to LimoncHello. You can type \"/help\" for a list of the available commands.".format(user.name).encode("utf8"))
    except:
        print("Communication error with {} ({}).".format(address, user.name))
        client.close()
        return
    broadcast("{} has joined the main room.".format(user.name))

    # Handles specific messages in a different way (user commands)
    current_conv=list_conv[0]
    user.socket.send("/room 0".encode("utf8"))  #tells the client app in which room it is right now

    while True:
        try:
            message = client.recv(2048).decode("utf8")
            if searching_key:
                key_ex = message
                message = client.recv(2048).decode("utf8")
            if message == "/help":
                client.send("\nAvailable commands are :\
                    \n/quit to quit the chat app, \
                    \n/online to see people online, \
                    \n/roommates to see people present in your current room, \
                    \n/room to see in which room you currently are,\
                    \n/mp to send a private message to someone, \
                    \n/conv to create a new conversation, \
                    \n/join to join an existing room, \
                    \n/display to display the rooms you're already in, \
                    \n/load to load the history of the current conversation you're in &\
                    \n/lobby to go to the lobby room".encode("utf8"))
            elif message == "/quit":
                client.send("You left the chat!".encode("utf8"))
                user.unconnect()
                client.close()
                print("{} ({}) has left.".format(address, user.name))
                break
            elif message == "/online":
                onlineUsers = ', '.join([user.name for user in list_users if user.socket!= "NE"])
                client.send("Users online are: {}".format(onlineUsers).encode("utf8"))
            elif message == "/roommates":
                pass
                roommates = ', '.join([user.name for user in current_conv.users])
                client.send("Your roommates are: {}".format(roommates).encode("utf8"))
            elif message == "/mp":
                client.send("Who do you want to send a message to ?".encode("utf8"))
                message = client.recv(2048).decode("utf8")
                try :
                    conv = get_pv_conv(user,message)
                    if conv == "NE":
                        client.send("{} doesn't exist in our database...".format(message).encode("utf8"))
                    else :
                        current_conv = conv
                        key_exchange(conv)
                        client.send("/room {} ".format(current_conv.idRoom).encode("utf8"))  #tells the client app in which room it is right now
                        client.send("\nYou are in Room {} with {}".format(current_conv.idRoom,message).encode("utf8"))
                except:
                    client.send("Unable to reach {}".format(message).encode("utf8"))
            elif message=="/conv":
                print("ici")
                potential_new_room = get_conv(user)
                print("la"+str(potential_new_room))
                if potential_new_room != "NE":
                    current_conv=list_conv[potential_new_room]
                    client.send("You are in Room {} with {}".format(current_conv.idRoom,', '.join([u.name for u in current_conv.users])).encode("utf8"))

            elif message=="/lobby":
                current_conv=list_conv[0]
            elif message[0] == "/":
                client.send("Command {} not recognised. Type /help to see the available commands.".format(message).encode("utf8"))
            else:
                print("{} ({}): {}".format(address, user.name, message))
                current_conv.send_message(message, user.name)
        except:
            print("{} ({}) has left.".format(address, user.name))
            user.unconnect()
            client.close()
            broadcast("{} has abandoned you.".format(user.name), "SERVER")
            break

def login(client):
    message = ""
    client.send("Welcome to LimoncHello.".encode("utf8"))

    while message not in ["/s", "/l"]: 
        client.send(" Type (/l) to login or (/s) to subscribe :".encode("utf8"))
        message = client.recv(2048).decode("utf8")

    user = 0
    if message == "/s":
        user = subscribe(client)
    elif message == "/l":
        user = log(client)
    else :
        print("An error occured while login")
    return user

def subscribe(client):
    client.send("Choose a username:".encode("utf8"))
    username = client.recv(2048).decode("utf8")
    alreadyTaken = False

    names=[u.name for u in list_users]
    if username in names:
        alreadyTaken = True
        while alreadyTaken:
            client.send("This username has already been taken. Please choose a different one:".encode("utf8"))
            username = client.recv(2048).decode("utf8")
            if username not in names:
                alreadyTaken = False
    client.send("Choose your password:".encode("utf8"))
   
    pw = client.recv(2048).decode("utf8")
    u = User(username, pw)
    
    list_users.append(u)
    list_conv[0].add_user(u) #add the users to the main conversation (Room 0)
    return u

def log(client):
    client.send("Please type your username:".encode("utf8"))
    username = client.recv(2048).decode("utf8")

    names=[u.name for u in list_users]
    idx = -1

    while username not in names:
        client.send("This username isn't in the database... Try again :".encode("utf8"))
        username = client.recv(2048).decode("utf8")

    idx = names.index(username)

    if idx>=0 and idx<len(list_users) :
        user = list_users[idx]    
        client.send("Please type your password:".encode("utf8"))
        pw = client.recv(2048).decode("utf8")
        while user.password != pw:
            client.send("Wrong password, please try again :".encode("utf8"))
            pw = client.recv(2048).decode("utf8")
    else :
        print("Error while logging in")

    return user

def broadcast(message, sentBy = "SERVER"):
    # send a message to all the connected users (Room 0)
    try:
        list_conv[0].send_message(message, sentBy)
    except:
        print("Error while sending a message to everyone on room 0.")
    


# function to return user for a username 'val'
def get_usr_from_username(val):
    for usr in list_users:
        if usr.name == val:
            return usr
    return "NE"

def get_conv(user):
    client = user.socket
    message="/help"
    while message!="/end":
        if message=="/help":
            client.send("\nAvailable commands are :\
                \n/display to see current conversations,\
                \n/create to create a new conversation,\
                \n/join \
                \n/delete to delete a conversation,\
                \n/end to quit this configuration mode".encode("utf8"))
        elif message=="/create":
            client.send("Who do you want to add in your conversation ? Type /ok when you have finished adding people".encode("utf8"))
            list_people = [user]
            while message!="/ok":
                message = client.recv(2048).decode("utf8")
                usr = get_usr_from_username(message)
                if message=="/ok":
                    pass
                elif usr=="NE":
                    client.send("{} doesn't exits".format(message).encode("utf8"))    
                elif usr in list_people :
                    client.send("{} already added".format(message).encode("utf8"))
                else :
                    list_people.append(usr)
            conv = Conversation(len(list_conv))
            client.send("The number of your room is {}. Type /join to join it.".format(conv.idRoom).encode("utf8"))
            conv.add_users(list_people)
            list_conv.append(conv)
            
        elif message=="/join":
            client.send("What is the number of the room that you want to join ?".encode("utf8"))
            message = client.recv(2048).decode("utf8")
            id_rooms = []
            for co in list_conv:
                if user in co.users:
                    id_rooms.append(int(co.idRoom))
            if int(message) not in id_rooms:
                client.send("You can't join room {}. Type /display to see your conversations.".format(message).encode("utf8"))
            else:
                return int(message)           
        elif message=="/display":
            rooms = []
            for c in list_conv:
                if user in c.users:
                    rooms.append(c)
            str = ""
            for r in rooms:
                str += "\n-Room {} : ".format(r.idRoom) + ', '.join([u.name for u in r.users ]) 
            client.send(str.encode("utf8"))
        elif message=="/delete":
            pass
        message = client.recv(2048).decode("utf8")
    client.send("You've succesfully quitted the /conv configuration".encode("utf8"))
    return "NE"
 



# Get a conversation between an existing user (user_target) and potentially someone with the username (name_target)
def get_pv_conv(user_request, name_target):
    
    # check if target exists
    user_target=get_usr_from_username(name_target)  
    # check if conversation between the two already exists
    if user_target=="NE":
        return "NE"
    for conv in list_conv:
        if len(conv.users)==2 and user_request in conv.users and user_target in conv.users:
            print(3)
            return conv
    # otherwise, create and return a new conversation
    conv = Conversation(len(list_conv))
    list_conv.append(conv)
    conv.add_users([user_request,user_target])
    return conv

def key_exchange(conv):
    #key exchange initialized and facilitated by the server 
    global searching_key
    global key_ex
    users = conv.users
    print(users[0].name)
    sock1 = users[0].socket
    print(sock1)
    sock2 = users[1].socket
    print(sock2)
    try: 
        sock1.send('/Key {}'.format(conv.idRoom).encode('utf8'))
        key1 = sock1.recv(2048).decode("utf8")
    except: 
        print("problem with key echange from ", users[0].name)
    try: 
        searching_key = True
        sock2.send('/Key {}'.format(conv.idRoom).encode('utf8'))
        while key_ex == "":
            a=1
        key2 = key_ex
        key_ex = ""
        searching_key = False
    except:
        print("problem with key echange from ", users[1].name)
    try: 
        sock1.send(key2.encode('utf8'))
    except: 
        print("problem with key echange from ", users[0].name)
    try: 
        sock2.send(key1.encode('utf8'))
    except:
        print("problem with key echange from ", users[1].name)


def main():
    # host and port for the server
    host = ""
    port = 25000

    # Creates the socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Binds the serverSocket to the port number
    serverSocket.bind((host, port))

    # Enables accepting connections
    serverSocket.listen()

    print("LimoncHello server is running.")
    print("Waiting for new connections on port {}.".format(port))

    # Threads for each connection
    connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
    connThread.start()
    # Waits until it ends
    connThread.join()

    # Closes socket connection
    serverSocket.close()
    print("Server is closed.")





if __name__ == "__main__":
    main()
    pass