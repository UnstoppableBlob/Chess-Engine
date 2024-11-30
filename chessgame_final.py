import pygame
import chess
import chess.engine
import sys
import os

pygame.init()


SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
WHITE = (240, 240, 240)
BLACK = (34, 150, 34)
GREEN = (34, 150, 34)
SELECTED_COLOR = (0, 0, 255, 128)
HIGHLIGHT_COLOR = (255, 215, 0, 128)  


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

def draw_board():
  
    for row in range(8):
        for col in range(8):
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, BLACK, rect)

            
            pygame.draw.rect(screen, GREEN, rect, 1)  

def draw_pieces():
   
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_image = PIECES[piece.symbol()]
                piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(piece_image, piece_rect)

def highlight_legal_moves(legal_moves):
  
    for move in legal_moves:
        dest_row, dest_col = divmod(move.to_square, 8)
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, 
                           (dest_col * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - dest_row) * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

def handle_mouse_click():
    
    x, y = pygame.mouse.get_pos()
    col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
    return chess.square(col, 7 - row)

def get_legal_moves(square):

    legal_moves = []
    for move in board.legal_moves:
        if move.from_square == square:
            legal_moves.append(move)
    return legal_moves

def ai_move():
 
    result = engine.play(board, chess.engine.Limit(time=1.0)) 
    board.push(result.move)
    print("Bot move:", result.move)

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
def main():
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
            
            highlight_legal_moves(legal_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
                clicked_square = handle_mouse_click()

                if selected_square:
                 
                    if clicked_square == selected_square:
                        selected_square = None
                        legal_moves = []
                    else:
                        move_found = False
                        for move in legal_moves:
                            if move.to_square == clicked_square:
                                board.push(move)
                                selected_square = None
                                legal_moves = []
                                ai_move()  
                                move_found = True
                                break
                        if not move_found:
                            selected_square = None
                            legal_moves = []
                else:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                        legal_moves = get_legal_moves(clicked_square)

        pygame.display.update()

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
