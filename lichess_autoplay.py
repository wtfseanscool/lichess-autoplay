import configparser
import chess
import keyboard

from chess import engine
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from time import sleep
from math import ceil

'''
Required: Input moves with keyboard [lichess preferences]
'''

# Declare globals
driver = webdriver.Firefox()
config = configparser.ConfigParser()


def check_exists_by_xpath(xpath):
	try:
		driver.find_element(By.XPATH, xpath)
	except NoSuchElementException:
		return False
	return driver.find_element(By.XPATH, xpath)


def check_exists_by_class(classname):
	try:
		driver.find_element(By.CLASS_NAME, classname)
	except NoSuchElementException:
		return False
	return driver.find_element(By.CLASS_NAME, classname)


def find_color(board):
	while check_exists_by_class("follow-up"):
		sleep(1)

	# wait for move input box
	WebDriverWait(driver, 600).until(
		ec.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[1]/div[10]/input")))

	# wait for board
	WebDriverWait(driver, 600).until(
		ec.presence_of_element_located((By.CLASS_NAME, "cg-wrap")))

	board_set_for_white = check_exists_by_class("orientation-white")

	if board_set_for_white:
		our_color = 'W'
		play_game(board, our_color)
	else:
		our_color = 'B'
		play_game(board, our_color)


def new_game(board):
	board.reset()
	find_color(board)


def get_previous_moves(board):
	temp_move_number = 1

	# reset every move
	#board.reset()

	while temp_move_number < 999:  # just in-case, lol
		if check_exists_by_xpath("/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(temp_move_number) + "]"):
			move = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(temp_move_number) + "]").text
			board.push_san(move)
			temp_move_number += 1
		else:
			return temp_move_number


def get_seconds(time_str):
	semicolons = time_str.count(":")

	if semicolons == 2:
		# hh, mm, ss
		hh, mm, ss = time_str.split(':')
		return int(hh) * 3600 + int(mm) * 60 + int(ss)
	elif semicolons == 1:
		fixed = time_str.partition(".")
		# mm, ss
		mm, ss = fixed.split(':')
		return int(mm) * 60 + int(ss)

	return 0


# theres 2 approaches
# 1. recreate board and moves every time a new move is made
# 2. just update board with each move as it happens
# recreating every time can maybe account for takebacks/etc or some other bugs, but not sure if its necessary

def play_game(board, our_color):
	WebDriverWait(driver, 600).until(ec.presence_of_element_located((By.CLASS_NAME, "ready")))
	move_handle = driver.find_element(By.CLASS_NAME, "ready")

	_engine = chess.engine.SimpleEngine.popen_uci(config["engine"]["Path"])

	# add any additional UCI options
	_engine.configure({
		"Skill Level": int(config["engine"]["Skill Level"]),
		"Hash": int(config["engine"]["Hash"])})

	print("[INFO] :: Setting up initial position.")
	move_number = get_previous_moves(board)
	print("[INFO] :: Ready.")

	# while game is in progress (no rematch/analysis button, etc)
	while not check_exists_by_class("follow-up"):
		our_turn = False

		if board.turn and our_color == "W":
			our_turn = True
		elif not board.turn and our_color == "B":
			our_turn = True

		if our_turn:
			if config["general"]["MoveType"] == "key" and keyboard.is_pressed(config["general"]["MoveKey"]) or config["general"]["MoveType"] == "auto":
				# our_time = 1

				#if config["general"]["MoveType"] == "auto":
					#if check_exists_by_xpath("/html/body/div[2]/main/div[1]/div[8]/div[2]"): # clock
						#lichess_time = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[1]/div[8]/div[2]").text
						#our_time = get_seconds(lichess_time)

				result = _engine.play(board, chess.engine.Limit(depth=int(config["engine"]["Depth"])), game=object, info=chess.engine.INFO_NONE)

				print(str(ceil(move_number / 2)) + '. ' + str(result.move) + ' [us]')

				board.push(result.move)

				move_handle.send_keys(Keys.RETURN)
				move_handle.clear()
				move_handle.send_keys(str(result.move))

				move_number += 1

		else:
			opp_moved = check_exists_by_xpath("/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(move_number) + "]")
			if opp_moved:
				opp_move = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(move_number) + "]").text
				uci = board.push_san(opp_move)

				print(str(ceil(move_number / 2)) + '. ' + uci.uci())

				move_number += 1

		# sleep(0.1) # if you want

	# Game complete
	_engine.quit()
	print("[INFO] :: Game complete. Waiting for new game to start.")
	new_game(board)


def read_config():
	config.read('config.ini')


def sign_in():
	# Signing in
	signin_button = driver.find_element(by=By.XPATH, value="/html/body/header/div[2]/a")
	signin_button.click()
	username = driver.find_element(By.ID, "form3-username")
	password = driver.find_element(By.ID, "form3-password")
	username.send_keys(config["lichess"]["Username"])
	password.send_keys(config["lichess"]["Password"])
	driver.find_element(By.XPATH, "/html/body/div/main/form/div[1]/button").click()  # submit


def main():
	read_config()
	board = chess.Board()

	driver.get("https://www.lichess.org")
	sign_in()
	new_game(board)


if __name__ == "__main__":
	main()





