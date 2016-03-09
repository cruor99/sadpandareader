from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
from os.path import join
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App

from models import Search, db


class CaptchaPopup(Popup):

    action = StringProperty("")

    def try_again(self):
        self.action = "try_again"
        self.dismiss()

    def non_restricted(self):
        self.action = "front_screen"
        self.dismiss()


class SearchPopup(Popup):

    global data_dir

    def savesearch(self):
        newsearch = Search(searchterm=self.ids.searchstring.text)
        db.add(newsearch)
        db.commit()
        self.dismiss()

    def open_filters(self):
        fpop = FilterPopup()
        fpop.bind(on_dismiss=self.set_filters)
        fpop.open()

    def set_filters(self, instance):
        App.get_running_app().root.set_filters(instance)


class FilterPopup(Popup):
    doujinshi = NumericProperty(0)
    manga = NumericProperty(0)
    artistcg = NumericProperty(0)
    gamecg = NumericProperty(0)
    western = NumericProperty(0)
    nonh = NumericProperty(0)
    imageset = NumericProperty(0)
    cosplay = NumericProperty(0)
    asianporn = NumericProperty(0)
    misc = NumericProperty(0)

    global data_dir

    def __init__(self, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        filterjson = JsonStore(join(data_dir, "filterstore.json"))
        if filterjson.exists("filters"):
            self.doujinshi = filterjson["filters"]["filters"]["doujinshi"]
            self.manga = filterjson["filters"]["filters"]["manga"]
            self.artistcg = filterjson["filters"]["filters"]["artistcg"]
            self.gamecg = filterjson["filters"]["filters"]["gamecg"]
            self.western = filterjson["filters"]["filters"]["western"]
            self.nonh = filterjson["filters"]["filters"]["nonh"]
            self.imageset = filterjson["filters"]["filters"]["imageset"]
            self.cosplay = filterjson["filters"]["filters"]["cosplay"]
            self.asianporn = filterjson["filters"]["filters"]["asianporn"]
            self.misc = filterjson["filters"]["filters"]["misc"]
        if self.doujinshi == 1:
            self.ids.doujinshi.state = "down"
        if self.manga == 1:
            self.ids.manga.state = "down"
        if self.artistcg == 1:
            self.ids.artistcg.state = "down"
        if self.gamecg == 1:
            self.ids.gamecg.state = "down"
        if self.western == 1:
            self.ids.western.state = "down"
        if self.nonh == 1:
            self.ids.nonh.state = "down"
        if self.imageset == 1:
            self.ids.imageset.state = "down"
        if self.cosplay == 1:
            self.ids.cosplay.state = "down"
        if self.asianporn == 1:
            self.ids.asianporn.state = "down"
        if self.misc == 1:
            self.ids.misc.state = "down"
