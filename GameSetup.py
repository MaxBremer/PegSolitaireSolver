import copy
#Peg Solitaire basic setup

#Board is stored in three forms: a 2d list that accurately represents the board,
#a 1d list that enumerates the states of the pegs that are usable, and
#an integer that represents that 1d list.
#1d for use in algorithm, int for storage/queue of board states, 2d for final input/output
#1d = BL (for board list), 2d = board, int = BE (for board encoding)
aSyms = []
def initDefaultBoard():
    BL = [1] * 33
    BL[16] = 0
    board = BLtoBoard(BL)
    return board

def initEasyBoard():
    BL = [0] * 33
    BL[1] = 1
    BL[4] = 1
    BL[16] = 1
    board = BLtoBoard(BL)
    return board

def BEtoBL(BE):
    BL = [0] * 33
    for x in range(len(BL)):
        if (BE %(2**(x + 1))) >= (2**x):
            BL[x] = 1
    return BL

def BLtoBE(BL):
    BE = 0
    for x in range(len(BL)):
        if BL[x] == 1:
            BE += 2**x
    return BE

def BLtoBoard(BL):
    board = []
    index = 0
    for i in range(7):
        row = []
        for j in range(7):
            if (i in range(2) or i in range(5,7)) and (j in range(2) or j in range(5,7)):
                row.append('x')
            else:
                row.append(digitToChar(BL[index]))
                index += 1
                
        board.append(row)
    return board

def boardToBL(board):
    BL = []
    for i in range(7):
        for j in range(7):
            if not ((i in range(2) or i in range(5,7)) and (j in range(2) or j in range(5,7))):
                BL.append(charToDigit(board[i][j]))
    return BL

def boardToBE(board):
    BL = boardToBL(board)
    return BLtoBE(BL)

def BEtoBoard(BE):
    BL = BEtoBL(BE)
    return BLtoBoard(BL)

def digitToChar(d):
    if d == 1:
        return 'o'
    else:
        return '.'

def charToDigit(c):
    if c == 'o':
        return 1
    else:
        return 0

#Simple helper function finds manhattan distance between points.
def mDist(x1,y1,x2,y2):
    return abs(x1-x2) + abs(y1-y2)

def printBoard(board):
    for r in board:
        temp = "| "
        for x in r:
            temp = temp + x + " | "
        print(temp)
    print("_____________________")

def adjacentSquares(x,y,board):
    adjs = []
    if x > 0:
        adjs.append([x-1,y])
    if x < len(board)-1:
        adjs.append([x+1,y])
    if y > 0:
        adjs.append([x,y-1])
    if y < len(board[0])-1:
        adjs.append([x,y+1])
    return adjs
    
#Given a board and a point on it, finds possible moves that jump the peg at that spot.
#Move storage format: [startx, starty, endx, endy, subjectx, subjecty]
def possibleMovesAtPos(x,y,board):
    moves = []
    width = len(board)-1
    height = len(board[0])-1
    
    if board[x][y] == 'o':
        if 0 < x < width:
            if board[x-1][y] == '.' and board[x+1][y] == 'o':
                moves.append([x+1, y, x-1, y, x, y])
            elif board[x-1][y] == 'o' and board[x+1][y] == '.':
                moves.append([x-1, y, x+1, y, x, y])
        if 0 < y < height:
            if board[x][y-1] == '.' and board[x][y+1] == 'o':
                moves.append([x, y+1, x, y-1, x, y])
            elif board[x][y-1] == 'o' and board[x][y+1] == '.':
                moves.append([x, y-1, x, y+1, x, y])
    return moves

#Given a board, finds all possible moves for that board.
def getMoves(board):
    viableMoves = []
    for row in range(len(board)):
        for entry in range(7):
            moves = possibleMovesAtPos(row,entry,board)
            if len(moves) > 0:
                for m in moves:
                    viableMoves.append(m)
            
    return viableMoves

def doMove(b, move, moveList = 1):
    b[move[0]][move[1]] = '.'
    b[move[2]][move[3]] = 'o'
    b[move[4]][move[5]] = '.'
    if not isinstance(moveList, int):
        moveList.append(move)

def undoMove(b, move, moveList = None):
    b[move[0]][move[1]] = 'o'
    b[move[2]][move[3]] = '.'
    b[move[4]][move[5]] = 'o'
    if moveList:
        x = moveList.pop()

def doMoveList(b, moveList):
    for m in moveList:
        doMove(b,m,[])

def numPegs(board):
    count = 0
    for row in board:
        count += row.count('o')
    return count

def getPegs(board):
    pegLocs = []
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 'o':
                pegLocs.append([row, col])
    return pegLocs

def isSoln(board):
    return (numPegs(board) == 1)

def rotateBoard(mat): 
      
    # Consider all squares one by one 
    for x in range(0, int(7/2)): 
          
        # Consider elements in group    
        # of 4 in current square 
        for y in range(x, 7-x-1): 
              
            # store current cell in temp variable 
            temp = mat[x][y] 
  
            # move values from right to top 
            mat[x][y] = mat[y][7-1-x] 
  
            # move values from bottom to right 
            mat[y][7-1-x] = mat[7-1-x][7-1-y] 
  
            # move values from left to bottom 
            mat[7-1-x][7-1-y] = mat[7-1-y][x] 
  
            # assign temp to left 
            mat[7-1-y][x] = temp


def symmetricBoards(board):
    returner = []
    boardBE = boardToBE(board)
    boardR = BEtoBoard(boardBE)
    for row in range(len(boardR)):
        boardR[row].reverse()
    returner.append(boardToBE(boardR))
    boardR.reverse()
    returner.append(boardToBE(boardR))
    boardR2 = BEtoBoard(boardBE)
    boardR2.reverse()
    returner.append(boardToBE(boardR2))
    b1rot = BEtoBoard(boardBE)
    rotateBoard(b1rot)
    returner.append(boardToBE(b1rot))
    rotateBoard(b1rot)
    rotateBoard(b1rot)
    returner.append(boardToBE(b1rot))
    return returner

def printEBoards(boards):
    for b in boards:
        printBoard(BEtoBoard(b))

def removeSym(board, moves):
    syms = []
    removals = []
    for m in moves:
        doMove(board, m)
        tsyms = symmetricBoards(board)
        BE = boardToBE(board)
        for s in tsyms:
            if (s in syms):# or s in aSyms):
                if not m in removals:
                    removals.append(m)
        for s in tsyms:
            if not s in syms:
                syms.append(s)
            #if not s in aSyms:
                #aSyms.append(s)
        syms.append(BE)
        #aSyms.append(BE)
        undoMove(board, m)
    for r in removals:
        moves.remove(r)

def removeDead(board, moves):
    removals = []
    for m in moves:
        doMove(board, m)
        newMoves = getMoves(board)
        if (len(newMoves)<1) and (numPegs(board) > 1):
            removals.append(m)
        undoMove(board, m)
    for r in removals:
        moves.remove(r)

def smartGetMoves(board):
    moves = getMoves(board)
    if moves:
        removeSym(board, moves)
        #removeDead(board, moves)
    return moves

def testConversions():
    board = initDefaultBoard()
    print("The default board is as follows:")
    printBoard(board)
    print("All possible moves at default board:")
    print(getMoves(board))
    
    
    
    
