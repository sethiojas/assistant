import speech_recognition
from gtts import gTTS
import webbrowser
from functools import wraps
import subprocess
from time import sleep
import os
from random import choice
import wolframalpha

client = wolframalpha.Client('<APP ID>')
stt = speech_recognition.Recognizer()

stt.dynamic_energy_threshold = True

def add_voice(func):
	@wraps(func)
	def inner(*args, **kwargs):
		subprocess.run(['mpg123', './responses/on_it.mp3'])
		sleep(1)
		return_value = func(*args, **kwargs)

		return return_value
	return inner

def recognize_voice():
	try:
		with speech_recognition.Microphone() as source:
			print("\n\nListening")
			audio = stt.listen(source, timeout = 5)
		
		command = stt.recognize_google(audio)
		
		return command
	except speech_recognition.UnknownValueError:
	    print("Sorry. I didn't quite catch that.")
	    subprocess.run(['mpg123', choice('./responses/sorry.mp3', './responses/wrong_ones_zeros')])

	
	except speech_recognition.RequestError:
	    print("Could not request results. Check the Internet connection")
	    subprocess.run(['mpg123', './responses/conn_err.mp3'])
	
	except speech_recognition.WaitTimeoutError:
		print("No voice detected")
		subprocess.run(['mpg123', './responses/no_voice.mp3'])

def speak(content):
	name = "./responses/temp.mp3"
	tts = gTTS(content, lang = 'en')
	tts.save(name)
	subprocess.run(["mpg123",name])
	os.remove(name)


@add_voice
def search_web(query):
	query = query.split()
	query = "+".join(query)
	URL = "https://www.google.com/search?q="
	webbrowser.open(URL+query, new = 2, autoraise = True)

@add_voice
def wolfram_search(query_term):
	response = client.query(query_term)
	if response["@success"] == 'true':
		response = next(response.results).text
		print(response)
		return speak(response)
	else:
		subprocess.run(["mpg123","./responses/no_result.mp3"])



if __name__ == '__main__':
	