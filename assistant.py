import speech_recognition
from gtts import gTTS
import webbrowser
from functools import wraps
import subprocess
from time import sleep
import os
from random import choice
import wolframalpha

client = wolframalpha.Client('<APP ID HERE>')
stt = speech_recognition.Recognizer()

stt.dynamic_energy_threshold = True

def play_audio(audio_name):
	audio_name = "./responses/"+audio_name
	subprocess.run(["mpg123",audio_name])

def add_voice(func):
	@wraps(func)
	def inner(*args, **kwargs):
		play_audio("on_it.mp3")
		sleep(1)
		return_value = func(*args, **kwargs)

		return return_value
	return inner

def recognize_voice():
	try:
		with speech_recognition.Microphone() as source:
			print("\n\nListening")
			audio = stt.listen(source, timeout = 2)
		
		command = stt.recognize_google(audio)
		print(command)
		return command
	except speech_recognition.UnknownValueError:
	    print("Sorry. I didn't quite catch that.")
	    audio = choice(('sorry.mp3', 'wrong_ones_zeros.mp3'))
	    play_audio(audio)

	
	except speech_recognition.RequestError:
	    print("Could not request results. Check the Internet connection")
	    play_audio("conn_err.mp3")
	
	except speech_recognition.WaitTimeoutError:
		print("No voice detected")
		play_audio("no_voice.mp3")

def speak(content):
	file_name = "temp.mp3"
	tts = gTTS(content, lang = 'en')
	tts.save(name)
	play_audio(name)
	os.remove(file_name)

def search_web(query):
	play_audio("google.mp3")
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
		play_audio("no_result.mp3")
		sleep(0.5)
		return search_web(query_term)

if __name__ == '__main__':

	while True:
		query = recognize_voice()
		if query in ['exit', 'bye', 'goodbye', 'go to sleep']:
			break
		elif query:
			wolfram_search(query)
	play_audio("see_you.mp3")
	