from pyecs import Scene, SystemList

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
    assert scene.has_component(ent, Type1) and scene.has_component(ent, Type2)

    for comp in scene.get_components(Type2):
        scene.destroy_component(ent, comp)
    assert comp2 not in scene.get_components(Type2)

    scene.destroy_entity(ent)
    assert comp1 not in scene.get_components(Type1)
    assert not (scene.has_component(ent, Type1) and scene.has_component(ent, Type2))

def test_Scene_match():
    scene = Scene()
    ent_to_comps = {}
    for _ in range(10):
        scene.add_entity(Type1())
        scene.add_entity(Type2())
        comps = Type1(), Type2()
        ent_to_comps[scene.add_entity(*comps)] = comps
    
    assert {(ent, *comp) for ent, comp in ent_to_comps.items()}\
        == set(scene.match_components(int, Type1, Type2))
    
    assert set(ent_to_comps.keys()) == scene.match_entities(Type1, Type2)

def test_SystemList():
    scene = Scene()
    d = 0
    def func(scene: Scene):
        nonlocal d
        d = 1
    syslist = SystemList((func,))
    
    syslist(scene)
    assert d == 1