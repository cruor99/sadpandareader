from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import ListProperty, StringProperty, NumericProperty

from os.path import join

# Self made components
from components import TagButton

from models import db, Gallery, GalleryTags, Search, Favourites

import kivymd.snackbar as Snackbar

class GalleryPreviewScreen(Screen):

    gallery_tags = ListProperty([])
    gallery_id = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    gallery_token = StringProperty("")
    gallery_thumb = StringProperty("")
    filesize = NumericProperty(0)
    title = StringProperty("Preview and Tags")

    def on_enter(self):
        gallerydata = db.query(Gallery).filter_by(gallery_id=self.gallery_id).first()
        tags = db.query(GalleryTags).filter_by(galleryid=gallerydata.id).all()
        taglist = []
        for tag in tags:
            taglist.append(tag.tag)
        self.gallery_id = gallerydata.gallery_id
        self.gallery_token = gallerydata.gallery_token
        self.pagecount = gallerydata.pagecount
        self.gallery_name = gallerydata.gallery_name
        self.gallery_tags = taglist
        self.gallery_thumb = gallerydata.gallery_thumb
        self.filesize = gallerydata.filesize

        Clock.schedule_once(self.populate_tags)

    def add_favourite(self, *args):
        existfavourite = db.query(Favourites).filter_by(gallery_id=self.gallery_id).first()
        if existfavourite:
            return
        else:
            newfav = Favourites()
            newfav.gallery_id = self.gallery_id
            newfav.gallery_token = self.gallery_token
            newfav.pagecount = self.pagecount
            newfav.gallery_name = self.gallery_name
            newfav.gallery_thumb = self.gallery_thumb
            newfav.filesize = self.filesize
            db.add(newfav)
            db.commit()
            Snackbar.make("Added to favourites!")

    def populate_tags(self, *args):
        self.ids.tag_layout.clear_widgets()
        for tag in self.gallery_tags:
            taglabel = TagButton(tagname=tag)
            taglabel.bind(on_press=self.search_tag)
            self.ids.tag_layout.add_widget(taglabel)

    def view_gallery(self):
        galleryscreen = App.get_running_app().root.ids.sadpanda_screen_manager.get_screen("gallery_screen")
        galleryscreen.gallery_id = self.gallery_id
        App.get_running_app().root.next_screen("gallery_screen")

    def search_tag(self, instance):

        tag = instance.text
        search = Search(searchterm=tag)
        db.add(search)
        db.commit()
        App.get_running_app().root.next_screen("front_screen")
