from random import randint
from random import getrandbits


class SeaBattleExceptions(Exception):
    pass


class BoardOutException(SeaBattleExceptions):
    def __str__(self):
        return "Вы стреляете за пределы поля!"


class ShotTwiceException(SeaBattleExceptions):
    def __str__(self):
        return "Вы сюда уже стреляли!"


class ShipOutException(SeaBattleExceptions):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

    def __str__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, length, head, horizontal):
        self.length = length
        self.head = head
        self.horizontal = horizontal
        self.hp = length

    @property
    def dots(self):
        result = []
        for _ in range(self.length):
            current_dot_x = self.head.x
            current_dot_y = self.head.y
            if self.horizontal:
                current_dot_y += _
            else:
                current_dot_x += _
            result.append(Dot(current_dot_x, current_dot_y))
        return result


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid

        self.field = [['~'] * size for _ in range(size)]
        self.ships = []
        self.busy = []
        self.shoten_dots = []
        self.ship_count = 0

    def add_ship(self, ship):
        for d in ship.dots:
            if d in self.busy or self.out(d):
                raise ShipOutException

        for d in ship.dots:
            self.field[d.y][d.x] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.ship_count += 1

    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)

    def contour(self, ship, show=False):
        contour_cords = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for cx, cy in contour_cords:
                c_dot = Dot(d.x + cx, d.y + cy)
                if c_dot not in self.busy and not self.out(c_dot):
                    if show:
                        self.field[c_dot.y][c_dot.x] = '.'
                        self.shoten_dots.append(Dot(c_dot.x, c_dot.y))
                    self.busy.append(c_dot)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.shoten_dots:
            raise ShotTwiceException()
        self.busy.append(dot)
        self.shoten_dots.append(dot)
        for ship in self.ships:
            if dot in ship.dots:
                self.field[dot.y][dot.x] = 'X'
                ship.hp -= 1
                if ship.hp == 0:
                    print('Корабль потоплен!')
                    self.contour(ship, show=True)
                    self.ship_count -= 1
                else:
                    print('Корабль повреждён!')
                return True
            self.field[dot.y][dot.x] = '.'
        print('Мимо')
        return False

    def __str__(self):
        _out = ''
        for _ in range(self.size + 1):
            _out += f'{_} | '
        for i, j in enumerate(self.field):
            _out += f'\n{i + 1} | ' + ' | '.join(j) + ' |'
        if self.hid:
            _out = _out.replace('■', '~')
        return _out

    def set_busy(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        try:
            if not self.enemy_board.shot(self.ask()):
                return True
        except SeaBattleExceptions as err:
            print(err)


class AI(Player):
    def ask(self):
        return Dot(randint(0, self.board.size - 1), randint(0, self.board.size - 1))


class User(Player):
    def ask(self):
        while True:
            x = input('X: ')
            if not x.isdigit():
                print('Введите целое число!!!')
                continue
            x = int(x)
            y = input('Y: ')
            if not y.isdigit():
                print('Введите целое число!!!')
                continue
            y = int(y)
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self):
        self.user_board = False
        self.ai_board = False
        while not self.user_board:
            self.user_board = self.random_board
        while not self.ai_board:
            self.ai_board = self.random_board
            self.ai_board.hid = True        # <-------------------------ЧИТ КОД ТУТ
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    @staticmethod
    def greet():
        print('''Приветствую Вас в игре Морской Бой!
Ниже Вы видите два поля: первое - Ваше, второе - поле компьютера.
На обоих полях расположено 7 кораблей: один трёхпалубный, два двухпалубных и четыре однопалубных.
Ваша задача - подбить все корабли на поле противника раньше, чем уничтожат ваши корабли.
Стрельба ведётся по очереди, при попадании Вы стреляете до тех пор, пока не промахнётесь.
Для выстрела введите сначала координату Х, далее Enter, потом координату Y и вновь Enter.
Вы ходите первым. Удачи!
        ''')

    @property
    def random_board(self):
        board = Board()
        ship_size_list = [3, 2, 2, 1, 1, 1, 1]
        for ship_size in ship_size_list:
            counter = 0
            while True:
                try:
                    ship = Ship(ship_size, Dot(randint(0, board.size), randint(0, board.size)), bool(getrandbits(1)))
                    board.add_ship(ship)
                    board.contour(ship)
                    break
                except SeaBattleExceptions:
                    counter += 1
                    if counter > 1000:
                        return False
                    continue
        board.set_busy()
        return board

    def loop(self):
        while True:
            print(f'Ваше поле: \n{self.user_board}\nОсталось кораблей: {self.user_board.ship_count}')
            print(f'Поле противника: \n{self.ai_board}\nОсталось кораблей: {self.ai_board.ship_count}')
            if not self.ai_board.ship_count:
                return 'Победа!'
            if not self.user_board.ship_count:
                return 'Вы проиграли!'
            if not self.user.move():
                continue
            if not self.ai.move():
                continue

    def start(self):
        self.greet()
        return self.loop()


if __name__ == '__main__':
    while True:
        game = Game()
        print(game.start())
        if input('Напиши "stop", чтобы закончить. Любая другая строка - повторить игру. ') == 'stop':
            break
