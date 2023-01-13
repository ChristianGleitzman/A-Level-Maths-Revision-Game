from menus import menuMain
from clientNetworking import TravClient

if __name__ == "__main__":
    #Creates instance of client class
    clientInstance = TravClient()
    #Calls the main menus subroutine
    menuMain(clientInstance)
    #After all windows are closed, the user is disconnected from the server
    clientInstance.disconnectReq()
    
    
    