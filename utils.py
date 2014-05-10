from sys import exit

import pyglet


class Notification:
    """
    A simple notification on the top right border. It needs a background image,
    'notification.png', which is 150x50 in size.

    To use, do the following in the window class:

    1. Add a list 'self.notifications'
    2. Add the following 2 methods in the class for ease of use

        def show_notifications(self):
            for n in self.notifications:
                n.draw()

        def add_notification(self, title, text):
            notification = Notification(self, title, text, group=GAME_LAYER)
            self.notifications.append(notification)
            pyglet.clock.schedule_once(lambda x: self.notifications.remove(notification), 5)
    """

    def __init__(self, window, title, text, group=None, time=5):
        self.background_image = pyglet.resource.image('notification.png')
        self.position = [window.width - self.background_image.width - 5,
                         window.height - self.background_image.height - 5]

        self.background = pyglet.sprite.Sprite(self.background_image, self.position[0], self.position[1])
        self.background.opacity = 100

        size = 15
        self.title = pyglet.text.Label(title, font_size=size, bold=True,
                                       x=self.position[0] + 5,
                                       y=self.position[1] + self.background_image.height - size - 8)

        size = 8
        self.text = pyglet.text.Label(text, font_size=size,
                                      x=self.position[0] + 7,
                                      y=self.position[1] + self.background_image.height - size - 30)

    def draw(self):
        self.background.draw()
        self.title.draw()
        self.text.draw()


class Menu:
    """
    This class is made specifically for the TwoZeroFourMate game. Will be
    changed to be more usable in other games later on.

    The menu is of size 200x200.

    By default has a exit button. Set exit_button to False to remove that.

    Btw, don't try to understand this code. It just is.
    """

    def __init__(self, window, size=(250, 250), exit_button=True):
        self.window = window
        self.exit_button = exit_button

        self.background_image = pyglet.resource.image('menu_background.png')
        self.background_image.width, self.background_image.height = size
        self.background = pyglet.sprite.Sprite(self.background_image,
                                               window.width / 2 - self.background_image.width / 2,
                                               window.height / 2 - self.background_image.height / 2)
        self.background.opacity = 80

        # to avoid magic numbers
        self.space_between_items = -3 # negative = overlapping
        self.space_before_title = 3
        self.space_after_title = 25

        self.title = pyglet.text.Label('Menu', font_size=30)
        self.title.anchor_x = 'center'
        self.title.anchor_y = 'top'
        self.title.x, self.title.y = self.background.width / 2, self.background.height - self.space_before_title

        self._items = []

        # add an exit button by default
        if self.exit_button:
            self.add_item('EXIT', exit, size=18, color=(255, 0, 0, 200))

    def add_item(self, text, action, size=15, color=(255, 255, 255, 255)):
        """
        Adds an menu item to the items list. An item just represents a
        dict with some info in it. The action argument is a func which
        will be run when clicked on the item.
        """
        label = pyglet.text.Label(text, font_size=size, color=color, anchor_x='center')
        if len(self._items) == 0:
            position = [self.background.width / 2,
                        self.title.y - self.title.content_height / 2 - self.space_after_title -
                        self.space_before_title - label.content_height]
        else:
            position = [self.background.width / 2,
                        self._items[-1]['label'].y - label.content_height - self.space_between_items]
        label.x, label.y = position

        menu_item = {
            'text': text,
            'action': action,
            'size': size,
            'color': color,
            'pos': position,
            'label': label
        }

        self._items.append(menu_item)
        #self._items.insert(0, menu_item)

    def on_mouse_press(self, x, y, button, modifiers):
        for item in self._items:
            if x in range(item['label'].x - item['label'].content_width / 2,  # since it anchor is in the center
                          item['label'].x + item['label'].content_width / 2) and \
               y in range(item['label'].y, item['label'].y + item['label'].content_height):
                item['action']()

    def show(self):
        """
        Show the menu.
        """
        self.background.draw()
        self.title.draw()
        for item in self._items: item['label'].draw()