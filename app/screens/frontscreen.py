from kivy.uix.screenmanager import Screen
import time
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.lang import Builder
from kivy.logger import Logger
import urllib

from os import linesep
from functools import partial

# Self created components
from components.buttons import ThumbButton, AvatarSampleWidget

import json
from favouritescreen import FavouriteScreen
from settingsscreen import SettingsScreen

#to unescape gallery strings
from HTMLParser import HTMLParser

from BeautifulSoup import BeautifulSoup as BS
import urllib

from models import Search, Filters, Gallery, GalleryTags

Builder.load_file("kv/frontscreen.kv")


class FrontScreen(Screen):

    gallery_thumbs = ListProperty([])
    gidlist = ListProperty([])
    searchword = StringProperty("")
    searchpage = NumericProperty(0)
    newstart = BooleanProperty(True)
    title = StringProperty("Front page")
    last_widget = ObjectProperty()
    has_entered = False
    has_refreshed = True

    def __init__(self, **kwargs):
        super(FrontScreen, self).__init__(**kwargs)

    def on_enter(self):
        # This is required if the screen is the initial screen.
        # Done in order to ensure that we have everythign initialized before doing stuff witht he main app
        Clock.schedule_once(self.do_entry)

    def do_entry(self, *args):
        App.get_running_app().root.ids.sadpanda_screen_manager.add_widget(
            FavouriteScreen(name="favourite_screen"))
        App.get_running_app().root.ids.sadpanda_screen_manager.add_widget(
            SettingsScreen(name="settings_screen"))
        #App.get_running_app(
        #).root.cookies += "; uconfig=xl_10x1034x2058x20x1044x2068x30x1054x2078x40x1064x2088x50x1074x2098x60x1084x2108x70x1094x2118x80x1104x2128x90x1114x2138x100x1124x2148x110x1134x2158x120x1144x2168x130x1154x2178x254x1278x2302x255x1279x2303"
        self.ids.galleryscroll.bind(scroll_y=self.check_scroll_y)
        db = App.get_running_app().db
        self.do_search(self.searchword)


    def do_search(self, searchterm):
        Logger.info("Search query: {}".format(searchterm))
        Logger.info("Previous search term: {}".format(self.searchword))
        if self.newstart is True:
            self.searchword = searchterm
            self.new_search()
            self.newstart = False
        else:
            if self.searchword == searchterm:
                pass
            else:
                self.searchword = searchterm
                self.new_search()

    def new_search(self):
        self.ids.main_layout.clear_widgets()
        self.searchpage = 0

        self.gallery_thumbs = []

        Clock.schedule_once(self.populate_front)
        Clock.schedule_once(partial(self.entered, True))

    def entered(self, conditional, dt):
        self.has_entered = True

    def enter_gallery(self, instance):

        if not App.get_running_app(
        ).root.ids.sadpanda_screen_manager.has_screen(
                "gallery_preview_screen"):
            from screens.gallerypreviewscreen import GalleryPreviewScreen
            preview_screen = GalleryPreviewScreen(
                name="gallery_preview_screen")
            preview_screen.galleryinstance = instance
            App.get_running_app().root.ids.sadpanda_screen_manager.add_widget(
                preview_screen)
        else:
            preview_screen = App.get_running_app(
            ).root.ids.sadpanda_screen_manager.get_screen(
                "gallery_preview_screen")
            preview_screen.galleryinstance = instance
        App.get_running_app().root.next_screen("gallery_preview_screen")

    def check_scroll_y(self, instance, somethingelse):
        if self.has_refreshed == True:
            if self.ids.galleryscroll.scroll_y <= -0.02:
                self.populate_front()
                self.has_refreshed = False
            else:
                pass

    def populate_front(self, *largs):
        # filter store
        print(App.get_running_app().root.baseurl)
        db = App.get_running_app().db
        filters = db.query(Filters).order_by(Filters.id.desc()).first()
        #filters = filterstore.get("filters")
        #filtertemp = filters["filters"]
        self.gidlist = []
        headers = {'User-agent': 'Mozilla/5.0',
                   "Cookie": "",
                   "Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        cookies = App.get_running_app().root.cookies
        headers["Cookie"] = cookies
        searchword = self.searchword
        if App.get_running_app().root.username.lower() == "sadpandareader":
            self.searchword += ' english -swimsuit -lolicon -hitsuji -elf -uro -pixiv -"females only"'
            searchword += ' english -swimsuit -lolicon -hitsuji -elf -uro -pixiv -"females only"'
        elif App.get_running_app().root.baseurl == "e-hentai":
            self.searchword += ' english -swimsuit -hitsuji -elf -uro -pixiv -"females only"'
            searchword += ' english -swimsuit -hitsuji -elf -uro -pixiv -"females only"'
        page0searchurl = str(
            "http://" + App.get_running_app().root.baseurl + ".org/?" +
            "f_doujinshi=" + str(filters.doujinshi) + "&f_manga=" + str(
                filters.manga) + "&f_artistcg=" + str(filters.artistcg) +
            "&f_gamecg=" + str(filters.gamecg) + "&f_western=" + str(
                filters.western) + "&f_non-h=" + str(filters.nonh) +
            "&f_imageset=" + str(filters.imageset) + "&f_cosplay=" + str(
                filters.cosplay) + "&f_asianporn=" + str(filters.asianporn) +
            "&f_misc=" + str(filters.misc) + "&f_search=" + urllib.quote_plus(
                self.searchword) + "&f_apply=Apply+Filter")
        pagesearchurl = str(
            "http://" + App.get_running_app().root.baseurl + ".org/?" + "page="
            + str(self.searchpage) + "f_doujinshi=" + str(filters.doujinshi) +
            "&f_manga=" + str(filters.manga) + "&f_artistcg=" + str(
                filters.artistcg) + "&f_gamecg=" + str(filters.gamecg) +
            "&f_western=" + str(filters.western) + "&f_non-h=" + str(
                filters.nonh) + "&f_imageset=" + str(filters.imageset) +
            "&f_cosplay=" + str(filters.cosplay) + "&f_asianporn=" + str(
                filters.asianporn) + "&f_misc=" + str(
                    filters.misc) + "&f_search=" + urllib.quote_plus(
                        self.searchword) + "&f_apply=Apply+Filter")
        if self.searchpage == 0:
            req = UrlRequest(page0searchurl,
                             on_success=self.got_result,
                             on_failure=self.got_failure,
                             on_error=self.got_error,
                             req_headers=headers,
                             method="GET")
        else:
            req = UrlRequest(pagesearchurl,
                             self.got_result,
                             req_headers=headers)

        self.searchpage += 1
        # pure html of ehentai link

    def got_failure(self, req, r):
        print req
        print r

    def got_error(self, req, r):
        print req
        print r

    def got_result(self, req, r):
        data = r

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

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            'User-agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            "Cookie": ""
        }
        payload = {"method": "gdata", "gidlist": self.gidlist}
        cookies = App.get_running_app().root.cookies
        headers["Cookie"] = cookies
        self.headers = headers

        self.grabthumbs(headers, payload, cookies)

    def grabthumbs(self, headers, payload, cookies, *largs):
        params = urllib.urlencode(payload)
        r = UrlRequest("http://api.e-hentai.org/api.php",
                       on_success=self.thumbgrab,
                       on_error=self.thumb_error,
                       on_failure=self.thumb_failure,
                       req_body=json.dumps(payload),
                       req_headers=headers)

    def thumb_error(self, req, r):
        print req.resp_status
        print r

    def thumb_failure(self, req, r):
        print req.resp_status
        print r

    def thumbgrab(self, req, r):
        requestdump = r
        requestdump.rstrip(linesep)
        requestjson = json.loads(requestdump)
        i = 0
        try:
            for gallery in requestjson["gmetadata"]:
                self.add_button(gallery, i)
                i += 1
        except Exception as e:
            print e

    def add_button(self, gallery, i, *largs):
        Logger.info("What is i?: {}".format(i))
        escapedtitle = gallery["title"]
        unescapedtitle = HTMLParser().unescape(escapedtitle)

        gallerybutton = ThumbButton(
            #gallerysource=gallery["thumb"],
            gallery_id=str(gallery["gid"]),
            gallery_token=str(gallery["token"]),
            pagecount=int(gallery["filecount"]),
            gallery_name=unescapedtitle,
            gallery_tags=gallery["tags"],
            gallery_thumb=gallery["thumb"],
            filesize=gallery["filesize"],
            category=gallery["category"],
            size_hint_x=1, )
        gallerybutton.bind(on_release=self.enter_gallery)
        gallerybutton.add_widget(AvatarSampleWidget(source=gallery["thumb"]))
        if i == 24:
            if self.last_widget:
                self.ids.galleryscroll.scroll_to(self.last_widget)
            self.last_widget = gallerybutton
            self.ids.main_layout.add_widget(self.last_widget)
        else:
            self.ids.main_layout.add_widget(gallerybutton)
        self.has_refreshed = True

