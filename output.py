import pygame
import os

# Initialize Pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TASKBAR_HEIGHT = 50

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (0,255,255)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simulated Desktop")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load Background Image
IMG_FOLDER = './imgs'
background_path = os.path.join(IMG_FOLDER, 'background.jpg')
background = pygame.image.load(background_path) if os.path.exists(background_path) else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Define the browser window
browser_window = pygame.Rect(150, 100, 500, 400)
browser_open = True
taskbar_rect = pygame.Rect(0, SCREEN_HEIGHT - TASKBAR_HEIGHT, SCREEN_WIDTH, TASKBAR_HEIGHT)

# Taskbar icons (Browser)
taskbar_icons = [
    {"rect": pygame.Rect(10, SCREEN_HEIGHT - 40, 30, 30), "label": "Browser", "active": True}
]

# Buttons for browser window
close_button = pygame.Rect(browser_window.right - 20, browser_window.top + 5, 15, 15)
minimize_button = pygame.Rect(browser_window.right - 40, browser_window.top + 5, 15, 15)

def draw_taskbar():
    """Draw the taskbar and icons."""
    pygame.draw.rect(screen, GRAY, taskbar_rect)
    for icon in taskbar_icons:
        color = BLUE if icon["active"] else BLACK
        pygame.draw.rect(screen, color, icon["rect"])
        label = pygame.font.Font(None, 20).render(icon["label"], True, WHITE)
        screen.blit(label, (icon["rect"].x + 35, icon["rect"].y + 5))

def draw_browser():
    """Draw the browser window."""
    pygame.draw.rect(screen, WHITE, browser_window)
    pygame.draw.rect(screen, RED, close_button)
    pygame.draw.rect(screen, YELLOW, minimize_button)
    title_bar = pygame.font.Font(None, 24).render("Simple Browser", True, BLACK)
    screen.blit(title_bar, (browser_window.x + 10, browser_window.y + 10))

def main():
    running = True
    global browser_open

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Check if taskbar icon is clicked
                for icon in taskbar_icons:
                    if icon["rect"].collidepoint(mouse_pos):
                        icon["active"] = True
                        browser_open = True  # Only one app for now
                # Check close button
                if browser_open and close_button.collidepoint(mouse_pos):
                    browser_open = False
                    taskbar_icons[0]["active"] = False  # For this sample

                # Check minimize button
                if browser_open and minimize_button.collidepoint(mouse_pos):
                    browser_open = False  # Browser closed for simplicity
                    taskbar_icons[0]["active"] = True  # Highlighted on bar if not off for practice simplicity.

        # Draw environment
        screen.blit(background, (0, 0))
        if browser_open:
            draw_browser()
        draw_taskbar()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
