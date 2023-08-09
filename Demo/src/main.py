import asyncio
from ble_serial.bluetooth.ble_interface import BLE_interface
import logging
import matplotlib.pyplot as plt
import numpy as np
import collections
from bluetooth import *

async def bleMain():
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = "0000ffe9-0000-1000-8000-00805f9a34fb"
    READ_UUID = "0000ffe4-0000-1000-8000-00805f9a34fb"
    DEVICE = "F8:9C:FE:38:6E:5C"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", 10.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "rw")

        #calibrate 
        print('calibrate')
        ble.queue_send(bytes.fromhex('FF AA 01 01 00'))

        #start getting data and update graph
        print('start loop')
        await asyncio.gather(ble.send_loop(), display_vals())
    finally:
        await ble.disconnect()

async def display_vals():
    while True:
        await asyncio.sleep(.1)
        print(ax_q)

def receive_callback(value: bytes):
    row = value.hex(':')
    if row[:5] == '55:61':
        #data record
        #acceleration
        axl = int(row[6:8],16)
        axh = int(row[9:11],16)
        ayl = int(row[12:14],16)
        ayh = int(row[15:17],16)
        azl = int(row[18:20],16)
        azh = int(row[21:23],16)
        ax = ((axh<<8)|axl)/32768*(16*9.8)
        ay = ((ayh<<8)|ayl)/32768*(16*9.8)
        az = ((azh<<8)|azl)/32768*(16*9.8)
        ax_q.popleft()
        ax_q.append(ax)
        ay_q.popleft()
        ay_q.append(ay)
        az_q.popleft()
        az_q.append(az)
        #velocity
        vxl = int(row[6:8],16)
        vxh = int(row[9:11],16)
        vyl = int(row[12:14],16)
        vyh = int(row[15:17],16)
        vzl = int(row[18:20],16)
        vzh = int(row[21:23],16)
        wx = ((vxh<<8)|vxl)/32768*2000
        wy = ((vyh<<8)|vyl)/32768*2000
        wz = ((vzh<<8)|vzl)/32768*2000
        wx_q.popleft()
        wx_q.append(wx)
        wy_q.popleft()
        wy_q.append(wy)
        wz_q.popleft()
        wz_q.append(wz)
    else:
        print("Received:", row)

async def regen_graph():
    while True:
        await asyncio.sleep(1.0)
        # clear axis
        ax.cla()
        # plot cpu
        ax.plot(ax_q)
        ax.scatter(len(ax_q)-1, ax_q[-1])
        ax.text(len(ax_q)-1, ax_q[-1]+2, "{}%".format(ax_q[-1]))
        ax.set_ylim(0,100)
        fig.show()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #set up data for graph
    ax_q = collections.deque(np.zeros(25))
    ay_q = collections.deque(np.zeros(25))
    az_q = collections.deque(np.zeros(25))
    wx_q = collections.deque(np.zeros(25))
    wy_q = collections.deque(np.zeros(25))
    wz_q = collections.deque(np.zeros(25))

    #build graph
    # fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
    # ax = plt.subplot(121)
    # ax.set_facecolor('#DEDEDE')
    
    
    asyncio.run(bleMain())