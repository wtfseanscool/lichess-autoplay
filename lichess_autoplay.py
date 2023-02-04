import configparser
import chess
import keyboard
import os.path
import undetected_chromedriver as uc
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from chess import engine
from time import sleep
from math import ceil

'''
Required: Input moves with keyboard [lichess preferences]
'''

# Declare globals
webdriver_options = uc.ChromeOptions()
webdriver_options.add_argument(
    f'--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"')
driver = uc.Chrome(webdriver_options)
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
    # board.reset()

    while temp_move_number < 999:  # just in-case, lol
        if check_exists_by_xpath("/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(temp_move_number) + "]"):
            move = driver.find_element(By.XPATH,
                                       "/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(temp_move_number) + "]").text
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


def clear_arrow():
    driver.execute_script("""
                   g = document.getElementsByTagName("g")[0];
                   g.textContent = "";
                   """)


def draw_arrow(result, our_color):
    transform = get_piece_transform(result.move, our_color)

    move_str = str(result.move)
    src = str(move_str[:2])
    dst = str(move_str[2:])

    board_style = driver.find_element(By.XPATH,
                                      "/html/body/div[2]/main/div[1]/div[1]/div/cg-container").get_attribute(
        "style")
    board_size = re.search(r'\d+', board_style).group()

    driver.execute_script("""
                                            var x1 = arguments[0];
                                            var y1 = arguments[1];
                                            var x2 = arguments[2];
                                            var y2 = arguments[3];
                                            var size = arguments[4];
                                            var src = arguments[5];
                                            var dst = arguments[6];

                                            defs = document.getElementsByTagName("defs")[0];

                                            child_defs = document.getElementsByTagName("marker")[0];

                                            if (child_defs == null)
                                            {
                                                child_defs = document.createElementNS("http://www.w3.org/2000/svg", "marker");
                                                child_defs.setAttribute("id", "arrowhead-g");
                                                child_defs.setAttribute("orient", "auto");
                                                child_defs.setAttribute("markerWidth", "4");
                                                child_defs.setAttribute("markerHeight", "8");
                                                child_defs.setAttribute("refX", "2.05");
                                                child_defs.setAttribute("refY", "2.01");
                                                child_defs.setAttribute("cgKey", "g");

                                                path = document.createElement('path')
                                                path.setAttribute("d", "M0,0 V4 L3,2 Z");
                                                path.setAttribute("fill", "#15781B");  
                                                child_defs.appendChild(path);

                                                defs.appendChild(child_defs);
                                            }

                                            g = document.getElementsByTagName("g")[0];

                                            var child_g = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                                            child_g.setAttribute("stroke","#15781B");
                                            child_g.setAttribute("stroke-width","0.15625");
                                            child_g.setAttribute("stroke-linecap","round");
                                            child_g.setAttribute("marker-end","url(#arrowhead-g)");
                                            child_g.setAttribute("opacity","1");
                                            child_g.setAttribute("x1", x1);
                                            child_g.setAttribute("y1", y1);
                                            child_g.setAttribute("x2", x2);
                                            child_g.setAttribute("y2", y2);
                                            child_g.setAttribute("cgHash", `${size}, ${size},` + src + `,` + dst + `,green`);

                                            g.appendChild(child_g);

                                            """, transform[0], transform[1], transform[2], transform[3], board_size,
                          src,
                          dst)


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

        previous_move_number = move_number

        need_draw_arrow = True

        # only get best move once
        if our_turn:
            result = _engine.play(board, chess.engine.Limit(depth=int(config["engine"]["Depth"])), game=object,
                                  info=chess.engine.INFO_NONE)

        while our_turn:
            if previous_move_number != move_number:
                break

            # check for made move
            move = check_exists_by_xpath("/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(move_number) + "]")
            if move:
                clear_arrow()

                move = driver.find_element(By.XPATH,
                                               "/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(
                                                   move_number) + "]").text
                uci = board.push_san(move)

                print(str(ceil(move_number / 2)) + '. ' + str(uci.uci()) + ' [us]')

                move_number += 1

            else:
                if config["general"]["arrow"] == "true" and need_draw_arrow:
                    draw_arrow(result, our_color)
                    need_draw_arrow = False

                if config["general"]["movetype"] == "auto" or config["general"]["MoveType"] == "key" and keyboard.is_pressed(config["general"]["MoveKey"]):
                    clear_arrow()

                    print(str(ceil(move_number / 2)) + '. ' + str(result.move) + ' [us]')

                    board.push(result.move)

                    move_handle.send_keys(Keys.RETURN)
                    move_handle.clear()
                    move_handle.send_keys(str(result.move))

                    move_number += 1
        # sleep(0.1) # if you want
        else:
            clear_arrow()
            opp_moved = check_exists_by_xpath("/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(move_number) + "]")
            if opp_moved:
                opp_move = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[1]/rm6/l4x/kwdb[" + str(
                    move_number) + "]").text
                uci = board.push_san(opp_move)

                print(str(ceil(move_number / 2)) + '. ' + uci.uci())

                move_number += 1

    # sleep(0.1) # if you want

    # Game complete
    _engine.quit()
    print("[INFO] :: Game complete. Waiting for new game to start.")
    new_game(board)


def get_board_square_size():
    board_style = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[1]/div[1]/div/cg-container").get_attribute(
        "style")
    board_size = re.search(r'\d+', board_style).group()
    piece_size = int(board_size) * .125  # / 8
    return piece_size


def get_piece_transform(move, our_color):
    files = ['1', '2', '3', '4', '5', '6', '7', '8']
    ranks = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


    rank_values_w = [("a", -3.5), ("b", -2.5), ("c", -1.5), ("d", -0.5), ("e", 0.5), ("f", 1.5), ("g", 2.5), ("h", 3.5)]
    file_values_w = [(1, 3.5), (2, 2.5), (3, 1.5), (4, 0.5), (5, -0.5), (6, -1.5), (7, -2.5), (8, -3.5)]

    rank_values_b = [("a", 3.5), ("b", 2.5), ("c", 1.5), ("d", 0.5), ("e", -0.5), ("f", -1.5), ("g", -2.5), ("h", -3.5)]
    file_values_b = [(1, -3.5), (2, -2.5), (3, -1.5), (4, -0.5), (5, 0.5), (6, 1.5), (7, 2.5), (8, 3.5)]

    move_str = str(move)
    _from = str(move_str[:2])
    _to = str(move_str[2:])

    a1 = 0
    a2 = 0

    for i, pair in enumerate(rank_values_w if our_color == "W" else rank_values_b):
        if pair[0] == _from[0]:
            a1 = i
            break

    for i, pair in enumerate(file_values_w if our_color == "W" else file_values_b):
        if pair[0] == int(_from[1]):
            a2 = i
            break

    src_x = rank_values_w[a1][1] if our_color == "W" else rank_values_b[a1][1]
    src_y = file_values_w[a2][1] if our_color == "W" else file_values_b[a2][1]


    b1 = 0
    b2 = 0

    for i, pair in enumerate(rank_values_w if our_color == "W" else rank_values_b):
        if pair[0] == _to[0]:
            b1 = i
            break

    for i, pair in enumerate(file_values_w if our_color == "W" else file_values_b):
        if pair[0] == int(_to[1]):
            b2 = i
            break

    dst_x = rank_values_w[b1][1] if our_color == "W" else rank_values_b[b1][1]
    dst_y = file_values_w[b2][1] if our_color == "W" else file_values_b[b2][1]

    return [src_x, src_y, dst_x, dst_y]


def sign_in():
    # Signing in
    signin_button = driver.find_element(by=By.XPATH, value="/html/body/header/div[2]/a")
    signin_button.click()
    username = driver.find_element(By.ID, "form3-username")
    password = driver.find_element(By.ID, "form3-password")
    username.send_keys(config["lichess"]["Username"])
    password.send_keys(config["lichess"]["Password"])
    driver.find_element(By.XPATH, "/html/body/div/main/form/div[1]/button").click()  # submit


def create_config():
    config["engine"] = {
        "Path": "C:\Path\To\Engine\Binary",
        "Depth": "5",
        "Hash": "2048",
        "Skill Level": "14"
    }
    config["lichess"] = {
        "Username": "user",
        "Password": "pass"
    }
    config["general"] = {
        "MoveType": "key",
        "MoveKey": "end"
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def main():
    config_exists = os.path.isfile("./config.ini")

    if config_exists:
        config.read("config.ini")
    else:
        create_config()
        config.read("config.ini")

    board = chess.Board()
    driver.get("https://www.lichess.org")
    sign_in()
    new_game(board)


if __name__ == "__main__":
    main()
