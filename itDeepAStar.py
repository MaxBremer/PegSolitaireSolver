import GameSetup as gs
import heapq as hq
import copy
import timeit
import random
import math
#Set to 0 to print every board checked.
#Otherwise, prints after every PRINT_FREQ boards
PRINT_FREQ = 1000

HEURISTIC_WEIGHT = 1.0
COST_WEIGHT = 1.0
AVG_HEURISTICS = False

COUNT = 10000
CUTOFF = 10000
CUTOFF_ENABLED = False

EXPERIMENT_SHUTDOWN_TIME = 600.0

ITERATIVE_DEEPENING_ENABLED = False


class DataPack:
    def __init__(self, BE, ML, HV):
        self.BE = BE
        self.ML = ML
        self.HV = HV
    def __lt__(self, other):
        return (self.HV < other.HV)
    def __gt__(self, other):
        return (self.HV > other.HV)
        
#HEURISTICS
#Heuristics must accept only and exactly the board as a parameter.
#Heuristics must always be a property we want to minimize.
#Note, NumPegs is not functional even as a simple heuristic because all moves
#reduce the number of pegs in the same way.

#This calculates the ratio of pegs in the center 3x3 to the edge zones.
#An optimized board has a higher ratio, we want more pegs in the center.
#Based on the idea that we wish to move as many pegs as possible away from
#limiting edges and inwards towards the middle.
def zoneRatio(board):
    total = gs.numPegs(board)
    center = 0
    for i in range(2,5):
        for j in range(2,5):
            if board[i][j] == 'o':
                center += 1
    edge = total - center
    if center < 1:
        return edge/total
    else:
        return (edge/center)

#A sort of variant on the above idea
def avgZonePegCount(board):
    total = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if not (i in range(2,5) or j in range(2,5)):
                if board[i][j] == "o":
                    total += 1
    return total/4

#Let us define a "bad peg" as a peg that fulfills one of the following conditions: (inclusive or)
#   It has no neighbors that are also pegs (NN)
#   It is adjacent to an x (edge)
#   It is completely surrounded by pegs (sur)
#Each of these possibilities is weighted differently.
def badPegCount(board):
    NN = 0
    edge = 0
    sur = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 'o':
                sqs = gs.adjacentSquares(i,j,board)
                n = 0
                for s in sqs:
                    if board[s[0]][s[1]] == 'o':
                        n += 1
                    if board[s[0]][s[1]] == 'x':
                        edge += 1
                if i in [0, len(board)-1] or j in [0, len(board[0])-1]:
                    edge += 1
                if n == 0:
                    NN += 1
                if n == len(sqs):
                    sur += 1  
                
    return NN + edge + sur
                    
#counts empty squares adjacent to a peg, and then returns the negative.
#The idea is we want to maximize adjacent pegs, and thus minimize empty squares
#adjacent to pegs
def adjEmptys(board):
    AECount = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == '.':
                adjs = gs.adjacentSquares(i,j,board)
                for a in adjs:
                    if board[a[0]][a[1]] == 'o':
                        AECount += 1
                        break
    return AECount

#The following heuristic is based on a somewhat circular idea that we weigh boards based on the average number of
#moves there are available after the moves that exist.
def innerMoves(board):
    moves = gs.getMoves(board)
    if len(moves)==0:
        return math.inf
    total = 0
    for m in moves:
        gs.doMove(board, m)
        total += len(gs.getMoves(board))
        gs.undoMove(board, m)
    return -(total/len(moves))

#A faster alternative to the above, judges based on number of moves available after a random move within that set of moves.
def innerMoveArbitrary(board):
    moves = gs.getMoves(board)
    if len(moves)==0:
        if gs.numPegs(board) <= 1:
            return 0
        else:
            return math.inf
    move = random.choice(moves)
    gs.doMove(board, move)
    total = len(gs.getMoves(board))
    gs.undoMove(board, move)
    return -total

#Finds the largest manhattan distance between any two pegs on the board. Based on the idea that we want to minimize
#overall distance between pegs, keeping them grouped closely together.
def largestManhattanDistance(board):
    pegs = gs.getPegs(board)
    largest = 0
    for p in range(len(pegs)-1):
        for p2 in range(p, len(pegs)):
            largest = max(gs.mDist(pegs[p][0], pegs[p][1], pegs[p2][0], pegs[p2][1]), largest)
    return largest

#Corner pegs are by far the worst ones to attempt to solve out. This heuristic simply counts pegs in corners.
def cornerHate(board):
    numCorners = 0
    corns = [0, 2, 6, 20, 30, 32, 12, 26]
    BL = gs.boardToBL(board)
    for c in corns:
        if BL[c] == 1:
            numCorners += 1
    return numCorners

#This scary acronym stands for "Peg Count Lowest Non-Zero Zone". Based on the idea that optimal solutions to this puzzle
#empty one edge "zone" at a time, this heuristic prefers paths that continue to empty the non-empty zone with the
#lowest peg count.
def PCLNZZ(board):
    BL = gs.boardToBL(board)
    zoneIndices = [range(6),[6,7,13,14,20,21],[11,12,18,19,25,26],range(27,33)]
    zoneCountMin = math.inf
    zoneCountMult = 4
    for zI in zoneIndices:
        zoneTotal = 0
        for i in zI:
            zoneTotal += BL[i]
        if zoneTotal == 0:
            zoneCountMult -= 1
        elif (zoneTotal < zoneCountMin):
            zoneCountMin = zoneTotal
    if zoneCountMult == 0:
        #print("0 in all zones")
        return 0
    else:
        return (zoneCountMult * 6) + zoneCountMin

heurs = [zoneRatio, avgZonePegCount, badPegCount, adjEmptys, innerMoves, innerMoveArbitrary, largestManhattanDistance, cornerHate, PCLNZZ]
        
#CURRENT BOARD VALUE is simply represented by the count of 'o' in board, which accurately
#represents the number of moves we've made so far since each move must remove
#a peg.
def astar(board, heuristic, weights, start):
    if not len(heuristic)==len(weights):
        print("ERROR: Enter a single weight for each heuristic")
        return None
    q = []
    moveRoute = []
    totalPegs = gs.numPegs(board)
    if not heuristic:
        print("ERROR: Enter at least 1 heuristic")
        return None
    if gs.isSoln(board):
        return moveRoute
    firstHV = 0
    for heu in range(len(heuristic)):
        firstHV += heuristic[heu](board) * weights[heu]
        
    entry = DataPack(gs.boardToBE(board),moveRoute,firstHV)
    
    depthBound = firstHV
    hq.heappush(q, entry)
    f = PRINT_FREQ
    c = COUNT

    biggerHVs = []
    
    while q:
        n = hq.heappop(q)
        #print("Popped item heuristic value: ", n.HV)
        #if q:
            #n2 = hq.heappop(q)
            #print("The next items heuristic value: ", n2.HV)
            #hq.heappush(q, n2)
        curBoard = gs.BEtoBoard(n.BE)
        
        if f == 0:
            print("Check-in board state:")
            gs.printBoard(curBoard)
            print("Checked boards HV: ", n.HV)
            cur = timeit.default_timer() - start
            print("Time elapsed so far: ", cur)
            if ITERATIVE_DEEPENING_ENABLED:
                print("CURRENT DEPTH BOUND: ", depthBound)
            f = PRINT_FREQ
        else:
            f = f - 1
        if CUTOFF_ENABLED:
            if c == 0:
                temp = []
                print("CUTOFF OCCURRING: Cutting off ", CUTOFF, " entries every ", COUNT, " expansions.")
                for i in range(CUTOFF):
                    if q:
                        hq.heappush(temp, hq.heappop(q))
                q = temp
                print("ENTRIES REMAINING AFTER CUTOFF: ", len(q))
                c = COUNT
            else:
                c = c - 1
        if gs.isSoln(curBoard):
            return n.ML
        
        moves = gs.smartGetMoves(curBoard)
        
        for m in moves:
            newRoute = copy.deepcopy(n.ML)
            gs.doMove(curBoard, m, newRoute)
            HV = COST_WEIGHT * (totalPegs - gs.numPegs(curBoard))
            hs = 0
            for heur in range(len(heuristic)):
                hs += heuristic[heur](curBoard) * weights[heur]
            HV += HEURISTIC_WEIGHT * (hs)#/len(heuristic))
            if ITERATIVE_DEEPENING_ENABLED:
                if HV <= depthBound:
                    newEntry = DataPack(gs.boardToBE(curBoard), newRoute, HV)
                    hq.heappush(q, newEntry)
                else:
                    biggerHVs.append(HV)
            else:
                newEntry = DataPack(gs.boardToBE(curBoard), newRoute, HV)
                hq.heappush(q, newEntry)
            #undo move done on curBoard
            gs.undoMove(curBoard, m)
        if ((not q) and (len(biggerHVs) > 0)) and ITERATIVE_DEEPENING_ENABLED:
            depthBound = min(biggerHVs)
            biggerHVs = []
            hq.heappush(q, entry)
    print("FAILURE: NO SOLUTION FOUND.")
    return None

if __name__ == "__main__":
    board = gs.initDefaultBoard()
    start = timeit.default_timer()
    winner = astar(board, [PCLNZZ, largestManhattanDistance], [0.5, 4], start)
    stop = timeit.default_timer()
    time = stop - start
    print("The winning route is: ", winner)
    print("This method took ", time, " seconds.")
    tboard = gs.initDefaultBoard()
    print("THE FOLLOWING BOARD SEQUENCE SHOWS THE WINNING MOVES:")
    gs.printBoard(tboard)
    for m in winner:
        gs.doMove(tboard, m)
        gs.printBoard(tboard)
    print("END")


def runCheck(board, heurInds, hWeights, pf, hw, cw, itDeep):
    print("BEGINNING GAME")
    Lheurs = []
    for h in heurInds:
        Lheurs.append(heurs[h])
    start = timeit.default_timer()
    PRINT_FREQ = pf
    HEURISTIC_WEIGHT = hw
    COST_WEIGHT = cw
    ITERATIVE_DEEPENING_ENABLED = itDeep
    winningMoves = astar(board, Lheurs, hWeights, start)
    time = timeit.default_timer() - start
    print("We won, Mr Stark.")
    print("The winning route is: ", winningMoves)
    print("This method took ", time, " seconds.")
    tboard = gs.initDefaultBoard()
    print("THE FOLLOWING BOARD SEQUENCE SHOWS THE WINNING MOVES:")
    gs.printBoard(tboard)
    for m in winningMoves:
        gs.doMove(tboard, m)
        gs.printBoard(tboard)
    print("END")
    return winningMoves
