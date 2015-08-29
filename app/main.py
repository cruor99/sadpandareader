from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.image import AsyncImage as Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar

from os.path import join
import os
from functools import partial
from bs4 import BeautifulSoup as BS

import requests
import json


data_dir = ""


class ThumbButton(ButtonBehavior, Image):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagecount = NumericProperty(0)


class FrontScreen(Screen):

    global data_dir

    pb = ProgressBar(max=4500)
    gallery_thumbs = ListProperty([])
    gidlist = ListProperty([])
    # Because I am a n00b at using API's like these, I keep getting hour-bans
    # because of too many requests, as they do not like web scraping/api-usage
    proxyip = "104.197.107.186:3128"
    # works at 23:00proxyip = "209.66.193.244:8080"
    # works at 23:17proxyip = "168.62.191.144:3128"
    searchword = StringProperty("")

    def on_enter(self):

        searchstore = JsonStore("searchstore.json")
        if searchstore.exists("searchstring"):
            self.searchword = searchstore["searchstring"]["searchphrase"]
        else:
            self.searchword = ""

        for galleries in self.gallery_thumbs:
            self.ids.main_layout.remove_widget(galleries)

        self.pb.value = 0
        self.gallery_thumbs = []

        for i in range(45):
            Clock.schedule_once(self.increasepb, i)

        self.ids.main_layout.add_widget(self.pb)

        Clock.schedule_once(self.populate_front, 15)

    def increasepb(self, state):
        self.pb.value += 100
        if self.pb.value == 4500:
            self.ids.main_layout.remove_widget(self.pb)

    def enter_gallery(self, state):
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        galleryinfo = [state.gallery_id, state.gallery_token, state.pagecount]
        gallery_store.put("current_gallery", galleryinfo=galleryinfo)
        self.manager.current = "gallery_screen"

    def populate_front(self, state):
        # ehentai link
        proxies = {
            "http": self.proxyip
            }
        r = requests.get("http://g.e-hentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0&f_gamecg=0&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=0&f_asianporn=0&f_misc=0&f_search="+self.searchword+"&f_apply=Apply+Filter", proxies=proxies)
        # pure html of ehentai link
        data = r.text

        soup = BS(data)
        gallerylinks = []
        print(soup.prettify())

        # grabs all the divs with class it5 which denotes the gallery on the
        # page
        for link in soup.find_all('div', {'class': 'it5'}):
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
            print(self.gidlist)

        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        payload = {
            "method": "gdata",
            "gidlist": self.gidlist[:9]
            }

        Clock.schedule_once(partial(self.grabthumbs, headers, payload), 30)

    def grabthumbs(self, headers, payload, *largs):
        proxies = {
            "http": self.proxyip
            }
        r = requests.post("http://g.e-hentai.org/api.php",
                          data=json.dumps(payload), headers=headers,
                          proxies=proxies)
        print(r.content)
        requestdump = r.text
        requestdump.rstrip(os.linesep)
        print(requestdump)
        print(type(requestdump))
        requestjson = json.loads(requestdump)
        print(type(requestjson))
        i = 0
        for gallery in requestjson["gmetadata"]:
            i += 10
            Clock.schedule_once(partial(self.add_button, gallery), i)

    def add_button(self, gallery, *largs):
        if not os.path.isfile("img/"+str(gallery["gid"])+".jpg"):
            proxies = {
                "http": self.proxyip
                }
            rthumb = requests.get(gallery["thumb"], proxies=proxies,
                                  stream=True)
            print(rthumb.content)
            with open("img/"+str(gallery["gid"])+".jpg", 'wb') as out_file:
                for chunk in rthumb:
                    out_file.write(chunk)
        gallerybutton = ThumbButton(
            source="img/"+str(gallery["gid"])+".jpg",
            gallery_id=str(gallery["gid"]),
            gallery_token=str(gallery["token"]),
            pagecount=gallery["filecount"], allow_stretch=True)
        gallerybutton.bind(on_press=self.enter_gallery)
        self.ids.main_layout.add_widget(gallerybutton)
        """
        placeholderbutton = ThumbButton(
                source="img/sadpanda.jpeg", gallery_id="gid",
                gallery_token="gtok")
        placeholderbutton.bind(on_press=self.enter_gallery)
        self.gallery_thumbs.append(placeholderbutton)

        for galleries in self.gallery_thumbs:
            self.ids.main_layout.add_widget(galleries)
            """


class GalleryScreen(Screen):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagecount = NumericProperty(0)

    pb = ProgressBar(max=1500)

    global data_dir

    def on_enter(self):
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        if gallery_store.exists("current_gallery"):
            galleryinfo = gallery_store.get("current_gallery")
            self.gallery_id = galleryinfo["galleryinfo"][0]
            self.gallery_token = galleryinfo["galleryinfo"][1]
            self.pagecount = galleryinfo["galleryinfo"][2]
            print("galleryinfo: ", galleryinfo["galleryinfo"][2])
            print("pagecount: ", self.pagecount)
        self.populate_gallery()

    def populate_gallery(self):
        # change placehold.it with
        self.ids.gallery_carousel.add_widget(self.pb)

        for i in range(self.pagecount):
            i += 1
            self.pb.value += 100
            if self.pb.value == 1500:
                self.ids.gallery_carousel.remove_widget(self.pb)
            Clock.schedule_once(partial(self.grab_image, i), 15*i)

    def grab_image(self, i, *largs):
        print(i)
        src = "http://placehold.it/480x270.png&text=slide-%d&png" % i
        image = Image(source=src, allow_stretch=True)
        self.ids.gallery_carousel.add_widget(image)


class SearchPopup(Popup):

    global data_dir

    def savesearch(self):
        print(self.ids.searchstring.text)
        searchstore = JsonStore('searchstore.json')
        searchquery = self.ids.searchstring.text
        searchstore.put("searchstring", searchphrase=searchquery)
        self.dismiss()


class SadpandaRoot(BoxLayout):

    def __init__(self, **kwargs):
        super(SadpandaRoot, self).__init__(**kwargs)
        # list of previous screens
        self.screen_list = []

    def next_screen(self, neoscreen):

        if self.ids.sadpanda_screen_manager.current not in self.screen_list:
            self.screen_list.append(self.ids.sadpanda_screen_manager.current)

        self.ids.sadpanda_screen_manager.current = neoscreen

    def goto_front(self, instance):
        self.ids.sadpanda_screen_manager.current = "front_screen"

    def search_popup(self):
        spopup = SearchPopup()
        print(spopup)
        spopup.bind(on_dismiss=self.goto_front)
        spopup.open()


class SadpandaApp(App):

    def __init__(self, **kwargs):
        super(SadpandaApp, self).__init__(**kwargs)
        global data_dir
        data_dir = getattr(self, 'user_data_dir')

    def on_pause(self):
        return True

    def build(self):
        return SadpandaRoot()

if __name__ == "__main__":
    SadpandaApp().run()
