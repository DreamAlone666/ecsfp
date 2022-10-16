from typing import Any, Iterable, Type, TypeVar
from collections import defaultdict
from itertools import count

__all__ = [
    'Scene'
]

T = TypeVar('T')

class Scene:
    _entity_creator = count()
    
    def __init__(self):
        self.data:defaultdict[type,dict[int,Any]] = defaultdict(dict)
    
    def add_entity(self, *components) -> int:
        ent = next(self._entity_creator)
        self.data[int][ent] = ent
        for comp in components:
            self.add_component(ent, comp)
        return ent
    
    def add_component(self, entity:int, component):
        self.data[type(component)][entity] = component
    
    def destroy_entity(self, entity:int):
        """Try destroying an entity with its components whether it exist or not."""
        for objs in self.data.values():
            objs.pop(entity, None)
    
    def destroy_component(self, entity:int, component):
        """Try destroying a component whether it exist or not."""
        self.data[type(component)].pop(entity)
    
    def get_components(self, type_:Type[T]) -> Iterable[T]:
        return tuple(self.data[type_].values())