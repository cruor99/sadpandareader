# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, StringProperty, ObjectProperty
from kivy.loader import Loader
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock

from plyer import notification
from plyer.utils import platform
from plyer.compat import PY2

from threading import Thread
import time
from os.path import join, dirname, realpath
from functools import partial

import requests
from screens import *
from components import *
from models import User, Filters, Gallery, Pagelink, Search, Settings, db

# Socket-io stuff
from socketIO_client import SocketIO

#KivyMD stuff
from kivymd.theming import ThemeManager


class SadpandaRoot(BoxLayout):

    cookies = DictProperty({})
    username = StringProperty("")
    password = StringProperty("")
    baseurl = StringProperty("g.e-hentai")
    pushurl = StringProperty(
        "https://1dvxtg49adq5f5jtzm2a04p2sr2pje3fem1x6gfu2cyhr30p.pushould.com")
    client_token = StringProperty(
        "6rgcw2zlr4ubpvcegjajqpnmehx5gp5zm1yigjzp1mgfvy6c")
    newmessage = StringProperty("")

    def __init__(self, **kwargs):
        super(SadpandaRoot, self).__init__(**kwargs)
        # list of previous screens
        self.screen_list = []
        Loader.loading_image = CoreImage("img/loading.gif", size=(16, 16))
        
        self.default_settings()

        Clock.schedule_once(self.start_thread)

    def default_settings(self):
        if db.query(Settings).first() != None:
            pass
        else:
            db.add(Settings(logging=0))
            db.commit()

    def start_thread(self, *args):
        self.bind(newmessage=self.do_notify)
        pushthread = Thread(target=self.check_pushould)
        pushthread.daemon = True
        pushthread.start()

    def check_pushould(self):
        socketio = SocketIO(self.pushurl,
                            params={"transports": ["polling", "websocket"],
                                    "client_token": str(self.client_token)},
                            verify=False)
        socketio.on('send', self.add_message)
        socketio.emit("subscribe", {"room": "sadpandapush"})
        socketio.wait()

    def add_message(self, response):
        self.newmessage = response["message"]

    def do_notify(self, *args):
        notification.notify("Update available", self.newmessage, timeout=5000)

    def login_exhentai(self, username, password):
        self.username = username.text
        self.password = password.text

        payload = {
            "UserName": username.text,
            "PassWord": password.text,
            "returntype": "8",
            "CookieDate": "1",
            "b": "d",
            "bt": "pone"
        }
        headers = {'User-Agent': 'Mozilla/5.0'}

        r = requests.post(
            "https://forums.e-hentai.org/index.php?act=Login&CODE=01",
            data=payload,
            headers=headers)

        if len(r.cookies) <= 1:
            captchapopup = CaptchaPopup()
            captchapopup.bind(on_dismiss=self.login_captcha)
            captchapopup.open()

        else:
            self.cookies = r.cookies
            cookies = User(cookies=str(self.cookies))
            db.add(cookies)
            db.commit()
            self.baseurl = "exhentai"
            self.next_screen("front_screen")

    def login_captcha(self, instance):
        if instance.action == "try_again":
            pass
        else:
            self.baseurl = "g.e-hentai"
            self.next_screen("front_screen")

    def next_screen(self, neoscreen):

        self.screen_list.append(self.ids.sadpanda_screen_manager.current)

        if self.ids.sadpanda_screen_manager.current == neoscreen:
            cur_screen = self.ids.sadpanda_screen_manager.get_screen(neoscreen)
            cur_screen.new_search()
            search = db.query(Search).order_by(Search.id.desc()).first()
            newsearch = search.searchterm
            cur_screen.searchword = newsearch
        else:
            self.ids.sadpanda_screen_manager.current = neoscreen

    def goto_front(self):
        blanksearch = Search(searchterm=" ")
        db.add(blanksearch)
        db.commit()
        self.next_screen("front_screen")

    def start_search(self, instance):
        front_screen = self.ids.sadpanda_screen_manager.get_screen(
            "front_screen")
        searchword = front_screen.searchword
        search = db.query(Search).order_by(Search.id.desc()).first()
        if search:
            newsearch = search.searchterm
        else:
            newsearch = " "
        if newsearch == searchword:
            pass
        else:
            self.next_screen("front_screen")

    def search_popup(self):
        spopup = SearchPopup()
        spopup.bind(on_dismiss=self.start_search)
        spopup.open()

    def onBackBtn(self):
        # check if there are screens we can go back to
        if self.screen_list:
            currentscreen = self.screen_list.pop()
            self.ids.sadpanda_screen_manager.current = currentscreen
            # Prevents closing of app
            return True
        # no more screens to go back to, close app
        return False

    def show_filters(self):
        fpop = FilterPopup()
        fpop.bind(on_dismiss=self.set_filters)
        fpop.open()

    def set_filters(self, instance):
        filters = {
            "doujinshi": 0,
            "manga": 0,
            "artistcg": 0,
            "gamecg": 0,
            "western": 0,
            "nonh": 0,
            "imageset": 0,
            "cosplay": 0,
            "asianporn": 0,
            "misc": 0
        }
        if instance.ids.doujinshi.active == True:
            filters["doujinshi"] = 1
        if instance.ids.manga.active == True:
            filters["manga"] = 1
        if instance.ids.artistcg.active == True:
            filters["artistcg"] = 1
        if instance.ids.gamecg.active == True:
            filters["gamecg"] = 1
        if instance.ids.western.active == True:
            filters["western"] = 1
        if instance.ids.nonh.active == True:
            filters["nonh"] = 1
        if instance.ids.imageset.active == True:
            filters["imageset"] = 1
        if instance.ids.cosplay.active == True:
            filters["cosplay"] = 1
        if instance.ids.asianporn.active == True:
            filters["asianporn"] = 1
        if instance.ids.misc.active == True:
            filters["misc"] = 1

        newfilter = Filters(doujinshi=filters["doujinshi"],
                            manga=filters["manga"],
                            artistcg=filters["artistcg"],
                            gamecg=filters["gamecg"],
                            western=filters["western"],
                            nonh=filters["nonh"],
                            imageset=filters["imageset"],
                            cosplay=filters["cosplay"],
                            asianporn=filters["asianporn"],
                            misc=filters["misc"])
        db.add(newfilter)
        db.commit()


class SadpandaApp(App):

    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def __init__(self, **kwargs):
        super(SadpandaApp, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.onBackBtn)
        # Makes sure only non-h is the default.
        existfilters = db.query(Filters).order_by(Filters.id.desc()).first()
        if existfilters:
            pass
        else:
            clearstart = Filters(nonh=1,
                                 doujinshi=0,
                                 manga=0,
                                 artistcg=0,
                                 gamecg=0,
                                 western=0,
                                 imageset=0,
                                 cosplay=0,
                                 asianporn=0,
                                 misc=0)
            db.add(clearstart)
            db.commit()
        clearsearch = Search(searchterm=" ")
        db.add(clearsearch)
        db.commit()

    def onBackBtn(self, window, key, *args):
        # user presses back button
        if key == 27:
            return self.root.onBackBtn()

    def on_pause(self):
        return True

    def build(self):
        self.nav_drawer = SadpandaNavdrawer()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Grey"
        self.theme_cls.primary_hue = "900"

        return SadpandaRoot()


if __name__ == "__main__":
    SadpandaApp().run()
