from enum import IntEnum
from random import random, randint, choice, choices, shuffle, expovariate

Cell = IntEnum('Cell type', ['Free',  'Dirt', 'Playpen', 'Baby', 'SetBaby', 'Obstacle', 'Robot'], start=0)
CellSymbols = ['.', '¤', '©', 'õ', 'Õ', '#', 'ÿ']
Action = IntEnum('Move type', [
                            'Up'     , 'Down'     , 'Left'      , 'Right'     ,  
                            'UpRight', 'DownLeft' , 'LeftUp'    , 'RightDown' ,   
                            'UpLeft' , 'DownRight', 'LeftDown'  , 'RightUp'   ,
                            'UpUp'   , 'DownDown' , 'LeftLeft'  , 'RightRight',
                            'Clean', 'Drop', 'Stay'], start=0)

dx = [-1, 1, 0, 0, -1, 1, -1, 1, -1, 1, 1, -1, -2, 2, 0, 0]
dy = [0, 0, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 0, 0, -2, 2]

class KinderGarden:
    def __init__(self, n: int, m: int, dirt_p: int, obstacle_p: int, babies: list, robots: list, t: int):
        self.n, self.m, self.t = n, m, t
        area = n * m
        dirt_count = int(area * dirt_p / 100)
        obstacle_count = int(area * obstacle_p / 100)
        baby_count = len(babies)
        playpen_count = baby_count
        robot_count = len(robots)
        assert max(dirt_count + playpen_count, robot_count) + obstacle_count + baby_count <= area, 'Impossible build environment!'

        self.cells = [[Cell.Free] * m for _ in range(n)]
        self.babies = list(babies)
        self.robots = list(robots)

        cells = [Cell.Baby] * baby_count + [Cell.Dirt] * dirt_count  + [Cell.Obstacle] * obstacle_count  + [Cell.Playpen] * playpen_count
        for pos, cell in enumerate(cells):
            i, j = pos // m, pos % m
            self.cells[i][j] = cell
            if cell == Cell.Baby:
                self.babies[pos].set(i, j)

        self.variate()

    def action_robot(self, robot, action):
        x, y = robot.x, robot.y
        if action == Action.Clean:
            assert self.cells[x][y] == Cell.Dirt, f'Bad Move: {robot}-> {repr(action)}'
            self.cells[x][y] = Cell.Robot
        elif action == Action.Drop:
            assert self.cells[x][y] in [Cell.Robot, Cell.Playpen], f'Bad Move: {robot}-> {repr(action)}'
            robot.drop()
            self.cells[x][y] = Cell.SetBaby if self.cells[x][y] == Cell.Playpen else Cell.Baby
        elif Action.Up <= action <= Action.RightRight:
            ii, jj = x + dx[action % 4], y + dy[action % 4]
            i, j = x + dx[action], y + dy[action]
            assert ((ii, jj) == (i, j) or ((0 <= ii < self.n) and (0 <= jj < self.m) and (self.cells[ii][jj] <= Cell.Playpen) and robot.baby)) \
                and (0 <= i < self.n) and (0 <= j < self.m) and self.cells[i][j] <= Cell.Baby, \
                f'Bad Move: {robot}-> {repr(action)}'
            if self.cells[i][j] == Cell.Baby:
                baby, = (baby for baby in self.babies if baby.at(i, j))
                robot.hold(baby)
                self.cells[i][j] = Cell.Robot
            elif self.cells[i][j] == Cell.Free:
                self.cells[i][j] = Cell.Robot
            self.cells[x][y] = Cell.Free if self.cells[x][y] == Cell.Robot else self.cells[x][y]
            robot.set(i, j)

    def action_baby(self, baby, action):
        x, y = baby.x, baby.y
        if action <= Action.Right:
            i, j = x + dx[action], y + dy[action]
            assert self.cells[x][y] == Cell.Baby and (0 <= i < self.n) and (0 <= j < self.m) \
                and self.cells[i][j] in [Cell.Free, Cell.Obstacle],  f'Bad Move: {baby}-> {repr(action)}'
            if self.cells[i][j] == Cell.Obstacle:
                ii, jj = i, j
                while (0 <= ii < self.n) and (0 <= jj < self.m) and self.cells[ii][jj] == Cell.Obstacle:
                    ii += dx[action]
                    jj += dy[action]
                if (0 <= ii < self.n) and (0 <= jj < self.m) and self.cells[ii][jj] == Cell.Free:
                    self.cells[ii][jj] = self.cells[i][j]
                else:
                    i, j = x, y
            self.cells[x][y] = Cell.Free
            self.cells[i][j] = Cell.Baby
            baby.set(i, j)
            if (x, y) != (i, j) and (0 < x < self.n - 1) and (0 < y < self.m - 1):
                patch = [(x, y)] + [(x + d1, y + d2) for d1, d2 in zip(dx[:8], dy[:8])]
                nbs = 2 * sum(1 for x1, x2 in patch if self.cells[x1][x2] == Cell.Baby) - 1
                dirts = min(int(expovariate(1)), nbs)
                patch = [(x1, x2) for x1, x2 in patch if self.cells[x1][x2] == Cell.Free]
                shuffle(patch)
                for (x1, x2), _ in zip(patch, range(dirts)):
                    self.cells[x1][x2] = Cell.Dirt 
        elif action != Action.Stay:
            assert False, f'Bad Move: {baby}-> {repr(action)}'

    def variate(self, counts=None):
        set_babies = [baby for baby in self.babies if self.cells[baby.x][baby.y] == Cell.SetBaby]
        free_babies = [baby for baby in self.babies if self.cells[baby.x][baby.y] == Cell.Baby]

        if not counts: counts = self.get_stats()       
        self.cells = [[Cell.Free] * self.m for _ in range(self.n)]
        playpen = [(randint(0, self.n-1), randint(0, self.m-1))]
        for pos, _ in enumerate(self.babies):
            i, j = playpen[pos]
            if pos < counts[Cell.SetBaby]:
                self.cells[i][j] = Cell.SetBaby
                set_babies[pos].set(i, j)  
            else:
                self.cells[i][j] = Cell.Playpen
            nbs = list(zip(dx[:4], dy[:4]))
            shuffle(nbs)
            for x, y in nbs:
                ii, jj = i + x, j + y
                if (0 <= ii < self.n) and (0 <= jj < self.m) and (ii, jj) not in playpen:
                    playpen.append((ii, jj))
            pos += 1

        free_cells = [(i, j) for i in range(self.n) for j in range(self.m) if self.cells[i][j] == Cell.Free]
        ocupied_cells = [Cell.Dirt] * counts[Cell.Dirt] + [Cell.Obstacle] * counts[Cell.Obstacle]
        shuffle(free_cells)
        for (i, j), cell in zip(free_cells, ocupied_cells):
            self.cells[i][j] = cell
        for (i, j), baby in zip(free_cells[len(ocupied_cells):], free_babies):
            self.cells[i][j] = Cell.Baby
            baby.set(i, j)
        free_cells = [(i, j) for i in range(self.n) for j in range(self.m) if self.cells[i][j] <= Cell.Playpen]
        shuffle(free_cells)
        for (i, j), robot in zip(free_cells, self.robots):
            self.cells[i][j] = Cell.Robot if self.cells[i][j] == Cell.Free else self.cells[i][j]
            robot.set(i, j)

    def get_stats(self):
        counts = [0] * len(Cell)
        for row in self.cells:
            for cell in row:
                counts[cell] += 1
        return counts

    def simulate(self, iters=100, verbose=True):
        if verbose: print(f'Start environtment:', self, sep='\n')
        dirt_percents = []
        for ti in range(iters):
            for tj in range(self.t):
                if verbose: print(f'Turn: {ti * iters + tj}')
                for robot in self.robots:
                    act = robot.action(self)
                    self.action_robot(robot, act)

                for baby in self.babies:
                    act = baby.action(self)
                    self.action_baby(baby, act)

                if verbose: print(self)
                
                counts = self.get_stats()
                dp = counts[Cell.Dirt] / (counts[Cell.Dirt] + counts[Cell.Free])
                dirt_percents.append(dp)
                if dp > 0.6:
                    return -1, sum(dirt_percents)/len(dirt_percents)
                if counts[Cell.SetBaby] == len(self.babies) and dp == 0:
                    return 1, sum(dirt_percents)/len(dirt_percents)
            self.variate(counts=counts)
            if verbose: print(f'Varaition: {ti}', self, sep='\n')
        return int(counts[Cell.SetBaby] == len(self.babies) and dp < 0.4), sum(dirt_percents)/len(dirt_percents)


    def __str__(self):
        tbl = [[f'{CellSymbols[cell]} 'for cell in row] for row in self.cells]
        for robot in self.robots:
            i, j = robot.x, robot.y
            sym = CellSymbols[-1].upper() if robot.baby else CellSymbols[-1]
            if self.cells[i][j] != Cell.Robot:
                tbl[i][j] = tbl[i][j][:-1] + sym
            else:
                tbl[i][j] = f'.{sym}'
        return '\n'.join(' '.join(row) for row in tbl)

