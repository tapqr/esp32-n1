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

uri = 'http://192.168.8.13:8080/v1/keyevent'
setUri = 'http://192.168.8.13:8080/v1/action'
preKey = ''
# _IRQ_SCAN_RESULT = const(5)
# _IRQ_SCAN_DONE = const(6)

keyMap = {
    "34_202": 19, #上
    "34_210": 20, #下
    "34_153": 21, #左
    "34_193": 22, #右
    "34_149": 4, #返回
    "34_128": 24, #音量加
    "34_129": 25, #音量减
    "34_136": 3, #主界面
    "34_130": 82, #菜单
    "34_206": 23, #确认键
    "34_220": 26, #电源
    "34_141": 27, #设置
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
    global preKey
    if data < 0:
        print('repeat code.')
        doHttp(preKey)
    else:
        print('Data {:02x} Addr {:04x}'.format(data, addr))
        preKey = '%s_%s'%(addr, data)
        if preKey == '34_141':
            openSetting()
        else:
            if preKey == '34_220':
                # 模拟连接蓝牙，可以开机
                connectBle()
            doHttp(preKey)

def doHttp(key):
    code = keyMap[key]
    if code is not None:
        post_data = ujson.dumps({"keycode": keyMap[key], "longclick": False})
        requests.post(uri, headers = {'content-type': 'application/json'}, data = post_data)

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
