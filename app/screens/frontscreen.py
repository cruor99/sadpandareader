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


class FrontScreen(Screen):

    global data_dir

    gallery_thumbs = ListProperty([])
    gidlist = ListProperty([])
    searchword = StringProperty("")
    searchpage = NumericProperty(0)
    newstart = BooleanProperty(True)

    def on_enter(self):

        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        search_store = JsonStore(join(data_dir, 'search_store.json'))
        if search_store.exists("searchstring"):
            newsearch = search_store["searchstring"]["searchphrase"]
            if newsearch == self.searchword:
                if self.newstart is True:
                    self.new_search()
                    self.newstart = False
                else:
                    pass
            else:
                self.searchword = newsearch
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
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        galleryinfo = [instance.gallery_id, instance.gallery_token,
                       instance.pagecount, instance.gallery_name,
                       instance.gallery_tags, instance.gallery_thumb]
        gallery_store.put("current_gallery", galleryinfo=galleryinfo)
        App.get_running_app().root.next_screen("gallery_preview_screen")

    def populate_front(self, *largs):
        # filter store
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        filterstore = JsonStore(join(data_dir, "filterstore.json"))
        filters = filterstore.get("filters")
        filtertemp = filters["filters"]
        # ehentai link
        self.gidlist = []
        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        r = requests.get("http://"+App.get_running_app().root.baseurl+".org/?page="+str(self.searchpage) +
                         "f_doujinshi="+str(filtertemp["doujinshi"]) +
                         "&f_manga="+str(filtertemp["manga"]) +
                         "&f_artistcg="+str(filtertemp["artistcg"]) +
                         "&f_gamecg="+str(filtertemp["gamecg"]) +
                         "&f_western="+str(filtertemp["western"]) +
                         "&f_non-h="+str(filtertemp["nonh"]) +
                         "&f_imageset="+str(filtertemp["imageset"]) +
                         "&f_cosplay="+str(filtertemp["cosplay"]) +
                         "&f_asianporn="+str(filtertemp["asianporn"]) +
                         "&f_misc="+str(filtertemp["misc"]) +
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
