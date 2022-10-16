from typing import Tuple
from pyecs import Scene, SystemGroup

class Type1:
    pass

class Type2:
    pass

def test_Scene():
    scene = Scene()
    comp1, comp2 = Type1(), Type2()

    ent = scene.add_entity(comp1, comp2)
    assert ent != scene.add_entity()

    assert comp1 in scene.get_components(Type1)
    assert comp2 in scene.get_components(Type2)

    for comp in scene.get_components(Type2):
        scene.destroy_component(ent, comp)
    assert comp2 not in scene.get_components(Type2)

    scene.destroy_entity(ent)
    assert comp1 not in scene.get_components(Type1)

def test_Scene_tick():
    scene = Scene()
    d = {'value': 'before_tick'}
    def func(scene):
        d['value'] = 'after_tick'
    
    scene.add_system(func)
    scene.tick()
    assert d['value'] == 'after_tick'

def test_SystemGroup():
    sysgroup = SystemGroup()
    def func1(*comps:Tuple[Type1,Type2]):
        pass

    types1 = sysgroup._get_types(func1)
    assert (Type1, Type2) == types1

    sysgroup.add(func1, types1)
    assert func1 in sysgroup.systems[types1]

    @sysgroup.add
    def func2(*comps:Tuple[Type2,Type1]):
        pass
    assert func2 in sysgroup.systems[sysgroup._get_types(func2)]

    sysgroup.destroy(func1)
    assert func1 not in sysgroup.systems[types1]

def test_SystemGroup_tick():
    scene = Scene()
    ent = scene.add_entity(Type2(), Type1())
    sysgroup = SystemGroup()
    d = {'value': 'before_tick'}

    @sysgroup.add
    def func(*comps:Tuple[int,Type1,Type2]):
        for entity, type1, type2 in comps:
            assert entity == ent
            assert type(type1) is Type1
            assert type(type2) is Type2
            d['value'] = 'after_tick'
    sysgroup(scene)
    assert d['value'] == 'after_tick'