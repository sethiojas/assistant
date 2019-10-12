import speech_recognition
from gtts import gTTS
import webbrowser
from functools import wraps
import subprocess
from time import sleep
import os
from random import choice
import wolframalpha
import wikipedia
import re
import sys
from PyInquirer import prompt
import pyttsx3
import multiprocessing

########################Closed stderr file descriptor (line 21) to supress ALSA error messages
########################This aside from intended task supresses any and every error message
########################EXERCISE CAUTION

os.close(sys.stderr.fileno())

#Initialize wolframalpha, SpeechRecognition and pyttsx3 instances

engine = pyttsx3.init()
client = wolframalpha.Client('<APP ID HERE>')
stt = speech_recognition.Recognizer()

#set properties of pyttsx3 engine
engine.setProperty("voice", "english+f2")
engine.setProperty("rate", 145)

#Automatic sensitivity adjust for speech recognition
stt.dynamic_energy_threshold = True

def remove_words_from_string(string,*args, sep = " "):
	'''
	Removes certain word from string and joins them using the sep (seperator) provided.
	'''
	string = string.split()
	for word in args:
		if word in string:
			string.remove(word)

	string = sep.join(string)
	return string

def play_audio(audio_name):
	''' 
	play audio files in the response directory with mpg123 player
	'''
	audio_name = "./responses/"+audio_name+".mp3"
	subprocess.run(["mpg123", "-q",audio_name])

def add_voice(func):
	''' Adds on_it.mp3 to a function'''
	@wraps(func)
	def inner(*args, **kwargs):
		play_audio("on_it")
		sleep(1)
		return_value = func(*args, **kwargs)
		if return_value:
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

			print("Listening")
			audio = stt.listen(source, timeout = 10)
		
		command = stt.recognize_google(audio).lower()
		print(command)
		return command
	except speech_recognition.UnknownValueError:
	    print("Sorry. I didn't quite catch that.")
	    audio = choice(('sorry', 'wrong_ones_zeros'))
	    play_audio(audio)

	
	except speech_recognition.RequestError:
	    print("Could not request results. Check the Internet connection")
	    play_audio("conn_err")
	
	except speech_recognition.WaitTimeoutError:
		print("No voice detected")
		play_audio("no_voice")

def speak(content):
	'''
	Convert text to speech.
	Used to make audio responses other than that already present in
	responses directory.
	'''

	#Use Google Text-To-Speech to answer. If it take more than 5 second for the audio to download
	#Then response is played via pyttsx3 engine.
	#File created(if any) by gTTS is deleted in the exception block
	try:
		file_name = "temp"
		path = "responses/"+file_name+".mp3"

		tts = gTTS(content, lang = 'en')
		process = multiprocessing.Process(target = lambda: tts.save(path))
		process.start()
		process.join(5)

		if process.is_alive():
			process.terminate()
			process.join()
			raise Exception

		play_audio(file_name)
		os.remove(path)

	except:
		if os.path.exists(path):
			os.remove(path)
		engine.say(content)
		engine.runAndWait()

def search_google(query):
	'''
	Opens the google search result of a query in default browser
	'''
	play_audio("google")
	query = remove_words_from_string(query, 'google', sep = "+")
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
		play_audio("no_result")
		sleep(0.5)
		return search_google(query_term)

@add_voice
def wikipedia_search(search_term):	
	'''
	Search for wikipedia page of given search_term and display the summary.
	If the user wants the wikipedia page is also opened in the default browser.
	'''
	search_term = remove_words_from_string(search_term, 'wiki', 'wikipedia')
	
	try:
		res = wikipedia.page(search_term)
		play_audio("summary")
		print(res.summary)
		play_audio("wikipedia")
		choice = recognize_voice()
		if choice:
			if re.search("(yes|yeah|yea|sure|glad)", choice):
				webbrowser.open(res.url)

	except:
		play_audio('unable_to_fetch')

@add_voice
def youtube_video(query):
	'''
	Search for videos on youtube as per the given query
	'''
	query = remove_words_from_string(query, 'youtube', 'play',
	'search', 'on', sep= '+')
	URL = 'https://www.youtube.com/results?search_query='
	webbrowser.open(URL+query)

@add_voice
def open_app(name):
	'''
	Used to open system application i.e. the apps in
	/usr/bin
	'''
	path = "/usr/bin/" + name
	subprocess.run([path])

def save_notes():
	'''
	Save user's notes in a text file
	'''
	play_audio("note")
	note = recognize_voice()
	if note:
		note = '* ' + note + '\n'
		with open('./files/my_notes.txt', 'a') as saver:
			saver.write(note)
	play_audio('done')

def delete_saved_note():
	'''
	Deletes a saved note from the text file my_notes.txt
	'''
	play_audio('delete_note')

	with open("files/my_notes.txt", 'r') as file:
		current_notes = file.readlines()

	question = [
		{
			"type":"list",
			"name":"msg",
			"message":"Which note to delete?",
			"choices":current_notes
		}
	]
	answer = prompt(question)

	current_notes.remove(answer["msg"])
	with open('files/my_notes.txt', 'w') as file:
		for note in current_notes:
			file.write(note)

	play_audio('done')

def execute_command(query):
	'''
	Execute the appropriate function based on the query.
	'''
	if re.search("play (music|song|songs)", query):
	# open lollypop musicplayer is query is a match
		open_app("lollypop")
	
	elif re.search("(wikipedia|wiki)", query):
	#find wikipedia page of query
		wikipedia_search(query)
	
	elif re.search("youtube", query):
	#search for query on youtube
		youtube_video(query)
	
	elif re.search("(poweroff|shut ?down)", query):
	#Shutdown if query is a match
		subprocess.call('poweroff')
	
	elif re.search("google", query):
	#Search on google
		search_google(query)

	elif re.search("(take|save) ?([a-zA-Z]+)? note(s)?", query):
		#save a note
		save_notes()

	elif re.search("(show|display) ([a-zA-Z]+)? ?note(s)?", query):
		#dislpay text file containing all the notes
		subprocess.run(['gedit','./files/my_notes.txt'])
	
	elif re.search("(remove|delete) ([a-zA-Z]+)? ?note(s)?", query):
		#delete saved note
		delete_saved_note()
	
	elif query:
	#query wolfram if all the others were false
		try:
			wolfram_search(query)
		except:
			search_google(query)

if __name__ == '__main__':

	#Greet user
	play_audio('hello')
	while True:
		query = recognize_voice()
		
		if query:
			if query in ['exit', 'bye', 'goodbye', 'go to sleep', 'see you']: 
			#exit program if query is a match
				break
			else:
				execute_command(query)
	
	#Play audio on exit
	play_audio("see_you")
	