from Classes.Message import Message

class Conversation:

    def __init__(self, id):
        self.crypted = False
        self.idRoom = id
        self.users = []
        self.messages = []
        try :
            print("Created conv {}".format(id))
            file = open("./Serialisation/Conversations/conv{}.txt".format(id),"x")
            file.close()
        except:
            pass
            #file = open("./Serialisation/Conversations/conv{}.txt".format(id),"r")
            #self.users = file.readlines()[0].strip("\n").split("|")
            #file.close()

    def save(self):
        f = open("./Serialisation/Conversations/conv{}.txt".format(self.idRoom),"w")
        f.write('|'.join([u.name for u in self.users]))
        for m in self.messages :
            f.write("{}|{}|{}\n".format(format(m.date,m.author,m.content)))
        f.close()

            
    def add_users(self, users):
        for u in users:
            if u not in self.users:
                self.users.append(u)
        

    def add_user(self, user):
        # Model OO
        if user not in self.users:
            self.users.append(user)



    def send_message(self,message,author_name):
        try:
            m=Message(author_name, message)
            self.messages.append(m)
            file = open("./Serialisation/Conversations/conv{}.txt".format(self.idRoom),"a")
            file.write("\n{}|{}|{}".format(m.date,m.author,m.content))
            file.close()
            for u in self.users:
                u.receive_message("Room {} > {} : {}".format(self.idRoom,author_name,  message))
        except:
            print("Error while sending message in Room {}".format(self.idRoom))

    def add_message(self,date, message_content, author_name):
        self.messages.append(Message(date, author_name,message_content))
        
