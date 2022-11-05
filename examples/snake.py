from collections import deque
from dataclasses import dataclass, field
from functools import partial
from itertools import chain, islice, product
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

key_settings = {key.LEFT: Vec2((-1, 0)), key.RIGHT: Vec2((1, 0)),
    key.UP: Vec2((0, 1)), key.DOWN: Vec2((0, -1))}
is_over = False

@dataclass
class Unit:
    position: Vec2

@dataclass
class Head(Unit):
    direction: Vec2 = Vec2((1, 0))
    pre_direction: Vec2 = direction
    units: Deque[Unit] = field(init=False)

    def __post_init__(self):
        self.units = deque((self,))

class Body(Unit):
    pass

class Food(Unit):
    pass

def food_system(scene: Scene):
    foods = scene.get_components(Food)
    heads = scene.get_components(Head)
    for food, head in product(foods, heads):
        if food.position == head.position:
            food.position = Vec2(randint(0, size-1) for size in MAP_SIZE)

            body = Body(head.position)
            scene.add_entity(body,
                new_rect(*body.position, color=BODY_COLOR))
            head.units.appendleft(body)

def edge_solver(num, max_):
    if num >= max_:
        return 0
    if num < 0:
        return max_ - 1
    return num

def move_system(scene: Scene):
    for head in scene.get_components(Head):
        head.direction = head.pre_direction
        new_position = Vec2(map(edge_solver, head.position + head.direction, MAP_SIZE))
        for after, before in zip(head.units, islice(head.units, 1, None)):
            after.position = before.position
            if after.position == new_position:
                global is_over
                is_over = True

        head.position = new_position

def render_update(scene: Scene):
    heads = scene.get_components_group(Head, Rectangle)
    bodies = scene.get_components_group(Body, Rectangle)
    foods = scene.get_components_group(Food, Rectangle)
    for unit, rect in chain(heads, bodies, foods):
        rect.position = unit.position * UNIT_SIZE

def input_system(scene: Scene):
    try:
        new_direction = next(key_settings[key_] for key_ in key_settings if keys[key_])
    except StopIteration:
        return
    
    for head in scene.get_components(Head):
        if head.direction.dot(new_direction) == 0:
            head.pre_direction = new_direction

window = pyglet.window.Window(*MAP_SIZE*UNIT_SIZE, vsync=False)
fps = pyglet.window.FPSDisplay(window)
keys = key.KeyStateHandler()
window.push_handlers(keys)
batch = pyglet.graphics.Batch()
new_rect = partial(Rectangle, width=UNIT_SIZE, height=UNIT_SIZE, batch=batch)

scene = Scene()

scene.add_entity(Head(Vec2((0, 0))),
    new_rect(0, 0, color=HEAD_COLOR))
scene.add_entity(Food(Vec2((6, 0))),
    new_rect(6*UNIT_SIZE, 0, color=FOOD_COLOR))

def game_logic(dt, scene):
    move_system(scene)
    food_system(scene)
    render_update(scene)
    if is_over:
        pyglet.clock.unschedule(game_logic)

def main(dt, scene):
    input_system(scene)
    window.clear()
    batch.draw()
    fps.draw()

pyglet.clock.schedule(main, scene)
pyglet.clock.schedule_interval_soft(game_logic, INTERVAL, scene)
pyglet.app.run()