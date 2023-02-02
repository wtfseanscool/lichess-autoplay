# lichess-autoplay
Autoplay bot/cheat for lichess.org, created in Python

The default mode is set to 'key' and default key is 'end'.
This means the bot will wait for the 'end' key before making a move.
You also may need to make the first 1 or 2 moves for the game to register.

# Requirements:
* Created in Python 3.10
* pip install -r requirements.txt (undetected-chromedriver, configparser, chess, keyboard)            
* Configure 'config.ini'
  * Path to engine file (download stockfish for example)
  * Lichess user/pass
  * Any UCI options wanted
* Input moves with keyboard [in lichess user preferences]
