import sys
import pygame
from constants import *


def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def visualize_sudoku(screen, grid, x, y, size, block_size):
    margin = 140
    cell_size = min((SCREEN_WIDTH - 4 * margin) // size,
                    (SCREEN_HEIGHT - 4 * margin) // size)
    font_size = cell_size // 2
    font = pygame.font.Font(None, font_size)

    for i in range(size):
        for j in range(size):
            value = grid[i][j]
            if value != 0:
                text_surface = font.render(str(value), True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    center=(x + margin + j * cell_size + cell_size / 2, y + margin + i * cell_size + cell_size / 2))
                screen.blit(text_surface, text_rect)

            pygame.draw.rect(screen, (0, 0, 0),
                             (x + margin + j * cell_size, y + margin + i * cell_size, cell_size, cell_size), 2)

    # Draw rectangles around each block
    for i in range(block_size):
        for j in range(block_size):
            rect_x = x + margin + j * cell_size * block_size
            rect_y = y + margin + i * cell_size * block_size
            pygame.draw.rect(screen, (0, 0, 0), (rect_x, rect_y, cell_size * block_size, cell_size * block_size), 4)


def display_solved_message(screen):
    font = pygame.font.Font(None, 80)
    solved_text = "Sudoku Solved!"
    text_surface = font.render(solved_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(text_surface, text_rect)


def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))
    pygame.display.set_caption('Sudoku Solver')
    return screen
