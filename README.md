# lichess-autoplay
A simple Python script that allows you to play chess automatically on lichess.org with assistance from a chess engine.
Fast enough for ultrabullet; strong enough to win every game (if you want!); undetected.

# Demonstration
(real-time, depth: 10)
![](https://github.com/wtfseanscool/lichess-autoplay/blob/main/example.gif)

The default mode is set to 'key' and default key is 'end'.
This means the bot will wait for the 'end' key before making a move.
You also may need to make the first 1 or 2 moves for the game to register.

# Prerequisites
* Python 3.x

# Getting Started
1. Clone this repository to your local machine: ```git clone https://github.com/wtfseanscool/lichess-autoplay.git```
2. Install the required packages: ```pip install -r requirements.txt``` (undetected-chromedriver, configparser, chess, keyboard)
4. Configure 'config.ini'
     * Path to engine file (download [stockfish](https://stockfishchess.org/download/) for example)
     * Lichess user/pass
     * Any UCI options wanted (add to lichess-autoplay.py as well)
5. Run the script: python lichess-autoplay.py

# Note
This script is for educational purposes only. Use it at your own risk.
If you use an engine at full strength, odds are you will get banned.
