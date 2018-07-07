from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.carousel import Carousel
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage as Image
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.logger import Logger

Builder.load_file("kv/images.kv")


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


class GalleryImage(Image, ScatterLayout):
    do_rotation = False
    scale_max = 2
