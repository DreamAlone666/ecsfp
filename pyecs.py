from collections import defaultdict
from functools import reduce
from itertools import count
from operator import and_
from typing import (TYPE_CHECKING, Any, Callable, DefaultDict, Dict, Iterable,
                    List, Set, Tuple, Type, TypeVar, overload)

__all__ = [
    'Scene',
    'SystemList',
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
    
    def add_entity(self, *components: Any) -> int:
        """Also calls `add_component` to add the given `components`."""
        ent = next(self._entity_creator)
        self.data[int][ent] = ent
        for comp in components:
            self.add_component(ent, comp)
        return ent
    
    def add_component(self, entity: int, component: Any):
        """The existing component of the same type will be replaced."""
        self.data[type(component)][entity] = component
    
    def destroy_entity(self, entity: int):
        """Try destroying `entity` with its components whether it exists or not."""
        for objs in self.data.values():
            objs.pop(entity, None)
    
    def destroy_component(self, entity: int, component: Any):
        """Try destroying `component` whether it exists or not."""
        self.data[type(component)].pop(entity)
    
    def get_component(self, entity: int, type_: Type[T]) -> T:
        """Raises `KeyError` if component does not exist."""
        return self.data[type_][entity]
    
    def get_components(self, type_: Type[T]) -> Iterable[T]:
        return tuple(self.data[type_].values())
    
    def has_component(self, entity: int, type_: type) -> bool:
        return entity in self.data[type_]

    if TYPE_CHECKING:
        @overload
        def match_components(self, t1: Type[T1], t2: Type[T2], /) -> Iterable[Tuple[T1, T2]]: ...
        @overload
        def match_components(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], /) -> Iterable[Tuple[T1, T2, T3]]: ...
        @overload
        def match_components(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], t4: Type[T4], /) -> Iterable[Tuple[T1, T2, T3, T4]]: ...
        @overload
        def match_components(self, t1: Type[T1], t2: Type[T2], t3: Type[T3], t4: Type[T4], t5: Type[T5], /) -> Iterable[Tuple[T1, T2, T3, T4, T5]]: ...
        @overload
        def match_components(self, *types:type) -> Iterable[Tuple[Any, ...]]: ...

    def match_components(self, *types: type) -> Iterable[Tuple[Any, ...]]:
        """Get components of given `types` that belong to the same entity."""
        # Get entities common to types
        comp_dicts: Tuple[Dict[int, Any], ...] = tuple(map(self.data.__getitem__, types))
        entities: Set[int] = reduce(and_, map(dict.keys, comp_dicts)) # type: ignore[arg-type]
        return tuple(zip(*[map(comp_dict.__getitem__, entities) for comp_dict in comp_dicts]))
    
    def match_entities(self, *types: type) -> Set[int]:
        """Get entities that has components of given `types`.
        
        Raises `IndexError` if no type is given.
        """
        if types[1:2]:
            return reduce(and_, map(dict.keys, map(self.data.__getitem__, types))) # type: ignore[arg-type]
        
        return set(self.data[types[0]].keys())

Sys_T = TypeVar('Sys_T', bound=Callable[..., Any])

class SystemList(List[Sys_T]):
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """Call all the systems with the given `args` and `kwargs`."""
        for system in self:
            system(*args, **kwargs)