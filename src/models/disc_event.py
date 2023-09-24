import json

class DiscEvent:
    accRange = 16.0
    gyroRange = 2000.0
    angleRange = 180.0
    displayRange = 100
    encoded_method = 'utf-8'

    def __init__(self, device: str, row: bytearray) -> None:
        self.device = device
        #data record
        #acceleration
        axl = int(row[2],16)
        axh = int(row[3],16)
        ayl = int(row[4],16)
        ayh = int(row[5],16)
        azl = int(row[6],16)
        azh = int(row[7],16)
        self.ax = (axh << 8 | axl) / 32768.0 * self.accRange
        self.ay = (ayh << 8 | ayl) / 32768.0 * self.accRange
        self.az = (azh << 8 | azl) / 32768.0 * self.accRange
        if self.ax >= self.accRange:
            self.ax -= 2 * self.accRange
        if self.ay >= self.accRange:
            self.ay -= 2 * self.accRange
        if self.az >= self.accRange:
            self.az -= 2 * self.accRange
        # gyro
        gxl = int(row[8],16)
        gxh = int(row[9],16)
        gyl = int(row[10],16)
        gyh = int(row[11],16)
        gzl = int(row[12],16)
        gzh = int(row[13],16)
        self.gx = ((gxh<<8)|gxl)/32768*self.angleRange
        self.gy = ((gyh<<8)|gyl)/32768*self.angleRange
        self.gz = ((gzh<<8)|gzl)/32768*self.angleRange
        if self.gx >= self.gyroRange:
            self.gx -= 2 * self.gyroRange
        if self.gy >= self.gyroRange:
            self.gy -= 2 * self.gyroRange
        if self.gz >= self.gyroRange:
            self.gz -= 2 * self.gyroRange
        # angle
        rxl = int(row[14],16)
        rxh = int(row[15],16)
        ryl = int(row[16],16)
        ryh = int(row[17],16)
        rzl = int(row[18],16)
        rzh = int(row[19],16)
        self.rx = ((rxh<<8)|rxl)/32768*self.angleRange # nose angle
        self.ry = ((ryh<<8)|ryl)/32768*self.angleRange # hyzer angle
        self.rz = ((rzh<<8)|rzl)/32768*self.angleRange # "spin" angle -180 - 180 then resets
        if self.rx >= self.angleRange:
            self.rx -= 2 * self.angleRange
        if self.ry >= self.angleRange:
            self.ry -= 2 * self.angleRange
        if self.rz >= self.angleRange:
            self.rz -= 2 * self.angleRange
    
    def getEncodedMessage(self):
        msg = {
            'device':self.device,
            'ax':self.ax,
            'ay':self.ay,
            'az':self.az,
            'gx':self.gx,
            'gy':self.gy,
            'gz':self.gz,
            'rx':self.rx,
            'ry':self.ry,
            'rz':self.rz
        }
        return json.dumps(msg).encode(self.encoded_method)
    
    def getEncodedKey(self):
        return self.device.encode(self.encoded_method)