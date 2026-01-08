# brickbreak

A simple brick breaker game built in Python that runs in Google Colab using
`ipycanvas`.

## Run in Google Colab

```python
!pip -q install ipycanvas

from brick_breaker import BrickBreakerGame

game = BrickBreakerGame()
await game.start()
```

Use the left/right arrow keys (or A/D) to move the paddle.

### Restart the game

```python
game.reset()
await game.start()
```
