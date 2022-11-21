from collections import deque
from dataclasses import InitVar, dataclass, field
from functools import partial
from itertools import islice, product
from math import isclose
from random import randint
from typing import Any, Deque, Tuple

import pyglet
from pyglet.shapes import Rectangle
from pyglet.window import key

from pyecs import Scene

class Vec2(Tuple[Any, Any]):
    def __add__(self, other) -> 'Vec2':
        return Vec2((self[0]+other[0], self[1]+other[1]))
    
    def __radd__(self, other) -> 'Vec2':
        return self.__add__(other)
    
    def __sub__(self, other) -> 'Vec2':
        return Vec2((self[0]-other[0], self[1]-other[1]))
    
    def __mul__(self, other) -> 'Vec2':
        if isinstance(other, tuple):
            return Vec2((self[0]-other[0], self[1]-other[1]))
        return Vec2((self[0]*other, self[1]*other))
    
    def dot(self, other):
        return self[0]*other[0] + self[1]*other[1]

MAP_SIZE = Vec2((10, 10))
UNIT_SIZE = 50
INTERVAL = 0.6

HEAD_COLOR = 255, 125, 25
BODY_COLOR = 255, 150, 50
FOOD_COLOR = 25, 255, 125

ANIMATION_BEZIER = 0.25, 0, 0, 1

key_settings = {key.LEFT: Vec2((-1, 0)), key.RIGHT: Vec2((1, 0)),
    key.UP: Vec2((0, 1)), key.DOWN: Vec2((0, -1))}
is_over = False

@dataclass
class Unit:
    position: Vec2

@dataclass
class Head():
    unit: InitVar[Unit]
    direction: Vec2 = Vec2((1, 0))
    pre_direction: Vec2 = direction
    units: Deque[Unit] = field(init=False)

    def __post_init__(self, unit):
        self.units = deque((unit,))

class Food():
    pass

@dataclass
class Tween:
    component: Any
    attr: str
    start: Any
    end: InitVar[Any]
    bezier: Tuple[float, float, float, float]
    duration: float
    time: float = 0
    delta: Any = field(init=False)

    def __post_init__(self, end):
        self.delta = end - self.start

def food_system(scene: Scene):
    foods = scene.match_components(Unit, Food)
    heads = scene.match_components(Unit, Head)
    for (food_unit, _), (head_unit, head) in product(foods, heads):
        if food_unit.position == head_unit.position:
            food_unit.position = Vec2(randint(0, size-1) for size in MAP_SIZE)

            unit = Unit(head_unit.position)
            rect = new_rect(*unit.position*UNIT_SIZE, color=BODY_COLOR)
            scene.add_entity(unit,
                rect,
                new_tween(rect))
            head.units.appendleft(unit)

def edge_solver(num, max_):
    if num >= max_:
        return 0
    if num < 0:
        return max_ - 1
    return num

def move_system(scene: Scene):
    for head_unit, head in scene.match_components(Unit, Head):
        head.direction = head.pre_direction
        new_position = Vec2(map(edge_solver, head_unit.position + head.direction, MAP_SIZE))
        for after, before in zip(head.units, islice(head.units, 1, None)):
            after.position = before.position
            if after.position == new_position:
                global is_over
                is_over = True

        head_unit.position = new_position

def render_update(scene: Scene):
    for unit, rect, tween in scene.match_components(Unit, Rectangle, Tween):
        tween.start = Vec2(rect.position)
        tween.delta = unit.position * UNIT_SIZE - rect.position
        tween.time = 0

def input_system(scene: Scene):
    try:
        new_direction = next(key_settings[key_] for key_ in key_settings if keys[key_])
    except StopIteration:
        return
    
    for head in scene.get_components(Head):
        if head.direction.dot(new_direction) == 0:
            head.pre_direction = new_direction

def cubic_bezier(x1: float, y1: float, x2: float, y2: float, x: float,
        *, accuracy=0.05, left=0, right=1) -> float:
    t = x
    while True:
        current_x = 3 * (1-t) * t * (x1 + (x2-x1)*t) + t**3
        if isclose(current_x, x, rel_tol=accuracy):
            return 3 * (1-t) * t * (y1 + (y2-y1)*t) + t**3
        if x < current_x:
            right = t
            t = (left + t) / 2
        else:
            left = t
            t = (right + t) / 2

def tween_system(scene: Scene, dt: float):
    for tween in scene.get_components(Tween):
        if tween.time < tween.duration:
            tween.time += dt
            setattr(tween.component, tween.attr,
                tween.start + tween.delta * cubic_bezier(*tween.bezier, min(tween.time/tween.duration, 1)))

window = pyglet.window.Window(*MAP_SIZE*UNIT_SIZE, vsync=False)
fps = pyglet.window.FPSDisplay(window)
keys = key.KeyStateHandler()
window.push_handlers(keys)
batch = pyglet.graphics.Batch()

new_rect = partial(Rectangle, width=UNIT_SIZE, height=UNIT_SIZE, batch=batch)
def new_tween(rect: Rectangle) -> Tween:
    return Tween(rect, 'position',
        Vec2(rect.position), Vec2(rect.position),
        ANIMATION_BEZIER, INTERVAL, time=INTERVAL)

scene = Scene()

def init_game(dt, scene: Scene):
    unit = Unit(Vec2((0, 0)))
    rect = new_rect(*unit.position, color=HEAD_COLOR)
    scene.add_entity(unit,
        Head(unit),
        rect,
        new_tween(rect))

    rect = new_rect(6*UNIT_SIZE, 0, color=FOOD_COLOR)
    scene.add_entity(Unit(Vec2((6, 0))),
        Food(),
        rect,
        new_tween(rect))

def game_logic(dt, scene):
    move_system(scene)
    food_system(scene)
    render_update(scene)
    if is_over:
        pyglet.clock.unschedule(game_logic)

def main(dt, scene):
    input_system(scene)
    tween_system(scene, dt)
    window.clear()
    batch.draw()
    fps.draw()

pyglet.clock.schedule(main, scene)
pyglet.clock.schedule_interval_soft(game_logic, INTERVAL, scene)
pyglet.clock.schedule_once(init_game, 0, scene)
pyglet.app.run()