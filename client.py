import pygame
import socket
import pickle
import threading

class Chess:
    def __init__(self, host='127.0.0.1', port=12345) -> None:
        pygame.init()
        self.width = 800
        self.height = 800

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess")
        
        self.background_color = (31, 36, 23)  # Màu đen

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.background_color)

        self.game_surface = self.surface.subsurface(pygame.Rect(80, 80, 640, 640))

        self.is_white = None
        self.can_move = False
        self.curr_co = ''
        self.move_info = ''

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            pygame.quit()
            return

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

        self.chesses = None
        self.images = {
            'wK' : pygame.transform.scale(pygame.image.load('chess/wk.png'), (70, 70)),
            'wQ' : pygame.transform.scale(pygame.image.load('chess/wq.png'), (70, 70)),
            'wB' : pygame.transform.scale(pygame.image.load('chess/wb.png'), (70, 70)),
            'wN' : pygame.transform.scale(pygame.image.load('chess/wn.png'), (70, 70)),
            'wR' : pygame.transform.scale(pygame.image.load('chess/wr.png'), (70, 70)),
            'wP' : pygame.transform.scale(pygame.image.load('chess/wp.png'), (70, 70)),

            'bK' : pygame.transform.scale(pygame.image.load('chess/bk.png'), (70, 70)),
            'bQ' : pygame.transform.scale(pygame.image.load('chess/bq.png'), (70, 70)),
            'bB' : pygame.transform.scale(pygame.image.load('chess/bb.png'), (70, 70)),
            'bN' : pygame.transform.scale(pygame.image.load('chess/bn.png'), (70, 70)),
            'bR' : pygame.transform.scale(pygame.image.load('chess/br.png'), (70, 70)),
            'bP' : pygame.transform.scale(pygame.image.load('chess/bp.png'), (70, 70)),
        }

        self.pre_moves = []

    def highlight(self, i, j):
        color = (169, 228, 149)
        if (i + j) % 2 == 1:
            color = (189, 248, 169)
        
        pygame.draw.rect(self.game_surface, color, (i * 80, j * 80, 80, 80))

    def draw_game_surface(self):
        self.game_surface.fill((238, 238, 210))
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    pygame.draw.rect(self.game_surface, (118, 150, 86), (i * 80, j * 80, 80, 80))

        if 'O-O' in self.move_info:
            pos1 = 'e'
            if 'O-O-O' in self.move_info:
                pos2 = 'c'
                if self.move_info[0] == 'w':
                    pos1 += '1'
                    pos2 += '1'
                else:
                    pos1 += '8'
                    pos2 += '8'

            else:
                pos2 = 'g'
                if self.move_info[0] == 'w':
                    pos1 += '1'
                    pos2 += '1'
                else:
                    pos1 += '8'
                    pos2 += '8'

            i, j = self.get_location_from_pos(pos1)
            self.highlight(i, j)
            i, j = self.get_location_from_pos(pos2)
            self.highlight(i, j)
        
        elif len(self.move_info) > 5:
            if not self.move_info[-1].isdigit():
                i, j = self.get_location_from_pos(self.move_info[-3 : -1])
            else:
                i, j = self.get_location_from_pos(self.move_info[-2:])
        
            self.highlight(i, j)
            i, j = self.get_location_from_pos(self.move_info[2:4])
            self.highlight(i, j)

        if self.curr_co is not None and self.curr_co in [co[-2:] for co in self.chesses]:
            i, j = self.get_location_from_pos(self.curr_co)
            self.highlight(i, j)
        
        for chess in self.chesses:
            image = self.images[chess[: 2]]
            pos = self.get_location_from_pos(chess[2 : 4])
            self.game_surface.blit(image, (pos[0] * 80 + 5, pos[1] * 80 + 5))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024)

                try:
                   message = message.decode()
                   self.move_info = message
                   print(self.move_info)
                except:
                    message = pickle.loads(message)

                if message == "black":
                    self.is_white = False
                    self.can_move = False

                elif message == "white":
                    self.is_white = True
                    self.can_move = True

                # pre move
                elif type(message) == list: 
                    self.pre_moves = message
                
                # reset 
                elif type(message) == tuple:
                    self.chesses = message

                else:
                    self.can_move = not self.can_move
                    
                    # castle
                    
                    # move
                    if message[0] == 'w' and self.is_white or message[0] == 'b' and not self.is_white:
                        self.pre_moves = []

                    # take
                    if 'x' in message and self.curr_co == message[-2:]:
                        self.pre_moves = []

                    if len(self.pre_moves) != 0 and message[-2:] in self.pre_moves:
                        self.client_socket.send(self.curr_co.encode())
                    
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def get_location_from_pos(self, pos) -> tuple:
        if self.is_white:
            return (ord(pos[0]) - 97, 7 - (int(pos[1]) - 1))
        else:
            return(7 - (ord(pos[0]) - 97), int(pos[1]) - 1)
    
    def get_pos_from_mouse(self, pos) -> str:
        if self.is_white:
            return f"{chr(97 + pos[0])}{8 - pos[1]}"
        else:
            return f"{chr(97 - (pos[0] - 7))}{pos[1] + 1}"
    
    def run(self):
        running = True
        self.pre_moves = []
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.curr_co = self.get_pos_from_mouse((mouse_x // 80 - 1, mouse_y // 80 - 1))

                    self.client_socket.send(self.curr_co.encode())

            if self.is_white is not None and self.chesses is not None:
                self.draw_game_surface()

                if len(self.pre_moves) != 0:
                    for pre_move in self.pre_moves:
                        if 't'  not in pre_move:
                            pos = self.get_location_from_pos(pre_move)
                            pygame.draw.circle(self.game_surface, (123, 123, 123), (pos[0] * 80 + 40, pos[1] * 80 + 40), 15)
                        
                        else:
                            pre_move = pre_move[1:]
                            pos = self.get_location_from_pos(pre_move)
                            pygame.draw.circle(self.game_surface, (150, 150, 150), (pos[0] * 80 + 40, pos[1] * 80 + 40), 37, 10)
                        
                
                self.screen.blit(self.surface, (0, 0))

            pygame.display.flip()
        
        self.client_socket.close()
        pygame.quit()

if __name__ == '__main__':
    chess = Chess()
    chess.run()