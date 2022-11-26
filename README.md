# pyecs

**简体中文** | [English](/README_EN.md)

---

一个简单灵活的 Python **实体-组件-系统**框架。

- 易于使用和与其他框架结合。
- 99% 类型注解，代码补全无处不在。

> 支持：Python 3.7+

## 设计

- **场景**

    `Scene` 是 pyecs 的主要类对象，作为实体和组件的管理者。

    ```python
    from pyecs import Scene

    scene = Scene()
    ```

- **实体**

    用来组织组件的唯一标识，在 pyecs 中只是一个整数。

    ```python
    entity = scene.add_entity()
    ```

    > 实体从 `0` 开始递增，同一实体只会出现一次。

- **组件**

    实体持有的数据，pyecs 支持任意类型的组件，每个实体仅能持有某个组件类型的一个实例。

    > 实体在内部被视为一个特殊的 `int` 类型组件，可以通过 `int` 类型像访问组件一样访问实体，但最好不要直接使用该类型的自定义组件。

    ```python
    class Position:
        ...

    class Velocity:
        ...

    scene.add_component(entity, Position())
    scene.add_component(entity, Velocity())

    # 或在添加实体时：
    # entity = scene.add_entity(Position(), Velocity())
    ```

- **系统**

    从场景中获取组件，执行逻辑。

    > pyecs 不是侵入式的框架，没有自己的系统管理。

    典型的系统是一个接受场景，利用组件的函数：

    ```python
    def move(scene: Scene):
        for position, velocity in scene.match_components(Position, Velocity):
            ...

    def render(scene: Scene):
        for position in scene.get_components(Position):
            ...
    ```

## 示例

一些使用 pyecs 的游戏[示例](/examples/)：

- [mine_sweeper](/examples/mine_sweeper.py) --- 终端界面的扫雷

> 以下示例结合了 [pyglet](https://github.com/pyglet/pyglet)，请先安装:
    `pip install pyglet`

- [snake](/examples/snake.py) --- 有动效的简易贪吃蛇

## 许可证

此项目使用 [MIT](/LICENSE) license 进行授权。