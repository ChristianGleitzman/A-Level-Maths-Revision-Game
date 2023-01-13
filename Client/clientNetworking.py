import socket
import pickle
from messaging import Message
from PIL import Image, ImageQt


class TravClient:
    def __init__(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Server IP address
        self.__SERVER = "192.168.0.28"
        self.__PORT = 5050
        #The header is the number of bits allocated to each message
        self.__HEADER = 16384
        #The disconnect message disconnects the client from the server when sent to the server
        self.__DISCONNECT_MESSAGE = "!DISCONNECT"
        self.__ADDR = (self.__SERVER, self.__PORT)
        #'message' is assigned as the initial message sent by the server when connecting
        self.__message = self.connect()
        #These attributes hold the ID and username of the client logged in. They are initially set to None
        self.__id = None
        self.__username = None
        #The client is initially not logged in
        self.__loggedIn = False

    def getMessage(self):
        #Returns the current message
        return self.__message
    
    def getLoggedIn(self):
        #Returns the current logged in status
        return self.__loggedIn

    def getID(self):
        #Returns the current client username
        return self.__id

    def getName(self):
        #Returns the current client username
        return self.__username
    
    def connect(self):
        try:
            #Connects the client to the server
            self.__client.connect(self.__ADDR)
            #Loads the initial message from the server
            return pickle.loads(self.__client.recv(self.__HEADER))
        except:
            pass
    
    def sendMessage(self, data):
        try:
            #Sends a message to the server
            self.__client.send(pickle.dumps(data))
            #Returns the corresponding response given by the server
            return pickle.loads(self.__client.recv(self.__HEADER))
        except socket.error as err:
            #An error is printed if a message cannot be sent or/received
            print(err)
        except EOFError as err:
            #Prints an error an ends application if the client doesn't receive anything from the server
            print(err)
            print('[ERROR] A server error occured')
            quit()
    
    def requestConfirmation(self, reqType):
        #Changes the message contents to the request type
        self.__message.modifyContent(reqType)
        #The request is sent to the server
        #The confirmation message is assigned to the confirmation variable
        confirmation = self.sendMessage(self.__message)
        #The confirmation contents are printed
        print(confirmation.getContent())

    def exchange(self, content):
        #The message contents are changed to the content that is to be sent to the server
        self.__message.modifyContent(content)
        #The message is sent to the server
        #The response given by the server is then assigned to 'message'
        self.__message = self.sendMessage(self.__message)
        #The contents of the message is returned
        return self.__message.getContent()

    def loginVerifyReq(self, username, password):
        #A login verification request is sent to the server
        self.requestConfirmation('0001')
        #The entered details are sent to the server which returns data based on login success
        returned = self.exchange([username, password])
        #The success of login, username and id returned are set to the returned data
        self.__loggedIn = returned[0]
        self.__id = returned[1]
        self.__username = returned[2]
    
    def emailVerifyReq(self, enteredEmail):
        #An email verification request is sent
        self.requestConfirmation('0010')
        #The entered email is sent to the server which returns a boolean value based on whether the email exists in the database
        return self.exchange(enteredEmail)

    def resetPassReq(self, email, password):
        #A reset password request is sent
        self.requestConfirmation('0011')
        #The password is sent to the server which returns a boolean value based on password update success
        return self.exchange([email,password])
        
    def registerReq(self, entered):
        #A registration request is sent
        self.requestConfirmation('0100')
        #The entered details are sent to the server which returns a boolean value based on registration success
        return self.exchange(entered)

    def linkTeacherReq(self):
        #A link teacher request is sent
        self.requestConfirmation('0101')
        #A placeholder message is sent to the server as part of an exchange where the server returns teachers in the database
        return self.exchange('[Placeholder]')

    def progressReq(self):
        #A progress request is sent
        self.requestConfirmation('0110')
        #The client's id is sent to the server and the server returns user progress and game data corresponding to the id
        return self.exchange(self.__id)

    def generatedQuestionReq(self):
        #A generated question request is sent
        self.requestConfirmation('0111')
        #The client receives a generated question from the server
        return self.exchange('[Placeholder]')
    
    def fetchedQuestionReq(self, usedDif):
        #A fetched question request is sent
        self.requestConfirmation('1001')
        #The client receives a question from the server based on difficulty required and already used questions
        question = list(self.exchange(usedDif))
        #Timeout is set
        self.__client.settimeout(0.5)
        #An image file is created and written to using the data received from the server
        imageFile = open('questionImage.png', 'wb')
        imageChunk = self.__client.recv(2048)
        while imageChunk:
            imageFile.write(imageChunk)
            try:
                imageChunk = self.__client.recv(2048)
            except socket.timeout:
                break
        #Once the server has finished sending data, the file is closed
        imageFile.close()
        #Timeout is reset
        self.__client.settimeout(None)
        #The received image is converted into a pyQt image object so it can be embedded in a window
        qtImage = ImageQt.ImageQt(Image.open('questionImage.png'))
        #The pyQt image object replaces the file image location in the question list
        question[1] = qtImage
        #The question list is returned from the method
        return question
    
    def endGameReq(self, won, score, time, baseNo):
        #An end game request is sent
        self.requestConfirmation('1000')
        #The client receives the success of insertion of game stats into the database
        return self.exchange([self.__id, won, score, time, baseNo])
        
    def disconnectReq(self):
        #Logs the user out
        self.__loggedIn = False
        #A disconnect request is sent to the server which disconnects the current client
        self.requestConfirmation(self.__DISCONNECT_MESSAGE)
    
    def setID(self, id):
        self.__id = id

