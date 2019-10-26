from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import threading
import assistant

rec_err = (
	"Sorry. I didn't quite catch that.",
	"Could not request results. Check the Internet connection",
	"No voice detected")

class OutputLabel(ScrollView):
	def __init__(self, **kwargs):
		super(OutputLabel, self).__init__(**kwargs)

		self.size = (Window.width, Window.height)
		self.layout = GridLayout(cols = 1, size_hint_y = None)
		
		self.add_widget(self.layout)

		self.chat_history = Label(size_hint_y = None)
		self.scroll_to_point = Label(size_hint_y = None)

		self.layout.add_widget(self.chat_history)
		self.layout.add_widget(self.scroll_to_point)

	def update_history(self, message):
		self.chat_history.text += "\n" + message
		
		self.layout.height = self.chat_history.texture_size[1] + 15
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width * 0.98, None)
		
		self.scroll_to(self.scroll_to_point)

class MainWindow(GridLayout):
	threading.Thread(target = assistant.play_audio, args = ("hello",)).start()
	def __init__(self,**kwargs):
		super(MainWindow, self).__init__(**kwargs)
		self.cols=1
		self.rows = 2
		self.history = OutputLabel()
		self.add_widget(self.history)

		self.btn = Button(text = "Speak")
		self.btn.bind(on_press = self.on_press)
		# self.btn.bind(on_release = self.execute)
		self.add_widget(self.btn)

	def rec_and_exec(self, *args):
		stt = assistant.recognize_voice()
		if stt:
			text = "You said: "+ stt
			self.history.update_history(text)
			if stt not in rec_err:
				threading.Thread(target = assistant.execute_command, args = (stt,)).start()
	
	def on_press(self, *args):
		self.history.update_history("Listening")

		if threading.active_count() < 2:
			threading.Thread(target = self.rec_and_exec).start()
		

class MyApp(App):
	def build(self):
		return MainWindow()

if __name__ == '__main__':
	MyApp().run()