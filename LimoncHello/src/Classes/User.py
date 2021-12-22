
class User:

    def __init__(self, username, password):
        self.name = username
        self.password = password
        self.socket = "NE"

    # Return the history of the conversation conv to the user
    def load(self, conv):
        try:
            if self not in conv.users:
                self.send("Good attempt but you cannot read a conversation you're not into !".encode("utf8"))
            else:
                self.socket.send("/beg_hist".encode("utf8"))
                for m in conv.messages:
                    self.socket.send("|{}>{}>Room{}>{}".format(m.date,m.author,conv.idRoom,m.content).encode("utf8"))
                self.socket.send("/end_hist".encode("utf8"))
        except:
            print("Error, user {} not connected.".format(self.name))


    def save(self):
        f = open("./Serialisation/users.txt","a")
        f.write("\n{}|{}".format(self.name, self.password))
        f.close()

    def __name__(self):
        return self.name

    def __password__(self):
        return self.password

    def receive_message(self, message):
        try :
            if self.socket != "NE":
                self.socket.send(message.encode("utf8"))
        except :
            print("({}) didn't receive a message.".format(self.name))

    def connect(self, socket):
        self.socket = socket
    
    def unconnect(self):
        self.socket.close()
        self.socket = "NE"
