
class Conversation:

    def __init__(self, id):
        self.idRoom = id
        self.users = []
        self.messages = []

    def add_users(self, users):
        for u in users:
            if u not in self.users:
                self.users.append(u)

    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)


    def send_message(self,message,author_name):
        try:
            self.messages.append(message)
            for u in self.users:
                u.receive_message("Room {} > {}".format(self.idRoom,author_name))
                u.receive_message(message)
        except:
            print("Error while sending message in Room {}".format(self.idRoom))

    def getUsers(self):
        return self.users

