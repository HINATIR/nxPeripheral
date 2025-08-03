from ctypes import *
import threading
import time
from enum import IntFlag, IntEnum, auto

btkeyLib = cdll.LoadLibrary("./btkeyLib.dll")

# ボタンのフラグの定義
# Proコンは左右joyconと同じフォーマットでデータを送信しますが、ProコンにSR/SLボタンが無い等の理由で一部のビットは使用できません。
class Button(IntFlag):
    Y = auto()
    X = auto()
    B = auto()
    A = auto()
    SR1 = auto() # ビットの関係上定義されていますが使用できません
    SL1 = auto() # ビットの関係上定義されていますが使用できません
    R = auto()
    ZR = auto()
    MINUS = auto()
    PLUS = auto()
    RCLICK = auto()
    LCLICK = auto()
    HOME = auto()
    CAPTURE = auto()
    UNUSED = auto() # ビットの関係上定義されていますが使用できません
    CHARGING = auto() # ビットの関係上定義されていますが使用できません
    DOWN = auto()
    UP = auto()
    RIGHT = auto()
    LEFT = auto()
    SR2 = auto() # ビットの関係上定義されていますが使用できません
    SL2 = auto() # ビットの関係上定義されていますが使用できません
    L = auto()
    ZL = auto()

# スティックの値の定義
# 上下と左右それぞれ12bitずつ
class Direction(IntEnum):
    UP = 0xFFF
    DOWN = 0
    LEFT = 0
    RIGHT = 0xFFF
    NEUTRAL = 0x800
    HULF_RIGHT = 0x800 + 0x333 # ±40%
    HULF_LEFT = 0x800 - 0x333

# threadingでdllを呼び出すための関数
def s():
    btkeyLib.start_gamepad()

# Bluetooth接続を開始するための関数
# 引数はコントローラー、ボタン、左グリップ、右グリップの色をカラーコードで指定する
def start(pad_color:int, button_color:int, leftgrip_color:int, rightgrip_color:int):
    btkeyLib.send_button.argtypes = (c_uint32, c_uint32)
    btkeyLib.send_stick_l.argtypes = (c_uint32, c_uint32, c_uint32)
    btkeyLib.send_stick_r.argtypes = (c_uint32, c_uint32, c_uint32)
    btkeyLib.send_gyro.argtypes = (c_int16, c_int16, c_int16)
    btkeyLib.send_accel.argtypes = (c_int16, c_int16, c_int16)
    btkeyLib.send_padcolor.argtypes = (c_uint32, c_uint32, c_uint32, c_uint32)
    btkeyLib.gamepad_paired.restypes = (c_bool,)
    btkeyLib.send_padcolor(pad_color, button_color, leftgrip_color, rightgrip_color)
    thread_1 = threading.Thread(target=s)
    thread_1.start()

# Bluetoothでswitchと接続されたかどうかを返す関数(bool)
# switchと接続されるとTrueが返されます
def is_paired():
    return btkeyLib.gamepad_paired()

# ボタンを一定時間押して離す関数
Buttonflg = 0
def press(key:Button, wait:int):
    global Buttonflg
    Buttonflg |= key.value
    btkeyLib.send_button(Buttonflg, 0)
    time.sleep(wait)
    Buttonflg &= ~key.value
    btkeyLib.send_button(Buttonflg, 0)

# ボタンをホールドする関数
def hold(key:Button):
    global Buttonflg
    Buttonflg |= key.value
    btkeyLib.send_button(Buttonflg, 0)

# ホールドしていたボタンを離す関数
def release(key:Button):
    global Buttonflg
    Buttonflg &= ~key.value
    btkeyLib.send_button(Buttonflg, 0)

# Lスティックを出来合いの値で倒す関数
# 引数は横方向、縦方向、時間
# 39行目で定義されているDirectionを使用する
def moveL(horizontal:Direction, vertical:Direction, wait:int):
    btkeyLib.send_stick_l(horizontal.value, vertical.value, 0)
    time.sleep(wait)
    btkeyLib.send_stick_l(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# Lスティックを自由な値で倒す関数
# 引数は横方向、縦方向、時間
# 縦横それぞれの値(0から4095)がどの方向を表しているかは39行目で定義されているDirectionを参照
def moveLfree(horizontal:int, vertical:int, wait:int):
    btkeyLib.send_stick_l(horizontal, vertical, 0)
    time.sleep(wait)
    btkeyLib.send_stick_l(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# Lスティックを出来合いの値でホールドする関数
# 引数は横方向、縦方向
# moveLとは違い、ニュートラルに戻さないので滑らかに移動できる
def holdL(horizontal:Direction, vertical:Direction):
    btkeyLib.send_stick_l(horizontal.value, vertical.value, 0)

# Lスティックを自由な値でホールドする関数
def holdLfree(horizontal:int, vertical:int):
    btkeyLib.send_stick_l(horizontal, vertical, 0)

# ホールドしていたLスティックをニュートラルに戻す関数
def releaseL():
    btkeyLib.send_stick_l(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# Rスティックを出来合いの値で倒す関数
def moveR(horizontal:Direction, vertical:Direction, wait:int):
    btkeyLib.send_stick_r(horizontal.value, vertical.value, 0)
    time.sleep(wait)
    btkeyLib.send_stick_r(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# Rスティックを自由な値で倒す関数
def moveRfree(horizontal:int, vertical:int, wait:int):
    btkeyLib.send_stick_r(horizontal, vertical, 0)
    time.sleep(wait)
    btkeyLib.send_stick_r(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# Rスティックを出来合いの値でホールドする関数
def holdR(horizontal:Direction, vertical:Direction):
    btkeyLib.send_stick_r(horizontal.value, vertical.value, 0)

# Rスティックを自由な値でホールドする関数
def holdRfree(horizontal:int, vertical:int):
    btkeyLib.send_stick_r(horizontal, vertical, 0)

# ホールドしていたRスティックをニュートラルに戻す関数
def releaseR():
    btkeyLib.send_stick_r(Direction.NEUTRAL.value, Direction.NEUTRAL.value, 0)

# switchとの接続を切る関数
def shutdown():
    btkeyLib.shutdown_gamepad()

# 実験的機能
# ジャイロの値を設定する関数
# いわゆるジャイロセンサーから取れるデータを設定できる
# dll側では符号付き整数で受け取っているので、符号周りの変換が必要
def gyro(x:int, y:int, z:int):
    btkeyLib.send_gyro(x, y, z)

# 実験的機能
# 加速度計の値を設定する関数
# いわゆる加速度センサーから取れるデータを設定できる
# dll側では符号付き整数で受け取っているので、符号周りの変換が必要
def accel(x:int, y:int, z:int):
    btkeyLib.send_accel(x, y, z)
