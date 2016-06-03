from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty

from models import Settings


class SettingsScreen(Screen):
    title = StringProperty("Settings")
    settingvals = DictProperty({})

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def on_enter(self):
        self.db_settings()
        # Set slider values to values from database
        if self.settingvals['logging'] == 1:
            self.ids.logging.active = True

    def on_leave(self):
        db = App.get_running_app().db
        q = db.query(Settings).first()
        if self.ids.logging.active is True:
            self.settingvals['logging'] = 1
            q.logging = 1
        else:
            self.settingvals['logging'] = 0
            q.logging = 0

        db.commit()

    def db_settings(self):
        db = App.get_running_app().db
        settings = db.query(Settings).first()

        self.settingvals['logging'] = settings.logging
