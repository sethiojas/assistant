from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import threading
import functions
from random import choice

#Speech Recognition Errors
rec_err = (
	"Sorry. I didn't quite catch that.",
	"Could not request results. Check the Internet connection",
	"No voice detected")

# Dictionary containing color code(hex) and respective rgb percentage (out of 1)

color_dict = {

	"be7575" : (0.745, 0.459, 0.459),#Slightly desaturated red
	"d597ce" : (0.835, 0.592, 0.808),#slightly desaturated magenta
	"537ec5" : (0.325, 0.494, 0.773),#Moderate blue
	"293a80" : (0.161, 0.227, 0.502),#Dark moderate blue
	"c70d3a" : (0.780, 0.510, 0.227),#Strong red
	"512c62" : (0.318, 0.173, 0.384),#Very dark desaturated violet
	"bd574e" : (0.741, 0.341, 0.306),#Moderate Red
	"11999e" : (0.670, 0.600, 0.620),#Dark cyan
}

screen_manager = ScreenManager()

class OutputLabel(ScrollView):
	'''
	Class handles the scrollable output window and also the
	updation of that window with latest messages.
	'''
	chat_history = ObjectProperty()
	scroll_to_point = ObjectProperty()
	layout = ObjectProperty()

	def update_history(self, message):
		'''
		Update Output label to display latest messages
		'''
		self.chat_history.text += "\n" + message
		color = choice(list(color_dict.keys()))
		self.chat_history.bg_color = color_dict[color]
		self.scroll_to(self.scroll_to_point)

class MainWindow(GridLayout):
	'''
	Contains Scrollable Display label and a button to start stt recognition
	via thread.
	'''
	# threading.Thread(target = functions.play_audio, args = ("hello",)).start()
	history = ObjectProperty()

	def rec_and_exec(self, *args):
		'''
		Convert speech-to-text then execute the recognized command
		via thread.
		'''
		stt = functions.recognize_voice()
		if stt:
			text = "You said: "+ stt
			if stt not in rec_err:
				self.history.update_history(text)
				threading.Thread(target = functions.execute_command, args = (stt,screen_manager)).start()
	
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
	layout = ObjectProperty()
	def __init__(self, **kwargs):
		
		super().__init__(**kwargs)
		self.notes = None
		self.load_notes()

	def load_notes(self, *args):
		'''
		Saved notes are displayed as buttons
		'''
		with open("files/my_notes.txt", 'r') as file:
			self.notes = file.readlines()
		for item in self.notes:
			btn = Button(text = item, size_hint_y = None, height = "40dp")
			btn.bind(on_press = self.delete)
			btn.background_color = [1, 0.835, 0.835, 1] #Pale red
			self.layout.add_widget(btn)

	def delete(self, instance):
		'''
		Delete a Single stored note
		'''
		self.notes.remove(instance.text)
		self.layout.remove_widget(instance)
		with open("files/my_notes.txt", 'w') as file:
			for item in self.notes:
				file.write(item)
		screen_manager.current = "main"
		functions.play_audio("done")

class WikipediaDisplay(Screen):
	'''
	Display Summary fetched from wikipedia
	'''
	
	display = ObjectProperty()

	def on_enter(self):
		'''
		When on_enter event is flagged display the summary via txt file
		'''
		path = "files/display.txt"
		if os.path.exists(path):
			with open(path, 'r') as file:
				text_to_display = file.read()

			self.display.text = text_to_display
			os.remove(path)

class NotesDisplay(Screen):
	'''
	Displays the saved notes
	'''

	dislpay = ObjectProperty()

	def on_enter(self):
		'''
		When on_enter event is flaged, open my_notes.txt and
		display its contents.
		'''
		path = "files/my_notes.txt"
		with open(path, 'r') as file:
			text_to_display = file.read()

		self.display.text = text_to_display

class AssistantApp(App):
	
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.manager = screen_manager
	
	def build(self):
		'''
		Create 'main' screen', 'delete notes', 'wiki' and
		'show_notes' screen.
		Return the ScreenManager Instance.
		'''

		self.MainWindow = MainWindow()
		screen = Screen(name = "main")
		screen.add_widget(self.MainWindow)
		screen_manager.add_widget(screen)

		self.DeleteNotes = DeleteNotes()
		screen = Screen(name = "delete_notes")
		screen.add_widget(self.DeleteNotes)
		screen_manager.add_widget(screen)

		screen_manager.add_widget(WikipediaDisplay(name = "wiki"))

		screen_manager.add_widget(NotesDisplay(name = "show_notes"))
		
		return screen_manager

if __name__ == '__main__':
	AssistantApp().run()