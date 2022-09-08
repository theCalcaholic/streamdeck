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
from streamdeck.config import load_config_from_file, load_default_config, load_test_config, AppConfig, Configuration
from streamdeck.kiosk import AppManager
from dataclasses import asdict

try:
    config = load_config_from_file()
except FileNotFoundError as e:
    print(e)
    config = load_default_config()
    #config = load_test_config()

app_manager = AppManager(config)


class SDRootWidget(BoxLayout):
    model = ObjectProperty(config, rebind=True)
    app_manager = ObjectProperty(app_manager)

    def __init__(self, config, **kwargs):
        print("Starting app...")
        super().__init__(**kwargs)
        self.model = config


class HLine(Widget):
    pass


class UserSelect(ScrollView, EventDispatcher):
    config = ObjectProperty(None)
    selected_user = StringProperty(defaultvalue=None, allownone=True)

    def __init__(self, **kwargs):
        self.selected_button: ToggleButton | None = None
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        users = self.config.steam_config.users
        self.clear()
        layout_height = 64
        for user in users:
            btn = ToggleButton(text=self.config.steam_config.get_user_name(user), height=44, size_hint_y=None)
            self.ids['layout'].add_widget(btn)
            btn.bind(on_release=lambda *args: self.select_user(user, *args))
            layout_height += 44
        self.ids['layout'].height = layout_height
        print(f"layout height: {layout_height}")

    def select_user(self, user: str, button: ToggleButton, *args):
        if button.state == 'down':
            if self.selected_button is not None:
                self.selected_button.state = "normal"
            self.selected_button = button
            self.selected_user = user
        else:
            self.selected_button = None
            self.selected_user = None

    def clear(self):
        for widget in self.children[0].children:
            if isinstance(widget, ToggleButton):
                self.children[0].remove_widget(widget)


class EditAppDialog(Popup, EventDispatcher):
    app_name = StringProperty('My App')
    app_url = StringProperty('https://youtube.com')
    app_show_address_bar = BooleanProperty(False)

    __events__ = ('on_apply', 'on_cancel')

    def __init__(self, app: AppConfig = None, **kwargs):
        if app is not None:
            self.app_name = app.name
            self.app_url = app.url
            self.app_show_address_bar = not app.hide_address_bar
        self.applied = False
        super().__init__(**kwargs)

    def on_edit_app(*args):
        pass

    def on_pre_dismiss(self):
        pass

    def apply(self, *args):
        print(args)
        self.applied = True
        self.dispatch('on_apply', self.app_name, self.app_url, not self.app_show_address_bar)
        self.dismiss()

    def on_apply(self, *_):
        pass

    def on_cancel(self, *_):
        pass

    def set_name(self, value: str):
        self.app_name = value

    def set_url(self, value: str):
        self.app_url = value

    def set_show_address_bar(self, value: bool):
        self.app_show_address_bar = value


class Apps(BoxLayout):
    model: Configuration = ObjectProperty(defaultvalue=None)
    app_manager: AppManager
    selected_user = StringProperty(defaultvalue=None, allownone=True)

    def show_edit_dialog(self, app: AppConfig | None):
        popup = EditAppDialog(app=app)
        def callback(_, *args):
            if app is None:
                return self.on_add_app(*args)
            else:
                return self.on_edit_app(app, *args)

        popup.bind(on_apply=callback)
        popup.open()

    def on_kv_post(self, base_widget):
        self.update_app_list()
        self.bind(selected_user=lambda *_: self.update_app_list())
        print(self.selected_user)

    def update_app_list(self):
        container: BoxLayout = self.ids['apps_container'].__self__
        container.clear_widgets()

        if self.model is None:
            return
        apps = self.model.apps

        app: AppConfig
        for app in sorted(apps, key=lambda a: a.name):
            app_widget = SDApp(app, self.selected_user)
            self.bind(selected_user=app_widget.setter('selected_user'))
            app_widget.bind(on_remove=self.on_remove_app)
            app_widget.bind(on_toggle_enabled=self.on_toggle_app_enabled)
            app_widget.bind(on_edit=lambda _, widget_app: self.show_edit_dialog(widget_app))
            container.add_widget(app_widget)
        #container.add_widget(HLine())

    def on_add_app(self, app_name: str, app_url: str, hide_address_bar: bool):
        self.app_manager.add_app(app_name, app_url, hide_adress_bar=hide_address_bar)
        self.update_app_list()
        self.save_model()

    def on_edit_app(self, app: AppConfig, app_name: str, app_url: str, hide_address_bar: bool):
        self.app_manager.update_app(app, AppConfig.load(asdict(app) | {
            'name': app_name,
            'url': app_url,
            'hide_address_bar': hide_address_bar
        }))
        self.update_app_list()
        self.save_model()

    def on_toggle_app_enabled(self, app_widget: 'SDApp'):
        app: AppConfig = app_widget.app
        if app.is_installed_for_user(self.selected_user):
            self.app_manager.uninstall_app(app_widget.app, self.selected_user)
        else:
            self.app_manager.install_app(app_widget.app, self.selected_user)
        app_widget.update_enabled_status()
        self.save_model()

    def on_remove_app(self, app_widget: 'SDApp'):
        self.app_manager.remove_app(app_widget.app)
        self.update_app_list()
        self.save_model()

    def save_model(self):
        self.model.dump(self.model.config_path)


class SDApp(BoxLayout, EventDispatcher):
    app: AppConfig = ObjectProperty(defaultvalue=None)
    selected_user = StringProperty(defaultvalue=None, allownone=True)
    is_enabled = BooleanProperty(False)

    __events__ = ('on_remove', 'on_toggle_enabled', 'on_edit')

    def __init__(self, app: AppConfig, selected_user: str, **kwargs):
        self.selected_user = selected_user
        self.app = app
        self.register_event_type('on_remove')
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.update_enabled_status()

    def update_enabled_status(self):
        self.is_enabled = self.selected_user is not None and self.app.is_installed_for_user(self.selected_user)

    def on_toggle_enabled(self):
        pass

    def on_remove(self, *arg):
        print(arg)
        pass

    def on_edit(self, *args):
        pass


class StreamDeckApp(App):

    def build(self):
        return SDRootWidget(config)


if __name__ == '__main__':
    print(config)
    StreamDeckApp().run()
