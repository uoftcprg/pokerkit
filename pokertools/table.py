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
    ):
        self.__limit_type = limit_type
        self.__variant_type = variant_type
        self.__stakes = stakes
        self.__buy_in_amounts = buy_in_amounts
        self.__seats = tuple(Seat(self) for _ in seat_count)

        self.__nature_time = nature_time
        self.__player_time = player_time
        self.__reset_time = reset_time

        self._game = None

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
    def game(self):
        return self._game

    def is_playing(self):
        return self.game is not None

    def has_seat(self, user_info):
        try:
            self.get_seat(user_info)
        except ValueError:
            return False

        return True

    def get_seat(self, user_info):
        for seat in filter(Seat.is_occupied, self.seats):
            if seat.user.info == user_info:
                return seat

        raise ValueError('User is not seated')

    def parse(self, user_info, command):
        self._parse(user_info, command)
        self._update()

    def create_game(self):
        ...  # TODO

    def remove_game(self):
        ...  # TODO

    def autoplay(self):
        ...  # TODO

    def _parse_user(self, user_info, command):
        ...

    def _parse_root(self, user_info, command):
        if command == 'c':
            if user_info is not None:
                raise ValueError('Users can\'t use this command')

            self.create_game()
        elif command == 'r':
            if user_info is not None:
                raise ValueError('Users can\'t use this command')

            self.remove_game()
        elif command == 'a':
            if user_info is not None:
                raise ValueError('Users can\'t use this command')

            self.autoplay()
        elif command.startswith('s '):
            self.seats[int(command[2:])].seat(user_info)
        elif command == 'us':
            self.get_seat(user_info).unseat()
        elif command.startswith('b '):
            self.get_seat(user_info).user.buy_in(int(command[2:]))
        elif self.get_seat(user_info).user.player == self.game.actor:
            self.game.parse(command)
        else:
            raise ValueError(f'Unknown command: {command}')

    def _update(self):
        ...  # TODO


class Seat:
    def __init__(self, table):
        self.__table = table
        self.__user = None

    @property
    def table(self):
        return self.__table

    @property
    def user(self):
        return self.__user

    def seat(self, user_info):
        if self.is_occupied():
            raise ValueError('The seat is already occupied')

        self.__user = User(self, user_info)

    def unseat(self):
        self.__user = None

    def is_occupied(self):
        return self.user is None


class User:
    def __init__(self, seat, info):
        self.__seat = seat
        self.__info = info
        self.__index = None
        self.__buy_in_amount = None
        self.__active_status = True

    @property
    def player(self):
        if not self.is_player():
            raise ValueError('The user is not a player')

        return self.table.game.players[self.index]

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
    def buy_in_amount(self):
        return self.__buy_in_amount

    def is_player(self):
        return self.index is not None

    def is_active(self):
        return self.__active_status

    def buy_in(self, amount):
        self.__buy_in_amount = amount
