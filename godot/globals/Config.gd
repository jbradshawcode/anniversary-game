# Engine tunables — the Godot mirror of the pygame `config.py` constants.
extends Node

const TILE_SIZE := 32
const MAP_COLS := 20  # SCREEN_WIDTH  / TILE_SIZE
const MAP_ROWS := 15  # SCREEN_HEIGHT / TILE_SIZE
const SCREEN_WIDTH := 640
const SCREEN_HEIGHT := 480
const TILE_MOVE_SPEED := 280.0  # px/sec during the smooth slide between tiles

const DIALOGUE_CPS := 45.0   # characters revealed per second (typewriter)
const DIALOGUE_FAST := 4.0   # multiplier while X (cancel) is held
