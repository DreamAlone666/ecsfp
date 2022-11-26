# pyecs

[简体中文](/README.md) | **English**

---

A simple and flexible **Entity-Component-System** framework for Python.

- Easy to use and be combined with other frameworks.
- 99% type annotated, completion everywhere.

> Support: Python 3.7+

## Design

- **Scene**

    `Scene` is the main class of pyecs as the manager of entities and components.

    ```python
    from pyecs import Scene

    scene = Scene()
    ```

- **Entity**

    A unique identifier used to organize components, which is simply an integer in pyecs.

    ```python
    entity = scene.add_entity()
    ```

    > Entities gradully increase from '0' and the same entity will only appear once.

- **Component**

    The data held by entities. pyecs supports any type of component, but each entity can only hold one instance of a component type.

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

    > pyecs is not an intrusive framework and does not have its own system management.

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

There are some [examples](/examples/) of games that use pyecs:

- [mine_sweeper](/examples/mine_sweeper.py) --- Minesweeper game in the terminal

> The following example combines [pyglet](https://github.com/pyglet/pyglet). Please have it installed:
    `pip install pyglet`

- [snake](/examples/snake.py) --- A simple snake game with animation effects

## License

This project is licensed under the [MIT](/LICENSE) license.