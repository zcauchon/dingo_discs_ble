import matplotlib
matplotlib.use('TKAgg')
import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt
import time

DEVICE = "F8:9C:FE:38:6E:5C"
LOCATION_ID = '0000ffe4-0000-1000-8000-00805f9a34fb'
accRange = 16.0
gyroRange = 2000.0
angleRange = 180.0
displayRange = 100

fig = None
time_q = [0]*displayRange
ax_q = [0]*displayRange
ay_q = [0]*displayRange
az_q = [0]*displayRange
gx_q = [0]*displayRange
gy_q = [0]*displayRange
gz_q = [0]*displayRange
rx_q = [0]*displayRange
ry_q = [0]*displayRange
rz_q = [0]*displayRange

def location_callback(handle, data: bytearray):
    global start_time
    row = data.hex(':').split(':')
    if row[:2] == ['55','61']:
      t = time.time()-start_time
      time_q.append(t)
      #data record
      #acceleration
      axl = int(row[2],16)
      axh = int(row[3],16)
      ayl = int(row[4],16)
      ayh = int(row[5],16)
      azl = int(row[6],16)
      azh = int(row[7],16)
      ax = (axh << 8 | axl) / 32768.0 * accRange
      ay = (ayh << 8 | ayl) / 32768.0 * accRange
      az = (azh << 8 | azl) / 32768.0 * accRange
      if ax >= accRange:
        ax -= 2 * accRange
      if ay >= accRange:
        ay -= 2 * accRange
      if az >= accRange:
        az -= 2 * accRange
      ax_q.append(ax)
      ay_q.append(ay)
      az_q.append(az)
      # gyro
      gxl = int(row[8],16)
      gxh = int(row[9],16)
      gyl = int(row[10],16)
      gyh = int(row[11],16)
      gzl = int(row[12],16)
      gzh = int(row[13],16)
      gx = ((gxh<<8)|gxl)/32768*180
      gy = ((gyh<<8)|gyl)/32768*180
      gz = ((gzh<<8)|gzl)/32768*180
      if gx >= gyroRange:
          gx -= 2 * gyroRange
      if gy >= gyroRange:
          gy -= 2 * gyroRange
      if gz >= gyroRange:
          gz -= 2 * gyroRange
      gx_q.append(gx)
      gy_q.append(gy)
      gz_q.append(gz)
      # angle
      rxl = int(row[14],16)
      rxh = int(row[15],16)
      ryl = int(row[16],16)
      ryh = int(row[17],16)
      rzl = int(row[18],16)
      rzh = int(row[19],16)
      rx = ((rxh<<8)|rxl)/32768*angleRange # nose angle
      ry = ((ryh<<8)|ryl)/32768*angleRange # hyzer angle
      rz = ((rzh<<8)|rzl)/32768*angleRange # "spin" angle -180 - 180 then resets
      if rx >= angleRange:
          rx -= 2 * angleRange
      if ry >= angleRange:
          ry -= 2 * angleRange
      if rz >= angleRange:
          rz -= 2 * angleRange
      rx_q.append(rx)
      ry_q.append(ry)
      rz_q.append(rz)
      print(t, ax, ay, az, gx, gy, gz, rx, ry, rz)

async def rebuild_graph():
    global ax_q, ay_q, az_q, time_q, fig, a1, a2, a3, fig
    if fig is None:
      # Create the line chart using matplotlib
      fig, (a1, a2, a3) = plt.subplots(3, 1)
      fig.subplots_adjust(hspace=0.3)
      a1.set_xlabel("Time (seconds)")
      a1.set_ylabel("Acc")
      a2.set_xlabel("Time (seconds)")
      a2.set_ylabel("Gyro")
      a3.set_xlabel("Time (seconds)")
      a3.set_ylabel("Angle")
    a1.cla()
    a2.cla()
    a3.cla()
    a1.plot(time_q[-displayRange:], ax_q[-displayRange:], label="ax")
    a2.plot(time_q[-displayRange:], gx_q[-displayRange:], label="gx")
    a3.plot(time_q[-displayRange:], rx_q[-displayRange:], label="rx")
    a1.plot(time_q[-displayRange:], ay_q[-displayRange:], label="ay")
    a2.plot(time_q[-displayRange:], gy_q[-displayRange:], label="gy")
    a3.plot(time_q[-displayRange:], ry_q[-displayRange:], label="ry")
    a1.plot(time_q[-displayRange:], az_q[-displayRange:], label="az")
    a2.plot(time_q[-displayRange:], gz_q[-displayRange:], label="gz")
    a3.plot(time_q[-displayRange:], rz_q[-displayRange:], label="rz")
    fig.legend()
    plt.pause(.001)
       
async def main(address):
  global start_time
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    await client.write_gatt_char(LOCATION_ID, data=bytes.fromhex('FF AA 01 01 00'))
    print('calibrating...')
    time.sleep(5.5)
    print('calibrated!')

    start_time = time.time()
    await client.start_notify(LOCATION_ID, location_callback)
    counter = 0
    while True:
      await asyncio.sleep(.33)
      await rebuild_graph()
      counter +=1
      if counter > 30:
        break

  input('Press any button to continue')

if __name__ == '__main__':
  asyncio.run(main(DEVICE))