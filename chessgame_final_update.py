import pygame
import chess
import chess.engine
import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
import time

pygame.init()


SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
WHITE = (240, 240, 240)
BLACK = (34, 150, 34)
GREEN = (34, 150, 34)
SELECTED_COLOR = (0, 0, 255, 128)
HIGHLIGHT_COLOR = (255, 215, 0, 128)
UNDO_BUTTON_COLOR = (200, 50, 50)
UNDO_BUTTON_HOVER_COLOR = (255, 100, 100)
UNDO_BUTTON_TEXT_COLOR = (255, 255, 255)
UNDO_BUTTON_RECT = pygame.Rect(BOARD_SIZE // 2 - 50, BOARD_SIZE + 10, 100, 40)


PIECES = {}
PIECE_FILES = {
    'K': 'wK.png', 'Q': 'wQ.png', 'R': 'wR.png', 'B': 'wB.png', 'N': 'wN.png', 'P': 'wP.png',
    'k': 'bK.png', 'q': 'bQ.png', 'r': 'bR.png', 'b': 'bB.png', 'n': 'bN.png', 'p': 'bP.png'
}

for piece, filename in PIECE_FILES.items():
    try:
        original_image = pygame.image.load(os.path.join('images', filename))
        PIECES[piece] = pygame.transform.smoothscale(original_image, (SQUARE_SIZE, SQUARE_SIZE))
    except pygame.error as e:
        print(f"Failed to load image for {piece}: {e}")
        sys.exit()

screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Chess Game")

board = chess.Board()

stockfish_path = "./chess_engine/stockfish_15_x64_bmi2.exe"
try:
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
except FileNotFoundError:
    print("Stockfish executable not found. Ensure the path is correct.")
    sys.exit()


def check_for_checkmate():
    if board.is_checkmate():
        winner = "White" if not board.turn else "Black"
        print(f"Checkmate! {winner} wins!")
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")


def draw_board():
    for row in range(8):
        for col in range(8):
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, BLACK, rect)


def draw_pieces(exclude_square=None):
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            if square == exclude_square:
                continue  
            piece = board.piece_at(square)
            if piece:
                piece_image = PIECES[piece.symbol()]
                piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(piece_image, piece_rect)


def animate_move(piece, start_square, end_square):
    start_col, start_row = chess.square_file(start_square), chess.square_rank(start_square)
    end_col, end_row = chess.square_file(end_square), chess.square_rank(end_square)
    start_x, start_y = start_col * SQUARE_SIZE, (7 - start_row) * SQUARE_SIZE
    end_x, end_y = end_col * SQUARE_SIZE, (7 - end_row) * SQUARE_SIZE

    frames = 10  
    delay = 0.01  

    for i in range(frames + 1):
        alpha = i / frames
        current_x = start_x + (end_x - start_x) * alpha
        current_y = start_y + (end_y - start_y) * alpha

        screen.fill(WHITE)
        draw_board()
        draw_pieces(exclude_square=start_square) 

        piece_image = PIECES[piece.symbol()]
        piece_rect = piece_image.get_rect(center=(current_x + SQUARE_SIZE // 2, current_y + SQUARE_SIZE // 2))
        screen.blit(piece_image, piece_rect)

        pygame.display.update()
        time.sleep(delay)




def handle_mouse_click():
    x, y = pygame.mouse.get_pos()
    col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
    return chess.square(col, 7 - row)


def get_legal_moves(square):
    return [move for move in board.legal_moves if move.from_square == square]


def make_player_move(move):
    piece = board.piece_at(move.from_square)
    if piece:
        animate_move(piece, move.from_square, move.to_square)
    board.push(move)
    check_for_checkmate()


def make_ai_move():
    result = engine.play(board, chess.engine.Limit(time=1.0))
    piece = board.piece_at(result.move.from_square)
    if piece:
        animate_move(piece, result.move.from_square, result.move.to_square)
    board.push(result.move)
    check_for_checkmate()


def draw_undo_button():
    mouse_pos = pygame.mouse.get_pos()
    color = UNDO_BUTTON_HOVER_COLOR if UNDO_BUTTON_RECT.collidepoint(mouse_pos) else UNDO_BUTTON_COLOR
    pygame.draw.rect(screen, color, UNDO_BUTTON_RECT, border_radius=5)

    font = pygame.font.Font(None, 24)
    text_surface = font.render("Undo", True, UNDO_BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=UNDO_BUTTON_RECT.center)
    screen.blit(text_surface, text_rect)


def undo_move():
    if len(board.move_stack) > 0:  
        board.pop() 
        if len(board.move_stack) > 0: 
            board.pop()



def set_difficulty_gui():

    font = pygame.font.Font(None, 36)
    difficulty_level = "1 - 20"
    input_box_width = 200  
    input_box_height = 40  
    
    input_box_x = (BOARD_SIZE - input_box_width) // 2
    input_box_y = (BOARD_SIZE - input_box_height) // 2
    input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height) 

    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = str(difficulty_level)

    
    while True:
        screen.fill(WHITE)  
        draw_board()
        draw_pieces()

        
        text_color = (0, 0, 0) 
        txt_surface = font.render(text, True, text_color)
        width = max(150, txt_surface.get_width())
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        
     
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        try:
                            difficulty_level = int(text)
                            if 0 <= difficulty_level <= 20:
                                engine.configure({"Skill Level": difficulty_level})
                                print(f"Bot difficulty set to {difficulty_level}")
                                return difficulty_level
                            else:
                                text = "0-20 only"
                        except ValueError:
                            text = "Invalid input"
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

difficulty_level = set_difficulty_gui()  



selected_square = None
legal_moves = []

running = True
while running:
    screen.fill(WHITE)
    draw_board()
    draw_pieces()

    if selected_square:
        selected_rect = pygame.Rect((selected_square % 8) * SQUARE_SIZE, (7 - selected_square // 8) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, SELECTED_COLOR, selected_rect, 3)

        for move in legal_moves:
            dest_row, dest_col = divmod(move.to_square, 8)
            pygame.draw.circle(screen, HIGHLIGHT_COLOR, 
                               (dest_col * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - dest_row) * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if UNDO_BUTTON_RECT.collidepoint(event.pos):
                undo_move()
            else:
                clicked_square = handle_mouse_click()
                screen.fill(WHITE)
                draw_board()
                draw_pieces()
                if selected_square:
                    if clicked_square == selected_square:
                        selected_square = None
                        legal_moves = []
                    else:
                        for move in legal_moves:
                            if move.to_square == clicked_square:
                                make_player_move(move)
                                make_ai_move()
                                selected_square = None
                                legal_moves = []
                                break
                        else:
                            selected_square = None
                            legal_moves = []
                else:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                        legal_moves = get_legal_moves(clicked_square)
    draw_undo_button()
    pygame.display.update()

engine.quit()
pygame.quit()
sys.exit()
