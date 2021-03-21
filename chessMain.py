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
    loadImages()

    run = True
    # no square selected initially(keeps track of last square selected)
    sqSelected = ()
    # keep track of player clicks e.g.(two tuples=>[(6,5),(5,5)])
    playerClicks = []

    while run:
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        print(move.getChessNotation())
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z  is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


""" Responsible for all the graphics within a current game state """


def drawGameState(screen, gs):
    # order of the two methods matter
    drawBoard(screen)  # draws sqare on board
    drawPieces(screen, gs.board)  # draw pieces


""" Draw the squares on board.
The top left square is always light 
"""


def drawBoard(screen):
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


if __name__ == "__main__":
    main()
