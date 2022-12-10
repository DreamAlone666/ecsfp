# ecsfp

[简体中文](/README.md) | **English**

---

**ECS(Entity-Component-System) for Python, simple and flexible**

- Easy to use and be combined with other frameworks.
- 99% type annotated, completion everywhere.

> Only supports Python 3.7+ due to the use of type annotations.

## Installation

No dependencies, just put the [ecsfp](/ecsfp) folder into your project and use it.

It can also be installed as a package via the source code:

```shell
git clone https://github.com/DreamAlone666/ecsfp.git
pip install .
```

## Design

- **Scene**

    `Scene` is the main class of ecsfp as the manager of entities and components.

    ```python
    from ecsfp import Scene

    scene = Scene()
    ```

- **Entity**

    A unique identifier used to organize components, which is simply an integer in ecsfp.

    ```python
    entity = scene.add_entity()
    ```

    > Entities gradully increase from '0' and the same entity will only appear once.

- **Component**

    The data held by entities. ecsfp supports any type of component, but each entity can only hold one instance of a component type.

    > Entity is treated internally as a special `int` type component, which can be accessed like other components through the `int` type, but it is best not to use a custom component of that type directly.

    ```python
    class Position:
        ...

    class Velocity:
        ...

    scene.add_component(entity, Position())
    scene.add_component(entity, Velocity())

    # Or when adding an entity:
    # entity = scene.add_entity(Position(), Velocity())
    ```

- **System**

    To get components from the scene and perform the action.

    > ecsfp is not an intrusive framework and does not have its own system management.

    A typical system is a function which recieves scene and utilizes components:

    ```python
    def move(scene: Scene):
        for position, velocity in scene.match_components(Position, Velocity):
            ...

    def render(scene: Scene):
        for position in scene.get_components(Position):
            ...
    ```

## Example

There are some [examples](/examples/) of games that use ecsfp:

- [mine_sweeper](/examples/mine_sweeper.py) --- Minesweeper game in the terminal

> The following example combines [pyglet](https://github.com/pyglet/pyglet). Please have it installed:
    `pip install pyglet`

- [snake](/examples/snake.py) --- A simple snake game with animation effects

## License

This project is licensed under the [MIT](/LICENSE) license.