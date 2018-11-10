from kivy.app import App
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.logger import Logger
from kivy.lang import Builder

from YourApp.models import Search, Filters

from YourApp.kivymd.dialog import MDDialog
from YourApp.kivymd.textfields import MDTextField
from YourApp.kivymd.button import MDFlatButton

Builder.load_file("kv/popups.kv")


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
    search_suggestions = ListProperty([])
    search_buttons = ListProperty([])
    def __init__(self, **kwargs):
        super(SearchPopup, self).__init__(**kwargs)
        self.add_action_button("Search", action=lambda *x: self.savesearch())

    def savesearch(self):
        db = App.get_running_app().db
        already_exists = db.query(Search).filter_by(searchterm=self.ids.searcharea.text).first()
        front_screen = App.get_running_app().root.ids.sadpanda_screen_manager.get_screen("front_screen")
        front_screen.do_search(self.ids.searcharea.text)
        if already_exists:
            self.dismiss()
        else:
            newsearch = Search(searchterm=self.ids.searcharea.text)
            db.add(newsearch)
            db.commit()
            self.dismiss()

    def on_search_suggestions(self, object, value):
        for button in self.search_buttons:
            self.ids.searchlist.remove_widget(button)
        self.search_buttons = []
        for suggestion in value:
            button = MDFlatButton(text=suggestion, size_hint=(1, None))
            button.bind(on_release=self.button_search)
            self.search_buttons.append(button)
            self.ids.searchlist.add_widget(button)

    def button_search(self, instance):
        searchterm = instance.text
        Logger.info("Button text: {}".format(searchterm))
        front_screen = App.get_running_app().root.ids.sadpanda_screen_manager.get_screen("front_screen")
        front_screen.do_search(searchterm)
        self.dismiss()

    def find_search(self, searchterm):
        if len(searchterm) > 0:
            db = App.get_running_app().db
            suggestions = db.query(Search).filter(Search.searchterm.like("{}%".format(searchterm))).all()
            Logger.info("Suggestions: {}".format(suggestions))
            terms = set()
            for suggestion in reversed(suggestions):
                terms.add(suggestion.searchterm)
            self.search_suggestions = list(terms)
    def open_filters(self):
        fpop = FilterPopup()
        fpop.bind(on_dismiss=self.set_filters)
        fpop.open()

    def set_filters(self, instance):
        App.get_running_app().root.set_filters(instance)


class SearchArea(MDTextField):

    def savesearch(self):
        newsearch = Search(searchterm=self.ids.searchstring.text)
        db = App.get_running_app().db
        db.add(newsearch)
        db.commit()
        self.dismiss()


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
