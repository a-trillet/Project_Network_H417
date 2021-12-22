
from datetime import datetime

class Message:

    def __init__(self, nickname, text , moment= datetime.now().strftime("%d/%m/%Y %H:%M:%S")):
        self.date = moment
        self.content = text
        self.author = nickname
        
    def __date__(self):
        return self.date

    def __author__(self):
        return self.author

    def __content__(self):
        return self.content