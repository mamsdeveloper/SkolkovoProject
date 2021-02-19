import csv
import os
import sys

from itertools import zip_longest
from random import choice, shuffle
from tkinter import TclError, Tk, filedialog

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField


class MainWidget(ScreenManager):
    pass


class MainScreen(MDScreen):
    def on_kv_post(self, *args):
        self._tk_window = Tk()
        self._tk_window.geometry('0x0+1920+1080')

    def redirect_to_view(self):
        keys_to_count = self._pars_bd(self.path)
        if not keys_to_count:
            return

        self.parent.add_widget(
            ViewScreen(
                name='View',
                keys_to_count=keys_to_count
        ))
        self.parent.current = 'View'

    def _pars_bd(self, filepath):
        keys_count = {}

        try:
            with open(filepath, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                keys = ['']

                for row in spamreader:
                    string = row[0]

                    if string == 'time,key':
                        continue

                    string = string[(string.find('{')+1):]
                    string = string[:-2]
                    string = string.replace("'", '')
                    row_keys = string.split(',')

                    for key in row_keys:
                        if not key in keys[-1]:
                            if key in keys_count:
                                keys_count[key] += 1
                            else:
                                keys_count[key] = 1
                    keys += [row_keys]
                keys_count.pop('')    
            return keys_count

        except FileNotFoundError:
            return 0

    def _ask_save_file(self):
        self._tk_window = Tk()
        self._tk_window.geometry('0x0+1920+1080')
        
        file = filedialog.asksaveasfilename(
            title="Открыть файл",
            initialdir="/",
            filetypes=[("Text files", '*.txt')]
        )

        self._tk_window.destroy()

        if not '.txt' in file:
            file += '.txt'

        return file
    
    def save_keys_file(self):
        keys_to_count = self._pars_bd(self.path)
        if not keys_to_count:
            return

        file = self._ask_save_file()
        if file == '.txt':
            return

        with open(file, 'w') as keys_file:
            for key, count in keys_to_count.items():
                keys_file.write(f'Key "{key}" was pressed {count} times\n')


class ViewScreen(MDScreen):
    def __init__(self, **kwargs):
        self._keys_to_count = kwargs['keys_to_count']
        super().__init__(name=kwargs['name'])

    def on_kv_post(self, *args):
        self._create_key_cards()

    def _sort_keys(self):
        keys = list(self._keys_to_count.keys())
        sorted_keys = []

        short = filter(lambda x: len(x) == 1, keys)
        long = filter(lambda x: len(x) > 1, keys)

        alone_keys = []

        for l_key, s_key in zip_longest(long, short, fillvalue=None):
            if l_key:
                if len(l_key) % 2:
                    sorted_keys += [(s_key, l_key)]
                else:
                    sorted_keys += [(l_key, s_key)]
            else:
                alone_keys += [s_key]

        for grouped_key in zip(*[iter(alone_keys)] * 3):
            sorted_keys += [grouped_key]

        shuffle(sorted_keys)
        sorted_keys += alone_keys[-(len(alone_keys) % 3):]

        result = {}

        for grouped_key in sorted_keys:
            for key in grouped_key:
                result.update({key: self._keys_to_count[key]})

        return result

    def _create_key_cards(self):
        for key, count in self._sort_keys().items():
            self.ids['layout'].add_widget(KeyCard(key, count))

    def redirect_to_main(self):
        self.parent.current = 'Main'
        self.parent.remove_widget(self)


class GlassInput(MDTextField):
    pass


class GlassButton(AnchorLayout):
    def on_kv_post(self, *args, **kwargs):
        self.children[0].children[0]._radius = 15 // 1.5


class KeyCard(AnchorLayout):
    def __init__(self, key, count=0):
        self.key = key
        self.count = str(count)
        self.is_wide = len(key) > 1
        super().__init__()


class HHPApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Gray'
        
        if hasattr(sys, '_MEIPASS'):
            self.location = sys._MEIPASS.replace('\\', '\\\\')
        else:
            self.location = os.path.abspath(".").replace('\\', '\\\\')

        with open(os.path.join(self.location, 'HHP.kv'), 'r') as file:
            Builder.load_string(file.read())

        self.icon = os.path.join(self.location, 'icon.png')
        
        Window.bind(on_dropfile=self._on_file_drop)
        Config.set('graphics', 'resizable', False)
        Config.write()
        
        self.scale = 1080 / Window.height
        Window.size = (506 // self.scale, 708 // self.scale)

        self._main_widget = MainWidget()
        self._main_widget.add_widget(MainScreen(name='Main'))
        self._main_widget.current = 'Main'

        return self._main_widget

    def on_stop(self):
        if self._main_widget.current == 'View':
            return

        try:
            self._main_widget.children[-1]._tk_window.destroy()
        except TclError:
            pass

    def _on_file_drop(self, window, filepath):
        if self._main_widget.current == 'Main':
            self._main_widget.current_screen.ids['input'].text = filepath


def main():
    HHPApp().run()


if __name__ == '__main__':
    main()
