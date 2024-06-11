from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.popup import Popup
from jnius import autoclass
from kivy.clock import Clock

# Java classes for window management
PythonActivity = autoclass('org.kivy.android.PythonActivity')
WindowManager = autoclass('android.view.WindowManager')
View = autoclass('android.view.View')
LayoutParams = autoclass('android.view.WindowManager$LayoutParams')


class PasswordActivity(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Variable to store password
        self.password = "1234"

        # Initialize TextInput for password entry
        self.password_input = TextInput(password=True, multiline=False, readonly=True)
        self.add_widget(self.password_input)

        # Initialize Button to check password
        self.check_button = Button(text="Проверить")
        self.check_button.bind(on_release=self.check_password)
        self.add_widget(self.check_button)

        # Initialize Label for messages
        self.message_label = Label(text="")
        self.add_widget(self.message_label)

        # Add virtual keyboard
        self.virtual_keyboard = VirtualKeyboard(self.password_input)
        self.add_widget(self.virtual_keyboard)

    def check_password(self, instance):
        entered_password = self.password_input.text

        # Check the entered password
        if entered_password == self.password:
            # Password is correct, terminate the program
            App.get_running_app().stop()
        else:
            # Password is incorrect, display error message
            self.message_label.text = "Неверный пароль"


class VirtualKeyboard(GridLayout):
    def __init__(self, text_input, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.text_input = text_input
        self.key_sets = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'],
            ['&', '@', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '\\', '|', ';', ':', '\'', '\"', ',', '<', '.', '>', '/', '?']
        ]
        self.current_key_set = 0
        self.draw_keys()

    def draw_keys(self):
        self.clear_widgets()
        for key in self.key_sets[self.current_key_set]:
            button = Button(text=key)
            button.bind(on_release=self.on_key_press)
            self.add_widget(button)

        # Add backspace button
        backspace_button = Button(text='<-')
        backspace_button.bind(on_release=self.on_backspace_press)
        self.add_widget(backspace_button)

        # Add switch button
        switch_button = Button(text='Символы' if self.current_key_set == 0 else 'Цифры')
        switch_button.bind(on_release=self.switch_key_set)
        self.add_widget(switch_button)

    def on_key_press(self, instance):
        self.text_input.text += instance.text

    def on_backspace_press(self, instance):
        self.text_input.text = self.text_input.text[:-1]

    def switch_key_set(self, instance):
        self.current_key_set = (self.current_key_set + 1) % len(self.key_sets)
        self.draw_keys()


class PasswordApp(App):
    def build(self):
        Window.bind(on_request_close=self.prevent_close)
        Window.bind(on_keyboard=self.on_key)
        Window.fullscreen = 'auto'  # Fullscreen mode
        Window.show_cursor = False  # Hide cursor

        # Get the current activity
        activity = PythonActivity.mActivity

        def set_flags():
            win = activity.getWindow()
            # Set flags to lock the bottom navigation bar and notifications
            win.addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)
            win.addFlags(LayoutParams.FLAG_DISMISS_KEYGUARD)
            win.addFlags(LayoutParams.FLAG_FULLSCREEN)
            win.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )

        # Run the flag changes in the UI thread
        activity.runOnUiThread(set_flags)

        self.last_attempt_time = 0  # Time of the last attempt to close

        return PasswordActivity()

    def prevent_close(self, *args):
        current_time = Clock.get_time()
        if current_time - self.last_attempt_time < 1:  # 1-second delay between attempts
            return True
        self.last_attempt_time = current_time

        # Intercept the attempt to close the app
        popup = Popup(title='Ошибка',
                      content=Label(text='Вы не можете закрыть приложение. Введите правильный пароль.'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
        return True  # Return True to prevent window closure

    def on_key(self, window, key, scancode, codepoint, modifier):
        if key in (27, 1001, 1002, 1003, 1004):  # 27 is the code for "Back" key on Android, 1001-1004 are other system keys
            current_time = Clock.get_time()
            if current_time - self.last_attempt_time < 1:  # 1-second delay between attempts
                return True
            self.last_attempt_time = current_time

            # Intercept the attempt to press system keys
            popup = Popup(title='Ошибка',
                          content=Label(text='Вы не можете выйти из приложения. Введите правильный пароль.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return True  # Return True to prevent default action
        return False


# Run the app
if __name__ == "__main__":
    PasswordApp().run()