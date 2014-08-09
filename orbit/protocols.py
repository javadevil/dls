import re
from datetime import datetime,timezone
from orbit.models import Device,Crumb

class Base(object):
    
    NAME = ''
    
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = '[{}({})]'.format(addr[0],addr[1])
        
    def run(self):
        try:
            print(self.addr,'connected')
            while 1:
                raw = self.conn.recv(128)
            
                if not raw:
                    break

                if not self.recv(str(raw,'utf-8')):
                    break
        finally:
            self.conn.close()
            print(self.addr,'disconnect')
            
    def recv(self,data):
        pass

class Gps103(Base):
    
    NAME = 'GPS103'
    
    data_p = re.compile(r'imei:'
                         '(?P<imei>\d+),'
                         '(?P<signal>[^,]+),'
                         '(?P<year>\d{2})/?(?P<month>\d{2})/?(?P<day>\d{2})\s?'
                         '(?P<local_hour>\d{2}):?(?P<local_min>\d{2})(?:\d{2})?,'
                         '[^,]*,'
                         '[FL],'
                         '(?P<utc_hour>\d{2})(?P<utc_min>\d{2})(?P<sec>\d{2})\.(?P<ms>\d+),'
                         '([AV]),'
                         '(?P<lat1>\d+)(?P<lat2>\d{2}\.\d+),'
                         '(?P<lat3>[NS])?,'
                         '(?P<lng1>\d+)(?P<lng2>\d{2}\.\d+),'
                         '(?P<lng3>[EW])?,'
                         '(?P<spd>\d+\.?\d*),'
                         '(?P<crs>\d+\.?\d*)?,?'
                         '(?P<alt>\d+\.?\d*)?,?'
                         '(?P<ext1>[^,]+)?,?'
                         '(?P<ext2>[^,]+)?,?'
                         '(?P<ext3>[^,]+)?,?'
                         '(?P<ext4>[^,]+)?,?'
                         '.*')
    auth_p = re.compile(r'^##,imei:(?P<imei>\d+),A;')
    ping_p = re.compile(r'^[0-9]*;')
    
    def recv(self,data):
        # Auth response
        auth_m = self.auth_p.match(data)
        if auth_m:
            try:
                self.device = Device.objects.get(imei=auth_m.group('imei'))
                self.conn.sendall(b'LOAD')
                print('Auth:',auth_m.group('imei'))
                return True
            except:
                print(self.addr,'device invalid')
                return False
            
        # Ping response 
        if self.ping_p.match(data):
            self.conn.sendall(b'ON')
            print(self.addr,'ON')
            
        data_m = self.data_p.match(data)
        if data_m:
            print(self.addr,data)
            
            signal  = Crumb.SIG_UNKNOW
            if data_m.group('signal') == 'tracker':
                signal = Crumb.SIG_TRACKING
            
            d       = datetime(year=int(data_m.group('year')),month=int(data_m.group('month')),day=int(data_m.group('day')))
            local   = d.replace(hour=int(data_m.group('local_hour')),minute=int(data_m.group('local_min')))
            utc     = d.replace(hour=int(data_m.group('utc_hour')),minute=int(data_m.group('utc_min')))
            delta   = local-utc
            stamp   = local.replace(second=int(data_m.group('sec')),tzinfo=timezone(delta))

            lat = float(data_m.group('lat1'))
            lat += float(data_m.group('lat2')) / 60.0
            if data_m.group('lat3') == 'S':
                lat = -lat
                
            lng = float(data_m.group('lng1'))
            lng += float(data_m.group('lng2')) / 60.0
            if data_m.group('lng3') == 'W':
                lng = -lng
            
            spd = 0.0
            if data_m.group('spd'):
                spd = float(data_m.group('spd'))
            
            vec = 0.0
            if data_m.group('crs'):
                vec = float(data_m.group('crs'))
            
            c = Crumb(device=self.device,signal=signal,lat=lat,lng=lng,spd=spd,vec=vec,stamp=stamp)
            c.save()
        return True
            
        