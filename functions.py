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
import pyttsx3
import multiprocessing
import threading
import sys

#Initialize wolframalpha, SpeechRecognition and pyttsx3 instances
try:
	engine = pyttsx3.init()
	#client = wolframalpha.Client('<APP ID HERE>')
	stt = speech_recognition.Recognizer()

	#set properties of pyttsx3 engine
	engine.setProperty("voice", "english+f2")
	engine.setProperty("rate", 145)

	#Automatic sensitivity adjust for speech recognition
	stt.dynamic_energy_threshold = True

except:
	print("Failed to Initialize instances\n"
		"(wolframalpha/SpeechRecognition/pyttsx3)")
	sys.exit()

#Speech Recognition Errors
rec_err = (
	"Sorry. I didn't quite catch that.",
	"Could not request results. Check the Internet connection",
	"No voice detected")

def remove_words_from_string(string,*args, sep = " "):
	'''
	Removes certain word from string and join the rest using the sep (seperator) provided.
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
	try:
		audio_name = "./responses/"+audio_name+".mp3"
		subprocess.run(["mpg123", "-q",audio_name])
	except:
		msg = "Check your installation of mpg123 player"
		print(msg + "\nCheck if mpg123 is in system PATH")
		speak(msg)
		sys.exit()

def add_voice(func):
	''' Plays on_it.mp3 before executing a function'''
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
	Converts speech to text if detection is successfull
	otherwise displays the suitable error.
	'''
	try:
		with speech_recognition.Microphone() as source:
			#wait for a second to let the recognizer adjust the  
	        #energy threshold based on the surrounding noise level
			# stt.pause_threshold = 1
			# stt.adjust_for_ambient_noise(source, duration	= 1)

			print("Listening")
			audio = stt.listen(source, timeout = 10)
		
		command = stt.recognize_google(audio).lower()
		print(command)
		return command

	#Could not make sense of audio
	except speech_recognition.UnknownValueError:
	    audio = choice(('sorry', 'wrong_ones_zeros'))
	    threading.Thread(target = play_audio, args=(audio,)).start()
	    return "Sorry. I didn't quite catch that."
	
	#Could not fetch results
	except speech_recognition.RequestError:
	    threading.Thread(target = play_audio, args=("conn_err")).start()
	    return "Could not request results. Check the Internet connection"
	
	#No voice was detected and recognition timed out
	except speech_recognition.WaitTimeoutError:
		threading.Thread(target = play_audio, args=("no_voice",)).start()
		return "No voice detected"


def tts_save(content, path):
	'''
	Generates and saves tts response
	'''
	tts = gTTS(content, lang = 'en')
	tts.save(path)	

def speak(content):
	'''
	Convert text to speech.
	Used to make audio responses other than that already present in
	responses directory.
	'''

	#Use Google Text-To-Speech to answer. If it takes more than 5 second to fetch the audio
	#Then response is played via pyttsx3 engine.
	#File created(if any) by gTTS is deleted
	try:
		
		file_name = "temp_response"
		path = "responses/"+file_name+".mp3"

		process = multiprocessing.Process(target = tts_save, args = (content,path))
		process.run()
		#wait 5 sec before continuing execution.
		process.join(5)

		#Terminate process if its running after 5 sec.
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
	Opens the results of google search of the query, in default browser
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
	#check if query was a success
	if response["@success"] == 'true':
		response = next(response.results).text #text returned as a result of query
		print(response)
		return speak(response)
	else:
		#if query wasn't a success then google search for the same query
		play_audio("no_result")
		return search_google(query_term)

@add_voice
def wikipedia_search(search_term, screen_manager):	
	'''
	Search for wikipedia page of given search_term and save the summary
	in files/display.txt.
	If the user wants the wikipedia page, open it in the default browser.
	'''

	search_term = remove_words_from_string(search_term, 'wiki', 'wikipedia')
	
	try:
		res = wikipedia.page(search_term)
	except Exception as err:
		play_audio('unable_to_fetch')
		print(err)

	else:
		play_audio("summary")
		with open("files/display.txt", 'w') as file:
			file.write(res.summary)

		screen_manager.current = "wiki"
	
		play_audio("wikipedia")

		choice = recognize_voice()
		if choice and choice not in rec_err:
			if re.search("(yes|yeah|yea|sure|glad)", choice):
				webbrowser.open(res.url)
			play_audio("alright")


@add_voice
def youtube_video(query):
	'''
	Search for videos on youtube as per the given query
	and open the URL of results.
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
	if note and note not in rec_err:
		note = '* ' + note + '\n'
		with open('./files/my_notes.txt', 'a') as saver:
			saver.write(note)
	play_audio('done')

def delete_saved_note(screen_manager):
	'''
	Change the screen to delete_notes if the size of my_notes.txt
	is greater than zero i.e. the file is not empty.
	'''		
	if os.path.getsize("files/my_notes.txt"):
		play_audio('delete_note')
		screen_manager.current = "delete_notes"
	else:
		play_audio("no_note")

def show_notes(screen_manager):
	'''
	Change the screen to show_notes if the size of my_notes.txt
	is greater than zero i.e. the file is not empty.
	'''
	if os.path.getsize("files/my_notes.txt"):
		play_audio("on_it")
		screen_manager.current = "show_notes"
	else:
		play_audio("no_note_to_display")

def execute_command(query, screen_manager):
	'''
	Execute the appropriate function based on the query.
	'''
	if re.search("play (music|song|songs)", query):
	# open lollypop musicplayer is query is a match
		open_app("lollypop")
	
	elif re.search("(wikipedia|wiki)", query):
	#find wikipedia page of query
		wikipedia_search(query, screen_manager)
	
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
		#dislpay the notes
		show_notes(screen_manager)

	elif re.search("(remove|delete) ([a-zA-Z]+)? ?note(s)?", query):
		#delete saved note
		delete_saved_note(screen_manager)
	
	elif query:
	#query wolfram if all the others were false
		# try:
		# 	wolfram_search(query)
		# except:
		search_google(query)

if __name__ == '__main__':
	main()