from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.scatter import Scatter
from kivy.uix.carousel import Carousel
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage as Image
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import BooleanProperty

from kivy.clock import Clock
from kivy.animation import Animation

Builder.load_file("kv/images.kv")

import time


class GalleryImageScreen(Screen):
    pass


class GalleryContainerLayout(FloatLayout):
    pass


class GalleryCarousel(Carousel):

    def startmove(self, *args):
        try:
            self.root.testmove(self._offset, self.min_move, self.direction)
        except Exception as e:
            Logger.exception(e)
            Logger.debug("Not attached to parent yet")


class GalleryImage(Image):
    auto_bring_to_front = False
    do_rotation = False
    scale_max = 2
    scale_min = 1
    do_collide_after_children = True
    zoomed = False
    animating = False
    current_touch = None
    scheduled_func = None
    hide_buttons = BooleanProperty(False)
    disable_gallery = BooleanProperty(False)


    def __init__(self, **kwargs):
        super(GalleryImage, self).__init__(**kwargs)
        self.default_center_x = App.get_running_app().root.center_x
        self.default_center_y = App.get_running_app().root.center_y

    def on_scale(self, instance, value):
        Logger.info("Scaled changed: {}".format(value))
        if value >= 1.1:
            self.zoomed = True
            self.do_translation = True
            self.disable_gallery = True
        elif value <= 1.1 and value > 1.02:
            self.do_translation = False
            self.zoomed = False
        elif value <= 1.01:
            new_pos = App.get_running_app().root.pos
            animation = Animation(pos=new_pos, t="out_back", duration=.3)
            animation.start(self)
            self.do_translation = False
            self.zoomed = False
        elif value == 1.0:
            self.zoomed = False
            self.do_translation = False


    def on_touch_down(self, touch):
        Logger.info("Current touch: {}".format(self.current_touch))
        super(GalleryImage, self).on_touch_down(touch)
        self.hide_buttons = True
        if self.current_touch is not None:
            x_difference = abs(self.current_touch.pos[0] - touch.pos[0])
            y_difference = abs(self.current_touch.pos[1] - touch.pos[1])
            # Logger.info("X diff: {}".format(x_difference))
            # Logger.info("Y diff: {}".format(y_difference))
            if x_difference <= 20 and y_difference <= 20:
                Clock.unschedule(self.scheduled_func)
                self.double_touch(touch)
        else:
            self.current_touch = touch
            self.scheduled_func = Clock.schedule_once(self.single_touch, .3)

    def on_touch_up(self, touch):
        super(GalleryImage, self).on_touch_up(touch)
        self.hide_buttons = False

    def double_touch(self, touch, *args):
        # Logger.info("Double touch")
        # Logger.info("The touch pos: {}".format(touch.pos))
        # Logger.info("The image pos: {}".format(self.pos))
        if self.zoomed:
            self.scale = 1
            new_pos = App.get_running_app().root.pos
            animation = Animation(pos=new_pos, t="out_back", duration=.3)
            animation.start(self)
            self.zoomed = False
        else:
            self.scale = 1.5
            old_center_x = self.center_x
            old_center_y = self.center_y
            x_difference = old_center_x - touch.pos[0]
            y_difference = old_center_y - touch.pos[1]
            self.center_x = old_center_x + x_difference
            self.center_y = old_center_y + y_difference
            mouse_pos = self.get_root_window().mouse_pos
            self.zoomed = True
        self.current_touch = None

    def single_touch(self, *args):
        Logger.info("Single touch")
        self.current_touch = None

    def on_pos(self, instance, value):
        # Logger.info("New pos: {}".format(value))
        center_x_difference = self.default_center_x - self.center_x
        center_y_difference = self.default_center_y - self.center_y
#
    def animation_complete(self, *args):
        self.animating = False



