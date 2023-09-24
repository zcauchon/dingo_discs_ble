import asyncio
from bleak import BleakClient
import time
from kafka import KafkaProducer
from models.disc_event import DiscEvent

DEVICE = "F8:9C:FE:38:6E:5C"
LOCATION_ID = '0000ffe4-0000-1000-8000-00805f9a34fb'

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092', compression_type='gzip', linger_ms=100)

def data_callback(handle, data: bytearray):
    row = data.hex(':').split(':')
    if row[:2] == ['55','61']:
      event = DiscEvent(DEVICE, row)
      msg = event.getEncodedMessage()
      producer.send(topic='disc_events', value=msg, key=event.getEncodedKey())

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
      if counter > 25:
        break

if __name__ == '__main__':
  asyncio.run(main(DEVICE))