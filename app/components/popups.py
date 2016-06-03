from kivy.app import App
from kivy.properties import StringProperty, NumericProperty

from models import Search, Filters

from kivymd.dialog import MDDialog
from kivymd.textfields import SingleLineTextField


class CaptchaPopup(MDDialog):

    action = StringProperty("")

    def __init__(self, **kwargs):
        super(CaptchaPopup, self).__init__(**kwargs)
        self.add_action_button("Try Again", action=lambda *x: self.try_again())
        self.add_action_button("Continue",
                               action=lambda *x: self.non_restricted())

    def try_again(self):
        self.action = "try_again"
        self.dismiss()

    def non_restricted(self):
        self.action = "front_screen"
        self.dismiss()


class SearchPopup(MDDialog):
    def __init__(self, **kwargs):
        super(SearchPopup, self).__init__(**kwargs)
        # self.content = SearchArea()

        self.add_action_button("Search", action=lambda *x: self.savesearch())
        self.add_action_button(
            "Filters",
            action=lambda *x: App.get_running_app().root.show_filters())

    def savesearch(self):
        newsearch = Search(searchterm=self.ids.searcharea.text)
        db = App.get_running_app().db
        db.add(newsearch)
        db.commit()
        self.dismiss()

    def open_filters(self):
        fpop = FilterPopup()
        fpop.bind(on_dismiss=self.set_filters)
        fpop.open()

    def set_filters(self, instance):
        App.get_running_app().root.set_filters(instance)


class SearchArea(SingleLineTextField):
    def savesearch(self):
        newsearch = Search(searchterm=self.ids.searchstring.text)
        db = App.get_running_app().db
        db.add(newsearch)
        db.commit()
        self.dismiss()


class FilterPopup(MDDialog):
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

    def __init__(self, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        db = App.get_running_app().db
        filters = db.query(Filters).order_by(Filters.id.desc()).first()
        if filters:
            self.doujinshi = filters.doujinshi
            self.manga = filters.manga
            self.artistcg = filters.artistcg
            self.gamecg = filters.gamecg
            self.western = filters.western
            self.nonh = filters.nonh
            self.imageset = filters.imageset
            self.cosplay = filters.cosplay
            self.asianporn = filters.asianporn
            self.misc = filters.misc
        if self.doujinshi == 1:
            self.ids.doujinshi.active = True
        if self.manga == 1:
            self.ids.manga.active = True
        if self.artistcg == 1:
            self.ids.artistcg.active = True
        if self.gamecg == 1:
            self.ids.gamecg.active = True
        if self.western == 1:
            self.ids.western.active = True
        if self.nonh == 1:
            self.ids.nonh.active = True
        if self.imageset == 1:
            self.ids.imageset.active = True
        if self.cosplay == 1:
            self.ids.cosplay.active = True
        if self.asianporn == 1:
            self.ids.asianporn.active = True
        if self.misc == 1:
            self.ids.misc.active = True
