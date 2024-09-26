import socket
import threading
import pickle
import time
import numpy as np
from abc import ABC, abstractmethod

def coor_from_pos(pos):
    return ((ord(pos[0]) - 97), int(pos[1]) - 1)

def pos_from_coor(coor):
    return chr(int(coor[0]) + 97) + str(coor[1] + 1) 

def get_chess_from_number(number):
    if abs(number) == 1:
        return King
    elif abs(number) == 2:
        return Queen
    elif abs(number) == 3:
        return Bishop
    elif abs(number) == 4:
        return Knight
    elif abs(number) == 5:
        return Rook
    elif abs(number) == 6:
        return Pawn
    else:
        raise "number error"
    
def can_move(curr, pos, king_pos, enemies, matrix):
    tmp = matrix[coor_from_pos(pos)]
    tmp2 = matrix[coor_from_pos(curr)]

    matrix[coor_from_pos(pos)] = tmp2
    matrix[coor_from_pos(curr)] = 0

    for enemy in enemies:
        if enemy != coor_from_pos(pos) and get_chess_from_number(abs(matrix[enemy])).is_attack_at(pos_from_coor(enemy), king_pos, matrix):
            matrix[coor_from_pos(pos)] = tmp
            matrix[coor_from_pos(curr)] = tmp2
            return False
        
    matrix[coor_from_pos(pos)] = tmp
    matrix[coor_from_pos(curr)] = tmp2
    return True

def append_pre_move(pre_moves: list, pos: str, curr_coor: tuple, matrix):
    if matrix[coor_from_pos(pos)] == 0:
        pre_moves.append(pos)
        return True
    else:
        if matrix[coor_from_pos(pos)] * matrix[curr_coor] < 0:
            pre_moves.append('t' + pos)
        return False
    
def get_enemies_and_king(is_white: bool, matrix):
    if is_white:
        enemies = np.where(matrix < 0)
        enemies = list(zip(enemies[0], enemies[1]))
        coor = np.where(matrix == 1)
        king_pos = pos_from_coor([coor[0][0], coor[1][0]])
    else:
        enemies = np.where(matrix > 0)
        enemies = list(zip(enemies[0], enemies[1]))
        coor = np.where(matrix == -1)
        king_pos = pos_from_coor([coor[0][0], coor[1][0]])

    return enemies, king_pos


def is_error_pos(pos):
    return '0' in pos or 'i' in pos or '9' in pos or '`' in pos

class Co(ABC):
    @abstractmethod
    def pos_can_move(self, matrix):
        pass

    @abstractmethod
    def way_to_enemy_king(self, king_pos):
        pass


class King(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white
        self.is_moved = False
        
    def __str__(self) -> str:
        if self.is_white:
            return 'wK' + self.pos
        else:
            return 'bK' + self.pos
        
    @staticmethod
    def is_attack_at(start_pos: str, goal_pos: str, matrix):
        row = ord(start_pos[0])
        col = int(start_pos[1])
        
        if col + 1 <= 8:
            pos = chr(row) + str(col + 1)
            if pos == goal_pos:
                return True
            
        if col - 1 >= 1:
            pos = chr(row) + str(col - 1)
            if pos == goal_pos:
                return True
        
        if row + 1 <= 104:
            pos = chr(row + 1) + str(col)
            if pos == goal_pos:
                return True
            
        if col + 1 <= 8 and row + 1 <= 104:
            pos = chr(row + 1) + str(col + 1)
            if pos == goal_pos:
                return True
            
        if col - 1 >= 1 and row + 1 <= 104:
            pos = chr(row + 1) + str(col - 1)
            if pos == goal_pos:
                return True
            
        
        if row - 1 >= 97:
            pos = chr(row - 1) + str(col)
            if pos == goal_pos:
                return True
            
        if col + 1 <= 8 and row - 1 >= 97:
            pos = chr(row - 1) + str(col + 1)
            if pos == goal_pos:
                return True
            
        if col - 1 >= 1 and row - 1 >= 97:
            pos = chr(row - 1) + str(col - 1)
            if pos == goal_pos:
                return True
            
        return False
    
    def way_to_enemy_king(self, king_pos):
        return []
        
    def pos_can_move(self, matrix):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        pre_moves = []
        
        curr_coor = coor_from_pos(self.pos)
        if col + 1 <= 8:
            pos = chr(row) + str(col + 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
            
        if col - 1 >= 1:
            pos = chr(row) + str(col - 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        
        if row + 1 <= 104:
            pos = chr(row + 1) + str(col)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
            
            if col + 1 <= 8:
                pos = chr(row + 1) + str(col + 1)
                append_pre_move(pre_moves, pos, curr_coor, matrix)
            if col - 1 >= 1:
                pos = chr(row + 1) + str(col - 1)
                append_pre_move(pre_moves, pos, curr_coor, matrix)
        
        if row - 1 >= 97:
            pos = chr(row - 1) + str(col)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
            if col + 1 <= 8:
                pos = chr(row - 1) + str(col + 1)
                append_pre_move(pre_moves, pos, curr_coor, matrix)
            if col - 1 >= 1:
                pos = chr(row - 1) + str(col - 1)
                append_pre_move(pre_moves, pos, curr_coor, matrix)
        
        return pre_moves

class Queen(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white

    def __str__(self) -> str:
        if self.is_white:
            return 'wQ' + self.pos
        else:
            return 'bQ' + self.pos
        
    def way_to_enemy_king(self, king_pos):
        row = ord(self.pos[0])
        col = int(self.pos[1])

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        return [self.pos]
    
    @staticmethod
    def is_attack_at(start_pos: str, goal_pos: str, matrix):
        return Rook.is_attack_at(start_pos, goal_pos, matrix) or Bishop.is_attack_at(start_pos, goal_pos, matrix)
        
    def pos_can_move(self, matrix):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        pre_moves = []
        enemies, king_pos = get_enemies_and_king(self.is_white, matrix)
        curr_coor = coor_from_pos(self.pos)

        for i in range(1, 9):
            pos = chr(row + i) + str(col)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row + i) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break
                
        for i in range(1, 9):
            pos = chr(row - i) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row + i) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        return pre_moves    

class Rook(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white
        self.is_moved = False

    def __str__(self) -> str:
        if self.is_white:
            return 'wR' + self.pos
        else:
            return 'bR' + self.pos
    
    def way_to_enemy_king(self, king_pos):
        row = ord(self.pos[0])
        col = int(self.pos[1])

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        return [self.pos]
    
    @staticmethod
    def is_attack_at(start_pos: str, goal_pos: str, matrix):
        row = ord(start_pos[0])
        col = int(start_pos[1])

        for i in range(1, 9):
            pos = chr(row) + str(col + i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row) + str(col - i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row + i) + str(col)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        return False

    def pos_can_move(self, matrix):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        pre_moves = []
        enemies, king_pos = get_enemies_and_king(self.is_white, matrix)
        curr_coor = coor_from_pos(self.pos)

        for i in range(1, 9):
            pos = chr(row + i) + str(col)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        return pre_moves

class Knight(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white

    def __str__(self) -> str:
        if self.is_white:
            return 'wN' + self.pos
        else:
            return 'bN' + self.pos
        
    def way_to_enemy_king(self, king_pos):
        return [self.pos]
    
    @staticmethod
    def is_attack_at(start_pos: str, goal_pos: str, matrix):
        row = ord(start_pos[0])
        col = int(start_pos[1])

        if row + 2 <= 104 and col + 1 <= 8:
            pos = chr(row + 2) + str(col + 1)
            if pos == goal_pos:
                return True
            
        if row + 2 <= 104 and col - 1 >= 1:
            pos = chr(row + 2) + str(col - 1)
            if pos == goal_pos:
                return True
            
        if row - 2 >= 97 and col + 1 <= 8:
            pos = chr(row - 2) + str(col + 1)
            if pos == goal_pos:
                return True
            
        if row - 2 >= 97 and col - 1 >= 1:
            pos = chr(row - 2) + str(col - 1)
            if pos == goal_pos:
                return True

        if row + 1 <= 104 and col + 2 <= 8:
            pos = chr(row + 1) + str(col + 2)
            if pos == goal_pos:
                return True
            
        if row + 1 <= 104 and col - 2 >= 1:
            pos = chr(row + 1) + str(col - 2)
            if pos == goal_pos:
                return True
            
        if row - 1 >= 97 and col + 2 <= 8:
            pos = chr(row - 1) + str(col + 2)
            if pos == goal_pos:
                return True
            
        if row - 1 >= 97 and col - 2 >= 1:
            pos = chr(row - 1) + str(col - 2)
            if pos == goal_pos:
                return True
            
        return False
    
    def pos_can_move(self, matrix):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        pre_moves = []
        
        curr_coor = coor_from_pos(self.pos)

        if row + 2 <= 104 and col + 1 <= 8:
            pos = chr(row + 2) + str(col + 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row + 2 <= 104 and col - 1 >= 1:
            pos = chr(row + 2) + str(col - 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row - 2 >= 97 and col + 1 <= 8:
            pos = chr(row - 2) + str(col + 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row - 2 >= 97 and col - 1 >= 1:
            pos = chr(row - 2) + str(col - 1)
            append_pre_move(pre_moves, pos, curr_coor, matrix)

        if row + 1 <= 104 and col + 2 <= 8:
            pos = chr(row + 1) + str(col + 2)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row + 1 <= 104 and col - 2 >= 1:
            pos = chr(row + 1) + str(col - 2)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row - 1 >= 97 and col + 2 <= 8:
            pos = chr(row - 1) + str(col + 2)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
        if row - 1 >= 97 and col - 2 >= 1:
            pos = chr(row - 1) + str(col - 2)
            append_pre_move(pre_moves, pos, curr_coor, matrix)
            
        return pre_moves

class Bishop(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white

    def __str__(self) -> str:
        if self.is_white:
            return 'wB' + self.pos
        else:
            return 'bB' + self.pos
        
    def way_to_enemy_king(self, king_pos):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row + i) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col - i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        res = [self.pos]
        for i in range(1, 9):
            pos = chr(row - i) + str(col + i)
            if pos == king_pos:
                return res
            else:
                res.append(pos)

        return [self.pos]
    
    @staticmethod
    def is_attack_at(start_pos: str, goal_pos: str, matrix):
        row = ord(start_pos[0])
        col = int(start_pos[1])

        for i in range(1, 9):
            pos = chr(row + i) + str(col + i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row + i) + str(col - i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col - i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col + i)
            if pos == goal_pos:
                return True
            if is_error_pos(pos) or matrix[coor_from_pos(pos)] != 0:
                break

        return False
    
    def pos_can_move(self, matrix: np.ndarray):
        row = ord(self.pos[0])
        col = int(self.pos[1])
        
        pre_moves = []
        enemies, king_pos = get_enemies_and_king(self.is_white, matrix)
        curr_coor = coor_from_pos(self.pos)

        for i in range(1, 9):
            pos = chr(row + i) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break
                
        for i in range(1, 9):
            pos = chr(row - i) + str(col - i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row + i) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        for i in range(1, 9):
            pos = chr(row - i) + str(col + i)
            if is_error_pos(pos) or matrix[curr_coor] * matrix[coor_from_pos(pos)] > 0 or (can_move(self.pos, pos, king_pos, enemies, matrix) and not append_pre_move(pre_moves, pos, curr_coor, matrix)):
                break

        return pre_moves    

class Pawn(Co):
    def __init__(self, pos, is_white) -> None:
        self.pos = pos
        self.is_white = is_white
        self.is_moved = False

    def __str__(self) -> str:
        if self.is_white:
            return 'wP' + self.pos
        else:
            return 'bP' + self.pos
        
    def way_to_enemy_king(self, king_pos):
        return [self.pos]
    
    @staticmethod
    def is_attack_at(begin_pos: str, goal_pos: str, matrix):
        row = begin_pos[0]
        col = int(begin_pos[1])
        if matrix[coor_from_pos(begin_pos)] == 6:
            pos = chr(ord(row) - 1) + str(col + 1)
            if pos == goal_pos:
                return True
                
            pos = chr(ord(row) + 1) + str(col + 1)
            if pos == goal_pos:
                return True

        else:
            pos = chr(ord(row) - 1) + str(col - 1)
            if pos == goal_pos:
                return True
        
            pos = chr(ord(row) + 1) + str(col - 1)
            if pos == goal_pos:
                return True

        return False
    
    def pos_can_move(self, matrix):
        row = self.pos[0]
        col = int(self.pos[1])

        pre_moves = []

        if self.is_white:
            if col + 1 <= 8:
                pos = row + str(col + 1)
                if matrix[coor_from_pos(pos)] == 0:
                    pre_moves.append(pos)
                    if self.is_moved is False:
                        pos = row + str(col + 2)
                        if matrix[coor_from_pos(pos)] == 0:
                            pre_moves.append(pos)

                if ord(row) - 1 >= 97:
                    pos = chr(ord(row) - 1) + str(col + 1)
                    if matrix[coor_from_pos(pos)] < 0:
                        pre_moves.append('t' + pos)
                        
                if ord(row) + 1 <= 104:
                    pos = chr(ord(row) + 1) + str(col + 1)
                    if matrix[coor_from_pos(pos)] < 0:
                        pre_moves.append('t' + pos)

        else:
            if col - 1 >= 1:
                pos = row + str(col - 1)
                if matrix[coor_from_pos(pos)] == 0:
                    pre_moves.append(pos)
                    if self.is_moved is False:
                        pos = row + str(col - 2)
                        if matrix[coor_from_pos(pos)] == 0:
                            pre_moves.append(pos)

                if ord(row) - 1 >= 97:
                    pos = chr(ord(row) - 1) + str(col - 1)
                    if matrix[coor_from_pos(pos)] > 0:
                        pre_moves.append('t' + pos)
                
                if ord(row) + 1 <= 104:
                    pos = chr(ord(row) + 1) + str(col - 1)
                    if matrix[coor_from_pos(pos)] > 0: 
                        pre_moves.append('t' + pos)
            
        return pre_moves

class Player:
    def __init__(self, client_address, is_white) -> None:
        self.client_address = client_address
        self.is_white = is_white
        self.curr = None

class Game:
    def __init__(self, players, time = 600) -> None:
        self.chesses = [
            King('e1', True),
            Queen('d1', True),
            Bishop('c1', True),
            Bishop('f1', True),
            Knight('b1', True),
            Knight('g1', True),
            Rook('a1', True),
            Rook('h1', True),
            Pawn('a2', True),
            Pawn('b2', True),
            Pawn('c2', True),
            Pawn('d2', True),
            Pawn('e2', True),
            Pawn('f2', True),
            Pawn('g2', True),
            Pawn('h2', True),

            King('e8', False),
            Queen('d8', False),
            Bishop('c8', False),
            Bishop('f8', False),
            Knight('b8', False),
            Knight('g8', False),
            Rook('a8', False),
            Rook('h8', False),
            Pawn('a7', False),
            Pawn('b7', False),
            Pawn('c7', False),
            Pawn('d7', False),
            Pawn('e7', False),
            Pawn('f7', False),
            Pawn('g7', False),
            Pawn('h7', False)
        ]
        
        self.matrix = self.set_new_matrix()
        self.move_info = []
        
        self.players = players # 0: white, 1: black
        self.time = time
        self.white_turn = True
        self.is_white_checked = None
        # những vị trí có thể giải hóa nước chiếu
        self.break_check = []

    def set_new_matrix(self):
        matrix = np.zeros((8, 8), dtype=np.int8)

        # White King
        matrix[coor_from_pos('e1')] = 1 
        # White Queen
        matrix[coor_from_pos('d1')] = 2 
        # White Bishop
        matrix[coor_from_pos('c1')] = 3 
        matrix[coor_from_pos('f1')] = 3
        # White Knight
        matrix[coor_from_pos('b1')] = 4 
        matrix[coor_from_pos('g1')] = 4
        # White Rook
        matrix[coor_from_pos('a1')] = 5 
        matrix[coor_from_pos('h1')] = 5 
        # White Pawn 
        matrix[coor_from_pos('a2')] = 6 
        matrix[coor_from_pos('b2')] = 6 
        matrix[coor_from_pos('c2')] = 6 
        matrix[coor_from_pos('d2')] = 6 
        matrix[coor_from_pos('e2')] = 6 
        matrix[coor_from_pos('f2')] = 6 
        matrix[coor_from_pos('g2')] = 6 
        matrix[coor_from_pos('h2')] = 6
        
        # Black King
        matrix[coor_from_pos('e8')] = -1
        # Black Queen
        matrix[coor_from_pos('d8')] = -2 
        # Black Bishop
        matrix[coor_from_pos('c8')] = -3
        matrix[coor_from_pos('f8')] = -3
        # Black Knight
        matrix[coor_from_pos('b8')] = -4 
        matrix[coor_from_pos('g8')] = -4
        # Black Rook
        matrix[coor_from_pos('a8')] = -5 
        matrix[coor_from_pos('h8')] = -5 
        # Black Pawn 
        matrix[coor_from_pos('a7')] = -6 
        matrix[coor_from_pos('b7')] = -6 
        matrix[coor_from_pos('c7')] = -6 
        matrix[coor_from_pos('d7')] = -6 
        matrix[coor_from_pos('e7')] = -6 
        matrix[coor_from_pos('f7')] = -6 
        matrix[coor_from_pos('g7')] = -6 
        matrix[coor_from_pos('h7')] = -6

        return matrix

    def pos_from_coor(self, coor):
        return chr(coor[0] + 97) + str(coor[1] + 1)

    def coor_from_pos(self, pos):
        return ((ord(pos[0]) - 97), int(pos[1]) - 1)

    def get_chesses(self):
        li = []
        for co in self.chesses:
            li.append(str(co))
        
        return tuple(li)
    
    def move(self, curr, pos):

        coor1 = coor_from_pos(curr)
        coor2 = coor_from_pos(pos)  
        co = self.get_co_from_pos(curr)

        if type(co) is King and not co.is_moved and abs(ord(curr[0]) - ord(pos[0])) == 2:
            self.move_info = self.move_info[:-1]
            if pos == 'c1':
                self.move('a1', 'd1')
                self.move_info.append('wO-O-O')
            elif pos == 'g1':
                self.move('h1', 'f1')
                self.move_info.append('wO-O')
            elif pos == 'c8':
                self.move('a8', 'd8')
                self.move_info.append('bO-O-O')
            elif pos == 'g8':
                self.move('h8', 'f8')
                self.move_info.append('bO-O')
                
        self.matrix[coor1], self.matrix[coor2] = self.matrix[coor2], self.matrix[coor1]
        co.pos = pos

        if type(co) is Pawn or type(co) is King or type(co) is Rook:
            co.is_moved = True

    def take(self, curr, pos):
        for co in self.chesses:
            if co.pos == pos:
                self.chesses.remove(co)
                break
        self.matrix[coor_from_pos(pos)] = 0
        self.move(curr, pos)

    def is_check(self, player):
        self.break_check = []
        for co in self.chesses:
            if co.is_white == player.is_white:
                for move in co.pos_can_move(self.matrix):
                    if 't' in move and type(self.get_co_from_pos(move[1:])) is King:
                        self.break_check = co.way_to_enemy_king(move[1:])
                        
        return len(self.break_check) != 0
    
    def is_checkmate(self, player):
        for co in self.chesses:
            if co.is_white == player.is_white:
                tmp = self.pos_can_move(co, player)
                print(tmp)
                if len(tmp) != 0:
                    return False
            
        return True
    
    def pre_castling(self, rook_pos, enemies, pre_moves):
        rook = self.get_co_from_pos(rook_pos)
        
        if rook is not None and type(rook) is Rook and not rook.is_moved:
            if rook_pos == 'a1':
                poses = ['b1', 'c1', 'd1']
                pre = 'c1'
            elif rook_pos == 'h1':
                poses = ['f1', 'g1']
                pre = 'g1'
            elif rook_pos == 'a8':
                poses = ['b8', 'c8', 'd8']
                pre = 'c8'
            elif rook_pos == 'h8':
                poses = ['f8', 'g8']
                pre = 'g8'

            can_castle = True
            for pos in poses:
                if self.get_co_from_pos(pos) is None:
                    for enemy in enemies:
                        if get_chess_from_number(abs(self.matrix[enemy])).is_attack_at(pos_from_coor(enemy), pos, self.matrix):
                            can_castle = False
                            break
                else:
                    can_castle = False
                    break
            
            if can_castle:
                pre_moves.append(pre)
    
    def pos_can_move(self, co, player):
        pre_moves = co.pos_can_move(self.matrix)
        if self.is_white_checked is None:
            if type(co) is King and not co.is_moved:
                enemies, _ = get_enemies_and_king(player.is_white, self.matrix)
                if player.is_white:
                    self.pre_castling('a1', enemies, pre_moves)
                    self.pre_castling('h1', enemies, pre_moves)
                
                else:
                    self.pre_castling('a8', enemies, pre_moves)
                    self.pre_castling('h8', enemies, pre_moves)
                
            return pre_moves
        else:
            if self.is_white_checked == player.is_white:
                return pre_moves

            if type(co) is not King:
                tmp = []
                for i in pre_moves:
                    if i in self.break_check or i[1:] in self.break_check:
                        tmp.append(i)
                return tmp
            else:
                tmp = []
                enemies, _ = get_enemies_and_king(player.is_white, self.matrix)
                
                for pos in pre_moves:
                    can_move = True
                    p = pos
                    if len(pos) == 3:
                        p = pos[1:]
                    
                    for enemy in enemies:
                        if get_chess_from_number(abs(self.matrix[enemy])).is_attack_at(pos_from_coor(enemy), p, self.matrix):
                            can_move = False
                            break
                    
                    if can_move:
                        tmp.append(pos)

                return tmp
        
    def handle(self, client_address, pos):
        co = self.get_co_from_pos(pos)

        for p in self.players:
            if p.client_address == client_address:
                player = p
        
        if player.curr is not None:
            pre_moves = self.pos_can_move(self.get_co_from_pos(player.curr), player)

        # move
        if co is None and player.curr is not None and self.white_turn == player.is_white and (pos in pre_moves):
            self.move_info.append(str(self.get_co_from_pos(player.curr)) + pos)
            self.move(player.curr, pos)

            if self.is_check(player):
                self.is_white_checked = self.white_turn
                if self.is_checkmate(self.players[1 - self.players.index(player)]):
                    self.move_info[-1] += '#'
                else:
                    self.move_info[-1] += '+'
            else:
                self.is_white_checked = None

            player.curr = None
            self.white_turn = not self.white_turn
            return self.get_chesses()

        if co is not None:
            # take
            if co.is_white != player.is_white: 
                if player.curr is not None and ('t' + pos) in pre_moves:
                    self.move_info.append(str(self.get_co_from_pos(player.curr)) + 'x' + pos)
                    self.take(player.curr, pos)

                    if self.is_check(player):
                        self.is_white_checked = self.white_turn
                        if self.is_checkmate(self.players[1 - self.players.index(player)]):
                            self.move_info[-1] += '#'
                        else:
                            self.move_info[-1] += '+'
                    else:
                        self.is_white_checked = None

                    player.curr = None
                    self.white_turn = not self.white_turn
                    return self.get_chesses()

                else:
                    player.curr = None
                    return []

            else:
                player.curr = co.pos
                return self.pos_can_move(co, player)
            
        else:
            return []

    def get_co_from_pos(self, pos):
        for co in self.chesses:
            if co.pos == pos:
                return co
        return None

class Server:
    def __init__(self, host='127.0.0.1', port=12345) -> None:
        self.host = host
        self.port = port
        self.clients = {}
        self.client_in_game = {}

        self.games = []
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(6)
        print(f"Server listening on {self.host}:{self.port}")

        self.is_white_turn = True
        
    def handle_client(self, client_socket, client_address):
        while True:
            try:
                msg = client_socket.recv(1024).decode('utf-8')
                
                curr_game = None
                for game in self.games:
                    if game.players[0].client_address == client_address or game.players[1].client_address == client_address:
                        curr_game = game
                        break
                
                if len(msg) == 2:
                    res = curr_game.handle(client_address, msg)
                    
                    if type(res) is list:
                        client_socket.sendall(pickle.dumps(res))
                    elif type(res) is tuple:
                        self.clients[curr_game.players[0].client_address].sendall(pickle.dumps(res))
                        self.clients[curr_game.players[1].client_address].sendall(pickle.dumps(res))

                        self.clients[curr_game.players[0].client_address].send(curr_game.move_info[-1].encode())
                        self.clients[curr_game.players[1].client_address].send(curr_game.move_info[-1].encode())

                    else:
                        client_socket.send(res.encode())

                else:
                    
                    pass
                
            except ConnectionResetError:
                print(f"[-] Connection lost from {client_address}")
                break

        client_socket.close()
        pass

    def run(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients[client_address] = client_socket
            self.client_in_game[client_address] = False
            print(f"[+] New connection from {client_address}")

            threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()
            
            if len(self.clients) % 2 == 0 and len(self.clients) != 0:
                players = []
                for address, in_game in self.client_in_game.items():
                    if len(players) == 2:
                        break

                    if in_game is False:
                        players.append(address)

                
                self.games.append(Game([Player(players[0], True), Player(players[1], False)], 600))
                chesses = pickle.dumps(self.games[-1].get_chesses())

                self.clients[players[0]].send('white'.encode('utf-8'))
                self.clients[players[0]].sendall(chesses)
                self.clients[players[1]].send('black'.encode('utf-8'))
                self.clients[players[1]].sendall(chesses)
                
                self.client_in_game[players[0]] = True
                self.client_in_game[players[1]] = True

            
if __name__ == '__main__':
    sv = Server()
    sv.run() 