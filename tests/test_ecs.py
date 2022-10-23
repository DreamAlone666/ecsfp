from typing import Iterable, Tuple
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

    assert comp1 is scene.get_component(ent, Type1)
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
    def groupsystem(scene, comps: Iterable[Tuple[Type1,Type2]]):
        pass

    types1 = sysgroup._get_types(groupsystem)
    assert (Type1, Type2) == types1

    sysgroup.add(groupsystem, types1)
    assert groupsystem in sysgroup.systems[types1]

    @sysgroup.add
    def system(scene):
        pass
    assert system in sysgroup.no_comps_systems

    sysgroup.destroy(groupsystem)
    assert groupsystem not in sysgroup.systems[types1]
    sysgroup.destroy(system)
    assert system not in sysgroup.no_comps_systems

def test_SystemGroup_tick():
    scene = Scene()
    ent = scene.add_entity(Type2(), Type1())
    sysgroup = SystemGroup()
    d = {'system': 'before_tick', 'groupsystem': 'before_tick'}

    @sysgroup.add
    def system(scene):
        d['system'] = 'after_tick'
    @sysgroup.add
    def groupsystem(scene, comps: Iterable[Tuple[int,Type1,Type2]]):
        for entity, type1, type2 in comps:
            assert entity == ent
            assert type(type1) is Type1
            assert type(type2) is Type2
            d['groupsystem'] = 'after_tick'

    sysgroup(scene)
    assert d['system'] == 'after_tick'
    assert d['groupsystem'] == 'after_tick'