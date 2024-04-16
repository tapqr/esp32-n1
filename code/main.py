# main.py -- put your code here!

import network
from machine import Pin
from time import sleep
from ir_rx.nec import NEC_8
import urequests as requests
import ujson
import ubluetooth
# from micropython import const

led = Pin(2, Pin.OUT)
irPin = Pin(23, Pin.IN)

uri = 'http://192.168.8.13/v1/keyevent'
setUri = 'http://192.168.8.13/v1/action'
# _IRQ_SCAN_RESULT = const(5)
# _IRQ_SCAN_DONE = const(6)

keyMap = {
    "34_202": 19, #上
    "34_210": 20, #下
    "34_153": 20, #左
    "34_193": 20, #右
    "34_149": 20, #返回
    "34_128": 20, #音量加
    "34_129": 20, #音量减
    "34_136": 20, #主界面
    "34_130": 20, #菜单
    "34_206": 20, #确认键
    "34_220": 20, #电源
    "34_141": 20, #设置
}

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('ssid', 'password')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def irCallback(data, addr, ctrl):
    if data < 0:
        print('repeat code.')
    else:
        key = '%s_%s'%(addr, data)
        if key == '34_141':
            openSetting()
        else:
            if key == '34_220':
                # 模拟连接蓝牙，可以开机
                connectBle()
            doHttp(key)
        # print('Data {:02x} Addr {:04x}'.format(data, addr))

def doHttp(key):
    code = keyMap[key]
    if code is not None:
        post_data = ujson.dumps({"keycode": keyMap[key], "longclick": False})
        res = requests.post(uri, headers = {'content-type': 'application/json'}, data = post_data)
        print(res.text)

def openSetting():
    post_data = ujson.dumps({"action":"setting"})
    requests.post(setUri, headers = {'content-type': 'application/json'}, data = post_data)

def ble_irq(event, data):
    if event == 5:
        # A single scan result.
        addr_type, addr, connectable, rssi, adv_data = data
        print(':'.join(['%02X' % i for i in addr]))
    elif event == 6:
        # Scan duration finished or manually stopped.
        print('scan complete')

def connectBle():
    ble = ubluetooth.BLE()
    ble.active(True)
    # ble.irq(ble_irq)
    # ble.gap_scan(10000, 1280000, 11250)
    ble.gap_connect(1, '00:B5:57:6B:70:1C', 2000)

if __name__ == "__main__":
    do_connect()
    ir = NEC_8(irPin, irCallback)
