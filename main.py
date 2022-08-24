from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition, FallOutTransition, \
    CardTransition, RiseInTransition
from kivy.factory import Factory
from kivy.clock import Clock
import logging
import search
import threading
import concurrent


class BlankScreen(Screen):
    pass


class SetupScreen1(Screen):
    def image_clicked(self, instance):
        print('down')
        instance.source = 'assets/app_icons/bank_select.png'


class SetupScreen2(Screen):
    pass


class SetupScreen3(Screen):
    pass


class MainScreen(Screen):
    current_displayed_results = []

    def display_search(self, results: list):
        logging.info("Displaying results from search")
        self.manager.get_screen("main_screen").current_displayed_results = results
        for result in results:
            self.new_video_preview = Factory.VideoPreview()
            self.new_video_preview.preview_image = result["thumbnail"]
            self.new_video_preview.title = result["title"]
            self.new_video_preview.id = result["id"]
            self.new_video_preview.bind(on_touch_down=self.manager.get_screen("main_screen").preview_clicked)
            self.manager.get_screen("main_screen").ids.video_grid.add_widget(self.new_video_preview)

    def clear_results(self):
        self.ids.video_grid.clear_widgets()

    def open_menu(self):
        self.ids.menu_view.dismiss()

    def preview_clicked(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.manager.transition = RiseInTransition()
            self.manager.duration = 0
            self.manager.current = "video_screen"
            threading.Thread(target=self.fetch_video, args=(instance,)).start()

    def fetch_video(self, instance):
        # get id from instance, get url of that id and then convert that to a mp4 and send to the video widget
        with concurrent.futures.ThreadPoolExecutor() as executor:
            yt_dlp = executor.submit(search.url_to_mp4, self.current_displayed_results[instance.id]["page_url"])
            converted_url = yt_dlp.result()
        # converted_url = search.url_to_mp4(self.current_displayed_results[instance.id]["page_url"])
        # temporary only get 240p, because there is no quality selection yet
        self.manager.get_screen("video_screen").ids.video_widget.source = converted_url[0]["480p"]
        # Not really needed, coz video autostarts
        self.manager.get_screen("video_screen").ids.video_widget.preview = converted_url[1]
        self.manager.get_screen("video_screen").ids.video_widget.state = 'play'


class VideoScreen(Screen):
    show_controls = False
    controls_grabbed = False

    def toggle_video(self):
        if self.ids.video_widget.state == 'play':
            self.ids.video_widget.state = 'pause'
            self.controls_grabbed = True
        elif self.ids.video_widget.state == 'pause':
            self.ids.video_widget.state = 'play'
            self.controls_grabbed = False
            Clock.schedule_once(self.disable_controls, 0.5)

    def enable_controls(self):
        if not self.show_controls:
            self.show_controls = True
            # show all control widgets
            self.ids.controls_play.disabled = False
            self.ids.controls_background.disabled = False
            self.ids.controls_progress_bar.disabled = False

            Clock.schedule_once(self.disable_controls, 3)

    def disable_controls(self, unused):  # the unused var is there coz Clock.schedule_once gives two values
        if not self.controls_grabbed:
            self.ids.controls_play.disabled = True
            self.ids.controls_background.disabled = True
            self.ids.controls_progress_bar.disabled = True

            self.show_controls = False


class SearchScreen(Screen):

    def search(self):
        # add getting filters from gui

        # for testing
        MainScreen.display_search(self, search.search_request(["pornhub"], "", []))


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.keyboard)

    def select_start_screen(self):  # Decide whether setup screen needs to be shown to user
        self.transition = NoTransition()
        self.transition.duration = 0
        if skip_setup:
            self.current = 'main_screen'
        else:
            self.current = 'setup_screen_1'

    def keyboard(self, window, key, *args):
        # Back gesture on android
        if key == 27:
            # TODO: rewrite as match
            current_screen = self.current
            if current_screen == "setup_screen_1":
                return False
            elif current_screen == "setup_screen_2":
                self.transition = SlideTransition()
                self.transition.direction = "right"
                self.current = "setup_screen_1"
            elif current_screen == "setup_screen_3":
                self.transition = SlideTransition()
                self.transition.direction = "right"
                self.current = "setup_screen_2"
            elif current_screen == "main_screen":
                return False
            elif current_screen == "video_screen":
                self.get_screen("video_screen").ids.video_widget.state = 'pause'
                self.transition = FallOutTransition()
                self.current = "main_screen"
            elif current_screen == "search_screen":
                self.transition = CardTransition()
                self.transition.duration = 0.3
                self.transition.mode = 'pop'
                self.transition.direction = 'down'
                self.current = 'main_screen'
            return True  # key event consumed by app
        else:
            return False  # exits app to mainscreen


class MainApp(App):
    def build(self):
        Window.clearcolor = (26 / 255, 28 / 255, 25 / 255, 1)
        window_manager = WindowManager()
        window_manager.select_start_screen()
        # Window.maximize()
        # Window.fullscreen = True
        return window_manager


if __name__ == '__main__':
    skip_setup = True  # for testing
    MainApp().run()
