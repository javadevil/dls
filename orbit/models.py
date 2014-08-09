from django.db import models

# Create your models here.
class Device(models.Model):
    name = models.CharField(max_length=20)
    imei = models.TextField(max_length=17)
    
    def __str__(self):
        return 'name:{:<20}imei:[{}]'.format(self.name,self.imei)
    
class Crumb(models.Model):
    SIG_TRACKING        = 'TR'
    SIG_BEACON_ALERT    = 'BC'
    SIG_ACC_ON          = 'AO'
    SIG_ACC_OFF         = 'AF'
    SIG_UNKNOW          = 'UN'
    
    SIGNALS = (
        (SIG_TRACKING,'Tracking'),
        (SIG_BEACON_ALERT,'Beacon Alert'),
        (SIG_ACC_ON,'ACC on'),
        (SIG_ACC_OFF,'ACC off'),
        (SIG_UNKNOW,'Unknow Signal'),
    )
    device = models.ForeignKey(Device)
    signal = models.CharField(max_length=2,choices=SIGNALS,default='UN')
    stamp = models.DateTimeField()
    lat = models.FloatField()
    lng = models.FloatField()
    vec = models.FloatField(null=True)
    spd = models.FloatField(null=True)
    
    def __str__(self):
        return '[{}]{:3.6f},{:3.6f}'.format(self.stamp,self.lat,self.lng)
    
class Sense(models.Model):
    TITLES = (
        ('TM','Tempreture'),
        ('FL','Fuel Level'),
        ('UN','Unknow')
    )
    crumb = models.ForeignKey(Crumb)
    title = models.CharField(max_length=2,choices=TITLES,default='UN')
    value = models.FloatField()