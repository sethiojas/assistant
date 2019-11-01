from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
import assistant

#Speech Recognition Errors
rec_err = (
	"Sorry. I didn't quite catch that.",
	"Could not request results. Check the Internet connection",
	"No voice detected")

screen_manager = ScreenManager()

class OutputLabel(ScrollView):
	'''
	Class handles the scrollable output window and also the
	updation of that window with latest messages.
	'''
	def __init__(self, **kwargs):
		'''
		Scrollable display for displaying messages
		'''
		super(OutputLabel, self).__init__(**kwargs)

		self.size = (Window.width, Window.height)
		self.layout = GridLayout(cols = 1, size_hint_y = None)
		
		self.add_widget(self.layout)

		self.chat_history = Label(size_hint_y = None)
		self.scroll_to_point = Label(size_hint_y = None)

		self.layout.add_widget(self.chat_history)
		self.layout.add_widget(self.scroll_to_point)

	def update_history(self, message):
		'''
		Update Output label to display latest messages
		'''
		self.chat_history.text += "\n" + message
		
		self.layout.height = self.chat_history.texture_size[1] + 15
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width * 0.98, None)
		
		self.scroll_to(self.scroll_to_point)

class MainWindow(GridLayout):
	'''
	Contains Scrollable Display label and a button to start stt recognition
	via thread.
	'''
	def __init__(self,**kwargs):
		'''
		Main Window layout containing OutputLabel and a Button
		to start stt recognition
		'''
		super(MainWindow, self).__init__(**kwargs)
		threading.Thread(target = assistant.play_audio, args = ("hello",)).start()
		self.cols=1
		self.rows = 2
		self.history = OutputLabel()
		self.add_widget(self.history)

		self.btn_layout = FloatLayout()
		self.add_widget(self.btn_layout)

		self.btn = Button(text = "Speak", pos_hint= {"x": 0.45, "y": 0.1}, size_hint = (0.1,0.2))
		self.btn.bind(on_press = self.on_press)
		self.btn_layout.add_widget(self.btn)

	def rec_and_exec(self, *args):
		'''
		Convert speech-to-text then execute the recognized command
		via thread.
		'''
		stt = assistant.recognize_voice()
		if stt:
			text = "You said: "+ stt
			if stt not in rec_err:
				self.history.update_history(text)
				threading.Thread(target = assistant.execute_command, args = (stt,screen_manager)).start()
	
	def on_press(self, *args):
		'''
		Outputs 'Listening' and starts a thread to recognize voice
		'''
		self.history.update_history("Listening")

		if threading.active_count() < 2:
			threading.Thread(target = self.rec_and_exec).start()
		

class DeleteNotes(ScrollView):
	'''
	Class containing screen layout and functions related to deleting an
	existing note.
	'''
	def __init__(self, **kwargs):
		'''
		Displays saved notes as buttons
		'''
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
		'''
		Delete a Single stored note
		'''
		self.notes.remove(instance.text)
		with open("files/my_notes.txt", 'w') as file:
			for item in self.notes:
				file.write(item)
		screen_manager.current = "main"
		assistant.play_audio("done")

class AssistantApp(App):
	def build(self):
		'''
		Create 'main' screen and 'delete notes' screen.
		return the ScreenManager Instance
		'''

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