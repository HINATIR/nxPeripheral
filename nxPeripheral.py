import pygame
import math
import os
from pynput import keyboard, mouse
import time
import json
import btkeyLib
from btkeyLib import Button
import os
import glob
import ctypes

title = """
            _____          _       _                    _ 
           |  __ \        (_)     | |                  | |
 _ __ __  _| |__) |__ _ __ _ _ __ | |__   ___ _ __ __ _| |
| '_ \\ \/ /  ___/ _ \ '__| | '_ \| '_ \ / _ \ '__/ _` | |
| | | |>  <| |  |  __/ |  | | |_) | | | |  __/ | | (_| | |
|_| |_/_/\_\_|   \___|_|  |_| .__/|_| |_|\___|_|  \__,_|_|
                            | |                           
                            |_|                             
"""

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED_A = (255, 0, 0)
BLUE_B = (0, 0, 255)
YELLOW_Y = (255, 255, 0)
GREEN_X = (0, 255, 0)
BLACK_BUTTON = (30, 30, 30)
LIGHT_RED = (255, 182, 193) # 薄い赤色 (ピンク)

BUTTON_NAMES = [
    "A", "B", "X", "Y", "L", "R", "ZL", "ZR", "PLUS", "MINUS", 
    "LCLICK", "RCLICK", "UP", "DOWN", "RIGHT", "LEFT", "HOME", "CAPTURE"
]


# ジョイスティックの半径とスティックの半径
joystick_radius = 50
stick_radius = 20

# スティックUIの位置
wasd_joystick_center = (750,435)
mouse_joystick_center = (1060,540)

# (posx, posy, radius,should render text)
Buttons_Mapping = {
  "A": ((1220,435),30,False),
  "B": ((1160,485),30,False),
  "X": ((1160,385),30,False),
  "Y": ((1100,435),30,False),
  "L": ((660,335),30,True),
  "R": ((1255,335),30,True),
  "ZL": ((840,290),30,True),
  "ZR": ((1075,290),30,True),
  "PLUS": ((1055,375),15,False),
  "MINUS": ((865,375),15,False),
  "LCLICK": ((750,435),15,False),
  "RCLICK": ((1060,540),15,False),
  "UP": ((840,505),15,False),
  "DOWN": ((840,575),15,False),
  "RIGHT": ((805,540),15,False),
  "LEFT": ((880,540),15,False),
  "HOME": ((1015,435),15,False),
  "CAPTURE": ((905,435),15,False)
}

# 右ジョイスティック
axis = (0,0)
old_axis = (0,0)

# グローバル変数の初期化
pressed_keys = set()
old_pressed_keys = set()
prisets = set()


#マウスの値
rightClick = 0
leftClick = 0
mouse_scroll = 0


if not os.path.exists("keyconfig"):
    os.makedirs(f"keyconfig")

if not os.path.exists("presets"):
    os.makedirs(f"presets")

# キーが押されたときの処理

# (もともとの座標,移動先の座標,スケール)
def scaler(pos,to,scale):
    FHDcenter = (1920/2, 1080/2)
    temp = (FHDcenter[0] - pos[0],FHDcenter[1] - pos[1] )
    return (to[0] - int(scale * temp[0]), to[1] - int(scale * temp[1]))

def on_press(key):
    global pressed_keys
    try:
        pressed_keys.add(key.char.lower())
    except AttributeError:
        pressed_keys.add(str(key))

def on_release(key):
    global pressed_keys
    try:
        pressed_keys.remove(key.char.lower())
    except AttributeError:
        pressed_keys.remove(str(key))
    except KeyError:
        pass

# キーが離されたときの処理
def on_release(key):
    try:
        if key.char.lower() in pressed_keys:
            pressed_keys.remove(key.char.lower())
    except AttributeError:
        if key == keyboard.Key.space:
            if 'space' in pressed_keys:
                pressed_keys.remove('space')
        if str(key) in pressed_keys:
            pressed_keys.remove(str(key))


# マウス移動の正規化
def mouse_normalisation(d):
    if d > 1:
        return 1.0
    elif d < -1:
        return -1.0
    else:
        return d

# マウスクリック
def on_click(x, y, button, pressed):
    mouse_button_str = f"Mouse.{button}"

    if (button == mouse.Button.left)or(button == mouse.Button.right): 
        if pressed:
            pressed_keys.add(mouse_button_str)
        else:
            try:
                pressed_keys.remove(mouse_button_str)
            except KeyError:
                pass
            
# マウススクロール
def on_scroll(x, y, dx, dy):
    global mouse_scroll
    mouse_scroll = dy

# ---
# リスナー設定と開始
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)

keyboard_listener.start()
mouse_listener.start()


def openKeyConfig(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
    "A": "Key.space",
    "B": "q",
    "X": "e",
    "Y": "c",
    "L": "Mouse.Scroll.down",
    "R": "Mouse.Scroll.up",
    "ZL": "Mouse.Button.right",
    "ZR": "Mouse.Button.left",
    "PLUS": "Key.esc",
    "MINUS": "Key.tab",
    "LCLICK": "r",
    "RCLICK": "Key.shift",
    "UP": "Key.up",
    "DOWN": "Key.down",
    "RIGHT": "Key.right",
    "LEFT": "Key.left",
    "HOME": "Key.enter",
    "CAPTURE": "p"
    }

def printKeyConfig(path):
    temp = openKeyConfig(path)
    print()
    print("[Loaded Key Setting]\n")
    for button_name in BUTTON_NAMES:
        print(f"{button_name} == {temp.get(button_name)}")

def openPreset(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "jsons\\Default.json": "0"
        }

def printPreset(path):
    temp = openPreset(path)
    for filepath, key in temp.items():
        print(f"キー設定: {filepath}, 切り替えキー: {key}")

print(title)
print("")

preset_json_files = glob.glob(os.path.join("presets", '*.json'))
for n, fn in enumerate(preset_json_files):
    print(f"{n}: {fn}")

print()
load_file = preset_json_files[int(input("利用するプリセットの番号を入力して接続> "))]

presets = openPreset(load_file)

printPreset(load_file)


key_mappings = openKeyConfig(next(iter(presets)))

printKeyConfig(next(iter(presets)))

print()
dev_command = input("なにかキーを押すとSwitchにBluetooth接続を開始します")


isDemo_connection = False
if(dev_command == "demo"):
    isDemo_connection = True

# 実際には接続しないデモモード、キー入力の確認など
if(not isDemo_connection):
    # コントローラとして接続
    btkeyLib.start(0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF)
    while not btkeyLib.is_paired():
        time.sleep(1)
    print("接続が成功しました！\n")
else:
    print("実際にSwitchには接続しないデモモードです。\n")

# Pygameの初期化
pygame.init()

# Windowの大きさ
scale = 0.7

image = pygame.image.load("procon.jpg")
size = (int(image.get_width()* scale), int(image.get_height() * scale))
image = pygame.transform.scale(image, size)
    
# 取得したサイズでウィンドウを作成
screen = pygame.display.set_mode(size)


# 画面の幅と高さを取得
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# ウィンドウのタイトルを設定
pygame.display.set_caption("nxPeripheral")

# マウスカーソルを非表示にし、ウィンドウ内に固定
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# 変数を修正
size = (size[0]/2,size[0]/2 )
scale = scale * 1.2
wasd_joystick_center = pos = scaler( wasd_joystick_center,size,scale)
mouse_joystick_center = pos = scaler( mouse_joystick_center,size,scale)
stick_radius = int(stick_radius * scale)
joystick_radius = int(joystick_radius * scale)
# 右ジョイスティック（マウス）の中心
mouse_dot_x = float(mouse_joystick_center[0])
mouse_dot_y = float(mouse_joystick_center[1])

def limit_dot_position(center_pos, dot_pos_x, dot_pos_y, radius):
    """点が円の内部に留まるように座標を制限するヘルパー関数"""
    distance = math.sqrt((dot_pos_x - center_pos[0])**2 + (dot_pos_y - center_pos[1])**2)
    if distance > radius:
        dir_x = (dot_pos_x - center_pos[0]) / distance
        dir_y = (dot_pos_y - center_pos[1]) / distance
        dot_pos_x = center_pos[0] + dir_x * radius
        dot_pos_y = center_pos[1] + dir_y * radius
    return dot_pos_x, dot_pos_y

def draw_button(button_name,is_pressed):
    global Buttons_Mapping
    prope = Buttons_Mapping.get(button_name)

    global size
    global scale
    pos = scaler( prope[0],size,scale)

    radius = prope[1] * scale
    color = LIGHT_RED if is_pressed else GRAY # デフォルトのボタンの色を薄い赤に
    if is_pressed:
        pygame.draw.circle(screen, LIGHT_RED, pos, radius)
        pygame.draw.circle(screen, WHITE, pos, radius, 2)
    else:
        pygame.draw.circle(screen, color, pos, radius)
        pygame.draw.circle(screen, WHITE, pos, radius, 2)

    font = pygame.font.Font(None, int(radius * 2))    
    text = font.render(button_name, True, (0, 0, 0))
    font_rect = text.get_rect()
    font_rect.center = pos
    if prope[2]:
        screen.blit(text, font_rect)

def calculate_constrained_point(center_x, center_y, delta_x, delta_y, radius):
    # 新しい点の仮の座標を計算
    new_x = center_x + delta_x
    new_y = center_y + delta_y

    # 新しい点と中心の距離を計算
    distance_from_center = math.sqrt((new_x - center_x)**2 + (new_y - center_y)**2)

    # 距離が半径を超えた場合、点を円周上に制限する
    if distance_from_center > radius:
        # 中心から新しい点へのベクトル
        direction_x = new_x - center_x
        direction_y = new_y - center_y
        
        # ベクトルを正規化（単位ベクトルにする）
        if distance_from_center != 0:
            direction_x /= distance_from_center
            direction_y /= distance_from_center
        
        # 正規化されたベクトルに半径をかけて、円周上の座標を計算
        new_x = center_x + direction_x * radius
        new_y = center_y + direction_y * radius

    return (new_x, new_y)

def drawJoystick(isLjoy,x_axis, y_axis):
    pos = mouse_joystick_center
    if isLjoy:
        pos = wasd_joystick_center

    pygame.draw.circle(screen, WHITE, pos, joystick_radius, 2)
    dot = calculate_constrained_point(pos[0],pos[1],joystick_radius* x_axis,joystick_radius*y_axis* -1,joystick_radius)
    pygame.draw.circle(screen, RED_A, dot, stick_radius)
    

def limit_dot_position(center_pos, dot_pos_x, dot_pos_y, radius):
    """点が円の内部に留まるように座標を制限するヘルパー関数"""
    distance = math.sqrt((dot_pos_x - center_pos[0])**2 + (dot_pos_y - center_pos[1])**2)
    if distance > radius:
        dir_x = (dot_pos_x - center_pos[0]) / distance
        dir_y = (dot_pos_y - center_pos[1]) / distance
        dot_pos_x = center_pos[0] + dir_x * radius
        dot_pos_y = center_pos[1] + dir_y * radius
    return dot_pos_x, dot_pos_y

def nxInput():
    global old_pressed_keys
    global mouse_scroll
    global pressed_keys
    global key_mappings
    global axis
    global old_axis
    

    for filepath, key in presets.items():
        if key in pressed_keys:
            key_mappings = openKeyConfig(filepath)
            print(f"プリセットが {filepath} に変更されました。")


    # 押されているキーの組み合わせをチェック
    w_pressed = 'w' in pressed_keys
    a_pressed = 'a' in pressed_keys
    s_pressed = 's' in pressed_keys
    d_pressed = 'd' in pressed_keys

    p_w_pressed = 'w' in old_pressed_keys
    p_a_pressed = 'a' in old_pressed_keys
    p_s_pressed = 's' in old_pressed_keys
    p_d_pressed = 'd' in old_pressed_keys

    # 移動キーの制御 (設定変更不可)
    if w_pressed and a_pressed:
        if (not p_w_pressed)or(not p_a_pressed)or(p_s_pressed)or(p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.HULF_LEFT, btkeyLib.Direction.UP)
            #print("左上へ移動 (W+A)")
    elif w_pressed and d_pressed:
        if (not p_w_pressed)or(p_a_pressed)or(p_s_pressed)or(not p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.HULF_RIGHT, btkeyLib.Direction.UP)
            #print("右上へ移動 (W+D)")
    elif s_pressed and a_pressed:
        if (p_w_pressed)or(not p_a_pressed)or(not p_s_pressed)or(p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.HULF_LEFT, btkeyLib.Direction.DOWN)
            #print("左下へ移動 (S+A)")
    elif s_pressed and d_pressed:
        if (p_w_pressed)or(p_a_pressed)or(not p_s_pressed)or(not p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.HULF_RIGHT, btkeyLib.Direction.DOWN)
            #print("右下へ移動 (S+D)")
    elif w_pressed:
        if (not p_w_pressed)or(p_a_pressed)or(p_s_pressed)or(p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.NEUTRAL, btkeyLib.Direction.UP)
            #print("上へ移動 (W)")
    elif a_pressed:
        if (p_w_pressed)or(not p_a_pressed)or(p_s_pressed)or(p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.LEFT, btkeyLib.Direction.NEUTRAL)
            #print("左へ移動 (A)")
    elif s_pressed:
        if (p_w_pressed)or(p_a_pressed)or(not p_s_pressed)or(p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.NEUTRAL, btkeyLib.Direction.DOWN)
            #print("下へ移動 (S)")
    elif d_pressed:
        if (p_w_pressed)or(p_a_pressed)or(p_s_pressed)or(not p_d_pressed):
            btkeyLib.holdLfree(btkeyLib.Direction.RIGHT, btkeyLib.Direction.NEUTRAL)
            #print("右へ移動 (D)")
    else:
        if (p_w_pressed)or(p_a_pressed)or(p_s_pressed)or(p_d_pressed):
            btkeyLib.releaseL()
            #print("移動キーがはなされた")


    # マウスの制御 (設定変更不可)
    if axis != old_axis:
        old_axis = axis
        btkeyLib.holdRfree(0x800 + int(0x800 * axis[0]),0x800 + int(0x800 * axis[1]))
        #print(f"マウス移動: {hex(RS_directions[0] - 0x800)},{hex(RS_directions[1] - 0x800)}")
    else:
        btkeyLib.releaseR()

    # マウススクロールのリセット
    try:
        pressed_keys.remove("Mouse.Scroll.up")
    except KeyError:
        pass
    try:
        pressed_keys.remove("Mouse.Scroll.down")
    except KeyError:
        pass

    # マウススクロールの管理
    if mouse_scroll != 0:
        if mouse_scroll > 0:
            pressed_keys.add("Mouse.Scroll.up")
        else:
            pressed_keys.add("Mouse.Scroll.down")
        mouse_scroll = 0 # スクロールフラグをリセット

    # BUTTON_NAMESのリストをループで回し、それぞれのボタンの状態をチェック
    for button_name in BUTTON_NAMES:
        mapped_key = key_mappings.get(button_name)
        old_mapped_key = mapped_key in old_pressed_keys
        
        # 割り当てられたキーが、現在押されているキーのセットに含まれているか確認
        if mapped_key in pressed_keys:
            draw_button(button_name,True)
            if(not old_mapped_key):
                btkeyLib.hold(Button[button_name])
                #print(f"{button_name}に割り当てられたキー {mapped_key} が押されている")
        else:
            draw_button(button_name,False)
            if(old_mapped_key):
                btkeyLib.release(Button[button_name])
                #print(f"{button_name}に割り当てられたキー {mapped_key} が離された")


    # 現在フレームで押されているキーを保存
    old_pressed_keys = pressed_keys.copy()

    screen.blit(image, (0, 0))

def nxRender():
    global old_pressed_keys
    global mouse_scroll
    global pressed_keys
    global key_mappings
    global axis

    # 押されているキーの組み合わせをチェック
    w_pressed = 'w' in pressed_keys
    a_pressed = 'a' in pressed_keys
    s_pressed = 's' in pressed_keys
    d_pressed = 'd' in pressed_keys

    if w_pressed and a_pressed:
        drawJoystick(True,-1,1)
    elif w_pressed and d_pressed:
        drawJoystick(True,1,1)
    elif s_pressed and a_pressed:
        drawJoystick(True,-1,-1)
    elif s_pressed and d_pressed:
        drawJoystick(True,1,-1)
    elif w_pressed:
        drawJoystick(True,0,1)
    elif a_pressed:
        drawJoystick(True,-1,0)
    elif s_pressed:
        drawJoystick(True,0,-1)
    elif d_pressed:
        drawJoystick(True,1,0)
    else:
        drawJoystick(True,0,0)

    # マウスの制御 (設定変更不可)
    if (axis != (0,0)):

        drawJoystick(False,axis[0],axis[1])
    else:
        drawJoystick(False,0,0)

    for button_name in BUTTON_NAMES:
        mapped_key = key_mappings.get(button_name)

        if mapped_key in pressed_keys:
            draw_button(button_name,True)
        else:
            draw_button(button_name,False)


last_time = 0
running = True

while running:
    screen.fill(WHITE)
    
    # --- 1. イベント処理 ---
    
    rel_x = 0
    rel_y = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        
        if event.type == pygame.MOUSEMOTION:
            rel_x, rel_y = event.rel

    # --- 2. ジョイスティックの座標更新 ---
    sensitivity = 2
    mouse_dot_x += rel_x * sensitivity
    mouse_dot_y += rel_y * sensitivity

    friction = 0.9
    mouse_dot_x = mouse_joystick_center[0] + (mouse_dot_x - mouse_joystick_center[0]) * friction
    mouse_dot_y = mouse_joystick_center[1] + (mouse_dot_y - mouse_joystick_center[1]) * friction
    if abs(mouse_dot_x - mouse_joystick_center[0]) < 0.5 and abs(mouse_dot_y - mouse_joystick_center[1]) < 0.5:
        mouse_dot_x = mouse_joystick_center[0]
        mouse_dot_y = mouse_joystick_center[1]

    # 点の座標に移動制限を適用
    mouse_dot_x, mouse_dot_y = limit_dot_position(
        mouse_joystick_center, 
        mouse_dot_x, 
        mouse_dot_y, 
        joystick_radius
    )
    
    # --- 3. ジョイスティックのaxis値を計算 ---
    # ドットの座標を、中心からの相対座標に変換
    relative_x = mouse_dot_x - mouse_joystick_center[0]
    relative_y = mouse_dot_y - mouse_joystick_center[1]
    
    # 正規化して-1.0から+1.0の範囲にする
    axis = (relative_x / joystick_radius,relative_y / joystick_radius * -1)

    # 経過時間を計算
    current_time = time.time()
    elapsed_time = current_time - last_time

    # 0.015秒に1回実行したい処理
    if elapsed_time >= 0.015:
        nxInput()

    nxRender()

    # マウスカーソルを中央に設定し直す
    #pygame.mouse.set_pos([screen_width // 2, screen_height // 2])
    
    pygame.display.flip()

# Pygameの終了
pygame.quit()

print("プログラムを終了します。")

# リスナーのスレッドが完全に終了するのを待つ
keyboard_listener.join()
mouse_listener.join()