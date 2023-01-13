from datetime import date
from sqlite3 import *
import socket 
import threading
import pickle
from urllib import response
from messaging import Message
from hashlib import sha256
from sympy import diff, integrate, symbols, simplify
import random
from PIL import Image, ImageQt

class Database:
    def __init__(self):
        #Database name set to database file name
        self.__dbname = 'pyramidTraversal.db'
    def connection(self):
        #Creates connection to database file
        con = connect(self.__dbname)
        cur = con.cursor()
        return con,cur
    def executeStatement(self, query, args=None):
        con,cur = self.connection()
        #Executes a given query on the database
        if not args:
            cur.execute(query)
        else:
            cur.execute(query, args)
        #Any data fetched from the database is assigned to 'selectedData'
        selectedData = cur.fetchall()
        #Any changes to the contents of the database are committed
        con.commit()
        #Connection to the database is closed
        con.close()
        #Any selected data is returned
        return selectedData
    def select(self, fields, table, selectBy=None, args=None):
        #Constructs a select statement based on arguments entered
        if not selectBy:
            query = f'SELECT {fields} FROM {table}'
        else:
            query = f'''SELECT {fields} FROM {table}
            WHERE {selectBy} = ?'''
        #returns the results of the execution of the query
        return self.executeStatement(query, args)

class TravServer:
    def __init__(self):
        #Instance of database class created
        self.db = Database()
        #Constants
        #The header is the number of bits allocated to each message
        self.__HEADER = 16384
        self.__PORT = 5050
        #The IP address the server is hosted on
        self.__IP = socket.gethostbyname(socket.gethostname())
        self.__ADDR = (self.__IP, self.__PORT)
        #Request Types
        self.__DISCONNECT_MESSAGE = "!DISCONNECT"
        self.__VERIFY_REQ = '0001'
        self.__EMAIL_REQ = '0010'
        self.__RESET_PASS_REQ = '0011'
        self.__REGISTER_REQ = '0100'
        self.__LINK_TEACHER_REQ = '0101'
        self.__PROGRESS_REQ = '0110'
        self.__GENERATED_QUESTION_REQ = '0111'
        self.__FETCHED_QUESTION_REQ = '1001'
        self.__ENDGAME_REQ = '1000'
    
        #Creation of server
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__server.bind(self.__ADDR)
        except socket.error:
            #Logs an error if the server cannot be created with the address and port
            print("[ERROR] This server has produced an error")

    #This method handles each client connected to the server in a seperate thread
    def handleClient(self, conn, addr):
        #New connection is added to server log
        print(f"[NEW CONNECTION] {addr} connected.")
        #Connection status set to true
        connected = True
        #Sends a connection confirmation message to client
        confirmation = Message('[CONNECTED] You are connected to the server')
        conn.send(pickle.dumps(confirmation))
        #Handles any messages sent to the client whilst they are connected
        while connected:
            try:
                #Server receives request message
                request = pickle.loads(conn.recv(self.__HEADER))
                if request:
                    #Request type is determined by request message contents
                    reqType = request.getContent()
                    #Based on the type of request, the corresponding method is executed to handle the request
                    if reqType == self.__DISCONNECT_MESSAGE:
                        print(f"[DISCONNECTION] {addr} disconnected.")
                        #Confirms disconnection to the user
                        confirmation = Message('[DISCONNECTED] You have disconnected from the server')
                        conn.send(pickle.dumps(confirmation))
                        #Sets connection status to false, causing the end of the method and thread
                        connected = False
                    elif reqType == self.__VERIFY_REQ:
                        self.verifyUserLogin(conn,addr)
                    elif reqType == self.__EMAIL_REQ:
                        self.verifyEmail(conn, addr)
                    elif reqType == self.__RESET_PASS_REQ:
                        self.resetPassword(conn, addr)
                    elif reqType == self.__REGISTER_REQ:
                        self.registerNewUser(conn, addr)
                    elif reqType == self.__LINK_TEACHER_REQ:
                        self.linkTeacher(conn, addr)
                    elif reqType == self.__PROGRESS_REQ:
                        self.fetchProgress(conn, addr)
                    elif reqType == self.__GENERATED_QUESTION_REQ:
                        self.sendGeneratedQuestion(conn, addr)
                    elif reqType == self.__FETCHED_QUESTION_REQ:
                        self.fetchQuestion(conn, addr)
                    elif reqType == self.__ENDGAME_REQ:
                        self.endGame(conn, addr)
                    else:
                        #In the case of the server receiving an invalid request, the connection with the client is terminated
                        print('[INVALID REQUEST] Invalid request received. Closing connection')
                        connected = False
            except socket.error as err:
                #Any possible errors produced by the server are caught and logged. The connection with the client is also terminated
                print(err)
                connected = False
            except:
                connected = False
        #Terminates connection
        conn.close()

    def start(self):
        #Server begins to listen for connections
        self.__server.listen()
        print(f"[LISTENING] Server is listening on {self.__IP}")
        while True:
            #Server accepts new client connection
            conn, addr = self.__server.accept()
            #Server creates a new thread to handle new client connection
            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()

    def confirmReq(self, conn, addr, type):
        try:
            #Request added to server log
            print(f"[{addr}] {type} Request Sent")
            #Confimation of request is sent to client
            confirmation = Message(f"[CONFIRMED] {type} Request Received")
            conn.send(pickle.dumps(confirmation))
        except socket.error as err:
            #Error is logged if request could not be confirmed
            print(f'[ERROR] {type} Request could not be confirmed')
            print(err)
    
    def acceptContent(self, conn):
        try:
            #Message is received by the server and message contents is collected
            received = pickle.loads(conn.recv(self.__HEADER))
            return received.getContent()
        except socket.error as err:
            #Any error in accepting client messages is logged
            print(err)
            print('[ERROR] The server could not accept a client message')
    
    def hashPassword(self, password):
        #Hashes password entered into function
        encoded = bytes(password, encoding='utf-8')
        m = sha256()
        m.update(encoded)
        #Returns hashed password
        return m.digest()

    def generateQuestion(self):
        try:
            #Initialises x as a symbol
            x = symbols('x')
            #Randomly choses the number of terms the expression will have
            terms = random.randint(1,3)
            #Expression is initially empty
            exp = ''
            #Each term in the expression is randomly generated and is added to the expression
            for i in range(terms):
                curr = str(random.randint(-20,20)) + '*x**' + str(random.randint(-5,5))
                if i == 0:
                    exp += curr
                else:
                    exp += '+' + curr
            #The expression is simplified of any redundancies (e.g. 1*x**4)
            exp = simplify(exp)
            #Randomly gererates another term for a wrong answer
            curr = str(random.randint(-20,20)) + '*x**' + str(random.randint(-5,5))
            #Differentiates expression with respect to x
            diffed = str(diff(exp, x))
            #Integrates expression with respect to x
            inted = str(integrate(exp, x))
            #Randomly chooses between the question requiring differentiation or integration
            choice = random.randint(1,2)
            #Generates final question, correct answer and wrong answers
            if choice == 1:
                correct = diffed
                wrong1 = inted + ' + C'
                wrong2 = str(simplify(str(exp) + curr))
                wrong3 = diffed + ' + C'
                #Creates question
                exp = '''Differentiate with respect to x:
    ''' + str(exp)
            else:
                correct = inted + ' + C'
                wrong1 = diffed
                wrong2 = str(simplify(str(exp) + curr)) + ' + C'
                wrong3 = inted
                #Creates question
                exp = '''Integrate with respect to x:
    ''' + str(exp)
            #Returns generated results
            return [exp, correct, wrong1, wrong2, wrong3]
        except:
            #If a question could not be generated, the function is called again
            print('[ERROR] Could not generate question')
            return self.generateQuestion()
    
    def sendGeneratedQuestion(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Generated Question')
        placeholder = pickle.loads(conn.recv(self.__HEADER))
        #A question is generated by calling the generate question method
        generated = self.generateQuestion()
        #A response message is instantiated
        response = Message(generated)
        #The generated question is sent to the client
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Generated Question Request Handled')

    def verifyUserLogin(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Login Verification')
        try:
            #Message containing user details is received
            details = self.acceptContent(conn)
            #The password the user entered is hashed
            hashedPass = self.hashPassword(details[1])
            #Database is queried based on password entered
            arg = (details[0],)
            fetched = self.db.select('studentID,password','tblStudents','username',arg)
            try:
                #Server returns True to client if password matches, otherwise returns False
                if hashedPass == fetched[0][1]:
                    response = Message([True, fetched[0][0], details[0]])
                else:
                    response = Message([False, None, None])
            except IndexError:
                #Server returns False if the username entered does not exist
                response = Message([False, None, None])
            conn.send(pickle.dumps(response))
            #Logs handling of request
            print(f'[{addr}] Login Request Handled')
        except socket.error as err:
            #Any errors sending messages are logged
            print(err)

    def verifyEmail(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Email Verification')
        #Database is queried based on the email entered by the user
        email = (self.acceptContent(conn),)
        fetched = self.db.select('studentID','tblStudents','email',email)
        #If the email entered does not exist in the database, the length of the list 'fetched' should be zero
        if len(fetched) == 0:
            #Returns false to the client if the email doesn't exist
            response = Message(False)
        else:
            #Returns true to the client if the email does exist
            response = Message(True)
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Email Request Handled')

    def resetPassword(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Reset Password')
        try:
            #Password is updated in the database to new password entered by the user
            entered = self.acceptContent(conn)
            hashedPass = self.hashPassword(entered[1])
            query = '''UPDATE tblStudents
            SET password = ?
            WHERE email = ?'''
            self.db.executeStatement(query, (hashedPass,entered[0]))
            #Sets success status of updating to true
            response = Message(True)
        except:
            #Any errors will cause the success status to be set to false
            response = Message(False)
        #Success status is sent to the client
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Reset Password Request Handled')
    
    def registerNewUser(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Registration')
        try:
            #Details entered by the client are saved to a variable
            details = self.acceptContent(conn)
            details[2] = self.hashPassword(details[2])
            #The new user is inserted into the students table of the database
            query = '''INSERT INTO tblStudents(email,username,password,teacherID)
            VALUES (?,?,?,?)'''
            self.db.executeStatement(query, details)
            #The success of registration is True if the email and username entered by the user are unique
            response = Message(True)
        except IntegrityError:
            #The success of registration is False if the email and username entered by the user are not unique
            response = Message(False)
        #Sends success of registration to the client
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Registration Request Handled')
    
    def linkTeacher(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Link Teacher')
        #Placeholder message is received
        placeholder = pickle.loads(conn.recv(self.__HEADER))
        #All the teacher IDs, titles and surnames are selected from the teacher table of the database
        fetched = self.db.select('teacherID,title,surname','tblTeachers')
        #Teacher information is sent to the client
        response = Message(fetched)
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Link Teacher Request Handled')

    def fetchProgress(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'Progress')
        #The client id is received
        clientID = self.acceptContent(conn)
        #Game data is fetched from the database based on the user id
        games = self.db.select('won,score,time,baseNo','tblGames','studentID', (clientID,))
        #The number of games played is the number of game records in the database from the current user
        gamesPlayed = len(games)
        #Can only create a new progress record if the user has played a few games
        if gamesPlayed < 3:
            performances = []
        else:
            self.newPerformanceRecord(clientID, gamesPlayed, games)
            performances = self.db.select('avgScore,avgTime,avgBaseNo,winRate,gamesPlayed,date','tblPerformance','studentID', (clientID,))
            if len(performances) >= 5:
                #Selects the most recent 5 performance data to send to the client if they have 5 or more performances
                #Otherwise, all performances are sent
                performances = performances[-5:]
        if gamesPlayed >= 5:
            #Selects the most recent 5 games to send to the client if they have played 5 or more games
            #Otherwise, all games are sent
            games = games[-5:]
        #Selects the teacher ID associated with the current user
        teacherID = self.db.select('teacherID','tblStudents','studentID', (clientID,))
        #Selects the teacher email associated with the teacher id selected
        teacherEmail = self.db.select('email','tblTeachers','teacherID', teacherID[0])
        #The server sends performances, games and teacher email to the client
        response = Message([performances, games, teacherEmail[0][0]])
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] Progress Request Handled')

    def newPerformanceRecord(self, clientID, gamesPlayed, games):
        #Performance IDs of performance records of the current client made today are fetched from the database
        query = '''SELECT performanceID FROM tblPerformance
        WHERE studentID = ?
        AND date = ?'''
        performanceIDs = self.db.executeStatement(query, (clientID, str(date.today())))
        #If the user has already created a new performance record today, a new record is not created
        if len(performanceIDs) == 0:
            #List of totals made for iteration
            totals = [0, 0, 0, 0]
            #Various totals are calculated
            for game in games:
                for i in range(len(totals)):
                    totals[i] += game[i]
            #Creation of insert statement
            query = '''INSERT INTO tblPerformance(studentID,avgScore,avgTime,avgBaseNo,winRate,gamesPlayed,date)
            VALUES (?,?,?,?,?,?,?)'''
            #Executes insert statement, inserting new performance data into the database
            self.db.executeStatement(query, (clientID, totals[1]/gamesPlayed, totals[2]/gamesPlayed, totals[3]/gamesPlayed, totals[0]/gamesPlayed, gamesPlayed, str(date.today())))
            
    
    def fetchQuestion(self, conn, addr):
        self.confirmReq(conn, addr, 'Fetched Question')
        #Message from client received
        received = self.acceptContent(conn)
        #Converts the question ids already used into a tuple for use in the query
        ids = tuple(received[0])
        if len(ids) == 0:
            #If there have been no other questions fetched, this query is executed
            query = '''SELECT questionID, fileName, correctAnswer, wrongAnswer1, wrongAnswer2, wrongAnswer3 FROM tblQuestions
            WHERE difficulty = ?'''
        else:
            #Selects all question info except difficulty based on the question difficulty required and whether the question has already been used
            query = f'''SELECT questionID, fileName, correctAnswer, wrongAnswer1, wrongAnswer2, wrongAnswer3 FROM tblQuestions
            WHERE difficulty = ?
            AND questionID NOT IN {ids}'''
            if len(ids) == 1:
                #Splices the query to move extra comma that causes an error when there is one question used
                query = query[:-2] + query[-1]
        #Executes statement
        fetched = self.db.executeStatement(query, (received[1],))
        #Choses a random question from the fetched questions
        chosen = random.choice(fetched)
        response = Message(chosen)
        #Sends question to client
        conn.send(pickle.dumps(response))
        #The image file of the selected question image is opened
        imageFile = open('questionImages/' + chosen[1], 'rb')
        #The image file is read from iteratively, sending chunks of image data to the client
        imageData = imageFile.read(2048)
        while imageData:
            conn.send(imageData)
            imageData = imageFile.read(2048)
        #Once the image has finished being read from, 
        #the file is closed and a message of None is sent to the client
        imageFile.close()
        #Logs handling of request
        print(f'[{addr}] Fetched Question Request Handled')

    def endGame(self, conn, addr):
        #Request is confirmed
        self.confirmReq(conn, addr, 'End Game')
        try:
            #Message from client received
            received = self.acceptContent(conn)
            #The game is inserted into the games table of the database
            query = '''INSERT INTO tblGames(studentID,won,score,time,baseNo)
            VALUES (?,?,?,?,?)'''
            self.db.executeStatement(query, received)
            #If an error is not raised, the success of insertion is True
            response = Message(True)
        except:
            #If an error is raised, the success of insertion is False
            print('[ERROR] Game details could not be saved')
            response = Message(False)
        #Sends response to client
        conn.send(pickle.dumps(response))
        #Logs handling of request
        print(f'[{addr}] End Game Request Handled')

if __name__ == "__main__":
    #Creates server instance and starts server
    print("[STARTING] server is starting...")
    serverInstance = TravServer()
    serverInstance.start()

    
    
