import GameSetup as gs
import itDeepAStar as ia
MENU_F = "menuText.txt"
OPTIONS_F = "optionsText.txt"
HELP_F = "helpText.txt"

def takeCommand(options):
    st = input()
    while not st in options:
        print("ERROR: Invalid input. Try again.")
        st = input()
    return st

def info(i):
    print(i)
    print("Back to menu? y/n")
    inp = takeCommand(["y", "n"])
    if inp=="y":
        startMenu(False)
    else:
        return

def startMenu(isIt):
    board = gs.initDefaultBoard()
    h_inds = [6, 8]
    h_ws = [4, 0.5]
    itDeep = isIt
    pf = ia.PRINT_FREQ
    hw = ia.HEURISTIC_WEIGHT
    cw = ia.COST_WEIGHT
    f = open(MENU_F, "r")
    fo = open(OPTIONS_F, "r")
    fh = open(HELP_F, "r")
    for line in f:
        print(line)
    select = takeCommand(["r", "e", "l", "h", "q"])
    if select=="r":
        ia.runCheck(board, h_inds, h_ws, pf, hw, cw, itDeep)
    #elif select=="o":
        #for lineo in fo:
            #print(lineo)
        #modify = takeCommand(["h", "hw", "c", "m"])
        #if modify == "m":
            #startMenu()
        #elif modify == "h":
            #temp = 0
            #fheur = open("HeuristicDescriptions.txt", r)
            #for lf in fheur:
                #print("(", temp, ") ", lf)
            #print("Select a heuristic you'd like to use, or enter -1 to exit")
    elif select=="e":
        startMenu(True)
    elif select=="l":
        fheur = open("HeuristicDescriptions.txt", "r")
        temp = 0
        for lf in fheur:
                print("(", temp, ") ", lf)
                temp += 1
        print("Return to start menu? y/n")
        inp = takeCommand(["y", "n"])
        if inp=="y":
            startMenu(isIt)
        else:
            return
    elif select == "q":
        return
    else:
        for lineh in fh:
            print(lineh)
        inp = takeCommand(["y", "n"])
        if inp=="y":
            startMenu(isIt)
        else:
            return
        
if __name__ == "__main__":
    startMenu(False)
        
