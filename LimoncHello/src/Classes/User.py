
class User:

    def __init__(self, username, password):
        self.name = username
        self.password = password
        self.socket = "NE"
        self.my_conversations = {}

    def __name__(self):
        return self.name

    def __password__(self):
        return self.password

    def receive_message(self, message): 
        try :
            if self.socket != "NE":
                self.socket.send(message.encode())
        except Exception as e:
            print("({}) didn't receive a message.".format(self.name))
            print(e)

    def connect(self, socket):
        self.socket = socket
    
    def unconnect(self):
        self.socket.close()
        self.socket = "NE"

    def add_conv(self, conv_name, key):
        self.my_conversations[conv_name] = key