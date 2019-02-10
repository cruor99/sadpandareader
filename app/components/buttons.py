from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage as Image
from kivy.uix.stencilview import StencilView
from kivy.uix.button import Button
from kivymd.button import MDFlatButton, MDRaisedButton
from kivymd.list import TwoLineAvatarListItem, ILeftBodyTouch, OneLineAvatarListItem
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.stencilview import StencilView

from kivy.uix.label import Label
from kivymd.label import MDLabel
from kivymd.card import MDCard

Builder.load_file("kv/buttons.kv")


class ThumbButton(ButtonBehavior, MDCard):
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    gallery_tags = ListProperty([])
    gallery_name = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_thumb = StringProperty("")
    filesize = NumericProperty(0)
    category = StringProperty("")
    category_colors = {
        "Non-H": (.89, .96, 1, .8),
        "Western": (0.85098039215, 1, 0.70588235294, .8),
        "Artist CG Sets": (0.96862745098, 0.94901960784, 0.74117647058, .7),
        "Game CG Sets": (0.69411764705, 0.84705882352, 0.69411764705, .6),
        "Doujinshi": (0.99607843137, 0.6431372549, 0.6431372549, .8),
        "Misc": (0.95294117647, 0.95294117647, 0.95294117647, .8),
        "Cosplay": (0.80392156862, 0.72549019607, 0.86274509803, .6),
        "Manga": (1, .8, 0.44705882352, .8),
        "Image Sets": (0.78823529411, 0.78823529411, 1, .8),
        "Asian Porn": (1, 0.89803921568, 1, .8)
    }

    def __repr__(self):
        return "ThumbButton: gid: {} gname: {}".format(self.gallery_id, self.gallery_name)

class TagButton(MDRaisedButton):

    tagname = StringProperty("")


class GalleryNavButton(Button):
    pass
