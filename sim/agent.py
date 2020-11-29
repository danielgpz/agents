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

class ReactiveRobot(Robot):
    def find_path(self, env, cell):
        n, m = env.n, env.m
        x, y = self.x, self.y
        queue = [(x, y)]
        parent = {(x, y): (x, y)}
        for it in range(n * m):
            try:
                x, y = queue[it]
            except IndexError:
                break

            for d1, d2 in zip(dx[:4], dy[:4]):
                pos = (i, j) = (x + d1, y + d2)
                if (pos not in parent) and (0 <= i < n) and (0 <= j < m):
                    if (env.cells[i][j] <= Cell.Playpen):
                        queue.append(pos)
                        parent[pos] = (x, y)
                    if env.cells[i][j] == cell:
                        path = [pos, (x, y)]
                        while True:
                            last = path[-1]
                            plast = parent[last]
                            if last != plast:
                                path.append(plast)
                            else:
                                return path

    def action(self, perception):
        x, y = self.x, self.y
        cell = perception.cells[x][y]

        if cell == Cell.Dirt: return Action.Clean

        if not self.baby:
            path = self.find_path(perception, Cell.Baby)
            if path:
                i, j = path[-2]
                dif = (i - x, j - y)
                act, = (t for t, d in enumerate(zip(dx, dy)) if d == dif)
                return Action(act)

        if self.baby:
            if cell == Cell.Playpen: return Action.Drop
            path = self.find_path(perception, Cell.Playpen)
            if path:
                i, j = path[-2]
                dif = (i - x, j - y)
                act, = (t for t, d in enumerate(zip(dx, dy)) if d == dif)
                try:
                    ii, jj = path[-3]
                    dif2 = (ii - x, jj - y)
                    act2, = (t for t, d in enumerate(zip(dx[act::4], dy[act::4])) if d == dif2)
                    return Action(act + 4 * act2)
                except IndexError:
                    return Action(act)

        path = self.find_path(perception, Cell.Dirt)
        if path:
            i, j = path[-2]
            dif = (i - x, j - y)
            act, = (t for t, d in enumerate(zip(dx, dy)) if d == dif)
            return Action(act)

        return Action.Stay
