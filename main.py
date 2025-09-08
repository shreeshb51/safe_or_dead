from kivy.config import Config
Config.set('graphics', 'width', '390') # default width when tested
Config.set('graphics', 'height', '700') # default height when tested
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.core.audio import SoundLoader
import random
from enum import Enum

class GameState(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    GAME_OVER = "game_over"

class RoundedButton(Button):
    def __init__(self, bg_color=(0.2, 0.6, 0.9, 1), **kwargs):
        if 'bg_color' in kwargs:
            bg_color = kwargs.pop('bg_color')
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])

class CustomPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.separator_color = (0.2, 0.7, 0.9, 1)
        self.separator_height = dp(3)
        self.title_color = (1, 0.9, 0.3, 1)
        self.title_size = '24sp'

        with self.canvas.before:
            Color(0.15, 0.15, 0.25, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class GameTile(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self._is_revealed = False
        self._tile_state = 'hidden' # 'hidden', 'safe', 'dead'
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self.reset_tile()

    def reset_tile(self):
        self.text = '?'
        self.font_size = '26sp'
        self.color = (1, 0.9, 0.4, 1) # golden yellow
        self.bold = True
        self._is_revealed = False
        self._tile_state = 'hidden'
        self._update_graphics()

    def reveal_safe(self):
        self.text = '[color=ffffff]SAFE[/color]'
        self.markup = True
        self.font_size = '20sp'
        self._is_revealed = True
        self._tile_state = 'safe'
        self._update_graphics()

    def reveal_dead(self):
        self.text = '[color=ffffff]DEAD[/color]'
        self.markup = True
        self.font_size = '20sp'
        self._is_revealed = True
        self._tile_state = 'dead'
        self._update_graphics()

    def _update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._tile_state == 'safe':
                Color(0.0, 0.4, 0.0, 1) # green
            elif self._tile_state == 'dead':
                Color(0.4, 0.0, 0.0, 1) # red
            else:
                Color(0.4, 0.4, 0.5, 1) # blue-gray
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ui()
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main_menu'), 3)

    def _setup_ui(self):
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)
        layout.add_widget(Label(
            halign='center',
            text='aRbiTrarY\nGames',
            font_size='52sp',
            color=(1, 0.8, 0.2, 1),
            bold=True
        ))
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ui()

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=self._update_bg, pos=self._update_bg)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=35)
        layout.add_widget(Label(
            text='SAFE or DEAD',
            font_size='48sp',
            color=(1, 0.1, 0.1, 1),
            size_hint_y=0.3,
            bold=True
        ))
        buttons = [
            ('Play Game', (0.2, 0.8, 0.3, 1), lambda x: setattr(self.manager, 'current', 'game')),
            ('Instructions', (0.3, 0.6, 0.9, 1), lambda x: setattr(self.manager, 'current', 'instructions')),
            ('Credits', (0.9, 0.5, 0.2, 1), lambda x: setattr(self.manager, 'current', 'credits')),
            ('Exit', (0.8, 0.2, 0.2, 1), lambda x: App.get_running_app().stop())
        ]
        button_container = BoxLayout(orientation='vertical', spacing=15, size_hint_x=None, width=dp(200), pos_hint={'center_x': 0.5})
        for text, color, callback in buttons:
            btn = RoundedButton(
                text=text,
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                font_size='20sp',
                color=(1, 1, 1, 1),
                bold=True,
                bg_color=color
            )
            btn.bind(on_press=callback)
            button_container.add_widget(btn)

        layout.add_widget(button_container)
        mute_btn = RoundedButton(
            text='UNMUTE' if App.get_running_app().sound_enabled else 'MUTE',
            size_hint=(None, None),
            size=(dp(60), dp(30)),
            pos_hint={'x': 0.02, 'top': 0.98},
            font_size='12sp',
            bg_color=(0.5, 0.5, 0.5, 1)
        )
        mute_btn.bind(on_press=self._toggle_sound)
        self.add_widget(layout)
        self.add_widget(mute_btn)

    def _toggle_sound(self, instance):
        app = App.get_running_app()
        app.sound_enabled = not app.sound_enabled
        instance.text = 'UNMUTE' if app.sound_enabled else 'MUTE'

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class InstructionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ui()

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=self._update_bg, pos=self._update_bg)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(
            text='How to Play',
            font_size='32sp',
            color=(1, 0.8, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
            bold=True
        ))

        scroll = ScrollView()
        instructions = Label(
            text='Choose "SAFE" tiles to progress and win coins!\n\nAvoid "DEAD" tiles or lose everything.\n\nEach level has different numbers of "DEAD" tiles and multipliers.\nThe higher you go, the more you can win!\n\nYou can cash out at any time to secure your winnings.\n\nReach level 8 to hit the JACKPOT!',
            text_size=(None, None),
            halign='center',
            valign='top',
            font_size='18sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        instructions.bind(width=lambda *x: instructions.setter('text_size')(instructions, (instructions.width, None)))
        scroll.add_widget(instructions)

        back_btn = RoundedButton(
            text='Back',
            size_hint_y=None,
            height=dp(50),
            font_size='20sp',
            color=(1, 1, 1, 1),
            bg_color=(0.6, 0.3, 0.8, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))

        layout.add_widget(scroll)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ui()

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=self._update_bg, pos=self._update_bg)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(
            text='Credits',
            font_size='32sp',
            color=(1, 0.8, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
            bold=True
        ))

        layout.add_widget(Label(
            text='Shreesh Bhattarai Games\nVersion: 1.0\nPlatform: Python-Kivy\nSounds: https://www.wavsource.com\n© 2025 All rights reserved',
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size='16sp',
            color=(0.9, 0.9, 0.9, 1)
        ))

        back_btn = RoundedButton(
            text='Back',
            size_hint_y=None,
            height=dp(50),
            font_size='20sp',
            color=(1, 1, 1, 1),
            bg_color=(0.6, 0.3, 0.8, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 1
        self.bet_amount = 10
        self.current_winnings = 0
        self.game_state = GameState.INACTIVE
        self.game_tiles = []
        self.all_dead_positions = {}
        self.MULTIPLIERS = [1.23, 2.78, 3.01, 10.55, 26.83, 42.16, 69.69, 89.69]
        self.DEAD_COUNTS = [1, 1, 2, 2, 2, 3, 3, 4]
        self._setup_ui()

    def _set_level_state(self, active_level=None, enable_all=False):
        for i, level_tiles in enumerate(self.game_tiles):
            should_enable = enable_all or (active_level is not None and i == active_level and self.game_state == GameState.ACTIVE)
            for tile in level_tiles:
                tile.disabled = not should_enable

    def _go_to_menu(self, instance):
        if self.game_state != GameState.ACTIVE:
            self._cleanup_resources()
        self.manager.current = 'main_menu'

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=self._update_bg, pos=self._update_bg)
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.balance_label = Label(text='Balance: 100 coins', font_size='20sp', color=(1, 0.8, 0.2, 1), bold=True)
        self.winnings_label = Label(text='Winnings: 0 coins', font_size='20sp', color=(0.2, 0.8, 0.3, 1), bold=True)
        info_layout.add_widget(self.balance_label)
        info_layout.add_widget(self.winnings_label)
        bet_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=15)
        bet_layout.add_widget(Label(
            text='Bet:',
            font_size='20sp',
            size_hint_x=None,
            width=dp(50),
            height=dp(50),
            color=(0.9, 0.9, 0.9, 1)
        ))
        self.bet_input = TextInput(
            text='10',
            multiline=False,
            input_filter='int',
            size_hint_x=None,
            width=dp(60),
            font_size='20sp',
            halign='center',
        )
        self.bet_input.bind(text=self._validate_bet_input)
        self.start_btn = RoundedButton(
            text='Start Game',
            size_hint_x=1,
            size_hint_y=None,
            height=dp(50),
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.2, 0.8, 0.3, 1)
        )
        self.start_btn.bind(on_press=self._start_game)
        bet_layout.add_widget(self.bet_input)
        bet_layout.add_widget(self.start_btn)
        self.levels_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.6)

        for display_idx in range(8):
            actual_level = 7 - display_idx
            level_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=10)
            multiplier_label = Label(
                text=f'Level {actual_level + 1}\n{self.MULTIPLIERS[actual_level]:.2f}x',
                size_hint_x=0.15, font_size='16sp', color=(1, 0.8, 0.2, 1), halign='center', bold=True
            )

            level_grid = GridLayout(cols=5, spacing=12, size_hint_x=0.85)
            level_tiles = []
            for j in range(5):
                tile = GameTile(disabled=True)
                tile.bind(on_press=lambda x, level=actual_level, pos=j: self._tile_clicked(level, pos))
                level_grid.add_widget(tile)
                level_tiles.append(tile)

            self.game_tiles.insert(0, level_tiles)
            level_container.add_widget(multiplier_label)
            level_container.add_widget(level_grid)
            self.levels_layout.add_widget(level_container)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=15)
        button_layout.pos_hint = {'center_x': 0.5}
        self.cash_out_btn = RoundedButton(
            text='Cash Out',
            disabled=True,
            size_hint=(None, None),
            size=(dp(120), dp(50)),
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.9, 0.6, 0.1, 1)
        )
        self.cash_out_btn.bind(on_press=self._cash_out)
        self.reset_btn = RoundedButton(
            text='Reset',
            size_hint=(None, None),
            size=(dp(120), dp(50)),
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.8, 0.3, 0.3, 1)
        )
        self.reset_btn.bind(on_press=self._reset_balance)
        back_btn = RoundedButton(
            text='Menu',
            size_hint=(None, None),
            size=(dp(120), dp(50)),
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.6, 0.3, 0.8, 1)
        )
        back_btn.bind(on_press=self._go_to_menu)
        self.restart_btn = RoundedButton(
            text='Restart Game',
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.2, 0.8, 0.3, 1)
        )
        self.restart_btn.bind(on_press=self._restart_game)

        self.home_btn = RoundedButton(
            text='Home',
            font_size='16sp',
            color=(1, 1, 1, 1),
            bg_color=(0.6, 0.3, 0.8, 1)
        )
        self.home_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        button_layout.add_widget(self.cash_out_btn)
        button_layout.add_widget(self.reset_btn)
        button_layout.add_widget(back_btn)

        self.game_over_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=15)
        self.game_over_layout.pos_hint = {'center_x': 0.5}
        self.game_over_layout.add_widget(self.restart_btn)
        self.game_over_layout.add_widget(self.home_btn)

        main_layout.add_widget(info_layout)
        main_layout.add_widget(bet_layout)
        main_layout.add_widget(self.levels_layout)
        main_layout.add_widget(button_layout)
        self.add_widget(main_layout)

    def _validate_bet_input(self, instance, text):
        try:
            if text and int(text) > 1000:
                instance.text = '1000'
        except ValueError:
            pass

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _start_game(self, instance):
        if self.game_over_layout.parent:
            main_layout = self.children[0]
            main_layout.remove_widget(self.game_over_layout)
            if hasattr(self, '_original_button_layout') and self._original_button_layout not in main_layout.children:
                main_layout.add_widget(self._original_button_layout)

        if self.game_state == GameState.ACTIVE:
            self._update_display()
            self._update_button_states()
            self._set_level_state(active_level=self.level - 1)
            return

        app = App.get_running_app()
        try:
            bet = int(self.bet_input.text) if self.bet_input.text else 10
            if bet > app.balance:
                return self._show_popup('Insufficient Balance!')
            if bet > 1000:
                return self._show_popup('Bet Too High!\nMaximum bet is 1000 coins')
            if bet <= 0:
                return self._show_popup('Invalid Bet!\nMust be greater than 0')
        except ValueError:
            return self._show_popup('Enter a valid bet!')

        self.all_dead_positions = {}
        for i in range(8):
            dead_count = self.DEAD_COUNTS[i]
            positions = list(range(5))
            random.shuffle(positions)
            self.all_dead_positions[i] = positions[:dead_count]

        app.balance -= bet
        self.bet_amount = bet
        self.level = 1
        self.current_winnings = 0
        self.game_state = GameState.ACTIVE
        self._reset_all_tiles()
        self._setup_level()
        self._update_display()
        self._update_button_states()

    def _reset_all_tiles(self):
        for level_tiles in self.game_tiles:
            for tile in level_tiles:
                tile.reset_tile()
                tile.disabled = True

        if hasattr(self, 'game_over_layout') and self.game_over_layout.parent:
            self.game_over_layout.parent.remove_widget(self.game_over_layout)

    def _setup_level(self):
        if self.level > 8:
            return self._win_game()

        if not hasattr(self, 'all_dead_positions') or not self.all_dead_positions:
            return

        self.dead_positions = self.all_dead_positions[self.level - 1]
        self._set_level_state(active_level=self.level - 1)
        self.cash_out_btn.disabled = self.level == 1

    def _tile_clicked(self, level, position):
        if self.game_state != GameState.ACTIVE or level != (self.level - 1):
            return

        tile = self.game_tiles[level][position]
        for t in self.game_tiles[level]:
            t.disabled = True

        app = App.get_running_app()
        if hasattr(app, 'sound_enabled') and app.sound_enabled and hasattr(app, 'button_sound') and app.button_sound:
            app.button_sound.play()

        if position in self.dead_positions:
            tile.reveal_dead()
            Clock.schedule_once(lambda dt: self._show_death_popup(), 0.2)

        else:
            tile.reveal_safe()
            Clock.schedule_once(lambda dt: self._level_complete(), 0.04)

    def _show_death_popup(self):
        popup = CustomPopup(
            title='',
            content=Label(
                text='Game Over!\nYou hit a DEAD tile.',
                color=(1, 0.9, 0.9, 1),
                font_size='16sp',
                text_size=(dp(250), None),
                halign='center'
            ),
            size_hint=(0.5, 0.2)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.4)
        Clock.schedule_once(lambda dt: self._reveal_all_and_end_game(), 1.6)

    def _reveal_all_and_end_game(self):
        for level_idx, level_tiles in enumerate(self.game_tiles):
            level_dead_positions = self.all_dead_positions.get(level_idx, [])
            for pos, tile in enumerate(level_tiles):
                if pos in level_dead_positions:
                    tile.reveal_dead()
                else:
                    tile.reveal_safe()
                tile.disabled = True

        self._show_game_over_buttons()
        self.game_state = GameState.GAME_OVER
        self.level = 1
        self.current_winnings = 0
        self.cash_out_btn.disabled = True
        self._update_display()
        self._update_button_states()

    def _show_game_over_buttons(self):
            main_layout = self.children[0]
            for child in main_layout.children:
                if hasattr(child, 'children'):
                    for subchild in child.children:
                        if hasattr(subchild, 'text') and 'Cash Out' in subchild.text:
                            self._original_button_layout = child
                            main_layout.remove_widget(child)
                            if self.game_over_layout not in main_layout.children:
                                main_layout.add_widget(self.game_over_layout)
                            return

    def _level_complete(self):
        self.current_winnings = int(self.bet_amount * self.MULTIPLIERS[self.level - 1])
        if self.level >= 8:
            return self._win_game()

        self.level += 1
        self.cash_out_btn.disabled = False
        self._setup_level()
        self._update_display()

    def _cash_out(self, instance):
        app = App.get_running_app()
        app.balance += self.current_winnings
        self._show_popup(f'You won\n{self.current_winnings} coins!')
        self._reset_all_tiles()
        self._show_game_over_buttons()
        self.game_state = GameState.GAME_OVER

    def _win_game(self):
        app = App.get_running_app()
        winnings = int(self.bet_amount * self.MULTIPLIERS[7])
        app.balance += winnings
        self._show_popup(f'JACKPOT!\nYou won {winnings} coins!')
        self._show_game_over_buttons()
        self.game_state = GameState.GAME_OVER
        self._update_display()

    def _reset_game_state(self):
        self.game_state = GameState.INACTIVE
        self.level = 1
        self.current_winnings = 0
        self.cash_out_btn.disabled = True

    def _update_button_states(self):
        if self.game_state == GameState.ACTIVE:
            self.start_btn.disabled = True
            self.reset_btn.disabled = True
            self.bet_input.disabled = True

        elif self.game_state == GameState.GAME_OVER:
            self.start_btn.disabled = True
            self.reset_btn.disabled = False
            self.bet_input.disabled = True

        elif self.game_state == GameState.INACTIVE:
            self.start_btn.disabled = False
            self.reset_btn.disabled = False
            self.bet_input.disabled = False

    def _cleanup_resources(self):
        Clock.unschedule(self._show_death_popup)
        Clock.unschedule(self._level_complete)
        Clock.unschedule(self._reveal_all_and_end_game)
        Clock.unschedule(self._dismiss_popup)
        for level_tiles in self.game_tiles:
            for tile in level_tiles:
                tile.unbind(on_press=tile.dispatch)

        if hasattr(self, 'all_dead_positions') and self.game_state != GameState.ACTIVE:
            self.all_dead_positions.clear()

    def _restart_game(self, instance):
        self._reset_game_state()
        self._update_button_states()
        if hasattr(self, 'all_dead_positions'):
            delattr(self, 'all_dead_positions')

        main_layout = self.children[0]
        if self.game_over_layout in main_layout.children:
            main_layout.remove_widget(self.game_over_layout)

        if hasattr(self, '_original_button_layout') and self._original_button_layout not in main_layout.children:
            main_layout.add_widget(self._original_button_layout)

        self._reset_all_tiles()
        self._update_display()

    def _reset_balance(self, instance):
        App.get_running_app().balance = 100
        self._update_display()
        self._show_popup('Balance reset to\n100 coins.')

    def _update_display(self):
        app = App.get_running_app()
        self.balance_label.text = f'Balance: {app.balance} coins'
        self.winnings_label.text = f'Winnings: {self.current_winnings} coins'

    def _show_popup(self, message):
        popup = CustomPopup(
            title='',
            content=Label(
                text=message,
                color=(0.9, 0.9, 1, 1),
                font_size='16sp',
                text_size=(dp(250), None),
                halign='center'
            ),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: self._dismiss_popup(popup), 1.4)

    def _dismiss_popup(self, popup):
        if popup:
            popup.dismiss()
            popup = None

    def on_enter(self):
        self._update_display()
        self._update_button_states()

class SafeOrDeadApp(App):
    def build(self):
        self.balance = 100
        self.sound_enabled = True
        self.button_sound = SoundLoader.load('button_click.wav')
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(InstructionsScreen(name='instructions'))
        sm.add_widget(CreditsScreen(name='credits'))
        sm.add_widget(GameScreen(name='game'))

        return sm

if __name__ == '__main__':
    SafeOrDeadApp().run()
