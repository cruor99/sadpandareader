# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.storage.jsonstore import JsonStore
from kivy.properties import DictProperty, StringProperty

from os.path import join

import requests
from screens import *
from components import *
from models import User, Filters, Gallery, Pagelink, Search, db

data_dir = ""


class SadpandaRoot(BoxLayout):

    cookies = DictProperty({})
    username = StringProperty("")
    password = StringProperty("")
    baseurl = StringProperty("g.e-hentai")
    global data_dir

    def __init__(self, **kwargs):
        super(SadpandaRoot, self).__init__(**kwargs)
        # list of previous screens
        self.screen_list = []

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

        r = requests.post("https://forums.e-hentai.org/index.php?act=Login&CODE=01",
                          data=payload, headers=headers)

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
            print instance.action
        else:
            print instance.action
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
        front_screen = self.ids.sadpanda_screen_manager.get_screen("front_screen")
        searchword = front_screen.searchword
        search = db.query(Search).order_by(Search.id.desc()).first()
        newsearch = search.searchterm
        print newsearch, "newsearch"
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
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
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
            "misc": 0}
        if instance.ids.doujinshi.state == "down":
            filters["doujinshi"] = 1
        if instance.ids.manga.state == "down":
            filters["manga"] = 1
        if instance.ids.artistcg.state == "down":
            filters["artistcg"] = 1
        if instance.ids.gamecg.state == "down":
            filters["gamecg"] = 1
        if instance.ids.western.state == "down":
            filters["western"] = 1
        if instance.ids.nonh.state == "down":
            filters["nonh"] = 1
        if instance.ids.imageset.state == "down":
            filters["imageset"] = 1
        if instance.ids.cosplay.state == "down":
            filters["cosplay"] = 1
        if instance.ids.asianporn.state == "down":
            filters["asianporn"] = 1
        if instance.ids.misc.state == "down":
            filters["misc"] = 1

        filterstore = JsonStore(join(data_dir, "filterstore.json"))
        filterstore.put("filters", filters=filters)


class SadpandaApp(App):

    def __init__(self, **kwargs):
        super(SadpandaApp, self).__init__(**kwargs)
        global data_dir
        data_dir = JsonStore("user_data_dir.json")
        data_dir.put("data_dir", data_dir=getattr(self, 'user_data_dir'))
        tempdatadir = getattr(self, "user_data_dir")
        Window.bind(on_keyboard=self.onBackBtn)
        filterstore = JsonStore(join(tempdatadir, "filterstore.json"))
        # Makes sure only non-h is the default.
        if filterstore.exists("filters"):
            pass
        else:
            filters = {
                "doujinshi": 0,
                "manga": 0,
                "artistcg": 0,
                "gamecg": 0,
                "western": 0,
                "nonh": 1,
                "imageset": 0,
                "cosplay": 0,
                "asianporn": 0,
                "misc": 0
                }
            filterstore.put("filters", filters=filters)

    def onBackBtn(self, window, key, *args):
        # user presses back button
        if key == 27:
            return self.root.onBackBtn()

    def on_pause(self):
        return True

    def build(self):
        return SadpandaRoot()

if __name__ == "__main__":
    SadpandaApp().run()
