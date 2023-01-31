# lichess-autoplay
Autoplay bot/cheat for lichess.org, created in Python

The default mode is set to 'key' and default key is 'end'.
This means the bot will wait for the 'end' key before starting calculations / making a move.

# Requirements:
* Created in Python 3.10
* pip install -r requirements.txt (selenium, configparser, chess, keyboard)            
* Configure 'config.ini'
  * Path to engine file (download stockfish for example)
  * Lichess user/pass
  * Any UCI options wanted
* Input moves with keyboard [in lichess user preferences]
