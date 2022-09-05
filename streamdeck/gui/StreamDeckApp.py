from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.event import EventDispatcher
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from dataclasses import asdict
from kivy.clock import mainthread
from streamdeck.config import load_config_from_file, load_default_config, AppConfig, Configuration
from streamdeck.kiosk import AppManager

try:
    config = load_config_from_file()
except FileNotFoundError:
    config = load_default_config()

app_manager = AppManager(config)


class SDRootWidget(BoxLayout):
    model = ObjectProperty(config)
    app_manager = ObjectProperty(app_manager)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.model = config

    def apply(self):
        self.model.dump(self.model.config_path)
        self.app_manager.apply_all()
        popup = Popup(title="Success", content=Label(
            text="Apps have been installed successfully!\n\nPlease restart Steam if it is currently running."),
            size_hint=(.5, .5))
        popup.open()


class UserSelect(ScrollView):
    config: ObjectProperty(Configuration)

    def on_kv_post(self, base_widget):
        users = self.config.steam_config.users
        self.clear()
        layout_height = 64
        for user in users:
            btn = ToggleButton(text=self.config.steam_config.get_user_name(user), height=44, size_hint_y=None)
            self.ids['layout'].add_widget(btn)
            btn.bind(on_press=lambda b: self.toggle_user(user, b.state))
            layout_height += 44
        self.ids['layout'].height = layout_height
        print(f"layout height: {layout_height}")

    def toggle_user(self, user: str, state: str):
        if state == 'down':
            if user not in self.config.users:
                self.config.users.append(user)
        else:
            if user in self.config.users:
                self.config.users.remove(user)

    def clear(self):
        for widget in self.children[0].children:
            if isinstance(widget, ToggleButton):
                self.children[0].remove_widget(widget)


class NewAppDialog(Popup, EventDispatcher):
    app_name = StringProperty('My App')
    app_url = StringProperty('https://youtube.com')
    app_show_address_bar = BooleanProperty(False)

    def __init__(self, app_manager: AppManager, **kwargs):
        self.app_manager = app_manager
        self.register_event_type('on_add_app')
        super().__init__(**kwargs)

    def on_add_app(*args):
        pass

    def on_pre_dismiss(self):
        self.app_manager.add_app(self.app_name, self.app_url, not self.app_show_address_bar)
        self.dispatch('on_add_app')

    def set_name(self, value: str):
        self.app_name = value

    def set_url(self, value: str):
        self.app_url = value

    def set_show_address_bar(self, value: bool):
        self.app_show_address_bar = value


class Apps(ScrollView):
    apps: ListProperty([])
    app_manager: AppManager

    def show_new_app_dialog(self):
        popup = NewAppDialog(app_manager)
        popup.bind(on_add_app=self.on_add_app)
        popup.open()

    def on_kv_post(self, base_widget):
        self.update_app_list()

    def update_app_list(self):
        container = self.ids['apps_container'].__self__

        for widget in container.children:
            container.remove_widget(widget)
        for app in self.apps:
            app_widget = SDApp(app)
            app_widget.bind(on_remove=self.on_remove_app)
            container.add_widget(app_widget)

    def on_add_app(self, *_):
        self.update_app_list()

    def on_remove_app(self, app_widget: 'SDApp'):
        self.app_manager.remove_app(app_widget.app)
        self.update_app_list()


class SDApp(BoxLayout, EventDispatcher):

    __events__ = ('on_remove',)

    def __init__(self, app: AppConfig, **kwargs):
        print(f'app_name: {app.name}')
        self.register_event_type('on_remove')
        self.app = app
        super().__init__(**kwargs)

    def on_remove(self, *arg):
        print(arg)
        pass


class StreamDeckApp(App):

    def build(self):
        return SDRootWidget(config)


if __name__ == '__main__':
    StreamDeckApp().run()
