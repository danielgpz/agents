from .environtment import Cell, Action, dx, dy
from random import choice

class Agent:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    def set(self, x: int, y: int):
        self.x, self.y = x, y

    def at(self, x: int, y: int):
        return self.x == x and self.y == y

    def action(self, percetion):
        return NotImplementedError()


class Baby(Agent):
    def action(self, perception):
        actions = [Action.Stay]
        x, y = self.x, self.y
        if perception.cells[x][y] == Cell.Baby:
            n, m = perception.n, perception.m
            for action in [Action.Up, Action.Down, Action.Left, Action.Right]:
                i, j = x + dx[action], y + dy[action]
                if (0 <= i < n) and (0 <= j < m) and perception.cells[i][j] in [Cell.Free, Cell.Obstacle]:
                    actions.append(action)
        return choice(actions)

    def __str__(self):
        return f'B[{self.x},{self.y}]'

class Robot(Agent):
    def __init__(self):
        super().__init__()
        self.baby = None

    def set(self, x: int, y: int):
        super().set(x, y)
        if self.baby: self.baby.set(x, y)

    def hold(self, baby: Baby):
        assert not self.baby, 'Already holding a baby!'
        self.baby = baby

    def drop(self):
        assert self.baby, 'There is no baby to drop!'
        baby = self.baby
        self.baby = None
        return baby

    def __str__(self):
        return f'R[{self.x},{self.y}]' + ('(B)' if self.baby else '')

class Person(Robot):
    def action(self, perception):
        return Action(int(input('Action: ')))

class StaticRobot(Robot):
    def action(self, perception):
        return Action.Stay
