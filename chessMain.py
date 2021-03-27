""" This is our main driver file. Responsible for handling userinput 
and displaying the current game state. """

import pygame as p
import chessEngine


WIDTH = HEIGHT = 768
DIMENSION = 8  # chess board dimension 8X8
SQ_SIZE = HEIGHT//DIMENSION  # square size
MAX_FPS = 15  # for animation
IMAGES = {}

""" 
Initialize a global dictionary of images.
Will be called only once in main.
"""


def loadImages():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wp",
              "bR", "bN", "bB", "bQ", "bK", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Now we can access an image from the dictionary IMAGES


"""
Main driver from our code
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    # game state object
    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when we animate a move
    loadImages()

    run = True
    # no square selected initially(keeps track of last square selected)
    sqSelected = ()
    # keep track of player clicks e.g.(two tuples=>[(6,5),(5,5)])
    playerClicks = []
    gameOver = False

    while run:
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):  # user clicked on same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        # append for both first and second clicks
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:  # after 2nd click
                        move = chessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                print(move.getChessNotation())
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                                animate = True
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z  is pressed
                    gs.undoMove()
                    animate = False
                    moveMade = True
                if e.key == p.K_r:  # reset the board when r is pressed
                    gameOver = False
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "BLACK WINS BY CHECKMATE")
            else:
                drawText(screen, "WHITE WINS BY CHECKMATE")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")

        clock.tick(MAX_FPS)
        p.display.flip()


""" Responsible for all the graphics within a current game state """


def drawGameState(screen, gs, validMoves, sqSelected):
    # order of the two methods matter
    drawBoard(screen)  # draws sqare on board
    highlightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces


""" Highlights the square selected and the moves for the piece selected """


def highlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # square selected piece can be moved
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight sq selected
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(140)  # transparancy value 0->transparent 255->opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight move from that square
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


""" Draw the squares on board.
The top left square is always light 
"""


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


""" Draw th pieces on the board using current gs.board """


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


""" Animating the move """


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow-move.startRow
    dC = move.endCol-move.startCol
    framesPerSquare = 10  # frames to move one square of an animation
    frameCount = (abs(dR)+abs(dC))*framesPerSquare

    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount,
                move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow+move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,
                           move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 50, False, False)
    textObject = font.render(text, 0, p.Color('red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2-textObject.get_width()/2, HEIGHT/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("darkblue"))
    screen.blit(textObject, textLocation.move(3, 3))


if __name__ == "__main__":
    main()
