# Assistant

A personal assistant which can take care of mostly all the basic task
such as taking notes, search google, wikipedia or youtube, open the music player (lollypop)
and shutting down the computer.

*** espeak is required for offline tts.***

## Table of Contents
* [Commands and Functionality](#commands-and-functionality)
* [Screenshots](#screenshots)
* [Requirments](#requirments)

## Commands and Functionality

Assistant uses regular expressions to match a command with a query.
If it is unable to find a suitable match, google search is performed
regarding the query in the default browser.

### Assistant is able to do the following tasks
#### Open music player 
***(Lollypop music player must be installed)***
Try saying `play music` or `play songs`.

#### Search wikipedia
Try saying `wikipedia eminem` or `new york wikipedia`.

A summary will be provided upon which the assistant will ask if the
respective wikipedia page should be opened in browser.
If replied with `yes`, `yeah`, `sure`, `gladly` link will be opened.

#### Search a video on YouTube
Try saying `youtube <terms to include in search>`.
Search results will be opened in default browser.

#### Poweroff Machine
Saying `poweroff` or `shut down` will shut down the machine.

#### Notes

* To save a note try saying `take note(s)` or `take a note`.

* To see saved notes try saying `show/display note(s)` or `show/display my note(s)`

* To delete a saved notes try saying `delete note(s)` or `delete my notes(s)`

## ScreenShots

![Main Window](https://github.com/sethiojas/readme_images/blob/master/Assistant/main_window.png)

![Wikipedia Summary Screen](https://github.com/sethiojas/readme_images/blob/master/Assistant/wiki.png)

![Show Notes Screen](https://github.com/sethiojas/readme_images/blob/master/Assistant/show_notes.png)

![Delete Notes Screen](https://github.com/sethiojas/readme_images/blob/master/Assistant/delete_note.png)

![Main Window](https://github.com/sethiojas/readme_images/blob/master/Assistant/main_window_2.png)

![Youtube Search](https://github.com/sethiojas/readme_images/blob/master/Assistant/youtube.png)

## Requirments
* espeak should be installed.
* Lollypop music player must be installed for assistant to open music player
* mpg123 player must be installed to get audio response by assistant.