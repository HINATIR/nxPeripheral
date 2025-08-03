import json
import time
import glob
import os
from pynput import mouse, keyboard

# 設定を保存する辞書
key_mappings = {}

# 入力待ちの状態を制御するフラグ
wait_for_input = False

# 取得した入力内容を保存する変数
captured_input = None

# 割り当てたいボタン名のリスト
BUTTON_NAMES = [
    "A", "B", "X", "Y", "L", "R", "ZL", "ZR", "PLUS", "MINUS", 
    "LCLICK", "RCLICK", "UP", "DOWN", "RIGHT", "LEFT", "HOME", "CAPTURE"
]

preset_config = {}

if not os.path.exists("keyconfig"):
    os.makedirs(f"keyconfig")

if not os.path.exists("presets"):
    os.makedirs(f"presets")


def on_press(key):
    """キーが押されたときの処理"""
    global wait_for_input, captured_input
    if wait_for_input:
        try:
            captured_input = f"Key.{key.name}" if hasattr(key, 'name') else key.char
        except AttributeError:
            captured_input = f"Key.{key.name}"
        return False

def on_click(x, y, button, pressed):
    """マウスクリックの処理"""
    global wait_for_input, captured_input
    if wait_for_input and pressed:
        captured_input = f"Mouse.Button.{button.name}"
        return False

def on_scroll(x, y, dx, dy):
    """マウスホイールの処理"""
    global wait_for_input, captured_input
    if wait_for_input:
        if dy > 0:
            captured_input = "Mouse.Scroll.up"
        else:
            captured_input = "Mouse.Scroll.down"
        return False

def get_user_input():
    """ユーザーからの入力を受け付け、取得する関数"""
    global wait_for_input, captured_input
    
    captured_input = None
    wait_for_input = True
    
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()
    
    while mouse_listener.running and keyboard_listener.running:
        time.sleep(0.1)

    if mouse_listener.running:
        mouse_listener.stop()
    if keyboard_listener.running:
        keyboard_listener.stop()
    
    mouse_listener.join()
    keyboard_listener.join()

    return captured_input

def keyConfig():
    print("キー設定を開始します。")
    print("それぞれの項目が表示された後、設定したいキーやボタンを入力してください。")
    keyconfig_name = input("キー設定名を入力> ")
    try:
        for button_name in BUTTON_NAMES:
            # 入力待ちのプロンプトを表示
            print(f"{button_name} = ", end="", flush=True)
            
            # ユーザーからの入力を取得
            user_input = get_user_input()
            
            # 取得した入力を辞書に保存
            key_mappings[button_name] = user_input
            
            # 入力が完了したことを表示
            print(f"'{user_input}' に設定されました。")
            
        print("\n--- 設定完了 ---")
        
        with open(f"keyconfig/{keyconfig_name}.json", 'w', encoding='utf-8') as f:
            json.dump(key_mappings, f, indent=2, ensure_ascii=False)
        print("キー設定を保存しました。\n")
    except KeyboardInterrupt:
        print("\nプログラムが中断されました。\n")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}\n")

def presetConfig():
    print("プリセット設定を開始します。")
    print("使用したいキー設定名を入力したら、それに対応させたいキーを入力。")
    print("最初に設定したキーは初期のキー設定になります。")
    print("")
    print("利用できるキー設定ファイルの番号")

    json_files = glob.glob(os.path.join("keyconfig", '*.json'))
    
    for n, fn in enumerate(json_files):
        print(f"{n}: {fn}")
    preset_name = input(f"プリセットファイル名を入力> ")

    presets_filenames = []
    try:
        i = 0
        while 1:

            fileindex = input(f"[{i}] キー設定ファイルの番号を入力。エンターで終了。> ")
            if(fileindex == ""):
                break
            presets_filenames.append(json_files[int(fileindex)])
            i = i+1
        
        while 1:
            for n, name in enumerate(presets_filenames):
                print(f"{n}: {name}に切り替えるためのキーを入力> ", end="", flush=True)
                user_input = get_user_input()
                preset_config[name] = user_input
                print(f"'{user_input}'")
            break


            
        print("\n--- 設定完了 ---")

        
        with open(f"presets/{preset_name}.json", 'w', encoding='utf-8') as f:
            json.dump(preset_config, f, indent=2, ensure_ascii=False)
        print("プリセットを保存しました。\n")

    except KeyboardInterrupt:
        print("\nプログラムが中断されました。\n")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}\n")

while 1:
    print("[nxPeripheralKeyConfig]")
    print("k > キー設定を作成する") 
    print("p > プリセットを作成する")
    inst = input()

    if inst == "k":
        keyConfig()
    elif inst == "p":
        presetConfig()