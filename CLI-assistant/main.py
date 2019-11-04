import assistant

if __name__ == '__main__':

	#Greet user
	assistant.play_audio('hello')
	while True:
		query = assistant.recognize_voice()
		
		if query:
			if query in ['exit', 'bye', 'goodbye', 'go to sleep', 'see you']: 
			#exit program if query is a match
				break
			else:
				assistant.execute_command(query)
	
	#Play audio on exit
	assistant.play_audio("see_you")