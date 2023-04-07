from random import randint


class Dot: # Класс точек игрового поля
    def __init__(self, x, y): # точка описывается координатами x и y
        self.x = x
        self.y = y

    def __eq__(self, other): # метод для проверки на равенство
        return self.x == other.x and self.y == other.y

    def __repr__(self): # вывод точки игрового поля в консоль
        return f"({self.x}, {self.y})"


class BoardException(Exception): # основной класс исключений
    pass


class BoardOutException(BoardException): # исключение выстрела вне игрового поля
    def __str__(self):
        return "Выcтрел вне игрового поля!"


class BoardUsedException(BoardException): # исключение повторного выстрела
    def __str__(self):
        return "В эту клетку вы уже стреляли"


class BoardWrongShipException(BoardException): # исключение для правильного расположения корабля на доске
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property # декоратор, позволяющий обращаться к точкам напрямую
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0: # горизонтальное расположение корабля, прирост координаты X
                cur_x += i

            elif self.o == 1: # вертикальное расположение корабля, прирост координаты Y
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=10): # задаем игровое поле с параметрами видимости и размера
        self.size = size
        self.hid = hid # видимость корабля на игровом поле

        self.count = 0 # стартовое значение хода

        self.field = [["o"] * size for _ in range(size)] # установка стартового символа клетки и размеров игрового поля

        self.busy = [] # список занятых точек игрового поля
        self.ships = [] # список кораблей

    def add_ship(self, ship): # метод добавления корабля на игровое поле

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False): # метод обвода контура корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10|\n"
        res += "   " + ("—" * 41)
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}  | " + " | ".join(row) + " |"
        
        if self.hid:
            res = res.replace("■", "o")
        return res

    def out(self, d): # описание расположения точки внутри игрового поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d): # исключение - выстрел вне игрового поля
            raise BoardOutException()

        if d in self.busy: # исключение - повторный выстрел в дянную точку
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self): # запрос выстрела
        raise NotImplementedError()

    def move(self): # запрос хода
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self): # метод хода компьютера, переопределен от метода родительского класса Player
        d = Dot(randint(0, 9), randint(0, 9))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self): # метод хода игрока, переопределен от метода родительского класса Player
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2: # если неправильно введены координаты выстрела
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()): # если координаты выстрела введены не числом
                print(" Введите 2 числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=10):
        self.size = size
        pl = self.random_board() # игровое поле игрока
        co = self.random_board() # игровое поле компьютера
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self): # генерация случайного игрового поля
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self): # описание типов (длин) кораблей на игровом поле
        lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("————————————————————")
        print("  Добро пожаловать  ")
        print("       в игру       ")
        print("     морской бой!   ")
        print("————————————————————")
        print(" формат ввода: x y  ")
        print(" x - номер строки   ")
        print(" y - номер столбца  ")


    def loop(self): # описание игрового цикла
        num = 0 # старт с 0
        while True:
            print("—" * 20)
            print("Доска игрока:")
            print(self.us.board) # отрисовка игровой доски игрока
            print("—" * 20)
            print("Доска компьютера:")
            print(self.ai.board) # отрисовка игровой доски компьютера
            if num % 2 == 0:
                print("—" * 20)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("—" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 10: # условие победы игрока
                print("—" * 20)
                print("Игрок выиграл!")
                break

            if self.us.board.count == 10: # условие победы компьютера
                print("—" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
