class Table:
    def __init__(
            self,
            limit_type,
            variant_type,
            stakes,
            buy_in_amounts,
            seat_count,
            nature_time,
            player_time,
            reset_time,
            min_player_count=2,
    ):
        self.__limit_type = limit_type
        self.__variant_type = variant_type
        self.__stakes = stakes
        self.__buy_in_amounts = buy_in_amounts
        self.__seats = tuple(Seat(self) for _ in seat_count)

        self.__nature_time = nature_time
        self.__player_time = player_time
        self.__reset_time = reset_time

        self.__min_player_count = min_player_count

        self.__game = None

    @property
    def limit_type(self):
        return self.__limit_type

    @property
    def variant_type(self):
        return self.__variant_type

    @property
    def stakes(self):
        return self.__stakes

    @property
    def buy_in_amounts(self):
        return self.__buy_in_amounts

    @property
    def seats(self):
        return self.__seats

    @property
    def nature_time(self):
        return self.__nature_time

    @property
    def player_time(self):
        return self.__player_time

    @property
    def reset_time(self):
        return self.__reset_time

    @property
    def min_player_count(self):
        return self.__min_player_count

    @property
    def game(self):
        return self.__game

    def is_playing(self):
        return self.game is not None

    def has_seat(self, user_info):
        try:
            self.get_seat(user_info)
        except ValueError:
            return False

        return True

    def get_seat(self, user_info):
        for seat in self.seats:
            if seat.user.info == user_info:
                return seat

        raise ValueError('User is not seated')

    def parse(self, user, command):
        ...


class Seat:
    def __init__(self, table):
        self.__table = table
        self.__user = None
        self.__index = None
        self.__pending_buy_in = None

    @property
    def table(self):
        return self.__table

    @property
    def user(self):
        return self.__user

    @property
    def index(self):
        return self.__index

    @property
    def pending_buy_in(self):
        return self.__pending_buy_in

    def seat(self, user_info):
        if self.user is not None:
            raise ValueError('The seat is already occupied')

        self.__user = User(self, user_info)

    def unseat(self):
        self.__user = None


class User:
    def __init__(self, seat, info):
        self.__seat = seat
        self.__info = info
        self.__index = None
        self.__buy_in = None

    @property
    def table(self):
        return self.seat.table

    @property
    def seat(self):
        return self.__seat

    @property
    def info(self):
        return self.__info

    @property
    def index(self):
        return self.__index

    @property
    def buy_in(self):
        return self.__buy_in

    @property
    def player(self):
        if self.index is None:
            raise ValueError('The user is not a player')

        return self.table.game.players[self.index]

    def is_player(self):
        return self.index is not None

    def parse(self, command):
        ...
