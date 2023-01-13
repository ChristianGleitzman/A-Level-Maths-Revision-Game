from PyQt5 import (QtWidgets,
                   QtCore,
                   QtGui,
                   uic,)
import sys
from sqlite3 import *
import re
from validator_collection import validators, checkers, errors
from random import choice, randint
import smtplib
from gameEngine import gameMain
import matplotlib.pyplot as plt

class StartMenu(QtWidgets.QMainWindow): 
    def __init__(self):
        super(StartMenu, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('startupMenu.ui',self) #Loads window design from the ui file
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.loginButton.clicked.connect(self.loginButtonMethod)
        self.registerButton.clicked.connect(self.registerButtonMethod)
        self.infoButton.clicked.connect(self.infoButtonMethod)
    
    def loginButtonMethod(self):
        #Creates login window when button is pressed
        self.loginWindow = Login()
        self.hide()
    def registerButtonMethod(self):
        #Creates new user registration window when button is pressed
        self.newUserWindow = NewUser()
        self.hide()
    def infoButtonMethod(self):
        #Creates game information window when button is pressed
        self.gameInfo = InfoWindow()
        self.hide()

class Login(QtWidgets.QMainWindow): 
    def __init__(self):
        super(Login, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('loginWindow.ui',self) #Loads window design from the ui file
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.submitButton.clicked.connect(self.submitButtonMethod)
        self.clrButton.clicked.connect(self.clrButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)
        self.fPassButton.clicked.connect(self.forgotPass)
        
    def submitButtonMethod(self):
        #Saves current contents of line edit widgets to variables
        username = self.usernameInput.text().lower()
        password = self.passInput.text()
        #Infoms user if any fields are blank
        if username == '' or password == '':
            messageBox('Blank Fields','Do not leave any fields blank!','warning')
        else:
            #A login request is made by the client which informs the success of the login
            clientInstance.loginVerifyReq(username,password)
            self.clrButtonMethod()
            #Checks if the user was logged in, and run codes based on login success
            if clientInstance.getLoggedIn():
                #Informs the user that their login was successful
                messageBox('Login Success', 'You have logged in sucessfully!')
                #Once logged on successfully, the login window and start menu can be closed
                self.close()
                startupMenu.close()
                #The home menu window is shown
                homeMenu.show()
            elif not clientInstance.getLoggedIn():
                #Informs user that their login attempt failed
                messageBox('Login Failed', 'Incorrect credentials entered. Please try again', 'warning')
            else:
                #Informs the user that an unexpected server error occured when attempting to login
                messageBox('Login Failed', 'An unexpected error occured. Please try again', 'warning')

    def clrButtonMethod(self):
        #Clears the current contents of the input widgets
        self.usernameInput.setText('')
        self.passInput.setText('')
    
    def backButtonMethod(self):
        #Takes the user back to the startup menu
        self.close()
        startupMenu.show()
    
    def forgotPass(self):
        #Creates the forgot password window and hides the current window
        self.forgotPassWindow = ForgotPass()
        self.hide()
 

class NewUser(QtWidgets.QMainWindow): 
    def __init__(self):
        super(NewUser, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('newUserWindow.ui',self) #Loads window design from the ui file
        self.show() #Window is shown when an instance of the class is made
        #Password input widget contents are initially hidden
        self.__passCov = True
        
        #handles the event of buttons being clicked
        self.submitButton.clicked.connect(self.submitButtonMethod)
        self.clrButton.clicked.connect(self.clrButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)
        self.checkPassButton.clicked.connect(self.checkButtonMethod)
        
    
    def submitButtonMethod(self):
        #Contents of input widgets are saved to variables
        email = self.emailInput.text().lower()
        username = self.usernameInput.text().lower()
        password = self.passInput.text()
        confirmedPassword = self.conPassInput.text()
        #Entered fields are saved to a list
        self.__enteredFields = [email,username,password,confirmedPassword]
        self.clrButtonMethod()
        #Checks if any of the fields have been left blank
        for i in range(len(self.__enteredFields)):
            if self.__enteredFields[i] == '':
                empty = True
                break
        else:
            empty = False
        if empty:
            #Informs the user that they have left fields blank
            messageBox('Empty Fields', 'Please fill out every field. Try again', 'warning')
        elif len(username) < 5 or len(username) > 12:
            messageBox('Invalid Username', 'Please ensure your username is between 5 and 12 characters!', 'warning')
        elif not checkers.is_email(email):
            #Informs the user they have entered an invalid email
            messageBox('Invalid Email', 'Invalid email entered. Please try again', 'warning')
        elif self.__enteredFields[2] != self.__enteredFields[3]:
            #Informs the user the password and confirmed password do not match
            messageBox('Password Mismatch', 'Password and Confirmed Password not identical. Please try again', 'warning')
        elif not testPass(self.__enteredFields[2]):
            #Tests the password entered and informs the user if the password entered is invalid
            messageBox('Invalid Password', 'Ensure your password is between 6-20 characters and contains at least one upper case letter, lower case letter, number and symbol.', 'warning')
        else:
            #If all the validity requirements are met, the confirmed password is removed from the list and the link teacher window is opened
            self.__enteredFields.pop()
            self.linkTeacherWindow = LinkTeacher(self.__enteredFields)
            self.hide()

    def clrButtonMethod(self):
        #Clears the current contents of the input widgets
        self.emailInput.setText('')
        self.usernameInput.setText('')
        self.passInput.setText('')
        self.conPassInput.setText('')

    def backButtonMethod(self):
        #Returns the user to the startup menu
        self.close()
        startupMenu.show()
    
    def checkButtonMethod(self):
        #Changes the password from being being hidden in the input widget to unhidden and vice versa
        if self.__passCov:
            self.passInput.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.conPassInput.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.passInput.setEchoMode(QtWidgets.QLineEdit.Password)
            self.conPassInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.__passCov = not self.__passCov

class LinkTeacher(QtWidgets.QMainWindow): 
    def __init__(self, enteredFields):
        super(LinkTeacher, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('linkTeacherWindow.ui',self) #Loads window design from the ui file
        #Saves the previously entered data to an attribute
        self.__enteredFields = enteredFields
        #Requests teacher information from the server
        self.__teachers = clientInstance.linkTeacherReq()
        #Adds each teacher to the combo box
        for i in range(len(self.__teachers)):
            self.teacherComboBox.addItem(self.__teachers[i][1] + ' ' + self.__teachers[i][2])
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.submitButton.clicked.connect(self.submitButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)
    
    def submitButtonMethod(self):
        #Saves the current index selected as the teacher id
        id = self.__teachers[self.teacherComboBox.currentIndex()][0]
        #Adds teacher id to the end of the list
        self.__enteredFields.append(id)
        #Registration request with entered fields is sent to the server. The success of registration is returned
        success = clientInstance.registerReq(self.__enteredFields)
        if success:
            #Informs the user of registration success
            messageBox('Creation Success','New user created successfully!')
            #Closes the current window + registration window and returns the user to the startup menu
            self.close()
            startupMenu.newUserWindow.close()
            startupMenu.show()
        else:
            #Informs the user of their registration failure
            messageBox('Creation Failure','New user could not be created. Either the email or username you entered is currently in use!', 'warning')
            #Closes the current window and returns the user to the registration window
            self.close()
            startupMenu.newUserWindow.show()
    
    def backButtonMethod(self):
        #Returns the user to the startup.menu
        self.close()
        startupMenu.newUserWindow.show()
            
class InfoWindow(QtWidgets.QMainWindow):   
    def __init__(self):
        super(InfoWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('gameInfoWindow.ui',self) #Loads window design from the ui file
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of the back button being clicked
        self.backButton.clicked.connect(self.backButtonMethod)
        
    def backButtonMethod(self):
        #Returns the user to the startup menu
        self.close()
        startupMenu.show()
            
class ForgotPass(QtWidgets.QMainWindow): 
    def __init__(self):
        super(ForgotPass, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('forgotWindow.ui',self) #Loads window design from the ui file
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.sendCodeButton.clicked.connect(self.sendCodeMethod)
        self.clrButton.clicked.connect(self.clrButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)
    
    def sendCodeMethod(self):
        try:
            #Saves the email in the input widget to a variable if valid, otherwise errors are raised
            enteredEmail = validators.email(self.emailInput.text().lower())
            #Verifies the email to check if the email is part of the existing database
            verifiedEmail = clientInstance.emailVerifyReq(enteredEmail)
            #Creates a random verification code and sends it in an email to the user
            if verifiedEmail:
                #Password reset code is generated
                resetCode = randint(1000,10000)
                #Reset code is sent to entered email
                sendMail('Pyramid Traversal Password Reset Email',f'''The verification code to reset your password is: {resetCode}
Please copy and enter this into the entry box so you can reset your password!''',enteredEmail)
                #Creates new window to reset password if all requirements are met and closes current window
                self.codeEntryWindow = CodeEntry(resetCode, enteredEmail)
                self.close()
            else:
                #Informs the user that the email they entered does not exist in the database
                messageBox('Unexisting Email','This email does not correspond to an existing user!','warning')
        except errors.EmptyValueError:
            #Informs the user the input widget was empty
            messageBox('Empty Field','Please enter an email address!','warning')
        except errors.InvalidEmailError:
            #Informs the user the email they entered is invalid
            messageBox('Invalid Email','Please enter an email of valid format!','warning')
        #Clears the input widget
        self.clrButtonMethod()
    
    def clrButtonMethod(self):
        #Clears the current contents of the input widget
        self.emailInput.setText('')
        
    def backButtonMethod(self):
        #Closes the current window and returns the user to the login window
        self.close()
        startupMenu.loginWindow.show()
        
class CodeEntry(QtWidgets.QMainWindow):
    def __init__(self, resetCode, enteredEmail):
        super(CodeEntry, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('codeEntryWindow.ui',self) #Loads window design from the ui file
        #Saves the previously entered email to a private attribute
        self.__enteredEmail = enteredEmail
        #Saves the reset code generated from the previous window to a private attribute
        self.__resetCode = resetCode
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.submitButton.clicked.connect(self.submitButtonMethod)
        self.clrButton.clicked.connect(self.clrButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)
        
    def submitButtonMethod(self):
        try:
            #The contents of the input widget are saved to a variable
            enteredCode = int(self.codeInput.text())
            if enteredCode == self.__resetCode:
                #If the code is correct, the current window is closed and the reset password window is opened
                self.close()
                self.resetPassWindow = ResetPass(self.__enteredEmail)
            else:
                #Informs the user they entered the incorrect code
                messageBox('Incorrect Code','Incorrect code entered. Please ensure the code is 4 digits!')
        except ValueError:
            #Informs the user they entered an invalid code format
            messageBox('Invalid Code','Please enter a valid 4 digit code!', 'warning')
        self.clrButtonMethod()
    def clrButtonMethod(self):
        #Clears the current contents of the input widget
        self.codeInput.setText('')
    def backButtonMethod(self):
        #Closes the current window and returns the user to the login window
        self.close()
        startupMenu.loginWindow.show()

class ResetPass(QtWidgets.QMainWindow): 
    def __init__(self, enteredEmail):
        super(ResetPass, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('ResetPassWindow.ui',self) #Loads window design from the ui file
        #Saves the previously entered email to a private attribute
        self.__enteredEmail = enteredEmail
        #Password entry widget contents are intially covered
        self.__passCov = True
        self.show() #Window is shown when an instance of the class is made
        
        #handles the event of buttons being clicked
        self.submitButton.clicked.connect(self.submitButtonMethod)
        self.clrButton.clicked.connect(self.clrButtonMethod)
        self.checkPassButton.clicked.connect(self.checkButtonMethod)
        self.backButton.clicked.connect(self.backButtonMethod)

    def submitButtonMethod(self):
        #Saves contents of input widgets to variables
        password = self.passInput.text()
        confirmedPassword = self.conPassInput.text()
        self.clrButtonMethod()
        if password == '' or confirmedPassword == '':
            #Informs the user if any of the input widgets have been left blank
            messageBox('Empty Fields','Please do not leave any fields blank!','warning')
        elif password != confirmedPassword:
            #Informs the user if the password and confirmed password do not match
            messageBox('Password Mismatch','Password and Confirmed Password not identical. Please try again','warning')
        elif not testPass(password):
            #The passwor is tested for validity and informs the user if an invalid password has been entered
            messageBox('Invalid Password', 'Ensure your password is between 6-20 characters and contains at least one upper case letter, lower case letter, number and symbol.', 'warning')
        else:
            #If all validity requirements are met, a reset password request is sent to the server
            #The success of the request is saved to a variable
            success = clientInstance.resetPassReq(self.__enteredEmail, password)
            if success:
                #Informs the user of reset success
                messageBox('Reset Success', 'Your password was successfully changed')
                self.close()
                startupMenu.loginWindow.show()
            else:
                #Informs the user of an unexpected server failure when attempting to reset the user's password
                messageBox('Reset Failure', 'An unexpected error occured. Please try again!', 'warning')
        
    def clrButtonMethod(self):
        #Clears the current contents of the input widgets
        self.passInput.setText('')
        self.conPassInput.setText('')

    def checkButtonMethod(self):
        #Changes the password from being being hidden in the input widget to unhidden and vice versa
        if self.__passCov:
            self.passInput.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.conPassInput.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.passInput.setEchoMode(QtWidgets.QLineEdit.Password)
            self.conPassInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.__passCov = not self.__passCov

    def backButtonMethod(self):
        #Closes the current window and returns the user to the login window
        self.close()
        startupMenu.loginWindow.show()

class HomeMenu(QtWidgets.QMainWindow): 
    def __init__(self):
        super(HomeMenu, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('homeMenu.ui', self) #Loads window design from the ui file
        #Initially, the user is not in a game
        self.inGame = False
        #Initially, the user has not sent any emails
        self.__progressEmails = 0
        self.__gameEmails = 0
        #These attributes hold the text displayed for game and progress overviews and are initially set to None
        self.recentPerformanceText = None
        self.recentGameText = None
        #This attribute will hold performance and game data as well as a teacher email
        self.userData = None
        #Default settings attributes
        self.volume = 0.5
        self.fps = 60
        #handles the event of buttons being clicked
        self.selectGameButton.clicked.connect(lambda: self.tabButtonMethod(4))
        self.progressButton.clicked.connect(self.progressButtonMethod)
        self.viewGamesButton.clicked.connect(lambda: self.tabButtonMethod(2))
        self.settingsButton.clicked.connect(lambda: self.tabButtonMethod(3))
        self.easyButton.clicked.connect(lambda: self.startGame(5))
        self.mediumButton.clicked.connect(lambda: self.startGame(6))
        self.hardButton.clicked.connect(lambda: self.startGame(7))
        self.viewAvgScoreButton.clicked.connect(lambda: self.createAvgPlot('Average Score',0))
        self.viewAvgBaseButton.clicked.connect(lambda: self.createAvgPlot('Average Base',2))
        self.viewRecentScoresButton.clicked.connect(lambda: self.createRecentPlot('Score',1))
        self.viewRecentTimesButton.clicked.connect(lambda: self.createRecentPlot('Time',2))
        self.sendPerfButton.clicked.connect(self.sendPerformance)
        self.sendGameButton.clicked.connect(self.sendGame)
        self.logOutButton.clicked.connect(self.logOut)
        self.confirmSettingsButton.clicked.connect(self.settingsButtonMethod)
        #Sets current tab to intro tab
        self.tabWidget.setCurrentIndex(0)
    
    def tabButtonMethod(self, index):
        #Sets current tab to tab index passed into the method
        self.tabWidget.setCurrentIndex(index)
    
    def progressButtonMethod(self):
        #User progress and game data is sent from the server
        self.userData = clientInstance.progressReq()
        #If the user has not played enough games to see a performance overview, they are informed of this
        if self.userData[0] == []:
            self.lblPerformanceData.setText('Play some more games to\n see a progress overview!')
        else:
            #A recent performance overview is created based on the most recent record in the data received
            self.recentPerformanceText = f'''Average Score: {round(self.userData[0][-1][0], 2)} pts
Average Time: {round(self.userData[0][-1][1], 2)} secs
Average Base Size Attempted: {round(self.userData[0][-1][2], 2)}
Games Played: {self.userData[0][-1][4]}
Win Rate: {round(self.userData[0][-1][3]*100, 2)}%'''
            self.lblPerformanceData.setText(self.recentPerformanceText)
        #If the user has not played a game, they are informed that there is not data that can be displayed
        if self.userData[1] == []:
            self.lblRecentGameData.setText("You have not yet completed a game!")
        else:
            #Otherwise, an overview is made of their most recent game played
            if self.userData[1][-1][0]:
                yesNo = 'Yes'
            else:
                yesNo = 'No'
            self.recentGameText = f'''Won? {yesNo}
Score: {self.userData[1][-1][1]} pts
Time: {self.userData[1][-1][2]} secs
Base Size: {self.userData[1][-1][3]}'''
            self.lblRecentGameData.setText(self.recentGameText)
        self.tabWidget.setCurrentIndex(1)

    def createAvgPlot(self, label, index):
        #If the user does not have enough performance data, a graph is not made and the user is informed
        if len(self.userData[0]) < 2:
            messageBox('Cannot Create Graph', 'You do not have enough performance data to create a graph!')
        else:
            ydata = []
            xdata = []
            #Depending on the graph required, lists are made for the x and y axis data for the graph 
            for i in range(len(self.userData[0])):
                xdata.append(self.userData[0][i][-1])
                ydata.append(self.userData[0][i][index])
            #The graph is plotted
            plt.plot(xdata, ydata)
            #The graph title, x axis and y axis label are set
            plt.ylabel(label)
            plt.xlabel('Dates')
            plt.title(label + ' Over Time')
            #The graph is displayed to the user
            plt.show()
        
    def createRecentPlot(self, label, index):
        #If the user does not have enough game data, a graph is not made and the user is informed
        if len(self.userData[1]) < 2:
            messageBox('Cannot Create Graph', 'You do not have enough game data to create a graph!')
        else:
            ydata = []
            #Depending on the graph required, a list is made for the y axis data for the graph
            for i in range(len(self.userData[1])):
                ydata.append(self.userData[1][i][index])
            #The graph is plotted
            plt.plot([1,2,3,4,5], ydata)
            #The graph title, x axis and y axis label are set  
            plt.xlabel('Game')
            plt.ylabel(label)
            plt.title(label + 's from Recent Games')
            #The graph is displayed to the user
            plt.show()
    
    def sendPerformance(self):
        #Only sends an email if there is any data to send
        if self.recentPerformanceText:
            if self.__progressEmails == 0:
                #Sends an email to the user's teacher with the data from a user's most recent performance data if under the email limit
                self.sendData('performance',clientInstance.getName(),self.recentPerformanceText)
                #Increments the number of emails sent
                self.__progressEmails += 1
            else:
                #Informs the user they have reached the email limit
                messageBox('Email Limit Reached','You have reached the email limit for progress data! Please try again later')
        else:
            #Informs the user they cannot send an email
            messageBox('No data','You do not have any performance data to send to a teacher!')
    
    def sendGame(self):
        #Only sends an email if there is any data to send
        if self.recentGameText:
            if self.__gameEmails < 3:
                #Sends an email to the user's teacher with the data from a user's most recent game if under the email limit
                self.sendData('game',clientInstance.getName(),self.recentGameText)
                #Increments the number of emails sent
                self.__progressEmails += 1
            else:
                #Informs the user they have reached the email limit
                messageBox('Email Limit Reached','You have reached the email limit for game data! Please try again later')
        else:
            #Informs the user they cannot send an email
            messageBox('No data','You do not have a game to send to a teacher!')
    
    def sendData(self, type, username, content):
        #Sends email containing relevant subject and content
        sendMail(f'Pyramid Traversal {type} from {username}', f'''{username} wanted to share their most recent {type} in Pyramid Traversal with you:
{content}
(This was an automated email sent by the Pyramid Traversal Maths Game)''', self.userData[2])
        #Informs the user the email was sent
        messageBox('Mail Sent', f'Your most recent {type} has been sent to your teacher!')

    def settingsButtonMethod(self):
        #Sets the fps setting to the position of the fps slider
        self.fps = self.fpsSlider.value()
        #Sets the volume setting based on volume slider position
        self.volume = self.volumeSlider.value()/100

    def startGame(self, baseNo):
        #Sets current tab to intro tab for if the user returns to the home menu
        self.tabWidget.setCurrentIndex(0)
        #Sets the ingame attribute to True
        self.inGame = True
        self.move(5000,5000)
        #Starts game with a pyramid size based on difficulty selected
        gameMain(clientInstance, baseNo, endGameWindow, answerWindow, self.volume, self.fps)

    def logOut(self):
        #Closes the home menu to end the application as a result
        self.close()

    def closeEvent(self, event):
        #Doesn't allow the user to close the home menu while in game to prevent errors
        if self.inGame:
            messageBox('In Game','Please finish your current game before trying to use the home menu!','warning')
            event.ignore()
        else:
            event.accept()

class AnswerWindow(QtWidgets.QMainWindow): 
    def __init__(self):
        super(AnswerWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('answerWindow.ui',self) #Loads window design from the ui file
        #Initially sets the current correct answer and block to None
        self.currentCorrect = None
        self.currentBlock = None
        #Holds buttons in a list for interation
        self.buttons = [self.answerButton1, self.answerButton2, self.answerButton3, self.answerButton4]
        #handles the event of buttons being clicked
        self.answerButton1.clicked.connect(lambda: self.answerButtonMethod(self.answerButton1))
        self.answerButton2.clicked.connect(lambda: self.answerButtonMethod(self.answerButton2))
        self.answerButton3.clicked.connect(lambda: self.answerButtonMethod(self.answerButton3))
        self.answerButton4.clicked.connect(lambda: self.answerButtonMethod(self.answerButton4))
    
    def updateQuestion(self, block):
        #Sets the current block to the block object passed into the method
        self.currentBlock = block
        if self.currentBlock.difficulty == 0:
            #Sets the question label to the expression generated
            self.questionImage.setText(self.currentBlock.getQuestion()[0])
            #Creates a list of the possible answers
            answers = [self.currentBlock.getQuestion()[i] for i in range(1,5)]
        else:
            #Pixmap is created based on qt image object
            pixmap = QtGui.QPixmap.fromImage(self.currentBlock.getQuestion()[1])
            #Question Image label's image in the answer window is set to the pixmap created
            self.questionImage.setPixmap(pixmap)
            #Creates a list of the possible answers
            answers = [self.currentBlock.getQuestion()[i] for i in range(2,6)]
        #Sets the correct answer to the first item in the answers list
        self.currentCorrect = answers[0]
        print(self.currentCorrect)
        #Randomly assigns an answer to each of the buttons
        for button in self.buttons:
            chosen = choice(answers)
            button.setText(chosen)
            answers.remove(chosen)
        #Displays window after updating
        self.show()
    def answerButtonMethod(self, buttonPicked):
        #Holds the answer the user picked
        userAns = buttonPicked.text()
        #If the user answers correctly, the current block's correct attribute is set to True
        if userAns == self.currentCorrect:
            #Hides the window
            self.hide()
            messageBox('Correct','You Answered Correctly!')
            self.currentBlock.correct = True
        else:
            #Hides the window
            self.hide()
            #If the user answers incorrectly, the current block's correct attribute is set to False
            if self.currentBlock.answerAttempts == 0:
                #Informs the user they got the question wrong
                messageBox('Incorrect','You Answered incorrectly! Have another go.')
            else:
                #Informs the user they got the question wrong and cannot try again
                messageBox('Incorrect','You Answered incorrectly! That was your last chance')
            #Increments the current blocks answer attempts
            self.currentBlock.answerAttempts += 1

class EndGameWindow(QtWidgets.QMainWindow): 
    def __init__(self):
        super(EndGameWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('endGameWindow.ui',self) #Loads window design from the ui file
        #handles the event of buttons being clicked
        self.replayButton.clicked.connect(self.replayButtonMethod)
        self.homeButton.clicked.connect(self.homeButtonMethod)
        #pixmap = QtGui.QPixmap.fromImage(question[1])
    def update(self, won, score, time, baseNo):
        #Sets the current baseNo of the current game to the baseNo argument
        self.currBaseNo = baseNo
        #Initially sets success of database insertion to False
        success = False
        #Sets initial time bonus to zero so if the player didn't win, it is reflected in their score
        timeBonus = 0
        #If the player won the game, this code is executed
        if won:
            #A time bonus is calculated based on the time taken to beat the level
            timeBonus = round((180*self.currBaseNo)/time)
            #Displays an overview of the performance of the player in the level
            self.lblWindowTitle.setText('You Won!')
            self.lblSub.setText('Congratulations on beating this level!')
            self.lblOverview.setText(f'''Your Game Overview:
Your score: {score} points
Your time: {time} seconds
Time Bonus: {timeBonus} points
Your Total Score: {score + timeBonus} points''')
        #If the player lost the game, this code is executed
        else:
            #Displays to the player that they lost the game
            self.lblWindowTitle.setText('Game Over')
            self.lblSub.setText("You didn't manage to beat the level this time!")
            self.lblOverview.setText('Press replay to retry the level or\ngo to the home menu to select another level')
        #Saves the game data to the database
        success = clientInstance.endGameReq(won, score+timeBonus, time, self.currBaseNo)
        #Displays the window
        self.show()
        #Informs the user on whether their game data could be saved
        if not success:
            messageBox('Save Failed', 'Your game data could not be saved!')
    def replayButtonMethod(self):
        #Hides the current window
        self.hide()
        #Starts another game with the same settings
        homeMenu.startGame(self.currBaseNo)
    def homeButtonMethod(self):
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        homeMenu.move(qtRectangle.topLeft())
        #The user is no longer in game, so can use the home menu
        homeMenu.inGame = False
        #Hides the current window
        self.hide()
    def closeEvent(self, event):
        self.homeButtonMethod()
        event.accept()
        
#This is used to validate new passwords and is used in multiple classes so is a general function
def testPass(password):
    #This variable contains the requirments for a secure password
    passwordRequirements = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!"£$%^&*#?@])[A-Za-z\d!"£$%^&*#?@]{6,20}$'
    compiled = re.compile(passwordRequirements)
    #The entered password is checked against the requirements
    valid = re.search(compiled, password)
    #If the password is valid, the function returns true and returns false otherwise
    if valid:
        return True
    else:
        return False
    

#This function is used to display pop-up message boxes to inform the user. The default is an info message
def messageBox(title, content, iconType="info"):
    #A message box object is created
    msgBox = QtWidgets.QMessageBox()
    #Sets the message box icon based on icon type passed as a parameter
    if iconType == "info":
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
    elif iconType == "question":
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
    elif iconType == "warning":
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    else:
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    #Sets text and title to arguments passed into the function
    msgBox.setText(content)
    msgBox.setWindowTitle(title)
    #Shows the message box to the user
    msgBox.exec()
     
#This function is used to send emails and is not specific to any classes
def sendMail(subject, body, emailRecipient):
    try:
        #Connects to gmail servers
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        #This gmail account was set up for this program to use and is logged into. The password has been removed for GitHub
        server.login("pyramidtraversal@gmail.com", "--------")
        #A message containing the subject and body is formatted
        msg = f"Subject: {subject}\n\n{body}"
        #This sends an email to a recipient with the entered subject and body
        server.sendmail("pyramidtraversal@gmail.com", emailRecipient, msg)
        server.quit()
    except:
        #Informs the user of an error when attempting to email
        messageBox('Emailing Error','An unexpected error occured when attempting to send an email. Please try again.')

def menuMain(client):
    #Receives client object from main client file
    global clientInstance
    clientInstance = client
    app = QtWidgets.QApplication(sys.argv)
    #Gets initial message from server. If there is no message, the server is not running
    if clientInstance.getMessage() == None:
        #Informs the user the server is not running and closes the application
        print("[ERROR] Server connect failed. The server is not running")
        messageBox('Server Down', 'The server is currently not running. Please try again later', 1)
        quit()
    else:
        #Prints connection confirmation message
        print(clientInstance.getMessage().getContent())
        #Initialises various menus
        global startupMenu
        startupMenu = StartMenu()
        global answerWindow
        answerWindow = AnswerWindow()
        global endGameWindow
        endGameWindow = EndGameWindow()
        global homeMenu
        homeMenu = HomeMenu()
        #Starts menu execution
        app.exec()
        #Quits menu execution when all windows are closed
        QtWidgets.QApplication.quit()
        

