from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.storage.jsonstore import JsonStore

from os.path import join


class StartScreen(Screen):

    global data_dir

    def on_enter(self):

        Clock.schedule_once(self.check_cookies)

    def check_cookies(self, *args):
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]

        cookie_store = JsonStore(join(data_dir, "cookie_store.json"))
        if cookie_store.exists("cookies"):
            App.get_running_app().root.cookies = cookie_store["cookies"]["cookies"]
            App.get_running_app().root.baseurl = "exhentai"
            App.get_running_app().root.next_screen("front_screen")
        else:
            pass
