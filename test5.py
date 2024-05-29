from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.popup import Popup
from jnius import autoclass

# Java классы для управления окнами
PythonActivity = autoclass('org.kivy.android.PythonActivity')
WindowManager = autoclass('android.view.WindowManager')
View = autoclass('android.view.View')
LayoutParams = autoclass('android.view.WindowManager$LayoutParams')

class PasswordActivity(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Переменная для хранения пароля
        self.password = "1234"

        # Инициализация TextInput для ввода пароля
        self.password_input = TextInput(password=True, multiline=False, readonly=True)
        self.add_widget(self.password_input)

        # Инициализация Button для проверки пароля
        self.check_button = Button(text="Проверить")
        self.check_button.bind(on_release=self.check_password)
        self.add_widget(self.check_button)

        # Инициализация Label для сообщений
        self.message_label = Label(text="")
        self.add_widget(self.message_label)

        # Добавляем виртуальную клавиатуру
        self.add_widget(VirtualKeyboard(self.password_input))

    def check_password(self, instance):
        entered_password = self.password_input.text

        # Проверка введенного пароля
        if entered_password == self.password:
            # Пароль введен правильно, завершаем программу
            App.get_running_app().stop()
        else:
            # Пароль введен неправильно, показываем сообщение об ошибке
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

        # Добавляем кнопку для удаления последнего символа
        backspace_button = Button(text='<-')
        backspace_button.bind(on_release=self.on_backspace_press)
        self.add_widget(backspace_button)

        # Добавляем кнопку для переключения клавиатуры
        switch_button = Button(text='Switch')
        switch_button.bind(on_release=self.switch_key_set)
        self.add_widget(switch_button)

    def draw_keys(self):
        self.clear_widgets()
        for key in self.key_sets[self.current_key_set]:
            button = Button(text=key)
            button.bind(on_release=self.on_key_press)
            self.add_widget(button)

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
        Window.fullscreen = 'auto'  # Полноэкранный режим
        Window.show_cursor = False  # Скрыть курсор

        # Получаем текущую активность
        activity = PythonActivity.mActivity

        def set_flags():
            win = activity.getWindow()
            # Устанавливаем флаги для блокировки нижней навигационной панели и уведомлений
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

        # Запускаем изменение флагов в UI потоке
        activity.runOnUiThread(set_flags)

        return PasswordActivity()

    def prevent_close(self, *args):
        # Перехват попытки закрытия приложения
        popup = Popup(title='Ошибка',
                      content=Label(text='Вы не можете закрыть приложение. Введите правильный пароль.'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
        return True  # Возвращаем True, чтобы предотвратить закрытие окна

    def on_key(self, window, key, scancode, codepoint, modifier):
        if key in (27, 1001, 1002, 1003, 1004):  # 27 это код клавиши "Назад" на Android, 1001-1004 - другие системные кнопки
            # Перехват попытки нажатия системных кнопок
            popup = Popup(title='Ошибка',
                          content=Label(text='Вы не можете выйти из приложения. Введите правильный пароль.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return True  # Возвращаем True, чтобы предотвратить действие по умолчанию
        return False

# Запуск приложения
if __name__ == "__main__":
    PasswordApp().run()
