import socket
import os
import threading
from Classes.User import User
from Classes.Conversation import Conversation
from Classes.Message import Message

# list of existing user that have an account already created
list_users = []

# list of existing conversation that have been created
list_conv = []

def connectionThread(sock):
    load_database()

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
    # Handles the client
    address = adrs[0]
    
    #Connexion phase
    try:
        user = login(client)
        user.connect(client)
    except:
        print("Error while setting the username for {}.".format(address))
        client.close()
        return    
    print("{} has logged in as {}".format(address ,user.name))

    try:
        client.send("Dear individual {}, You are now connected to LimoncHello. You can type \"/help\" for a list of the available commands.".format(user.name).encode("utf8"))
    except:
        print("Communication error with {} ({}).".format(address, user.name))
        client.close()
        return
    broadcast("{} has joined the main room.".format(user.name))

    # Handles specific messages in a different way (user commands)
    current_conv=list_conv[0]
    user.socket.send("/room 0".encode("utf8")) #tells the client app in which room it is right now
    while True:
        try:
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
                roommates = ', '.join([user.name for user in current_conv.users])
                client.send("Your roommates are: {}".format(roommates).encode("utf8"))
            elif message == "/room":
                client.send("You're actually in room {}.".format(current_conv.idRoom).encode("utf8"))
            elif message == "/mp":
                client.send("Who do you want to send a message to ?".encode("utf8"))
                message = client.recv(2048).decode("utf8")
                try :
                    conv = get_pv_conv(user,message)
                    if conv == "NE":
                        client.send("Error : {} doesn't exist in our database...".format(message).encode("utf8"))
                    else :
                        current_conv = conv
                        client.send("/room {}".format(current_conv.idRoom).encode("utf8"))
                        client.send("You are in Room {} with {}".format(current_conv.idRoom,message).encode("utf8"))
                except:
                    client.send("Unable to reach {}".format(message).encode("utf8"))
            elif message=="/conv":
                client.send("Who do you want to add in your conversation ? Type /ok when you have finished adding people".encode("utf8"))
                list_people = [user]
                while message!="/ok":
                    message = client.recv(2048).decode("utf8")
                    usr = get_usr_from_nickname(message)
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
                conv.save()
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
                    potential_new_room = int(message)
                    if potential_new_room != "NE":
                        current_conv=list_conv[potential_new_room]
                        client.send("/room {}".format(current_conv.idRoom).encode("utf8"))
                        client.send("You are in Room {} with {}".format(current_conv.idRoom,', '.join([u.name for u in current_conv.users])).encode("utf8"))
                        current_conv.save()       
            elif message=="/display":
                rooms = []
                for c in list_conv:
                    if user in c.users:
                        rooms.append(c)
                str = ""
                for r in rooms:
                    str += "\nRoom {} : ".format(r.idRoom) + ', '.join([u.name for u in r.users ])
                client.send(str.encode("utf8"))
            elif message=="/lobby":
                current_conv=list_conv[0]
                client.send("/room 0".encode("utf8"))
                client.send("You're back in the lobby !")
            elif message=="/load":
                user.load(current_conv)
            elif message[0] == "/":
                client.send("Command {} not recognised. Type /help to see available commands.".format(message).encode("utf8"))
            else:
                print("{} ({}) in (Room {}): {}".format(address, user.name, current_conv.idRoom ,message))
                current_conv.send_message(message, user.name)
        except:
            print("{} ({}) has left.".format(address, user.name))
            user.unconnect()
            client.close()
            broadcast("{} has abandoned you.".format(user.name))
            break

def login(client):
    message = ""
    client.send("Welcome to LimoncHello!".encode("utf8"))

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
    u.save()    
    list_users.append(u)
    list_conv[0].add_user(u) #add the users to the main conversation (Room 0)
    list_conv[0].save() 
    return u

def log(client):
    client.send("Please type your username:".encode("utf8"))
    username = client.recv(2048).decode("utf8")

    names=[u.name for u in list_users]
    idx = -1

    while username not in names:
        client.send("This username isn't in our database... Try again :".encode("utf8"))
        username = client.recv(2048).decode("utf8")

    idx = names.index(username)

    if idx>=0 and idx<len(list_users) :
        user = list_users[idx]    
        client.send("Please type your password:".encode("utf8"))
        pw = client.recv(2048).decode("utf8")
        while user.password != pw:
            client.send("Wrong password, please try again :".encode("utf8"))
            pw = client.recv(2048).decode("utf8")

    return user

def broadcast(message, sentBy = "SERVER"):
    # send a message to all users connected (Room 0)
    try:
        list_conv[0].send_message(message, sentBy)
    except:
        print("Error while sending a message to everyone on room 0.")
    


# function to return user for a username 'val'
def get_usr_from_nickname(val):
    for usr in list_users:
        if usr.name == val:
            return usr
    return "NE"

# Get a conversation between an existing user (user_target) and potentially someone with the username (name_target)
def get_pv_conv(user_request, name_target):
    
    # check if target exists
    user_target=get_usr_from_nickname(name_target)  
    # check if conversation between the two already exists
    
    if user_target=="NE":
        return "NE"
    
    for conv in list_conv:
        if len(conv.users)==2 and user_request in conv.users and user_target in conv.users:
            return conv
    # otherwise, create and return a new conversation
    conv = Conversation(len(list_conv))
    list_conv.append(conv)
    conv.add_users([user_request,user_target])
    conv.save()
    return conv

def load_database():
    # get users informations
    file = open("./Serialisation/users.txt","r")
    for line in file.readlines():
        x=line.strip("\n").split("|")
        if get_usr_from_nickname(x[0])=="NE":
            list_users.append(User(x[0],x[1]))
    file.close()

    # get conversations informations
    i=0
    while os.path.isfile("./Serialisation/Conversations/conv{}.txt".format(i)):
        f = open("./Serialisation/Conversations/conv{}.txt".format(i),"r")
        lines = f.readlines()
        conv = Conversation(i)
        nicknames = lines[0].strip("\n").split("|")

        for n in nicknames:
            u=get_usr_from_nickname(n)
            if u != "NE":
                conv.add_user(u)
            else :
                print("Error while loading conversation {} : user '{}' in conversation but not in existing user...".format(i, n))

        for li in lines[1:len(lines)]:
            s = li.split("|")
            conv.add_message(s[0],s[1],s[2])
        list_conv.append(conv)
        i+=1
        
    return

def main():
    # host and port for the server
    host = ""
    port = 25000

    # Creates the socket
    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    serverSocket = socket.socket(socketFamily, socketType)

    # Binds the serverSocket to the port number
    serverSocket.bind((host, port))

    # Enables accepting connections
    serverSocket.listen()

    print("LimoncHello server is up and running!")
    print("Listening for new connections on port {}.".format(port))

    #Threads for each connection
    connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
    connThread.start()
    # Waits for it to end
    connThread.join()

    # Closes socket connection
    serverSocket.close()
    print("Server has shut down.")


if __name__ == "__main__":
    main()
    pass