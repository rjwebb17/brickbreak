"""Simple brick breaker game for Jupyter/Colab using ipycanvas."""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import List, Tuple

from IPython.display import display
from ipycanvas import Canvas, hold_canvas


@dataclass
class Brick:
    x: float
    y: float
    width: float
    height: float
    alive: bool = True


class BrickBreakerGame:
    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        rows: int = 5,
        columns: int = 10,
    ) -> None:
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns

        self.canvas = Canvas(width=width, height=height)
        self.canvas.layout.border = "1px solid #ccc"

        self.paddle_width = 90
        self.paddle_height = 12
        self.paddle_x = (width - self.paddle_width) / 2
        self.paddle_speed = 6

        self.ball_radius = 6
        self.ball_x = width / 2
        self.ball_y = height - 40
        self.ball_speed = 4.5
        self.ball_vx = self.ball_speed
        self.ball_vy = -self.ball_speed

        self.score = 0
        self.game_over = False
        self.win = False

        self.left_pressed = False
        self.right_pressed = False

        self.bricks = self._create_bricks()

        self.canvas.on_key_down(self._handle_key_down)
        self.canvas.on_key_up(self._handle_key_up)

    def _create_bricks(self) -> List[Brick]:
        padding = 6
        offset_top = 40
        offset_left = 30
        brick_width = (self.width - 2 * offset_left - (self.columns - 1) * padding) / self.columns
        brick_height = 16

        bricks: List[Brick] = []
        for row in range(self.rows):
            for col in range(self.columns):
                x = offset_left + col * (brick_width + padding)
                y = offset_top + row * (brick_height + padding)
                bricks.append(Brick(x=x, y=y, width=brick_width, height=brick_height))
        return bricks

    def _handle_key_down(self, key: str, shift: bool, ctrl: bool, meta: bool) -> None:
        if key in ("ArrowLeft", "a", "A"):
            self.left_pressed = True
        if key in ("ArrowRight", "d", "D"):
            self.right_pressed = True

    def _handle_key_up(self, key: str, shift: bool, ctrl: bool, meta: bool) -> None:
        if key in ("ArrowLeft", "a", "A"):
            self.left_pressed = False
        if key in ("ArrowRight", "d", "D"):
            self.right_pressed = False

    def _move_paddle(self) -> None:
        if self.left_pressed:
            self.paddle_x -= self.paddle_speed
        if self.right_pressed:
            self.paddle_x += self.paddle_speed

        self.paddle_x = max(0, min(self.width - self.paddle_width, self.paddle_x))

    def _move_ball(self) -> None:
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_x <= self.ball_radius or self.ball_x >= self.width - self.ball_radius:
            self.ball_vx *= -1
        if self.ball_y <= self.ball_radius:
            self.ball_vy *= -1

        if self.ball_y >= self.height - self.ball_radius:
            self.game_over = True

    def _collide_with_paddle(self) -> None:
        paddle_top = self.height - 30
        if (
            paddle_top - self.ball_radius
            <= self.ball_y
            <= paddle_top + self.paddle_height
            and self.paddle_x - self.ball_radius
            <= self.ball_x
            <= self.paddle_x + self.paddle_width + self.ball_radius
            and self.ball_vy > 0
        ):
            hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width
            angle = (hit_pos - 0.5) * math.pi / 2.2
            self.ball_vx = self.ball_speed * math.sin(angle)
            self.ball_vy = -abs(self.ball_speed * math.cos(angle))

    def _collide_with_bricks(self) -> None:
        for brick in self.bricks:
            if not brick.alive:
                continue
            if (
                brick.x - self.ball_radius
                <= self.ball_x
                <= brick.x + brick.width + self.ball_radius
                and brick.y - self.ball_radius
                <= self.ball_y
                <= brick.y + brick.height + self.ball_radius
            ):
                brick.alive = False
                self.score += 10
                self.ball_vy *= -1
                break

        if all(not brick.alive for brick in self.bricks):
            self.win = True
            self.game_over = True

    def _update(self) -> None:
        if self.game_over:
            return
        self._move_paddle()
        self._move_ball()
        self._collide_with_paddle()
        self._collide_with_bricks()

    def _draw(self) -> None:
        with hold_canvas(self.canvas):
            self.canvas.clear()
            self.canvas.fill_style = "#1b1f24"
            self.canvas.fill_rect(0, 0, self.width, self.height)

            for brick in self.bricks:
                if brick.alive:
                    self.canvas.fill_style = "#4ade80"
                    self.canvas.fill_rect(brick.x, brick.y, brick.width, brick.height)

            paddle_top = self.height - 30
            self.canvas.fill_style = "#60a5fa"
            self.canvas.fill_rect(
                self.paddle_x,
                paddle_top,
                self.paddle_width,
                self.paddle_height,
            )

            self.canvas.begin_path()
            self.canvas.arc(self.ball_x, self.ball_y, self.ball_radius, 0, math.tau)
            self.canvas.fill_style = "#facc15"
            self.canvas.fill()

            self.canvas.fill_style = "#f8fafc"
            self.canvas.font = "16px sans-serif"
            self.canvas.fill_text(f"Score: {self.score}", 12, 20)

            if self.game_over:
                message = "You win!" if self.win else "Game over"
                self.canvas.fill_style = "#f8fafc"
                self.canvas.font = "26px sans-serif"
                self.canvas.fill_text(message, self.width / 2 - 60, self.height / 2)
                self.canvas.font = "16px sans-serif"
                self.canvas.fill_text(
                    "Run game.reset() to play again.",
                    self.width / 2 - 95,
                    self.height / 2 + 30,
                )

    async def start(self, fps: int = 60) -> None:
        """Display the canvas and start the game loop."""
        display(self.canvas)
        self.canvas.focus()
        frame_delay = 1 / fps
        while not self.game_over:
            self._update()
            self._draw()
            await asyncio.sleep(frame_delay)
        self._draw()

    def reset(self) -> None:
        self.paddle_x = (self.width - self.paddle_width) / 2
        self.ball_x = self.width / 2
        self.ball_y = self.height - 40
        self.ball_vx = self.ball_speed
        self.ball_vy = -self.ball_speed
        self.score = 0
        self.game_over = False
        self.win = False
        self.left_pressed = False
        self.right_pressed = False
        self.bricks = self._create_bricks()

    def show(self) -> None:
        """Display the canvas without starting the loop."""
        display(self.canvas)
        self.canvas.focus()


def create_game() -> BrickBreakerGame:
    """Convenience helper to create a game instance."""
    return BrickBreakerGame()


if __name__ == "__main__":
    game = BrickBreakerGame()
    asyncio.run(game.start())
