"""Ball basket sprite — single-tile volleyball cart"""
import pygame
from .base import GameObject

_BOX      = ( 35,  85, 185)
_BOX_DK   = ( 20,  60, 145)
_BOX_LT   = ( 65, 115, 220)
_BALL     = (240, 195,  20)
_BALL_HI  = (255, 235, 100)
_OUTLINE  = ( 20,  20,  20)
_STILT    = (170, 170, 185)
_STILT_DK = (120, 120, 135)
_WHEEL    = ( 45,  45,  52)


class BallBasket(GameObject):
    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = [
            {
                "text": "Its a basket of balls.\nTake one?",
                "choices": {
                    "Yes": ["Its empty."],
                    "No": [],
                },
            }
        ]

    def draw(self, screen: pygame.Surface):
        cx, cy = self.x, self.y

        bw, bh = 26, 11
        bx = cx - bw // 2
        by = cy - 5

        # Legs — slight outward splay
        leg_bot = cy + 11
        pygame.draw.line(screen, _STILT,
                         (bx + 4, by + bh), (bx + 2, leg_bot), 2)
        pygame.draw.line(screen, _STILT,
                         (bx + bw - 4, by + bh), (bx + bw - 2, leg_bot), 2)
        brace_y = by + bh + (leg_bot - by - bh) // 2
        pygame.draw.line(screen, _STILT_DK,
                         (bx + 3, brace_y), (bx + bw - 3, brace_y), 1)

        # Caster wheels
        for wx in (bx + 2, bx + bw - 2):
            pygame.draw.circle(screen, _WHEEL, (wx, leg_bot + 2), 2)
            pygame.draw.circle(screen, _OUTLINE, (wx, leg_bot + 2), 2, 1)

        # Balls peeking above the rim
        ball_y = by - 2
        for offset in (-7, 0, 7):
            bpx = cx + offset
            pygame.draw.circle(screen, _BALL, (bpx, ball_y), 4)
            pygame.draw.circle(screen, _BALL_HI, (bpx, ball_y - 1), 1)
            pygame.draw.circle(screen, _OUTLINE, (bpx, ball_y), 4, 1)

        # Blue fabric box — drawn last to cover ball bottoms
        pygame.draw.rect(screen, _BOX, (bx, by, bw, bh))
        pygame.draw.rect(screen, _BOX_DK, (bx, by, bw, bh), 1)
        pygame.draw.line(screen, _BOX_LT,
                         (bx + 1, by + 1), (bx + bw - 2, by + 1), 1)
