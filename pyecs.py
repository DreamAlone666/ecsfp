from collections import defaultdict
from functools import reduce
from inspect import signature
from itertools import count
from operator import and_, methodcaller
from typing import (TYPE_CHECKING, Any, Callable, DefaultDict, Dict, Iterable,
                    List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union,
                    cast, overload)

__all__ = [
    'Scene',
]

T = TypeVar('T')

if TYPE_CHECKING:
    T1 = TypeVar('T1')
    T2 = TypeVar('T2')
    T3 = TypeVar('T3')
    T4 = TypeVar('T4')
    T5 = TypeVar('T5')

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
    
    if TYPE_CHECKING:
        @overload
        def get_components_group(self, t1: Type[T1], t2: Type[T2], /) -> Iterable[Tuple[T1, T2]]: ...
        @overload
        def get_components_group(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], /) -> Iterable[Tuple[T1, T2, T3]]: ...
        @overload
        def get_components_group(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], t4: Type[T4], /) -> Iterable[Tuple[T1, T2, T3, T4]]: ...
        @overload
        def get_components_group(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], t4: Type[T4], t5: Type[T5], /) -> Iterable[Tuple[T1, T2, T3, T4, T5]]: ...
        @overload
        def get_components_group(self, *types:type) -> Iterable[Tuple[Any, ...]]: ...

    def get_components_group(self, *types: type) -> Iterable[Tuple[Any, ...]]:
        # Get entities common to types
        comp_dicts: Tuple[Dict[int, Any], ...] = tuple(map(self.data.__getitem__, types))
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