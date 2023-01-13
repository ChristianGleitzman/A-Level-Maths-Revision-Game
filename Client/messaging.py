
#Message class used to create message objects that can contain content of any data type
class Message:
    def __init__(self, content):
        #Content is a private attribute so cannot be altered/accessed outside the class
        self.__content = content
    def getContent(self):
        #Returns the content of the message
        return self.__content
    def modifyContent(self, newContent):
        #Modifies the current content of the message to the new content
        self.__content = newContent
