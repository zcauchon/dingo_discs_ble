import asyncio
from bleak import BleakClient
import time
import json
from kafka import KafkaProducer

DEVICE = "F8:9C:FE:38:6E:5C"
LOCATION_ID = '0000ffe4-0000-1000-8000-00805f9a34fb'
accRange = 16.0
gyroRange = 2000.0
angleRange = 180.0
displayRange = 100

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092', compression_type='gzip', linger_ms=100)

def data_callback(handle, data: bytearray):
    row = data.hex(':').split(':')
    if row[:2] == ['55','61']:
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
      msg={'ax':ax, 'ay':ay, 'az':az, 'gx':gx, 'gy':gy, 'gz':gz, 'rx':rx, 'ry':ry, 'rz':rz}
      msg_b = json.dumps(msg, indent=2).encode('utf-8')
      producer.send(topic='disc_events', value=msg_b, key=DEVICE.encode('utf-8'))

async def main(address):
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    await client.write_gatt_char(LOCATION_ID, data=bytes.fromhex('FF AA 01 01 00'))
    print('calibrating...')
    time.sleep(5.5)
    print('calibrated!')

    await client.start_notify(LOCATION_ID, data_callback)
    counter = 0
    while True:
      await asyncio.sleep(.1)
      counter +=1
      if counter > 30:
        break

if __name__ == '__main__':
  asyncio.run(main(DEVICE))