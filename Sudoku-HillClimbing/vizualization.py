import pygame


def visualize_sudoku(screen, grid, x, y, solved=False):
    cell_size = 100
    margin = 20
    block_size = 3  # Number of blocks in each row/column

    font = pygame.font.Font(None, 70)

    for i in range(9):
        for j in range(9):
            value = grid[i][j]
            if value != 0:
                text_surface = font.render(str(value), True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    center=(x + margin + j * cell_size + cell_size / 2, y + margin + i * cell_size + cell_size / 2))
                screen.blit(text_surface, text_rect)
            if solved:
                pygame.draw.rect(screen, (0, 0, 0),
                                 (x + margin + j * cell_size, y + margin + i * cell_size, cell_size, cell_size), 2)
            else:
                pygame.draw.rect(screen, (0, 0, 0),
                                 (x + margin + j * cell_size, y + margin + i * cell_size, cell_size, cell_size), 2)

    # Draw rectangles around each block
    for i in range(block_size):
        for j in range(block_size):
            rect_x = x + margin + j * cell_size * block_size
            rect_y = y + margin + i * cell_size * block_size
            pygame.draw.rect(screen, (0, 0, 0), (rect_x, rect_y, cell_size * block_size, cell_size * block_size), 4)


def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((2000, 1500))
    screen.fill((255, 255, 255))
    pygame.display.set_caption('Sudoku Solver')
    return screen
