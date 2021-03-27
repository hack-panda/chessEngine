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
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        # coordinates where the enpassant square capture is possible
        self.enpassantPossible = ()
        # castling rights
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    """ Takes Move as a parameter and executes it.
    Will not work for en-passant,pawn promition and castling"""

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap the chance of player
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+'Q'

        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capturing the pawn

        # update enpassant possible variable
        # only on two square pawn advances
        if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow+move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

        # make castle move
        if move.isCastleMove:
            if move.endCol-move.startCol == 2:  # king side castle
                # move the rook
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"  # erase the rook
            else:  # queen side castle
                # move the rook
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"  # erase the rook

        # update castling rights
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    """
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo enpassant move
            if move.isEnpassantMove:
                # leave the landing square blank
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightLog.pop()  # get rid of new castle rights
            # set the current castle rights
            newCastleRights = self.castleRightLog[-1]
            self.currentCastlingRight = CastleRights(
                newCastleRights.wks, newCastleRights.bks, newCastleRights.wqs, newCastleRights.bqs)
            # undo castle move
            if move.isCastleMove:
                if move.endCol-move.startCol == 2:  # king castle
                    self.board[move.endRow][move.endCol +
                                            1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:  # queen castle
                    self.board[move.endRow][move.endCol -
                                            2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

    """
    Update castle rights
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False

    """
    All moves considering checks
    """

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastlingRight = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                         self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1)generate all possible moves
        moves = self.getAllPossibleMoves()
        # get castle moves
        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 2)for each move ,make the move
        # when removing from a list go backward because indexes shrink after removing
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3)generate all opponent's moves
            # 4)see if any opponent attacks the king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5)if they do then it's not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # Either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:  # update to original if we undo move
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastlingRight
        return moves

    """
    Determine if the current player is in check
    """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determine if the enemy can attack the square r,c
    """

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

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
            if self.board[r-1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                # 2 square pawn advance
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0:  # captures to left
                if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7:  # captures to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else:  # black pawns
            if self.board[r+1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                # 2 square pawn advance
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0:  # captures to the right
                if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7:  # captures to the left
                if self.board[r+1][c+1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

        # add pawn promotions later

    """
    Get all the rook moves for a rook at (row,column)
    """

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up left down right
        # another way of writing an if statement
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:  # iterate through directions
            for i in range(1, 8):  # can move maximum 7 blocks
                endRow = r+d[0]*i  # change rows
                endCol = c+d[1]*i  # change columns

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # not an enemy piece
                        break
                else:  # off the board
                    break

    """
    Get all the knight moves for a Knight at (row,column)
    """

    def getKnightMoves(self, r, c, moves):
        # all possible moves of knight
        knightMoves = ((2, 1), (2, -1), (-2, 1), (-2, -1),
                       (1, 2), (1, -2), (-1, 2), (-1, -2))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in knightMoves:
            endRow = r+d[0]
            endCol = c+d[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # empty or enemy piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the Bishop moves for a Bishop at (row,column)
    """

    def getBishopMoves(self, r, c, moves):
        # upleft upright downleft downright
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        # another way of writing an if statement
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:  # iterate through directions
            for i in range(1, 8):  # can move maximum of 7 squares
                endRow = r+d[0]*i  # change rows
                endCol = c+d[1]*i  # change columns

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # not an enemy piece
                        break
                else:  # off the board
                    break

    """
    Get all the Queen moves for a Queen at (row,column)
    """

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    """
    Get all the King moves for a King at (row,column)
    """

    def getKingMoves(self, r, c, moves):
        # all possible moves of king
        kingMoves = ((1, 1), (-1, 1), (1, -1), (-1, -1),
                     (0, 1), (1, 0), (-1, 0), (0, -1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r+kingMoves[i][0]
            endCol = c+kingMoves[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # empty or enemy piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """ get CastleMoves """

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):  # cant castle if in check
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if (not self.squareUnderAttack(r, c+1)) and (not self.squareUnderAttack(r, c+2)):
                moves.append(
                    Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if (not self.squareUnderAttack(r, c-1)) and (not self.squareUnderAttack(r, c-2)):
                moves.append(
                    Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # map keys to values
    # for rows to ranks and columns to files and vice versa

    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle move
        self.isCastleMove = isCastleMove
        # pawn promotion
        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (
            self.pieceMoved == 'bp' and self.endRow == 7))
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
