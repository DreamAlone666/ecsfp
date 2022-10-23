from collections import defaultdict
from functools import reduce
from inspect import signature
from itertools import count
from operator import and_, methodcaller
from typing import (Any, Callable, DefaultDict, Dict, Iterable, List, Optional,
                    Sequence, Set, Tuple, Type, TypeVar, Union, cast)

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
    
    def get_component(self, entity: int, type_: Type[T]) -> T:
        """Raise `KeyError` if component does not exist."""
        return self.data[type_][entity]
    
    def get_components(self, type_: Type[T]) -> Iterable[T]:
        return tuple(self.data[type_].values())
    
    def get_components_group(self, *types: type) -> Iterable[Tuple[Any, ...]]:
        # Get entities common to types
        comp_dicts: Tuple[Dict[int, Any]] = tuple(map(self.data.__getitem__, types))
        entities: Set[int] = reduce(and_, map(dict.keys, comp_dicts))
        return tuple(
            tuple(comp_dict[entity] for comp_dict in comp_dicts)
            for entity in entities)
    
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
GroupSystem = Callable[[Scene, Iterable[Tuple[Any, ...]]], Any]

class SystemGroup:

    def __init__(self):
        self.no_comps_systems: List[System] = []
        self.systems: DefaultDict[Tuple[type, ...], List[GroupSystem]] = defaultdict(list)

    def add(self,
            system: Union[System, GroupSystem],
            types: Optional[Sequence[type]] = None):
        """Add a `system` to the group.
        
        If `types` is kept `None`, the annotations of `system` will be used.
        """
        if 'comps' not in signature(system).parameters:
            self.no_comps_systems.append(cast(System, system))

        else:
            if types is None:
                types = self._get_types(system)
            self.systems[tuple(types)].append(cast(GroupSystem, system))

        return system
    
    def destroy(self, system: Callable):
        """Try destroying a system whether it exists or not."""
        if 'comps' not in signature(system).parameters:
            try:
                return self.no_comps_systems.remove(system)
            except ValueError:
                pass
        
        try:
            self.systems[self._get_types(system)].remove(system)
        except ValueError or KeyError:
            pass

    def _get_types(self, system: Callable) -> Tuple[type, ...]:
        return getattr(system, '__annotations__')['comps'].__args__[0].__args__
    
    def __call__(self, scene: Scene):
        for system in self.no_comps_systems:
            system(scene)

        for types, systems in self.systems.items():
            comps = scene.get_components_group(*types)
            for system in systems:
                system(scene, comps)