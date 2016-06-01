from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, DictProperty

from models import db, Settings
from components import ThumbButton


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
        q = db.query(Settings).first()
        if self.ids.logging.active == True:
            self.settingvals['logging'] = 1
            q.logging = 1
        else:
            self.settingvals['logging'] = 0
            q.logging = 0
        
        db.commit()
    
    def db_settings(self):
        settings = db.query(Settings).first()
        
        self.settingvals['logging'] = settings.logging