from itertools import product, repeat
from random import shuffle
from typing import List

from pyecs import Scene

SIZE = 9, 9
MINE_NUM = 9

class TagMeta(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = super().__call__()

    def __call__(self):
        return self._instance

class Reveal(metaclass=TagMeta): pass

class MineNum(int):
    __slots__ = ()

GameMap = List[List[int]]

def get_around_index(x: int, y: int):
    for ax, ay in product(range(max(0, x-1), min(x+2, SIZE[0])), range(max(0, y-1), min(y+2, SIZE[1]))):
        if x == ax and y == ay:
            continue

        yield ax, ay

def new_game_map() -> GameMap:
    game_map = [*repeat(-1, MINE_NUM), *repeat(0, SIZE[0]*SIZE[1] - MINE_NUM)]
    shuffle(game_map)
    game_map = [list(row) for row in zip(*repeat(iter(game_map), SIZE[1]))]

    for x, y in product(range(SIZE[0]), range(SIZE[1])):
        if game_map[x][y] == -1:
            for ax, ay in get_around_index(x, y):
                if game_map[ax][ay] != -1:
                    game_map[ax][ay] += 1
    
    return game_map

def init_game(scene: Scene) -> GameMap:
    game_map = new_game_map()
    for x, y in product(range(SIZE[0]), range(SIZE[1])):
        game_map[x][y] = scene.add_entity(MineNum(game_map[x][y]))
    
    return game_map

def update_str(scene: Scene):
    reveals = scene.match_entities(MineNum, Reveal)
    hidens = scene.match_entities(MineNum) - reveals
    for r_ent in reveals:
        num = scene.get_component(r_ent, MineNum)
        scene.add_component(r_ent, ' ' if num == 0 else str(num))
    for h_ent in hidens:
        scene.add_component(h_ent, '*')

def reveal(scene: Scene, game_map: GameMap, x: int, y: int):
    to_reveal = {(x, y)}
    while to_reveal:
        x, y = to_reveal.pop()
        ent = game_map[x][y]
        if scene.has_component(ent, Reveal):
            continue

        if scene.get_component(ent, MineNum) == 0:
            to_reveal.update(get_around_index(x, y))
        
        scene.add_component(ent, Reveal())

def is_over(scene: Scene) -> bool:
    reveals = scene.match_entities(MineNum, Reveal)
    for r_ent in reveals:
        if scene.get_component(r_ent, MineNum) == -1:
            return True
    
    if len(reveals) == SIZE[0] * SIZE[1] - MINE_NUM:
        return True
    
    return False

scene = Scene()
game_map = init_game(scene)

while True:
    update_str(scene)

    print('\n X', *range(SIZE[0]), sep=' ')
    print('Y')
    for row, line in enumerate(zip(*game_map)):
        print(f'{row} ', *map(scene.get_component, line, repeat(str)))
    
    if is_over(scene):
        print("Game Over!")
        break

    x = int(input('X: '))
    y = int(input('Y: '))
    if x < 0 or x > SIZE[0] or y < 0 or y > SIZE[1]:
        continue

    reveal(scene, game_map, int(x), int(y))