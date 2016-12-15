from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage as Image
from kivy.uix.stencilview import StencilView
from kivy.uix.button import Button
from kivymd.button import MDFlatButton, MDRaisedButton
from kivymd.list import TwoLineAvatarListItem, ILeftBodyTouch
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.stencilview import StencilView

from kivy.uix.label import Label
from kivymd.label import MDLabel

Builder.load_file("kv/buttons.kv")


class ThumbButton(TwoLineAvatarListItem, Label):
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    gallery_tags = ListProperty([])
    gallery_name = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_thumb = StringProperty("")
    filesize = NumericProperty(0)
    category = StringProperty("")

    def __init__(self, **kwargs):
        super(ThumbButton, self).__init__(**kwargs)
        if len(self.gallery_name) > 110:
            self.secondary_text = self.gallery_name[:110] + "..."
        else:
            self.secondary_text = self.gallery_name

        self.ids._left_container.size = (self.size[0] - dp(10), self.size[1] - dp(10))
        self.ids._left_container.x = self.x + dp(5)
        self.ids._left_container.y = self.y + dp(2)
        self.ids._left_container.size_hint = (.145, .9)

        #print "==============="
        #print self.gallery_name
        #print self.category

        if self.category == "Non-H":
            with self.canvas.before:
                Color(.89, .96, 1, .8)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Western":
            with self.canvas.before:
                Color(0.85098039215, 1, 0.70588235294, .8)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Artist CG Sets":
            with self.canvas.before:
                Color(0.96862745098, 0.94901960784, 0.74117647058, .7)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Game CG Sets":
            with self.canvas.before:
                Color(0.69411764705, 0.84705882352, 0.69411764705, .6)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Doujinshi":
            with self.canvas.before:
                Color(0.99607843137, 0.6431372549, 0.6431372549, .8)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Misc":
            with self.canvas.before:
                Color(0.95294117647, 0.95294117647, 0.95294117647, .8)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Cosplay":
            with self.canvas.before:
                Color(0.80392156862, 0.72549019607, 0.86274509803, .6)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Manga":
            with self.canvas.before:
                Color(1, .8, 0.44705882352, .8)
                self.rect = Rectangle(
                    size=(self.size[0] / 2, self.size[1] / 2), pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Image Sets":
            with self.canvas.before:
                Color(0.78823529411, 0.78823529411, 1, .8)
                self.rect = Rectangle(
                    size=(self.size[0] / 2, self.size[1] / 2), pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        elif self.category == "Asian Porn":
            with self.canvas.before:
                Color(1, 0.89803921568, 1, .8)
                self.rect = Rectangle(
                    size=(self.size[0] / 2, self.size[1] / 2), pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        halfsize = (dp(65), instance.size[1])
        self.rect.size = halfsize


class AvatarSampleWidget(ILeftBodyTouch, Image):
    pass


class TagButton(MDRaisedButton):

    tagname = StringProperty("")


class GalleryNavButton(Button):
    pass
