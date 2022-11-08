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

    for comp in scene.get_components(Type2):
        scene.destroy_component(ent, comp)
    assert comp2 not in scene.get_components(Type2)

    scene.destroy_entity(ent)
    assert comp1 not in scene.get_components(Type1)

def test_SystemList():
    scene = Scene()
    d = 0
    def func(scene: Scene):
        nonlocal d
        d = 1
    syslist = SystemList((func,))
    
    syslist(scene)
    assert d == 1