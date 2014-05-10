#!/usr/bin/env python
from __future__ import print_function
from random import randrange, choice

import pyglet
from pyglet.window import key

from utils import Notification, Menu

pyglet.resource.path = ['resources']
pyglet.resource.reindex()

TILE_GRID_IMAGE = pyglet.resource.image('tile_grid.png')
TILE_GRID = pyglet.image.ImageGrid(TILE_GRID_IMAGE, 5, 5)

BATCH = pyglet.graphics.Batch() # less resource intensive
GAME_LAYER = pyglet.graphics.OrderedGroup(0) # draw order
MENU_LAYER = pyglet.graphics.OrderedGroup(1)

# to avoid magic numbers
DIRECTIONS = { # in x, y
    'DOWN': (0, -1),
    'UP': (0, 1),
    'RIGHT': (1, 0),
    'LEFT': (-1, 0)
}

def get_tile_image(number):
    area = {
        2: 20,
        4: 21,
        8: 22,
        16: 23
    }

    return TILE_GRID[area[number]]

def animate_position_change(sprite, new_x, new_y):
    """
    When a position changes position, it makes a nice
    animation as if it's moving to the new position.

    Takes a sprite and the new positions as input.
    """
    def update_x_position(dt):
        sprite.x += 1
    def update_y_position(dt):
        sprite.x += 1
    def stop(dt, func):
        pyglet.clock.unschedule(func)

    pixels_x = sprite.x - new_x if sprite.x > new_x else new_x - sprite.x
    pixels_y = sprite.y - new_y if sprite.y > new_y else new_y - sprite.y

    # 60 px bewegen in 60 Hz duurt 1 sec
    # 120 px bewegen in 60 Hz duurt 2 sec

    pyglet.clock.schedule_interval(update_x_position, 1./60.)
    pyglet.clock.schedule_once(stop, pixels_x/60., update_x_position)
    pyglet.clock.schedule_interval(update_y_position, 1./60.)
    pyglet.clock.schedule_once(stop, pixels_y/60., update_y_position)


class Tile(pyglet.sprite.Sprite):
    def __init__(self, number, x, y, batch=None, group=None):
        pyglet.sprite.Sprite.__init__(self, get_tile_image(number), x, y, batch=batch, group=group)

        self.number = number


class Board:
    """
    The virtual board where all the tiles are stored. The board is a list with
    size 4x4. Each square in the board is a dict with the tile object 'tile' and
    the position on the window 'pos'. The info of the tile can be called
    with self.board[y_coordinate][x_coordinate].
    """
    def __init__(self, window):
        self.window = window
        self.board_size = 4*4 # to avoid magic numbers

        #self.board = [[{'tile': None, 'pos': [x, y]} for y in range(5, 268, 67)] for x in range(5, 268, 67)]
        self.board = self.make_board()
        self.occupied = [] # list with occupied squares board_x and board_y positions

        self.add_random_tile()

    def make_board(self):
        """
        Tile size 64 with spacing of size 3, with border line size 5.
        """
        board = []
        for board_x, x in enumerate(range(5, 268, 67)):
            board.append([])
            for board_y, y in enumerate(range(5, 268, 67)):
                board[board_x].append({'tile': None,
                                       'pos': [x, y],
                                       'board_pos': [board_x, board_y]})
        return board

    def new_tile(self, number, board_x, board_y, append_to_occupied=True):
        """
        Board_x means the position in the self.board list. x means
        the actual position on the game window.
        """
        position = self.board[board_y][board_x]['pos']
        self.board[board_y][board_x]['tile'] = Tile(number, position[0], position[1],
                                                    batch=BATCH, group=GAME_LAYER)

        if append_to_occupied:
            self.occupied.append([board_x, board_y])

    def move_tile(self, board_x, board_y, new_board_x, new_board_y):
        """
        Passes the tile around the board. Doesn't move if the new
        tile is already occupied.
        """
        # the tile which is going to be moved
        passing_tile = self.board[board_y][board_x]['tile']

        try:
            if self.board[new_board_y][new_board_x]['tile'] is None:
                # pass the tile to it's new position and give the old position
                # tile dict entry a None
                self.board[new_board_y][new_board_x]['tile'] = passing_tile
                self.board[board_y][board_x]['tile'] = None

                # update the new x and y blit coordinates of the sprite
                self.board[new_board_y][new_board_x]['tile'].x = self.board[new_board_y][new_board_x]['pos'][0]
                self.board[new_board_y][new_board_x]['tile'].y = self.board[new_board_y][new_board_x]['pos'][1]

                print('Occupied list before: ', self.occupied)
                # change it's position in self.occupied
                self.occupied.remove([board_x, board_y])
                self.occupied.append([new_board_x, new_board_y])
                print('Moved tile.')

                print('Occupied list after: ', self.occupied)

            elif self.board[new_board_y][new_board_x]['tile'].number == passing_tile.number:
                self.board[board_y][board_x]['tile'] = None
                self.occupied.remove([board_x, board_y])
                self.new_tile(passing_tile.number*2, new_board_x, new_board_y, append_to_occupied=False)
        except IndexError:
            pass # Errors should never pass silently. Unless explicitly silenced.

    def move_tiles(self, direction):
        """
        Move the tiles every turn based on the direction.
        """
        for _ in range(3): # moves a tile from edge to edge
            for y, row in enumerate(self.board):
                for x, square in enumerate(row):
                    if square['tile'] is not None: # only move if it has a tile in it
                        self.move_tile(x, y, x+direction[1], y+direction[0])

    def find_empty_spot(self):
        """
        Finds a random place on the board which has no Tile object in it.
        Returns the board x and y position.
        """
        board_x, board_y = randrange(4), randrange(4)
        while [board_x, board_y] in self.occupied:
            board_x, board_y = randrange(4), randrange(4)

        return board_x, board_y

    def add_random_tile(self):
        """
        Adds a tile at a random place in the board.
        """
        board_x, board_y = self.find_empty_spot()
        self.new_tile(choice([2, 4]), board_x, board_y)
        print('Added a random tile at x:{} and y: {}.'.format(board_y+1, board_x+1))
        print('Occupied list: ', self.occupied)

    def can_move(self, direction):
        """
        Checks if the player is able to move the tiles in the desired direction.
        This method exist because if none of the available tiles can be moved in
        that direction, there shouldn't be a random tile added.
        Returns boolean:
            True  - tiles can move
            False - tiles can't move
        """
        pass

    def moves_left(self):
        """
        Checks if the user still has moves left. Returns a boolean:
            True  - Still moves left
            False - No moves left
        """
        # For now, just check if there is any place left to add a new tile
        # TODO: Make this more intelligent

        return not len(self.occupied) == self.board_size

    def update(self):
        """
        The game mechanics are in here.
        """
        if not self.moves_left():
            self.window.end()
            return

        self.add_random_tile()

    def show_tile_info(self):
        """

        """
        flattened_board = [j for i in self.board for j in i]
        for square in flattened_board:
            pyglet.text.Label('tile: {}, x:{}, y:{}'.format(str(square['tile'])[:4],
                                                            square['board_pos'][0],
                                                            square['board_pos'][1]),
                              x=square['pos'][0]+5, y=square['pos'][1]+50, color=(0, 255, 0, 255),
                              width=8, font_size=8, bold=True, multiline=True).draw()


class GameWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, width=275, height=275)

        # show and set the fps
        pyglet.clock.set_fps_limit(60.0)
        self.fps_display = pyglet.clock.ClockDisplay()

        # notification queue
        self.notifications = []

        # the menu with the options in it
        self.menu = Menu(self)
        self.menu_open = False

        # Show info about tiles
        self.debug = False

        # add items to the menu
        self.menu.add_item('Scoreboard', exit)
        self.menu.add_item('Restart', self.restart)

        # notification telling the player how to open the menu
        self.add_notification('Press \'M\'', 'to open the menu', duration=2.5)

        self.background = pyglet.resource.image('background.png')

        # the board object of the game. check the Board class for more info
        self.game_board = Board(self)

    def game_tick(self):
        """
        Runs only when a move has been made. Less resource intensive! :D
        """
        self.game_board.update()

    def show_notifications(self):
        for n in self.notifications:
            n.draw()

    def add_notification(self, title, text, duration=5):
        notification = Notification(self, title, text, group=GAME_LAYER)
        self.notifications.append(notification)
        pyglet.clock.schedule_once(lambda x: self.notifications.remove(notification), duration)

    def on_key_press(self, symbol, modifiers):
        if self.menu_open: # we're in the menu
            if symbol == key.F:
                print('Pressed \'F\' while in menu.')
        else:
            if symbol == key.DOWN:
                self.game_board.move_tiles(DIRECTIONS['DOWN'])
                self.game_tick()
            elif symbol == key.UP:
                self.game_board.move_tiles(DIRECTIONS['UP'])
                self.game_tick()
            elif symbol == key.LEFT:
                self.game_board.move_tiles(DIRECTIONS['LEFT'])
                self.game_tick()
            elif symbol == key.RIGHT:
                self.game_board.move_tiles(DIRECTIONS['RIGHT'])
                self.game_tick()
            elif symbol == key.R: # cheating, just to test
                pos = self.game_board.board[0][3]['pos']
                self.game_board.new_tile(choice([2, 4]), pos[0], pos[1])
            elif symbol == key.N:
                self.add_notification('WARNING', 'Watch out, storm ahead!')

        if symbol == key.M:
            self.menu_open = not self.menu_open
        if symbol == key.K:
            self.debug = not self.debug
    def on_mouse_press(self, x, y, button, modifiers):
        if self.menu_open:
            self.menu.on_mouse_press(x, y, button, modifiers)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)
        BATCH.draw()
        self.show_notifications()

        if self.debug:
            self.game_board.show_tile_info()
            self.fps_display.draw()

        if self.menu_open:
            self.menu.show()

    def start(self):
        """
        Starts the game.
        """
        pass

    def end(self):
        """
        Ends the game.
        """
        self.add_notification('You lost!', 'Too bad, haha!')

    def restart(self):
        self.game_board = Board(self)
        self.menu_open = False

def main():
    window = GameWindow()
    pyglet.app.run()

if __name__ == '__main__':
    main()