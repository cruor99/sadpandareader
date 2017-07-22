from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder

Builder.load_file("kv/startscreen.kv")


from models import User

import ast


class StartScreen(Screen):

    def on_enter(self):

        Clock.schedule_once(self.check_cookies)

    def check_cookies(self, *args):
        db = App.get_running_app().db
        user = db.query(User).first()
        if user:
            cookies = user.cookies
            App.get_running_app().root.cookies = cookies
            App.get_running_app().root.baseurl = "exhentai"
            App.get_running_app().root.goto_front()
            App.get_running_app().root.ids.nav_drawer.ids.login_out_button.icon = "logout"
            App.get_running_app().root.ids.nav_drawer.ids.login_out_button.text = "Log out"
            App.get_running_app().root.next_screen("front_screen")
        else:
            pass
