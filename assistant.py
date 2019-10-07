import speech_recognition
from gtts import gTTS
import webbrowser
from functools import wraps
import subprocess
from time import sleep
import os
from random import choice
import wolframalpha
import re

#Initialize wolframalpha and SpeechRecognition instances
client = wolframalpha.Client('<APP ID HERE>')
stt = speech_recognition.Recognizer()

#Automatic sensitivity adjust for speech recognition
stt.dynamic_energy_threshold = True

def play_audio(audio_name):
	''' 
	play audio files in the response directory with mpg123 player
	'''
	audio_name = "./responses/"+audio_name
	subprocess.run(["mpg123",audio_name])

def add_voice(func):
	''' Adds on_it.mp3 to a function'''
	@wraps(func)
	def inner(*args, **kwargs):
		play_audio("on_it.mp3")
		sleep(1)
		return_value = func(*args, **kwargs)

		return return_value
	return inner

def recognize_voice():
	'''
	Converts speech to text if detection is success otherwise displays the suitable error
	'''
	try:
		with speech_recognition.Microphone() as source:
			#wait for a second to let the recognizer adjust the  
	        #energy threshold based on the surrounding noise level
			stt.pause_threshold = 1
			stt.adjust_for_ambient_noise(source, duration	= 1)

			print("\n\nListening")
			audio = stt.listen(source, timeout = 10)
		
		command = stt.recognize_google(audio).lower()
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
	'''
	Convert text to speech.
	Used to make audio responses other than that already present in
	responses directory.
	'''
	file_name = "temp.mp3"
	tts = gTTS(content, lang = 'en')
	tts.save(name)
	play_audio(name)
	os.remove(file_name)

def search_google(query):
	'''
	Opens the google search result of a query in default browser
	'''
	play_audio("google.mp3")
	query = query.replace(' ', '+')
	URL = "https://www.google.com/search?q="
	webbrowser.open(URL+query, new = 2, autoraise = True)

@add_voice
def wolfram_search(query_term):
	'''
	Queries the WolframAlpha Simple API for the provided query_term
	'''
	response = client.query(query_term)
	if response["@success"] == 'true': #check if query was a success
		response = next(response.results).text #text returned as a result of query
		print(response)
		return speak(response)
	else:
		#if query wasn't a success then google search for the same query
		play_audio("no_result.mp3")
		sleep(0.5)
		return search_google(query_term)
@add_voice
def open_app(name):
	'''
	Used to open system application i.e. the apps in
	/usr/bin
	'''
	path = "/usr/bin/" + name
	subprocess.run([path])

if __name__ == '__main__':

	while True:
		query = recognize_voice()
		if query:
			if query in ['exit', 'bye', 'goodbye', 'go to sleep']: #exit program if query is a match
				break
			elif re.search("play (music|song|songs)", query):# open lollypop musicplayer is query is a match
				open_app("lollypop")
			elif re.search("(poweroff|shut ?down)", query): #Shutdown if query is a match
				subprocess.call('poweroff')
			elif query: #query wolfram if all the others were false
				wolfram_search(query)
	
	#Play audio on exit
	play_audio("see_you.mp3")
	