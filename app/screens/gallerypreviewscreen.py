from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.properties import ObjectProperty
from threading import Thread
from kivy.lang import Builder

Builder.load_file("kv/gallerypreviewscreen.kv")

# Self made components
from components.buttons import TagButton

from models import Gallery, GalleryTags, Search, Favourites

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
    galleryinstance = ObjectProperty()

    def on_enter(self):
               ####
        taglist = []
        Clock.schedule_once(self.store_gallery)
        gallerydata = self.galleryinstance
        for tag in gallerydata.gallery_tags:
            taglist.append(tag)
        self.gallery_id = gallerydata.gallery_id
        self.gallery_token = gallerydata.gallery_token
        self.pagecount = gallerydata.pagecount
        self.gallery_name = gallerydata.gallery_name
        self.gallery_tags = taglist
        self.gallery_thumb = gallerydata.gallery_thumb
        self.filesize = gallerydata.filesize

        Clock.schedule_once(self.populate_tags)

    def store_gallery(self, *args):
        instance = self.galleryinstance
        db = App.get_running_app().db
        existgallery = db.query(Gallery).filter_by(
            gallery_id=instance.gallery_id).first()
        if existgallery:
            pass
        else:
            gallery = Gallery(gallery_id=instance.gallery_id,
                              gallery_token=instance.gallery_token,
                              pagecount=instance.pagecount,
                              gallery_name=instance.gallery_name,
                              gallery_thumb=instance.gallery_thumb,
                              filesize=instance.filesize)
            db.add(gallery)
            db.commit()
            for tag in instance.gallery_tags:
                gallerytag = GalleryTags(galleryid=gallery.id, tag=tag)
                db.add(gallerytag)
                db.commit()


    def new_search(self, *args):
        pass

    def add_favourite(self, *args):
        db = App.get_running_app().db
        existfavourite = db.query(Favourites).filter_by(gallery_id=self.gallery_id).first()
        if existfavourite:
            Snackbar.make("Already favourited!")
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
        if not App.get_running_app(
        ).root.ids.sadpanda_screen_manager.has_screen(
                "gallery_screen"):
            from screens.galleryscreen import GalleryScreen
            galleryscreen = GalleryScreen(name="gallery_screen")
            galleryscreen.gallery_id = self.gallery_id
            App.get_running_app().root.ids.sadpanda_screen_manager.add_widget(galleryscreen)
        else:
            galleryscreen = App.get_running_app().root.ids.sadpanda_screen_manager.get_screen("gallery_screen")
            galleryscreen.gallery_id = self.gallery_id
        App.get_running_app().root.next_screen("gallery_screen")

    def search_tag(self, instance):

        tag = instance.text
        search = Search(searchterm=tag)

        db = App.get_running_app().db
        db.add(search)
        db.commit()
        App.get_running_app().root.next_screen("front_screen")
