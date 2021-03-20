""" Stores all the information about the current state of the game,
determines valid moves, keeps a move log. """


class GameState():
    def __init__(self):
        # board is a 8X8 2d list containing 2 characters
        # "xy" where x represents color and y represents type
        # y=>{K,Q,B,N,R,p}
        # "--" represents empty space with no keys
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves,
                              'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves
                              }
        self.whiteToMove = True
        self.moveLog = []

    """ Takes Move as a parameter and executes it.
    Will not work for en-passant,pawn promition and castling"""

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap the chance of player

    """
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    """ 
    All moves considering checks
    """

    def getValidMoves(self):
        # for now we will not consider for checks
        return self.getAllPossibleMoves()

    """
    All possible moves for a piece without considering checks 
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    peice = self.board[r][c][1]
                    self.moveFunctions[peice](r, c, moves)

        return moves

    """
    Get all the pawn moves for a pawn at (row,column)
    """

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawns
            if r > 0:
                if self.board[r-1][c] == "--":  # 1 square pawn advance
                    moves.append(Move((r, c), (r-1, c), self.board))
                    # 2 square pawn advance
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r, c), (r-2, c), self.board))

                if c-1 >= 0:  # captures to left
                    if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture
                        moves.append(Move((r, c), (r-1, c-1), self.board))

                if c+1 <= 7:  # captures to the right
                    if self.board[r-1][c+1][0] == 'b':
                        moves.append(Move((r, c), (r-1, c+1), self.board))
        else:  # black pawns
            if r < 7:
                if self.board[r+1][c] == "--":  # 1 square pawn advance
                    moves.append(Move((r, c), (r+1, c), self.board))
                    # 2 square pawn advance
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))

                if c-1 >= 0:  # captures to the right
                    if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
                        moves.append(Move((r, c), (r+1, c-1), self.board))

                if c+1 <= 7:  # captures to the left
                    if self.board[r+1][c+1][0] == 'w':  # enemy piece to capture
                        moves.append(Move((r, c), (r+1, c+1), self.board))

    """
    Get all the rook moves for a rook at (row,column)
    """

    def getRookMoves(self, r, c, moves):
        pass

    """
    Get all the knight moves for a Knight at (row,column)
    """

    def getKnightMoves(self, r, c, moves):
        pass
    """
    Get all the Bishop moves for a Bishop at (row,column)
    """

    def getBishopMoves(self, r, c, moves):
        pass
    """
    Get all the Queen moves for a Queen at (row,column)
    """

    def getQueenMoves(self, r, c, moves):
        pass
    """
    Get all the King moves for a King at (row,column)
    """

    def getKingMoves(self, r, c, moves):
        pass


class Move():
    # map keys to values
    # for rows to ranks and columns to files and vice versa

    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    """
    Overriding the equals method 
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
