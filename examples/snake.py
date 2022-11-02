from collections import deque
from dataclasses import dataclass, field
from itertools import islice, product
from random import randint
from typing import Deque
from pyecs import Scene

class Vec2(tuple):
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

map_size = Vec2((10, 10))

@dataclass
class Unit:
    position: Vec2

@dataclass
class Head(Unit):
    direction: Vec2 = Vec2((1, 0))
    units: Deque[Unit] = field(init=False)

    def __post_init__(self):
        self.units = deque((self,))

@dataclass
class Body(Unit):
    pass

@dataclass
class Food(Unit):
    pass

scene = Scene()

def food_system(scene: Scene):
    foods = scene.get_components(Food)
    heads = scene.get_components(Head)
    for food, head in product(foods, heads):
        if food.position == head.position:
            food.position = Vec2(randint(0, size) for size in map_size)

            body = Body(head.position)
            scene.add_entity(body)
            head.units.appendleft(body)

def move_snakes(scene: Scene):
    for entity, head in scene.get_components_group(int, Head):
        new_position = head.position + head.direction
        for after, before in zip(head.units, islice(head.units, 1, None)):
            after.position = before.position
            if after.position == new_position:
                raise
        head.position = new_position

snake = scene.add_entity(Head(Vec2((0, 0))))
for _ in range(3):
    body = Body(Vec2((0, 0)))
    scene.add_entity(body)
    scene.get_component(snake, Head).units.appendleft(body)
scene.add_entity(Food(Vec2((6, 0))))

while input() == '':
    print(f'Snake: {scene.get_component(snake, Head).position}')
    for body in scene.get_components(Body):
        print(body.position)
    for food in scene.get_components(Food):
        print(f'Food: {food.position}')
    food_system(scene)
    move_snakes(scene)