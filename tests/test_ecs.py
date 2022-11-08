from pyecs import Scene

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