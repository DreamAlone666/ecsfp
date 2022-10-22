from collections import defaultdict
from functools import reduce
from itertools import count
from operator import and_, methodcaller
from typing import (Any, Callable, DefaultDict, Dict, Iterable, List, Optional,
                    Sequence, Set, Tuple, Type, TypeVar)

__all__ = [
    'Scene',
    'SystemGroup',
]

T = TypeVar('T')

class Scene:
    _entity_creator = count()
    
    def __init__(self):
        self.data: DefaultDict[type, Dict[int, Any]] = defaultdict(dict)
        self.systems: List[System] = []
    
    def add_entity(self, *components) -> int:
        ent = next(self._entity_creator)
        self.data[int][ent] = ent
        for comp in components:
            self.add_component(ent, comp)
        return ent
    
    def add_component(self, entity: int, component):
        self.data[type(component)][entity] = component
    
    def destroy_entity(self, entity: int):
        """Try destroying an entity with its components whether it exists or not."""
        for objs in self.data.values():
            objs.pop(entity, None)
    
    def destroy_component(self, entity: int, component):
        """Try destroying a component whether it exists or not."""
        self.data[type(component)].pop(entity)
    
    def get_components(self, type_: Type[T]) -> Iterable[T]:
        return tuple(self.data[type_].values())
    
    def get_components_group(self, *types: type):
        # Get entities common to types
        comp_dicts: Tuple[Dict[int, Any]] = tuple(map(self.data.__getitem__, types))
        entities: Set[int] = reduce(and_, map(dict.keys, comp_dicts))
        return tuple(tuple(map(methodcaller('__getitem__', entity), comp_dicts)) for entity in entities)
    
    def add_system(self, system: 'System'):
        """`system` should recive the `Scene` as the first parameter."""
        self.systems.append(system)

    def destroy_system(self, system: Callable):
        """Try destroying a system whether it exists or not."""
        try:
            self.systems.remove(system)
        except ValueError:
            return
    
    def tick(self):
        """Call all the systems."""
        for system in self.systems.copy():
            system(self)

System = Callable[[Scene], Any]

class SystemGroup:

    def __init__(self):
        self.systems: DefaultDict[Tuple[type, ...], List[System]] = defaultdict(list)

    def add(self, system: System, types: Optional[Sequence[type]] = None):
        """Add a `system` to the group.
        
        If `types` is kept `None`, the annotations of `system` will be used.
        """
        if types is None:
            types = self._get_types(system)
        self.systems[tuple(types)].append(system)
        return system
    
    def destroy(self, system: Callable):
        """Try destroying a system whether it exists or not."""
        for systems in self.systems.values():
            try:
                systems.remove(system)
                return
            except ValueError:
                continue

    def _get_types(self, system: Callable) -> Tuple[type, ...]:
        try:
            return getattr(system, '__annotations__')['comps'].__args__
        except KeyError:
            return ()
    
    def __call__(self, scene: Scene):
        for types, systems in self.systems.items():
            comps = scene.get_components_group(*types)
            for system in systems:
                system(scene, *comps)