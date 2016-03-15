from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.properties import NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.app import App

from os import linesep
from os.path import join

# Self created components
from components import ThumbButton, GalleryButtonContainer, GalleryTitle

import requests
import json

from BeautifulSoup import BeautifulSoup as BS

from models import db, Search, Filters, Gallery, GalleryTags


class FrontScreen(Screen):


    gallery_thumbs = ListProperty([])
    gidlist = ListProperty([])
    searchword = StringProperty("")
    searchpage = NumericProperty(0)
    newstart = BooleanProperty(True)

    def on_enter(self):

        search = db.query(Search).order_by(Search.id.desc()).first()
        if search:
            if self.newstart is True:
                self.searchword = search.searchterm
                self.new_search()
                self.newstart = False
            else:
                if self.searchword == search.searchterm:
                    pass
                else:
                    self.searchword = search.searchterm
                    self.new_search()
        else:
            self.searchword = ""
            self.new_search()

    def new_search(self):
        self.ids.main_layout.clear_widgets()
        self.searchpage = 0

        self.gallery_thumbs = []

        # final integer determines the time for the front to be populated
        Clock.schedule_once(self.populate_front)

    def enter_gallery(self, instance):
        galleryinfo = [instance.gallery_id, instance.gallery_token,
                       instance.pagecount, instance.gallery_name,
                       instance.gallery_tags, instance.gallery_thumb]
        existgallery = db.query(Gallery).filter_by(gallery_id=instance.gallery_id).first()
        if existgallery:
            pass
        else:
            gallery = Gallery(gallery_id = instance.gallery_id,
                            gallery_token=instance.gallery_token,
                            pagecount=instance.pagecount,
                            gallery_name=instance.gallery_name,
                            gallery_thumb=instance.gallery_thumb)
            db.add(gallery)
            db.commit()
            for tag in instance.gallery_tags:
                gallerytag = GalleryTags(galleryid=gallery.id, tag=tag)
                db.add(gallerytag)
                db.commit()
        preview_screen = App.get_running_app().root.ids.sadpanda_screen_manager.get_screen("gallery_preview_screen")
        preview_screen.gallery_id = instance.gallery_id
        App.get_running_app().root.next_screen("gallery_preview_screen")

    def populate_front(self, *largs):
        # filter store
        filters = db.query(Filters).order_by(Filters.id.desc()).first()
        #filters = filterstore.get("filters")
        #filtertemp = filters["filters"]
        self.gidlist = []
        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        print self.searchword
        if self.searchpage == 0:
            r = requests.get("http://"+App.get_running_app().root.baseurl+".org/?"+
                            "f_doujinshi="+str(filters.doujinshi) +
                            "&f_manga="+str(filters.manga) +
                            "&f_artistcg="+str(filters.artistcg) +
                            "&f_gamecg="+str(filters.gamecg) +
                            "&f_western="+str(filters.western) +
                            "&f_non-h="+str(filters.nonh) +
                            "&f_imageset="+str(filters.imageset) +
                            "&f_cosplay="+str(filters.cosplay) +
                            "&f_asianporn="+str(filters.asianporn) +
                            "&f_misc="+str(filters.misc) +
                            "&f_search="+self.searchword+"&f_apply=Apply+Filter",
                            headers=headers, cookies=cookies)
        else:
            r = requests.get("http://"+App.get_running_app().root.baseurl+".org/?"+
                             "page="+str(self.searchpage) +
                             "&f_doujinshi="+str(filters.doujinshi) +
                             "&f_manga="+str(filters.manga) +
                             "&f_artistcg="+str(filters.artistcg) +
                             "&f_gamecg="+str(filters.gamecg) +
                             "&f_western="+str(filters.western) +
                             "&f_non-h="+str(filters.nonh) +
                             "&f_imageset="+str(filters.imageset) +
                             "&f_cosplay="+str(filters.cosplay) +
                             "&f_asianporn="+str(filters.asianporn) +
                             "&f_misc="+str(filters.misc) +
                             "&f_search="+self.searchword+"&f_apply=Apply+Filter",
                             headers=headers, cookies=cookies)

        self.searchpage += 1
        # pure html of ehentai link
        data = r.text

        soup = BS(data, fromEncoding='utf8')
        gallerylinks = []

        # grabs all the divs with class it5 which denotes the gallery on the
        # page
        for link in soup.findAll('div', {'class': 'it5'}):
            # grabs all the links, should only be gallery links as of 29th of
            # august 2015
            gallerylinks.append(link.find('a')["href"])

        for link in gallerylinks:
            splitlink = link.split('/')
            # grab the gallery token
            gtoken = splitlink[-2]
            # grab the gallery id
            gid = splitlink[-3]
            self.gidlist.append([gid, gtoken])

        headers = {"Content-type": "application/json", "Accept": "text/plain",
                   'User-agent': 'Mozilla/5.0'}
        payload = {
            "method": "gdata",
            "gidlist": self.gidlist
            }
        cookies = App.get_running_app().root.cookies

        self.grabthumbs(headers, payload, cookies)

    def grabthumbs(self, headers, payload, cookies, *largs):
        r = requests.post("http://"+App.get_running_app().root.baseurl+".org/api.php",
                          data=json.dumps(payload), headers=headers, cookies=cookies)
        requestdump = r.text
        requestdump.rstrip(linesep)
        requestjson = json.loads(requestdump)
        i = 0
        try:
            for gallery in requestjson["gmetadata"]:
                self.add_button(gallery)
                i += 1
        except:
            pass

    def add_button(self, gallery, *largs):
        gallerybutton = ThumbButton(
            source=gallery["thumb"],
            gallery_id=str(gallery["gid"]),
            gallery_token=str(gallery["token"]),
            pagecount=int(gallery["filecount"]),
            gallery_name=gallery["title"],
            gallery_tags=gallery["tags"],
            gallery_thumb=gallery["thumb"])
        gallerybutton.bind(on_press=self.enter_gallery)
        buttoncontainer = GalleryButtonContainer(orientation="horizontal")
        buttoncontainer.add_widget(gallerybutton)
        buttoncontainer.add_widget(GalleryTitle(titletext=gallery["title"]))
        self.ids.main_layout.add_widget(buttoncontainer)
