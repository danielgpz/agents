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

    def get_direction_to(self, env, cell, doble_steep=False):
        n, m = env.n, env.m
        start, it = (self.x, self.y), 0
        queue = [start]
        parent = {}
        path = []
        while it < len(queue):
            x, y = queue[it]
            it += 1
            for d1, d2 in zip(dx[:4], dy[:4]):
                pos = (i, j) = (x + d1, y + d2)
                if (pos not in parent) and (0 <= i < n) and (0 <= j < m):
                    if (env.cells[i][j] <= Cell.Playpen):
                        queue.append(pos)
                        parent[pos] = (x, y)
                    if env.cells[i][j] == cell:
                        path = [pos, (x, y)]
                        while path[-1] != start: path.append(parent[path[-1]])
                        (i, j), (x, y) = path[-2:]
                        dif = (i - x, j - y)
                        act, = (t for t, d in enumerate(zip(dx[:4], dy[:4])) if d == dif)
                        if doble_steep and len(path) > 2:
                            ii, jj = path[-3]
                            dif2 = (ii - x, jj - y)
                            act2, = (t for t, d in enumerate(zip(dx[act::4], dy[act::4])) if d == dif2)
                            return Action(act + 4 * act2)
                        return Action(act)
            

    def __str__(self):
        return f'R[{self.x},{self.y}]' + ('(B)' if self.baby else '')

class Person(Robot):
    def action(self, perception):
        return Action(int(input('Action: ')))

class StaticRobot(Robot):
    def action(self, perception):
        return Action.Stay

class Kangaroo(Robot):
    def action(self, perception):
        x, y = self.x, self.y
        cell = perception.cells[x][y]

        if cell == Cell.Dirt: return Action.Clean

        if self.baby:
            if cell == Cell.Playpen: return Action.Drop
            direct = self.get_direction_to(perception, Cell.Playpen, doble_steep=True)
            if direct: return direct
        
        if not self.baby:
            direct = self.get_direction_to(perception, Cell.Baby)
            if direct: return direct
            
        direct = self.get_direction_to(perception, Cell.Dirt, doble_steep=self.baby is not None)
        if direct: return direct
        
        return Action.Stay

class Cleaner(Robot):
    def action(self, perception):
        x, y = self.x, self.y
        cell = perception.cells[x][y]

        if cell == Cell.Dirt: return Action.Clean

        if self.baby:
            if cell == Cell.Playpen: return Action.Drop
            direct = self.get_direction_to(perception, Cell.Playpen, doble_steep=True)
            if direct: return direct
               
        direct = self.get_direction_to(perception, Cell.Dirt, doble_steep=self.baby is not None)
        if direct: return direct
        
        if not self.baby:
            direct = self.get_direction_to(perception, Cell.Baby)
            if direct: return direct
         
        return Action.Stay