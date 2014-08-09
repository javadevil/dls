from django.shortcuts import render
from django.http import HttpResponse
from orbit.models import Device,Crumb
import json
# Create your views here.
def latest(request):
    output = []
    devices = Device.objects.all()
    for device in devices:
        c = Crumb.objects.filter(device=device).order_by('-stamp')[0]
        c_out = {'stamp':c.stamp.isoformat(),'lat':c.lat,'lng':c.lng,'vec':c.vec,'spd':c.spd}
        d_out = {'name':device.name,'imei':device.imei,'crumb':c_out}
        output.append(d_out)
    return HttpResponse(json.dumps(output))