import math
from random import randint
import pygame

pygame.init() #Initialises pygame

#Window size and FPS constants
WIDTH = 1000
HEIGHT = 1000

#colour constants
WHITE = (255,255,255)
BLACK = (0,0,0)

def gameMain(clientInstance, baseNo, endGameWindow, answerWindow, volume, fps):
    try:
        #Initialises pygame font
        pygame.font.init()
        #Initialises sound
        pygame.mixer.init()
        #Sets global variable of running to True as the game begins
        global running
        running = True
        #Initially sets won to false as the player has not yet won the game
        global won
        won = False
        #Screen creation
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        #Sets the window caption to the game's title
        pygame.display.set_caption("Pyramid Traversal")
        #Initialises the pygame clock
        clock = pygame.time.Clock()
        
        #Loading game graphics
        playerRImg = pygame.image.load('images/playerR.png').convert()
        playerLImg = pygame.image.load('images/playerL.png').convert()
        background = pygame.image.load('images/jungle.jpg').convert()
        blockImg = pygame.image.load('images/block.png').convert()
        blockHoverImg = pygame.image.load('images/blockHover.png').convert()
        blockAnsweredImg = pygame.image.load('images/blockAnswered.png').convert()
        blockForfeitImg = pygame.image.load('images/blockForfeit.png').convert()
        vineImg = pygame.image.load('images/vines.png').convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        backgroundRect = background.get_rect()

        #Loading game sounds
        pygame.mixer.music.load('sounds/jungleMusic.ogg')
        collisionSound = pygame.mixer.Sound('sounds/collision.wav')
        correctSound = pygame.mixer.Sound('sounds/correct.wav')
        lostSound = pygame.mixer.Sound('sounds/lostJingle.wav')
        jumpSound = pygame.mixer.Sound('sounds/jump.wav')
        openSound = pygame.mixer.Sound('sounds/open.wav')
        wonSound = pygame.mixer.Sound('sounds/wonJingle.wav')
        #Setting music volume
        pygame.mixer.music.set_volume(volume)
        #Initially no questions from the database have been used
        questionsUsed = []
        #Sets initial score to zero
        global score
        score = 0

        class Player(pygame.sprite.Sprite):
            def __init__(self, x, y, py, width, height):
                pygame.sprite.Sprite.__init__(self)
                #Sets the width and height of the player
                self.width = width
                self.height = height
                #Sets player image to loaded graphic based on width and height
                self.image = pygame.transform.scale(playerRImg, (self.width, self.height))
                #Removes white around player graphic
                self.image.set_colorkey(WHITE)
                
                #Creates rect for player
                self.rect = self.image.get_rect()
                #Positions player
                self.rect.centerx = x
                self.rect.bottom = y
                #Jumping attributes
                bound = int(8.05*math.sqrt(baseNo))
                self.jumpingVelocity = [i for i in range(-bound,bound+1)]
                self.velocityIndex = 0
                self.jump = False
                self.jumpStrength = 0
                self.platformy = py
                #Sets the intial layer the player is on to zero
                self.currentLayer = 0

            def update(self):
                #Gets the current keys pressed
                keystate = pygame.key.get_pressed()
                #This stops the player from moving if they are currently answering a question
                if not answerWindow.isVisible():
                    if keystate[pygame.K_RETURN]:
                        #If the player presses enter, the answer method for all blocks they are collided with is called
                        blockCollision = pygame.sprite.spritecollide(self, blocks, False)
                        for block in blockCollision:
                            block.answer()
                    #If the player presses a, this code is executed
                    if keystate[pygame.K_a]:
                        #Sets image to left facing image
                        self.image = pygame.transform.scale(playerLImg, (self.width, self.height))
                        #Removes white around player graphic
                        self.image.set_colorkey(WHITE)
                        #Moves the player rect to the left
                        self.rect.x += -5
                    #If the player presses d, this code is executed
                    if keystate[pygame.K_d]:
                        #Sets image to right facing image
                        self.image = pygame.transform.scale(playerRImg, (self.width, self.height))
                        #Removes white around player graphic
                        self.image.set_colorkey(WHITE)
                        #Moves the player rect to the right
                        self.rect.x += 5
                    #If the player presses w and the player is not already jumping, this code is executed
                    if not self.jump and keystate[pygame.K_w]:
                        #The jump strength is increased for each frame the player is holding w
                        self.jumpStrength += 1
                        #If the player has held w for long enough, the player jumps
                        if self.jumpStrength > 30:
                            #Plays the jump sound effect
                            jumpSound.play()
                            self.jump = True
                    #If the player is jumping, this code is executed
                    if self.jump:
                        #Sets lineCollision to True if the player collides with any lines
                        lineCollision = pygame.sprite.spritecollide(self, lines, False)
                        #If the player hits a line, their velocity is reversed, causing them to move back down
                        if lineCollision:
                            #Collision sound is played
                            collisionSound.play()
                            self.velocityIndex = int((len(self.jumpingVelocity) + 1) / 2)
                        #Moves the player vertically based on their jumping velocity
                        self.rect.y += self.jumpingVelocity[self.velocityIndex]
                        #Increases the velocity index in order to complete the jump
                        self.velocityIndex += 1
                        #If the velocity index is at the end of the list but the jump has not finished, it sets the velocity index back
                        if self.velocityIndex >= len(self.jumpingVelocity) - 1:
                            self.velocityIndex = len(self.jumpingVelocity) - 1
                        #Calculates the vertical position of the platform above the player
                        abovePlatform = HEIGHT - (blockSpacing * self.currentLayer)
                        #If the player goes 'above' this platform, the current platform level is set to this platform position
                        #(i.e. the player moves up a level)
                        if self.rect.bottom < abovePlatform:
                            self.platformy = abovePlatform
                        #If the player reaches their current platform (i.e. they land), the player stops jumping and jumping attributes are reset
                        if self.rect.bottom > self.platformy:
                            self.rect.bottom = self.platformy
                            self.jump = False
                            self.jumpStrength = 0
                            self.velocityIndex = 0

                #These if statements prevent the player from moving outside the bounds of the game window    
                if self.rect.right > WIDTH:
                    self.rect.right = WIDTH
                if self.rect.left < 0:
                    self.rect.left = 0
                if self.rect.bottom > HEIGHT:
                    self.rect.bottom = HEIGHT
                if self.rect.top < 0:
                    self.rect.top = 0
        
        class Line(pygame.sprite.Sprite):
            def __init__(self, width, height, x, y):
                #Creates line sprite based on width, height, and position entered
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.transform.scale(vineImg, (int(width), int(height)))
                #Removes white around vine graphic
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                #Sets line position
                self.rect.x = x
                self.rect.top = y
                
        class Block(pygame.sprite.Sprite):
            def __init__(self, blockSize, x, y, layer):
                pygame.sprite.Sprite.__init__(self)
                self.size = int(blockSize)
                #Sets image to block graphic based on block size 
                self.image = pygame.transform.scale(blockImg, (self.size, self.size))
                #Removes white around block graphic
                self.image.set_colorkey(WHITE)
                self.rect = self.image.get_rect()
                #Sets position to x and y coordinates entered
                self.rect.x = x
                self.rect.bottom = y
                #Sets the layer of the block to the layer entered
                self.layer = layer
                #Calcualtes the question difficulty of the block based on its layer
                self.difficulty = round((self.layer / (baseNo-1)) * 4)
                #Adds the question id to the questions used if the difficulty is not zero
                if self.difficulty != 0:
                    #Fetches a question for the block to hold
                    self.__question = clientInstance.fetchedQuestionReq([questionsUsed, self.difficulty])
                    questionsUsed.append(self.__question[0])
                else:
                    self.__question = clientInstance.generatedQuestionReq()
                #Sets the attempts at answering the question in the block to zero
                self.answerAttempts = 0
                #The block has initially not been answered and not correct
                self.answered = False
                self.correct = False
            def getQuestion(self):
                #Returns the question held in the block object
                return self.__question
            def update(self):
                #Initially sets the image change to be the same appearance as before
                imageChange = blockImg
                #Colliding is set to true if the block rect is completely colliding with the player
                self.colliding = self.rect.collidepoint(player.rect.x,player.rect.y)
                #If the player is colliding with the block and answers it correctly, this code is executed
                if self.colliding and self.correct:
                    #The block is answered
                    self.answered = True
                    #The score is incremented based on the layer the player is on
                    global score
                    score += self.layer + 1
                    #Adds a bonus point if the player answers correctly first time
                    if self.answerAttempts == 0:
                        score += 3
                    #Removes the line blocking the player from moving upwards a layer 
                    layers[self.layer][-1].kill()
                    #Increments the players current layer
                    player.currentLayer += 1
                    #Sets correct back to false so the code is not repeated
                    self.correct = False
                    #If the players current layer is the same as the base size, the player wins the game and the game finishes
                    if player.currentLayer == baseNo:
                        #Plays game won sound
                        wonSound.play()
                        global won
                        won = True
                        global running
                        running = False
                    else:
                        correctSound.play()
                #If the block has been answered, the image changes to an answered graphic where the block is less damaged     
                if self.answered:
                    imageChange = blockAnsweredImg
                #If the player has attempted to answer too many times, the image changes to a forfeited graphic
                elif self.answerAttempts >= 2:
                    imageChange = blockForfeitImg
                #If the player is just colliding with the block, the block gets lighter to indicate the collision
                elif self.colliding:
                    imageChange = blockHoverImg
                self.image = pygame.transform.scale(imageChange, (self.size, self.size))
                #Removes white around block graphic
                self.image.set_colorkey(WHITE)
                #If the current layer that the player is on does not have any questions left to answer, the player has lost and the game finishes
                for block in layers[self.layer]:
                    try:
                        if block.answerAttempts < 2:
                            break
                    except:
                        pass
                else:
                    #Plays game lost sound
                    lostSound.play()
                    running = False
            def answer(self):
                #Calls the update question method on the answer question window if the conditions are met
                if self.colliding and self.answerAttempts < 2 and self.layer == player.currentLayer:
                    #Plays open question sound
                    openSound.play()
                    answerWindow.updateQuestion(self)

        #Creating sprite groups
        allSprites = pygame.sprite.Group()
        layers = []
        blocks = pygame.sprite.Group()
        lines = pygame.sprite.Group()

        #Calculates a block size based on the size of the screen and pyramid
        blockSize = HEIGHT / (baseNo+2)
        #Adds spacing between the blocks
        blockSpacing = blockSize + 5
        #Sets the initial x and y coordinates for the first blocks on the pyramid
        initialY = HEIGHT
        initialX = (WIDTH/2) - ((baseNo/2) * blockSpacing)
        #This for loop constructs the level
        for i in range(baseNo):
            currLayer = []
            if i != 0:
                #Increments the initial x coordinate for the first block in each layer above the first
                initialX += blockSpacing / 2
            for j in range(baseNo-i):
                #Creates blocks that are postioned to form a pyramid, with less blocks made you go up the layers
                block = Block(blockSize, initialX + (j*blockSpacing), initialY - (i*blockSpacing), i)
                #Adds the current block to the current layer list
                currLayer.append(block)
                #Adds the current block to sprite groups
                allSprites.add(block)
                blocks.add(block)
            if i != baseNo-1:
                #Sets the y postion of the current line
                currLineY = initialY - ((i+1)*blockSpacing)
                #Creates the line sprite to sit between the pyramid layers to block the player from moving up until it is destroyed
                line = Line((baseNo-i)*blockSpacing-5, 15, initialX, currLineY,)
                #Adds the line to the current layer list
                currLayer.append(line)
                #Adds the sprite to sprite groups
                allSprites.add(line)
                lines.add(line)
                #Creates two blocking line sprites for each layer to block the player from moving up between the sides of the screen and pyramid
                blocker = Line(initialX, 15, 0, currLineY)
                #Adds blocker to sprite group
                allSprites.add(blocker)
                lines.add(blocker)
                blocker = Line(initialX+5, 15, WIDTH-(initialX+5), currLineY)
                #Adds blocker to sprite group
                allSprites.add(blocker)
                lines.add(blocker)
            #Adds current layer list to list of all layers
            layers.append(currLayer)
                
        #Calculates the width and height of the player based on the size of the screen and pyramid
        playerW = int(WIDTH / (baseNo*4))
        playerH = int(HEIGHT / (baseNo*2.5))
        bound = int((WIDTH/2) - ((baseNo/2) * blockSpacing))
        #Chooses a random start position for the player along the first layer of the pyramid
        startx = randint(bound, WIDTH-bound)
        #Creates the player sprite
        global player
        player = Player(startx,HEIGHT,HEIGHT,playerW,playerH)
        #Adds the player to allSprites group
        allSprites.add(player)

        #Game Loop
        #Plays and loops background music
        pygame.mixer.music.play(loops=-1)
        #Gets the initial time of the game starting
        initTime = pygame.time.get_ticks()/1000
        #The game starts
        while running:
            #keeping the game running at the right speed
            clock.tick(fps)
            for event in pygame.event.get():
                #checks event for closing the window
                if event.type == pygame.QUIT:
                    print('User has closed the game')
                    #Disconnects the client from the server
                    clientInstance.disconnectReq()
                    #Closes the application
                    quit()
            #Updating sprites
            allSprites.update()            
            pygame.time.delay(10)
            #Screen rendering
            screen.fill(BLACK)
            #Adds the backround image to the background
            screen.blit(background, backgroundRect)
            #Drawing sprites on the screen
            allSprites.draw(screen)
            #Drawing timer on the screen
            currTime = pygame.time.get_ticks()/1000
            time = math.floor(currTime - initTime)
            mins = time // 60
            seconds = time % 60
            if mins < 1:
                mins = '00'
            elif mins < 10:
                mins = '0' + str(mins)
            if seconds < 10:
                seconds = '0' + str(seconds)
            drawText(screen,f'Time: {mins}:{seconds}',36,WIDTH/2,10)
            #Drawing current score on the screen
            drawText(screen,f'Current score: {score}' ,36,WIDTH/2,40)
            #Drawing logged in user on the screen
            drawText(screen,f'Playing as: {clientInstance.getName()}',20,WIDTH/10,10)
            #Drawing the player's current layer on the screen
            drawText(screen,f'Current Layer: {player.currentLayer}',20,WIDTH*0.9,10)
            #Displaying all resulting computations on the screen for the frame
            pygame.display.flip()

        #Updates the game window at the end of the game based on the outcome of the game
        endGameWindow.update(won, score, time, baseNo)
        #Closes the game
        pygame.quit()
    except pygame.error as err:
        #If a game error occurs, the error is outputted, the client disconnects and the application closes
        print(err)
        clientInstance.disconnectReq()
        quit()

#Procedure for drawing text on the screen
def drawText(surf,text,size, x, y, family='arial'):
    #Getting font family
    fontName = pygame.font.match_font(family)
    #Creates a font object
    font = pygame.font.Font(fontName,size)
    #Renders the text surface
    textSurface = font.render(text,True,BLACK)
    textRect = textSurface.get_rect() #Gets the rectangle for the text
    textRect.midtop = (x,y) #Puta x,y at the midtop of the rect 
    surf.blit(textSurface, textRect)       
