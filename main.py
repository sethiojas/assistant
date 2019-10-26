from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
import assistant

rec_err = (
	"Sorry. I didn't quite catch that.",
	"Could not request results. Check the Internet connection",
	"No voice detected")

screen_manager = ScreenManager()

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
				threading.Thread(target = assistant.execute_command, args = (stt,screen_manager)).start()
	
	def on_press(self, *args):
		self.history.update_history("Listening")

		if threading.active_count() < 2:
			threading.Thread(target = self.rec_and_exec).start()
		

class DeleteNotes(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.size = (Window.width, Window.height)
		self.layout = GridLayout(cols = 1, size_hint_y = None)
		self.layout.bind(minimum_height=self.layout.setter('height'))
		self.add_widget(self.layout)
		self.notes = None
		with open("files/my_notes.txt", 'r') as file:
			self.notes = file.readlines()
		if self.notes:
			for item in self.notes:
				btn = Button(text = item, size_hint_y = None, height = "40dp")
				btn.bind(on_press = self.delete)
				self.layout.add_widget(btn)

	def delete(self, instance):
		self.notes.remove(instance.text)
		with open("files/my_notes.txt", 'w') as file:
			for item in self.notes:
				file.write(item)
		screen_manager.current = "main"
		assistant.play_audio("done")

class AssistantApp(App):
	def build(self):

		self.MainWindow = MainWindow()
		screen = Screen(name = "main")
		screen.add_widget(self.MainWindow)
		screen_manager.add_widget(screen)

		self.DeleteNotes = DeleteNotes()
		screen = Screen(name = "delete_notes")
		screen.add_widget(self.DeleteNotes)
		screen_manager.add_widget(screen)
		
		return screen_manager

if __name__ == '__main__':
	AssistantApp().run()