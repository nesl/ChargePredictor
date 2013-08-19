from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from visualization.models import SystemSens
from visualization.models import PILOT1
from visualization.models import comments
from visualization.models import Deadline
from visualization.models import Client
from visualization.models import Profile
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection

import time, calendar, simplejson, datetime, os, math, sys
import struct

os.environ['MPLCONFIGDIR']='/home/nesl/.matplotlib/'
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
#import matplotlib.cbook as cbook
import matplotlib.cm as cm
import pylab
import numpy


hours    = mdates.HourLocator()   # every hour
days   = mdates.DayLocator()  # every day
hoursFmt = mdates.DateFormatter('%H')
daysFmt = mdates.DateFormatter('%m-%d  .')
mininterval = datetime.timedelta(hours=1)

border_width = 0.05
ax_size = [0+border_width, 0+5*border_width, 1-2*border_width, 1-6*border_width]


ONE_SECOND = 1000.0
ONE_MINUTE = 60 * ONE_SECOND
ONE_HOUR = 60 * ONE_MINUTE

cpucolors = {
        '0.0'   : (0, 0, 0), # Black 0-0-0
        '99.73' :  (0.88, 1, 1), # Light Cyan 224-255-255
        '99.4' :  (0.88, 1, 1), # Light Cyan 224-255-255
        '162.54': (0.88, 1, 1), # Light Cyan 224-255-255
        '199.47':  (0.88, 1, 1), # Light Cyan 224-255-255
        '199.8':  (0.88, 1, 1), # Light Cyan 224-255-255
        '254.77': (0.68, 0.85, 0.90), # Light blue 173-216-230
        '245.36': (0.68, 0.85, 0.90), # Light blue 173-216-230
        '280.24': (0.68, 0.85, 0.90), # Light blue 173-216-230
        '299.95': (0.68, 0.85, 0.90), # Light blue 173-216-230
        '305.72': (0.40, 0.80, 0.69), # Medium Aquamarine 102-205-170
        '331.2' : (0.56, 0.73, 0.56), # Dark sea green 143-188-143
        '356.67' : (0.56, 0.73, 0.56), # Dark sea green 143-188-143
        '382.15': (0.60, 0.80, 0.19), # Yellow green 154-205-50
        '383.38': (0.60, 0.80, 0.19), # Yellow green 154-205-50
        '398.95': (0.60, 0.80, 0.19), # Yellow green 154-205-50
        '398.6': (0.60, 0.80, 0.19), # Yellow green 154-205-50
        '407.63': (0.64, 0.71, 0.12),  # I don't know
        '433.11': (0.74, 0.71, 0.42),  # Dark khaki 189-183-107
        '458.58': (1, 0.63, 0.37), # Sandy brown 244-164-96
        '484.06': (1, 0.63, 0.37), # Sandy brown 244-164-96
        '535.01': (1, 0.58, 0), # Dark orange 255-140-0
        '560.49': (1, 0.39, 0.28), # Tomato 255-99-71
        '509.54': (1, 1, 0), # Yellow 255-255-0
        '585.97': (1, 1, 0), # Yellow 255-255-0
        '598.9': (1, 1, 0), # Yellow 255-255-0
        '611.45': (1, 1, 0), # Yellow 255-255-0
        '636.92' : (1, 0, 0),  # Red 255-0-0
        '662.4' : (1, 0, 0),  # Red 255-0-0
        '797.9' : (0.65, 0.16, 0.16), # Brown 165-42-42
        '796.2' : (0.65, 0.16, 0.16), # Brown 165-42-42
        '798.87' : (0.65, 0.16, 0.16), # Brown 165-42-42
        '997.37' : (0, 0, 0), # Black 0-0-0
        '996' : (0, 0, 0), # Black 0-0-0
        '998.84' : (0, 0, 0) # Black 0-0-0
        }


class User_Query:
    def __init__(self, start, end, imei):
        self.startdate = start
        self.enddate = end
        self.imei = imei


    def set_date(start, end):
        self.startdate = start
        self.enddate = end



def _query(imei, fdate=None, tdate=None, rtype='any'):
    #if tdate - fdate < mininterval:
    #    return []
    imei = imei.upper()

    table_name = check_table(imei)

    SystemSens._meta.db_table = table_name

    if fdate == None:
        q = SystemSens.objects.all()
    else:
        q = SystemSens.objects.filter(dt_record__gte=fdate)
        q = q.filter(dt_record__lte=tdate)

    if rtype != "any":
        q = q.filter(data_type__exact=rtype)
    q = q.order_by('dt_record')
    return q




def _date(in_date):

    if len(in_date) == 8:
        y_str = in_date[:4]
        m_str = in_date[4:6]
        d_str = in_date[-2:]
        return "%s-%s-%s" %(y_str, m_str, d_str)
    else:
        y_str = in_date[:4]
        m_str = in_date[4:6]
        d_str = in_date[6:8]
        h_str = in_date[8:10]
        mi_str = in_date[10:12]

        return "%s-%s-%s %s:%s:00" %(y_str, m_str, d_str, h_str, mi_str)



def correct_date(in_date):
    if len(in_date) > 10:
        res = datetime.datetime.strptime(in_date, '%Y-%m-%d %H:%M:%S')
        #res = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
    else:
        res = datetime.datetime.strptime(in_date, '%Y-%m-%d')
        #res = datetime.datetime(t.year, t.month, t.day)


    return res

def time_datetime(t):
    res = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour,
            t.tm_min, t.tm_sec)
    return res




#@login_required
#def screen_time(request, imei, fdate, tdate):
#    response = HttpResponse(mimetype='image/png')
#
#    from_date = _date(fdate)
#    to_date = _date(tdate)
#    q = _query(imei, from_date, to_date, 'screen')
#
#    plotvals = []
#    plotkeys = []
#    plotmap = {}
#
#    stime = 0
#
#    for e in q.all().order_by('dt_record'):
#        record = simplejson.loads(e.message)
#        data = record["data"]
#        if data["status"] == "ON":
#            plotkeys.append(record["date"])
#
#    return HttpResponse("Found " + str(len(plotkeys))  + " records"
#            + " Start date: " + from_date
#            + " End date: " + to_date
#            + str(plotkeys));
#
#



@login_required
def screen_time(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'screen')

    plotvals = []
    plotkeys = []
    plotmap = {}

    stime = 0

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        if data["status"] == "ON":
            stime = int(record["time_stamp"])

        if data["status"] == "OFF":
            etime = int(record["time_stamp"])
            slen = (etime - stime)/(1000)
            if slen < 1000:
                d = record["date"]
                t = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month + 1, t.day, t.hour)
                if t_idx not in plotmap.keys():
                    plotmap[t_idx] = slen
                else:
                    plotmap[t_idx] += slen


    for k in plotmap.keys():
        plotkeys.append(datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S'))

    plotkeys.sort()



    for t in plotkeys:
        t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
        plotvals.append(plotmap[t_idx])




    fig = Figure(figsize=(12.5,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=2, ms=10, alpha=0.7, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Length of Interactions (minutes)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)

    canvas.print_png(response)

    return response






@login_required
def sleep(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    tempresponse = HttpResponse(mimetype='text')



    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'screen')

    plotvals = []
    plotkeys = []
    plotmap = {}

    timeset = set()

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        t = e.dt_record
        timeset.add(t)
        if data["status"] == "ON":
            t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
            if t_idx not in plotmap.keys():
                plotmap[t_idx] = 1
            else:
                plotmap[t_idx] += 1


    z = datetime.timedelta(hours=1)
    t = correct_date(from_date) + datetime.timedelta(minutes=30)
    sleep_stime = t
    endtime = max(timeset)
    while t < endtime:
        plotkeys.append(t)
        t = t + z


    sleep_svec = []
    sleep_evec = []


    sleep_thresh = datetime.timedelta(hours=3)
    for t in plotkeys:
        t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
        t_day = "%s-%s-%s" %(t.year, t.month, t.day)

        if plotmap.has_key(t_idx):
            plotvals.append(plotmap[t_idx])
            sleep_length = t - sleep_stime
            if sleep_length > sleep_thresh and sleep_stime.hour < 12:
                tempresponse.write("start: " + str(sleep_stime) + " and length: " + str(sleep_length) + "\n")
                sleep_svec.append(sleep_stime)
                sleep_evec.append(t - z)
            sleep_stime = t + z

        else:
            plotvals.append(0)



    day_num = len(sleep_svec)


    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
    ax = fig.add_axes(ax_size)





    midpoints = []
    for i in range(0, day_num):
        thisplot_x = [sleep_svec[i].hour, sleep_evec[i].hour]
        thisplot_mid = thisplot_x[0] + (thisplot_x[1] - thisplot_x[0])/2
        midpoints.append(thisplot_mid)

        thisplot_y = [day_num - i, day_num- i]
        tempresponse.write(str(thisplot_x) + ": " + str(thisplot_y) + "\n")
        tempresponse.write(str(thisplot_mid) + ": " + str(thisplot_y) + "\n")
        ax.plot(thisplot_x, thisplot_y, 'b-', lw=4, ms=10, alpha=0.7, mfc='orange')



    midys = range(1, day_num + 1)
    midys.reverse()
    ax.plot(midpoints, midys, 'r-', lw=2, ms=10, alpha=0.7,)


    #return tempresponse


    ax.set_ylabel("Day")
    ax.set_xlabel("Hour of day")
    #ax.grid(True)
    #ax.grid(True, which='minor')


    ax.set_xlim(0, 23)
    ax.set_ylim(0, day_num + 1)




    #fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def screen_events(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    #COMEBACK



    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'screen')

    plotvals = []
    plotkeys = []
    plotmap = {}

    timeset = set()

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        t = e.dt_record
        timeset.add(t)
        if data["status"] == "ON":
            t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
            if t_idx not in plotmap.keys():
                plotmap[t_idx] = 1
            else:
                plotmap[t_idx] += 1


    z = datetime.timedelta(hours=1)
    t = correct_date(from_date) + datetime.timedelta(minutes=30)
    sleep_stime = t
    endtime = max(timeset)
    while t < endtime:
        plotkeys.append(t)
        t = t + z



    #for t in plotkeys:
    #    t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
    #    if plotmap.has_key(t_idx):
    #        plotvals.append(plotmap[t_idx])
    #    else:
    #        plotvals.append(0)


    sleep_svec = []
    sleep_evec = []
    sleep_srange = set([21, 22, 23, 0, 1, 2, 3, 4, 5, 6])


    sleep_thresh = datetime.timedelta(hours=3)
    for t in plotkeys:
        t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
        t_day = "%s-%s-%s" %(t.year, t.month, t.day)

        if plotmap.has_key(t_idx):
            plotvals.append(plotmap[t_idx])
            sleep_length = t - sleep_stime
            if sleep_length > sleep_thresh  and sleep_stime.hour in sleep_srange:
                sleep_svec.append(sleep_stime)
                sleep_evec.append(t - z)
            sleep_stime = t + z

        else:
            plotvals.append(0)








    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)




    ax.plot_date(plotkeys, plotvals, lw=2, ms=10, alpha=0.7, mfc='green')
    ax.plot_date(plotkeys, plotvals, 'g-', lw=2, ms=10, alpha=0.7, mfc='orange')

    day_num = len(sleep_svec)
    for i in range(0, day_num):
        thisplot_x = [sleep_svec[i], sleep_evec[i]]
        thisplot_mid = [sleep_svec[i] + (sleep_evec[i] -
            sleep_svec[i])/2]

        thisplot_y = [max(plotvals), max(plotvals)]
        ax.plot_date(thisplot_x, thisplot_y, 'r-', lw=4, ms=10, alpha=0.7, mfc='orange')
        ax.plot_date(thisplot_mid, thisplot_y[0], lw=2, ms=6, alpha=0.7, mfc='black')





    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max(plotvals) + 2)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Number of Interactions")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)
    canvas.print_png(response)

    return response




#def metrics(request, imei, fdate, tdate):
#    response = HttpResponse(mimetype='text/plain')
#
#
#    from_date = _date(fdate)
#    to_date = _date(tdate)
#
#    imei = imei.upper()
#
#    if imei in mobisys_users:
#        q = MOBISYS.objects.filter(imei__exact=imei)
#    elif imei in fast_users:
#        q = SS.objects.filter(imei__exact=imei)
#    elif imei in hs_users:
#        q = HS.objects.filter(imei__exact=imei)
#    elif imei in gin_users:
#        q = GIN.objects.filter(imei__exact=imei)
#    elif imei in sleep_users:
#        q = SleepSens.objects.filter(imei__exact=imei)
#    else:
#        q = SystemSens.objects.filter(imei__exact=imei)
#
#
#    q = q.filter(dt_record__gte=from_date)
#    q = q.filter(dt_record__lte=to_date)
#    q = q.filter(Q(data_type = 'battery') | Q(data_type = 'screen'))
#    q = q.order_by('dt_record')
#
#
#    firstRec = True
#    INTERVAL = 10
#    LONG = 5
#
#    tempList = []
#    screenmap = {}
#    chargemap = {}
#    levelmap = {}
#
#
#
#
#    for e in q.all():
#        record = simplejson.loads(e.message)
#        data = record["data"]
#        dtype = record['type']
#
#        t = e.dt_record
#        t_idx = "%s-%s-%s %s:00:00" %(t.year, t.month, t.day, t.hour)
#
#
#
#        if dtype == 'battery':
#            value = data["level"]
#            #value = data["voltage"]
#            ts = record["time_stamp"]
#            status = data["status"]
#
#
#            if t_idx in levelmap.keys():
#                levelmap[t_idx].append(value)
#            else:
#                levelmap[t_idx] = [value]
#
#            #response.write('battery ' + str(value) + '\n')
#
#
#
#        if dtype == 'screen':
#            if data["status"] == "ON":
#                if t_idx in screenmap.keys():
#                    screenmap[t_idx] += 1
#                    #response.write('screen: ' + str(lastValue) + '\n')
#                else:
#                    # A new hour
#                    screenmap[t_idx] = 1
#
#    c = q.all()[0].dt_record
#    endtime = q.all()[q.count() - 1].dt_record
#    h = datetime.timedelta(hours=1)
#
#    header = 'Date, Screen, ChargeRate, Level'
#    response.write(header + '\n')
#
#    while c < endtime:
#        idx = "%s-%s-%s %s:00:00" %(c.year, c.month, c.day, c.hour)
#        if idx in screenmap.keys():
#            screen = str(screenmap[idx])
#        else:
#            screen = '0'
#
#        if idx in levelmap.keys():
#            l = levelmap[idx]
#            d = len(l)
#            level = str(mean(l))
#            charge = str(l[d-1] - l[0])
#        else:
#            charge = 'NA'
#            level = 'NA'
#
#
#        response.write(str(idx)
#                + ', ' + screen
#                + ', ' + charge + ', ' + level
#                + '\n')
#
#        c = c + h
#
#
#
#
#
#    return response
#

def battery_data(request, imei, fdate, tdate):
    response = HttpResponse(mimetype='text')

    from_date = _date(fdate)
    to_date = _date(tdate)
    cur_status = True

    cur_level = 100
    cur_time = 'default'

    off = True
    incall = False
    flush = False

    cpuList = []
    memList = []

    curcrx = curctx = curwrx = curwtx = 0
    curdisc = screenCount = screenTime = curcall = 0
    curaccel = curaudio = curgps = curscan = 0

    paccel = paudiotime = pgps = pscan = 0
    pcrx = pctx = pwrx = pwtx = 0


    header = "user, time, level, charging, cpu, mem, ctx, crx, wrx, wtx, disconnect, events, screen, call, accel, audio, gps, scan\n"
    response.write(header)

    q = _query(imei, from_date, to_date)
    for e in q.all():
        record = simplejson.loads(e.message)
        mytype = record['type']
        data = record['data']
        timestamp = str(e.dt_record)


        ##
        # Resources
        ##

        if mytype == "cpu":
            if data.has_key('cpu'):
                cpu = data['cpu']
                if cpu.has_key('total'):
                    cpuList.append(cpu['total'])

        if mytype == "meminfo":
            if data.has_key('Active:'):
                memList.append(int(data['Active:']))

        if mytype == "netiflog":
            crx = data["MobileRxBytes"]
            ctx = data["MobileTxBytes"]
            wrx = (data["TotalRxBytes"] - crx)
            wtx = (data["TotalTxBytes"] - ctx)

            if crx > pcrx:
                curcrx += (crx - pcrx)
            if ctx > pctx:
                curctx += (ctx - pctx)
            if wrx > pwrx:
                curwrx += (wrx - pwrx)
            if wtx > pctx:
                curwtx += (wtx - pwtx)
            pcrx = crx
            pctx = ctx
            pwrx = wrx
            pwtx = wtx

        if mytype == 'dataconnection':
            network = data['network']
            if network.find('mobile') != -1:
                state = data['state']
                if state == 'disconnected':
                    curdisc += 1

        if mytype == "screen":
            if data["status"] == "ON" and off:
                laston = record["time_stamp"]
                off = False
                screenCount += 1
            elif data["status"] == "OFF" and not off:
                screenInterval = ((record["time_stamp"] - laston)/1000.0)
                screenTime += screenInterval
                off = True


        if mytype == "call":
            if data["state"] == "started" and not incall:
                callstart = record["time_stamp"]
                incall = True
            elif data["state"] == "ended" and incall:
                callLen = ((record["time_stamp"] - callstart)/1000.0)
                curcall += callLen
                incall = False

        ##
        # Adaptive Apps
        ##

        if mytype == "AccelService":
            accel = data["Accel"]
            if accel > paccel:
                curaccel += (accel - paccel)
            paccel = accel



        if mytype == "AcousticApp":
            if (data.has_key("acoustictime")):
                audiotime = data["acoustictime"]*1.0
                if audiotime > paudiotime:
                    curaudio += (audiotime - paudiotime)

                #response.write("audio: " + str(audiotime) + ", paudio: " + str(paudiotime) + " curaudio: " + str(curaudio) + "\n")
                paudiotime = audiotime


        #if mytype == "LocationTracker":

        #    response.write(str(imei) + " (" + mytype + ") " + str(data) + "\n")
        #    gps = data["gpstime"]

        #    if gps > pgps:
        #        curgps += (gps - pgps)
        #    pgps = gps

        if mytype == "WiFiGPSLocation":

            if data.has_key('gpstime'):
                gps = data["gpstime"]
                scan = data["wifiscan"]
            elif data.has_key("GPS"):
                gps = data["GPS"]
                scan = data["WiFiScan"]


            if gps > pgps:
                curgps += (gps - pgps)
                curscan += (scan - pscan)
            pgps = gps
            pscan = scan



        if mytype == "battery":
            status = data['status']
            level = data["level"]
            temperature = eval(data["temperture"])
            voltage = data["voltage"]
            if data.has_key('current'):
                current = data["current"]
            else:
                current = 0




            if status.find("Not") > -1 or status.find("Discharging") > -1:
                charging = False
            else:
                charging = True

            if charging != cur_status and not level == cur_level:
                flush = True
                curlevel = level
                #response.write(str(e.imei) + ", " + timestamp + ", " + str(level) + ", " + str(charging) + "\n")
                cur_status = charging
            elif (level - cur_level) > 10 and not charging:
                flush
                curlevel = cur_level
                #response.write(str(e.imei) + ", " + timestamp + ", " + str(cur_level) + ", " + str(charging) + "\n")



            if flush:
                flush = False

                avgcpu = mean(cpuList)
                avgmem = mean(memList)


                response.write("\"%s\", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" %( imei, timestamp, level, charging, avgcpu, avgmem, curctx, curcrx, curwrx, curwtx, curdisc, screenCount, screenTime, curcall, curaccel, curaudio, curgps, curscan))
                cpuList = []
                memList = []

                curcrx = curctx = curwrx = curwtx = 0
                curdisc = screenCount = screenTime = curcall = 0
                curaccel = curaudio = curgps = curscan = 0


            cur_level = level
            cur_time = timestamp


    return response




@login_required
def battery_level(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')



    #return HttpResponse(str(_date(tdate)))

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        plotkeys.append(e.dt_record)
        plotvals.append(data["level"])








    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=2, ms=3)#, alpha=0.7, mfc='orange')
    #ax.plot_date(plotkeys, plotvals, color='b', ls='-', marker='None', lw=2)


    dlines = Deadline.objects.filter(imei__exact=imei)
    dlines = dlines.filter(set_date__gte = from_date).order_by('set_date')


#    if dlines.count() > 0:
#        d = dlines.all()[dlines.count() - 1]
#        dl = d.level
#        ds = d.set_date
#        de = d.deadline
#        ax.plot_date([ds, de], [dl, 0L], color='r', ls='-', marker='None', lw=2)

    tempresp =  HttpResponse(mimetype='text')

    times = []
    levels = []

    for d in dlines.all():
        dl = d.level
        ds = d.set_date
        de = d.deadline

        tempresp.write("[" + str(dl) + "]: " + str(ds) + " --> " + str(de) + "\n")

        #tempresp.write("times[]: " + str(times) + "\n")

        #last = len(times) - 1
        #if last > 0:
        #    lasttime = times[last]
        #    lastlevel = levels[last]

        #    if lasttime > ds:

        #        starttime = times[last-1]
        #        startlevel = levels[last-1]

        #        delta = lasttime - starttime
        #        slope = startlevel * 1.0/delta.seconds

        #        newdelta = ds - starttime

        #        newlevel = startlevel - slope*newdelta.seconds


        #        times[last] = ds
        #        levels[last] = newlevel




        #        #tempresp.write("slope:" +  str(slope) + " ")
        #        #tempresp.write(str(times[0]) + "[ " + str(levels[0]) + "] -> " + str(times[1]) + "[" + str(levels[1]) + "] \n")




        #times = [ds, de]
        #levels = [dl, 0L]


        times = [ds, de]
        levels = [dl, 0l]
        ax.plot_date(times, levels, color='r', ls='-.', marker='None', lw=2)


    #ax.plot_date(times, levels, color='r', ls='-.', marker='None', lw=2)
    #return tempresp







    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)
    ax.xaxis.labelpad = 1
    #ax.xtick.major.pad = 5


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, 105)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Level %")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response

@login_required
def battery_temp(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]

        plotkeys.append(e.dt_record)
        plotvals.append(data["temperture"])



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)

    ax = fig.add_axes(ax_size)




    ax.plot_date(plotkeys, plotvals, lw=2, ms=4, ls='-')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)

    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Temperature (C)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response

@login_required
def battery_current(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        if data["status"] == "Discharging":
            plotkeys.append(e.dt_record)
            plotvals.append(-1 * data["current"]/1000.0)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=2, ms=4, ls='-')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)

    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    #ax.set_ylim(0, max(plotvals) + 100)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Current (mA)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def battery_volt(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        plotkeys.append(e.dt_record)
        plotvals.append(data["voltage"]/1000.0)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=2, ms=4, ls='-')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)

    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Voltage (V)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response


@login_required
def battery_power(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        if data["status"] == "Discharging":
            plotkeys.append(e.dt_record)
            current = -1 * data["current"]/1000.0
            voltage = data["voltage"]/1000.0
            plotvals.append(current * voltage)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=2, ms=4, ls='-', color='b')

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)

    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max(plotvals) + 100)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Power (mW)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response




@login_required
def accelservice(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    imei = request.user.profile.imei

    myres = HttpResponse()

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'AccelService')


    accell = []
    plotkeys = []

    paccel = 0

    firstTime = True

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key("Accel")):
            accel = data["Accel"]
        elif data.has_key("accel"):
            accel = data["accel"]


            if not firstTime and paccel < accel:
                ts_diff = ts - pts
                plotkeys.append(correct_date(record["date"]))
                if ts_diff < 10 * ONE_MINUTE:
                    accell.append((accel - paccel)/2.0)
                else:
                    accell[len(accell) - 1] = 0.0
                    accell.append(0.0)

            paccel = accel
            pts = ts

            firstTime = False



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, accell, 'r-', lw=2, ms=4,)

    ax.plot_date(plotkeys, accell, lw=2, ms=3, alpha=0.7, mfc='red')




    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    maxy = max(accell)*1.5
    #ax.set_ylim(0, 600)
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Samples per Minute")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Accelerometer'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response


@login_required
def resource(request, appname, resname, fdate, tdate):

    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    myres = HttpResponse()

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, appname)


    resl = []
    plotkeys = []

    bit = False
    tempvals = []

    pres =  0

    firstTime = True


    for e in q.all():
        record = simplejson.loads(e.message)
        date = record["date"]
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key(resname)):
            res = data[resname]*1.0


            if not firstTime:
                ts_diff = ts - pts
                minute_diff = (1.0*ts_diff)/(1000*60)
                if minute_diff == 0:
                    continue

                plotkeys.append(correct_date(record["date"]))
                tempvals.append(minute_diff)
                if minute_diff < 10 :
                    resl.append((res - pres)/minute_diff)

                else:
                    resl[len(resl) - 1] = 0.0
                    resl.append((res - pres)/minute_diff)


            pres = res
            pts = ts

            firstTime = False
            bit = bit ^ True



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)




    ax.plot_date(plotkeys, resl, 'b-', lw=2, ms=4,)




    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    #maxy = max(max(gpsl), max(wifil))*1.5
    maxy = max(resl)*1.5
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Units per Minute")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend([resname])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response


@login_required
def audio(request, fdate, tdate):
    imei = request.user.profile.imei
    response = HttpResponse(mimetype='image/png')

    myres = HttpResponse()

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'AcousticApp')


    timel = []
    countl = []
    plotkeys = []

    bit = False
    tempvals = []

    ptime =  0

    firstTime = True


    temp_res = HttpResponse()

    for e in q.all():
        record = simplejson.loads(e.message)
        date = record["date"]
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key("acoustictime")):
            audiotime = data["acoustictime"]*1.0


            if not firstTime:
                newVal = (audiotime - ptime)/2
                if newVal < 60:
                    timel.append(newVal)
                    plotkeys.append(correct_date(record["date"]))

            ptime = audiotime

            firstTime = False



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, timel, 'b-', lw=3, ms=4,)




    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    maxy = max(max(timel)*1.5, 1)
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Seconds per Minute")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Audio'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response







@login_required
def gps(request, fdate, tdate):
    imei = request.user.profile.imei
    response = HttpResponse(mimetype='image/png')

    myres = HttpResponse()

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'WiFiGPSLocation')
    #q = _query(imei, from_date, to_date, 'LocationTracker')


    timel = []
    countl = []
    plotkeys = []

    bit = False
    tempvals = []

    ptime = pcount = 0

    firstTime = True


    temp_res = HttpResponse()

    for e in q.all():
        record = simplejson.loads(e.message)
        date = record["date"]
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key("gpstime")):
            if data.has_key('gpstime'):
                gpstime = data["gpstime"]*1.0
            elif data.has_key("GPS"):
                gpstime = data["GPS"]*1.0


            gpstime = data["gpstime"]*1.0
            #gpscount = data["gpscount"]*1.0


            if not firstTime:
                temp_res.write(date + ": " + str(gpstime) + "<br>")
                newVal = (gpstime - ptime)/2
                if newVal < 10:
                    timel.append(newVal)
                    plotkeys.append(correct_date(record["date"]))
                #countl[len(countl) - 1] = 0.0
                #countl.append((gpscount - pcount)/minute_diff)

            ptime = gpstime
            #pcount = gpscount

            firstTime = False


    #return temp_res

    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





#    ax.plot_date(plotkeys, gpsl, color='b', lw=2, ms=8,)
#    ax.plot_date(plotkeys, wifil, color='r', lw=2, ms=8,)
#    ax.plot_date(plotkeys, tempvals, 'g-', lw=2, ms=4,)

    ax.plot_date(plotkeys, timel, 'b-', lw=2, ms=4,)

    ax.plot_date(plotkeys, timel, lw=2, ms=3, alpha=0.7, mfc='black')
#    ax.plot_date(plotkeys, countl, 'r-', lw=2, ms=4,)




    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    #maxy = max(max(gpsl), max(wifil))*1.5
    maxy = max(max(timel)*1.5, 1)
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Seconds per Minute")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

#    ax.legend(['GPS', 'WiFiScan'])
    ax.legend(['GPS'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response



@login_required
def net_packets(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'netiflog')


    cellrxl = []
    celltxl = []
    wifirxl = []
    wifitxl = []
    plotkeys = []

    firstTime = True

    pcellrx = pcelltx = pwifirx = pwifitx = 0

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key("MobileRxPackets")):
            cellrx = data["MobileRxPackets"]
            celltx = data["MobileTxPackets"]
            wifirx = data["TotalRxPackets"] - cellrx
            wifitx = data["TotalTxPackets"] - celltx

            crx = (cellrx - pcellrx)
            ctx = (celltx - pcelltx)
            wrx = (wifirx - pwifirx)
            wtx = (wifitx - pwifitx)

            if not firstTime:
                ts_diff = ts - pts
                plotkeys.append(e.dt_record)
                if ts_diff < 10 * ONE_MINUTE:
                    cellrxl.append(crx)
                    celltxl.append(ctx)
                    wifirxl.append(wrx)
                    wifitxl.append(wtx)
                else:
                    cellrxl[len(cellrxl) - 1] = 0.0
                    cellrxl.append(0)

                    celltxl[len(celltxl) - 1] = 0.0
                    celltxl.append(0)

                    wifirxl[len(wifirxl) - 1] = 0.0
                    wifirxl.append(0)

                    wifitxl[len(wifitxl) - 1] = 0.0
                    wifitxl.append(0)


            pcellrx = cellrx
            pcelltx = celltx
            pwifirx = wifirx
            pwifitx = wifitx
            pts = ts
            firstTime = False



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)



    maxy = max(max(celltxl), max(cellrxl), max(wifirxl), max(wifitxl))*1.5
    #maxy = 1500


    ax.plot_date(plotkeys, celltxl, 'b-', lw=2, ms=4,)
    ax.plot_date(plotkeys, cellrxl, 'r-', lw=2, ms=4,)
    ax.plot_date(plotkeys, wifitxl, 'g-', lw=2, ms=4,)
    ax.plot_date(plotkeys, wifirxl, 'y-', lw=2, ms=4,)


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("# Packets")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Cell Tx', 'Cell Rx', 'WiFi Tx', 'WiFi Rx'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response


def cell_signal(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'signal')


    signall = []
    biterrorl = []

    plotkeys = []


    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        ts = record["time_stamp"]
        if (data.has_key("signal")):
            signall.append(data["signal"])
            biterrorl.append(data["biterror"])

            plotkeys.append(e.dt_record)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)



    maxy = max(max(signall), max(biterrorl))*1.5
    miny = min(min(signall), min(biterrorl)) - 2
    #maxy = 1500


    ax.plot_date(plotkeys, signall, 'b-', lw=1, ms=4,)
    ax.plot_date(plotkeys, biterrorl, 'r-', lw=3, ms=4,)

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(miny, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("ASU")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Cell Signal', 'Cell Bit Error'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response






@login_required
def net_bytes(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')
    tempresponse = HttpResponse(mimetype='text')

    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'netiflog')

#    if q.count() == 0:
#        return HttpResponseRedirect( reverse('visualization.views.netdev_bytes', args=(imei, fdate, tdate)))
#


    cellrxl = []
    celltxl = []
    wifirxl = []
    wifitxl = []
    plotkeys = []

    pcellrx = pcelltx = pwifirx = pwifitx = 0

    firstTime = True


    cumulative = True

    if cumulative:
        for e in q.all():
            record = simplejson.loads(e.message)
            data = record["data"]
            ts = record["time_stamp"]
            if (data.has_key("MobileRxBytes")):
                cellrx = data["MobileRxBytes"]
                celltx = data["MobileTxBytes"]
                wifirx = data["TotalRxBytes"] - cellrx
                wifitx = data["TotalTxBytes"] - celltx


                if firstTime:
                    pcellrx = cellrx
                    pcelltx = celltx
                    pwifirx = wifirx
                    pwifitx = wifitx
                else:
                    plotkeys.append(e.dt_record)

                    crx = (cellrx - pcellrx)/(1024*1024.0)
                    ctx = (celltx - pcelltx)/(1024*1024.0)
                    wrx = (wifirx - pwifirx)/(1024*1024.0)
                    wtx = (wifitx - pwifitx)/(1024*1024.0)
                    cellrxl.append(crx)
                    celltxl.append(ctx)
                    wifirxl.append(wrx)
                    wifitxl.append(wtx)

                    tempresponse.write(str(e.dt_record) + ": " + str(ctx) + "\n")

                firstTime = False
                pts = ts
#        else:
#            for e in q.all():
#                record = simplejson.loads(e.message)
#                data = record["data"]
#                ts = record["time_stamp"]
#                if (data.has_key("MobileRxBytes")):
#                    cellrx = data["MobileRxBytes"]
#                    celltx = data["MobileTxBytes"]
#                    wifirx = data["TotalRxBytes"] - cellrx
#                    wifitx = data["TotalTxBytes"] - celltx
#
#                    crx = (cellrx - pcellrx)/(1024)
#                    ctx = (celltx - pcelltx)/(1024)
#                    wrx = (wifirx - pwifirx)/(1024)
#                    wtx = (wifitx - pwifitx)/(1024)
#
#
#                    if not firstTime:
#                        time_delta = ts - pts
#                        plotkeys.append(e.dt_record)
#                        if time_delta < 10*ONE_MINUTE:
#                            cellrxl.append(crx)
#                            celltxl.append(ctx)
#                            wifirxl.append(wrx)
#                            wifitxl.append(wtx)
#                        else:
#                            cellrxl[len(cellrxl) - 1] = 0.0
#                            cellrxl.append(0)
#
#                            celltxl[len(celltxl) - 1] = 0.0
#                            celltxl.append(0)
#
#                            wifirxl[len(wifirxl) - 1] = 0.0
#                            wifirxl.append(0)
#
#                            wifitxl[len(wifitxl) - 1] = 0.0
#                            wifitxl.append(0)
#
#
#
#                    pcellrx = cellrx
#                    pcelltx = celltx
#                    pwifirx = wifirx
#                    pwifitx = wifitx
#
#                    firstTime = False
#                    pts = ts

    #return tempresponse

    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)



    maxy = max(max(celltxl), max(cellrxl), max(wifirxl), max(wifitxl))*1.5
    #maxy = 1500


    ax.plot_date(plotkeys, celltxl, 'b-', lw=2, ms=4,)
    ax.plot_date(plotkeys, cellrxl, 'r-', lw=2, ms=4,)
    ax.plot_date(plotkeys, wifitxl, 'g-', lw=2, ms=4,)
    ax.plot_date(plotkeys, wifirxl, 'y-', lw=2, ms=4,)


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, maxy)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("KB")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Cell Tx', 'Cell Rx', 'WiFi Tx', 'WiFi Rx'])

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response



@login_required
def net_app(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'netlog')



    first = simplejson.loads(q.all()[0].message)['data']
    last = simplejson.loads(q.all()[q.count() - 1].message)['data']




    rxVal = {}
    txVal = {}

    for app in last.keys():
        if first.has_key(app):
            lastRec = last[app]
            firstRec = first[app]
            rxVal[app] = (lastRec['Rx'] - firstRec['Rx'])/1024.0
            txVal[app] = (lastRec['Tx'] - firstRec['Tx'])/1024.0

    appList = list()
    txList = list()
    rxList = list()


    for app in sorted(txVal, key=txVal.get, reverse=True):
        rxList.append(rxVal[app])
        txList.append(txVal[app])
        appName = app.split('.')[-1]
        appList.append(appName)


    ind = numpy.arange(len(appList))
    width = 0.45






    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.bar(ind, txList, width, color='r')
    #ax.bar(ind + width, rxList, width, color='y')


    ax.xaxis.set_ticks(ind+width)
    ax.xaxis.set_ticklabels(appList)
    ax.set_xlabel("Application")
    fig.autofmt_xdate(bottom=0.35, rotation=90)


    ax.set_ylim(0, 1.2*max(txList))
    ax.set_ylabel("Transmission (KB)")


    #fig.autofmt_xdate(bottom=0.25, rotation=90)




    canvas.print_png(response)

    return response





@login_required
def net_state(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'dataconnection')


    plotmap = {}

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        network = data['network']
        if network.find('mobile') == -1:
            continue


        t = e.dt_record
        t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)

        state = data['state']
        if state == 'disconnected':
            if t_idx not in plotmap.keys():
                plotmap[t_idx] = 1
            else:
                plotmap[t_idx] += 1


    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)






    plotkeys = []
    plotvals = []


    z = datetime.timedelta(hours=1)
    t = correct_date(from_date) + datetime.timedelta(minutes=30)
    while t < correct_date(to_date):
        plotkeys.append(t)
        t = t + z



    for t in plotkeys:
        t_idx = "%s-%s-%s %s:30:30" %(t.year, t.month, t.day, t.hour)
        if plotmap.has_key(t_idx):
            plotvals.append(plotmap[t_idx])
        else:
            plotvals.append(0)


    ax.plot_date(plotkeys, plotvals, lw=2, ms=12, alpha=0.7, mfc='red')
    ax.plot_date(plotkeys, plotvals, 'r-', lw=2, ms=12, alpha=0.7, mfc='red')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max(plotvals) + 2)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Number of Disconnections")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)
    canvas.print_png(response)

    return response






@login_required
def netstate(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'dataconnection')


    keyMap = {}
    valMap = {}

    connectedkeys = []
    disconnectedkeys = []
    connected = []
    disconnected = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        network = data['network']
        if network.find('mobile') == -1:
            continue

        state = data['state']
#        if state == 'connected':
#            value = 1.5
        if state == 'disconnected':
            value = 0.5
        else:
            value = 1.5

        if keyMap.has_key(network):
            keyMap[network].append(correct_date(record["date"]))
            valMap[network].append(value)
        else:
            keyMap[network] = [correct_date(record["date"])]
            valMap[network] = [value]





    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)




    colors = ['b', 'r', 'g', 'y', 'c']
    circles = []

    count = 0
    for key in keyMap.keys():
        ax.plot_date(keyMap[key], valMap[key], ms=6, color=colors[count])
        circles.append(Circle((0, 0), 0, fc=colors[count]))
        count += 1

#    ax.plot_date(disconnectedkeys, disconnected, lw=0, ms=3, color='red', alpha=0.7)


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    pos = [0.5, 1.5]
    stateList = ['Disconnected', 'Connected']
    ax.yaxis.set_ticks(pos)
    ax.yaxis.set_ticklabels(stateList)



    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, 2.5)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    #ax.set_ylabel("state")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)
    ax.legend(circles, keyMap.keys())


    canvas.print_png(response)

    return response






@login_required
def wifi_scan(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'wifiscan')


    plotvals = []
    plotkeys = []
    wifiset = {}

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        for wifi in data.keys():
            if wifiset.has_key(wifi):
                wifiset[wifi] += 1
            else:
                wifiset[wifi] = 1

    wifimap = {}
    for i, v in enumerate(sorted(wifiset)):
        wifimap[v] = i

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        #t = correct_date(record["date"])
        t = e.dt_record
        for wifi in data.keys():
            plotkeys.append(t)
            plotvals.append(wifimap[wifi])



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, plotvals, lw=0, ms=3, color='blue', alpha=0.7)
    #, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("WiFi APs ID")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response



def matches(key, l):

    for i in l:
        if key.find(i) != -1:
            return True

    return False

@login_required
def apps(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'activitylog')

    from_date =  correct_date(from_date)
    to_date =  correct_date(to_date)


    starttime = {}
    stoptime = {}
    y = {}
    laststart = {}
    inApp = {}
    appId = {}
    idCounter = 1


    myres = HttpResponse( q.count())



    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        #t = correct_date(record["date"])

        if len(data.keys()) < 1:
            continue

        for key in data.keys():
            ts = int(key)/1000000000
            t = time_datetime(time.localtime(ts))
            if (t < from_date) or (t > to_date):
                continue
            if "Event" in data[key]:
                ev = data[key].get("Event")
            else:
                ev = data[key].get("event")
            if "Activity" in data[key]:
                app = data[key].get("Activity").split('/')[0]
            else:
                app = data[key].get("activity").split('/')[0]

            #myres.write("<br> " + app + ": " + str(ts) + "-" + str(t) )

            if not starttime.has_key(app):
                starttime[app] = list()
                stoptime[app] = list()
                appId[app] = idCounter;
                idCounter += 1

            if matches(ev, ['resume', 'start', 'create']):
                starttime[app].append(t)

            if matches(ev, ['pause', 'stop', 'destroy']):
                stoptime[app].append(t)

    for app in appId.keys():
        myres.write("<br>::::"+  app
                + "-->" + str(starttime[app])
                )



    fig = Figure(figsize=(13,4), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
#    ax = fig.add_axes(ax_size)





    for app in appId.keys():
        startlist = list()
        stoplist = list()

        startlist.extend(starttime[app])
        stoplist.extend(stoptime[app])
        startlist.sort()
        stoplist.sort()

        minlen = min(len(startlist), len(stoplist))

        if minlen > 0:
            y = list()
            for i in range(0, minlen):
                y.append(appId[app])

            #ax.hlines(y, startlist[0:minlen], stoplist[0:minlen], lw=4)

            ax.plot_date(startlist[0:minlen], y, lw=2, ms=4)#, alpha=0.7, mfc='orange')
            ax.plot_date(stoplist[0:minlen], y, lw=2, ms=4)#, alpha=0.7, mfc='orange')



    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(from_date, to_date)
    #ax.set_xlim(min(datelist), max(datelist))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    pos = list()
    appList = list()
    for app in sorted(appId):
        appName = app.split('.')[-1]
        pos.append(appId[app])
        appList.append(appName)


    ax.yaxis.set_ticks(pos)
    ax.yaxis.set_ticklabels(appList)
    ax.set_ylabel("Application")
    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def calls(request, imei, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'call')


    outgoingstart = []
    outgoingend = []
    y = []
    inCall = False

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        t = correct_date(record["date"])

        if data["state"] == 'started':
            inCall = True
            laststart = t

        if data["state"] == 'ended' and inCall:
            outgoingstart.append(laststart)
            outgoingend.append(t)
            y.append(1)



    myres = HttpResponse()
    myres.write("xmin" + str(len(outgoingstart)))
    myres.write("xmax" + str(len(outgoingend)))

    #return myres


    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    #ax.hlines(y, outgoingstart, outgoingend, lw=4)
    #ax.plot_date(plotkeys, plotvals, lw=2, ms=4)#, alpha=0.7, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Call")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response




@login_required
def mem_usage(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'meminfo')


    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        if (data.has_key("MemTotal:")):
            plotkeys.append(e.dt_record)
            #plotvals.append((int(data["MemTotal:"]) - int(data["MemFree:"]))/1024)
            #plotvals.append((int(data["Active:"]))/1024)
            memval = (int(data["MemTotal:"]) - int(data["MemFree:"]) + int(data["Cached:"]))/1024.0
            plotvals.append(memval)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





#    ax.plot_date(plotkeys, plotvals, lw=2, ms=4)#, alpha=0.7, mfc='orange')

    ax.plot_date(plotkeys, plotvals, color='r', ls='-', marker='None', lw=3)


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def cpu_usage(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'cpu')

    plotvals = {}
    plotkeys = {}


    allplotkeys = []
    allplotvals = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        if (data.has_key("cpu")):
            #t = correct_date(record["date"])
            t = e.dt_record
            if data["cpu"].has_key("freq"):
                freq = str(data["cpu"].get("freq"))
            else:
                freq = '0.0'

            allplotkeys.append(t)
            allplotvals.append(data["cpu"].get("total"))

            if plotkeys.has_key(freq):
                plotkeys[freq].append(t)
                plotvals[freq].append(data["cpu"].get("total"))
            else:
                plotkeys[freq] = [t]
                plotvals[freq] =  [data["cpu"].get("total")]





    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    for freq in plotkeys.keys():
        ax.plot_date(allplotkeys, allplotvals, color='b', ls='-', marker='None', lw=2)
        #ax.plot_date(plotkeys[freq], plotvals[freq], lw=2, ms=4, color=cpucolors[str(freq)])
        #mfc=cpucolor[freq])#, alpha=0.7, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, 110)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("CPU %")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')


    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response

@login_required
def app_cpu(request, fdate, tdate, app):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'appresource')

    plotkeys = []
    user = []
    system = []

    appUser = 0.0
    appSystem = 0.0

    myres = HttpResponse(mimetype='text')

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        plotkeys.append(e.dt_record)
        uTotal = 0.0
        sTotal = 0.0
        for app_item in data.keys():
            packageItems = app_item.split('.')
            appName = packageItems[len(packageItems)-1]
            if appName.find(':') > 0:
                nameList = appName.split(':')
                appName = nameList[0]

            if appName == app:
                appUser = data[app_item].get('UserCpu')
                appSystem = data[app_item].get('SystemCpu')

        user.append(appUser)
        system.append(appSystem)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, user, color='b', ls='-', marker='None', lw=2)
    ax.plot_date(plotkeys, system, color='r', ls='-', marker='None', lw=2)

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, 100)
    #ax.set_ylim(0, max([max(user), max(system)])*1.1)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("CPU %")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['User', 'System'])


    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response



@login_required
def app_net(request, fdate, tdate, app):
    response = HttpResponse(mimetype='image/png')
    tempresponse = HttpResponse(mimetype='text')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'netlog')

    rx = []
    tx = []




    myres = HttpResponse(mimetype='text')

    firstCycle = True
    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        denom = 1024.0*1024.0
        for app_item in data.keys():
            packageItems = app_item.split('.')
            appName = packageItems[len(packageItems)-1]
            if appName.find(':') > 0:
                nameList = appName.split(':')
                appName = nameList[0]


            if appName == app:
                if not firstCycle:
                    curRx = data[app_item].get('Rx')
                    curTx = data[app_item].get('Tx')
                    if curRx >= pRx:
                        rx.append(( e.dt_record, (curRx - appRx)/denom))
                        pRx = curRx
                    if curTx >= pTx:
                        tx.append(( e.dt_record, (curTx - appTx)/denom))
                        pTx = curTx


                else:
                    firstCycle = False
                    appRx = data[app_item].get('Rx')
                    appTx = data[app_item].get('Tx')
                    pRx = appRx
                    pTx = appTx



                #appRx = data[app_item].get('Rx')
                #appTx = data[app_item].get('Tx')



    #return tempresponse

    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)




    TIME, TRAFFIC = (0, 1)
    ax.plot_date([r[TIME] for r in rx], [r[TRAFFIC] for r in rx], color='b', ls='-', marker='None', lw=2)
    ax.plot_date([r[TIME] for r in tx], [r[TRAFFIC] for r in tx], color='r', ls='-', marker='None', lw=2)

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max(1, max([r[TRAFFIC] for r in rx]), max([r[TRAFFIC] for r in tx])) *1.1
                )

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("MB")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['Rx', 'Tx'])


    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response

@login_required
def app_mem(request, fdate, tdate, app):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'appresource')

    plotkeys = []
    pss = []
    private = []
    shared = []

    appPss = 0.0
    appPrivate = 0.0
    appShared = 0.0



    myres = HttpResponse(mimetype='text')

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        plotkeys.append(e.dt_record)
        pssTotal = 0.0
        privateTotal = 0.0
        for app_item in data.keys():
            packageItems = app_item.split('.')
            appName = packageItems[len(packageItems)-1]
            if appName.find(':') > 0:
                nameList = appName.split(':')
                appName = nameList[0]


            #pssTotal += data[app_item].get('TotalPss')
            #privateTotal += data[app_item].get('PrivateDirty')
            if appName == app:
                appPss = data[app_item].get('TotalPss')
                appPrivate = data[app_item].get('PrivateDirty')
                appShared = data[app_item].get('SharedDirty')


        pss.append(appPss)
        private.append(appPrivate)
        shared.append(appShared)



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





    ax.plot_date(plotkeys, pss, color='b', ls='-', marker='None', lw=2)
    ax.plot_date(plotkeys, private, color='r', ls='-', marker='None', lw=2)
#    ax.plot_date(plotkeys, shared, color='g', ls='-', marker='None', lw=2)

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max([max(pss), max(private), max(shared)])*1.2)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("# Memory Pages")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    ax.legend(['PSS', 'SharedDirty'])


    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response


def set_deadline(request, imei, fdate, tdate, curlevel):

    response = HttpResponse(mimetype='text/plain')

    setdate_ = _date(fdate)
    deadline_ = _date(tdate)
    dline = Deadline(imei=imei, set_date=setdate_, deadline=deadline_, level=curlevel)
    dline.save()

    return response




def model(request, imei):
    response = HttpResponse(mimetype='text/plain')
    powermodel = open('/home/falaki/scripts/models/'+imei+'.model', 'r')
    firstLine = True
    mymodel = {}


    for line in powermodel:
        (param, coef) = line.split(' ')
        coefficient = eval(coef)
        if firstLine:
            intercept = coefficient
            firstLine = False
            mymodel["intercept"] = coefficient
            continue

#            if coefficient > 0:
#                mymodel["intercept"] = coefficient
#            else:
#                mymodel["intercept"] = 0.0
#
#        if param == 'delta' or param == 'level' or param == 'mem':
#            continue
#

#        if coefficient < 0:
#            continue

        mymodel[param] = coefficient


    response.write(str(mymodel))

    return response


def stats(request, imei):
    response = HttpResponse(mimetype='text/plain')
    powermodel = open('/home/falaki/scripts/stats/'+imei+'.stat', 'r')
    firstLine = True
    mystat = {}


    for line in powermodel:
        items = line.rsplit(' ')
        curmean = eval(items[1])
        cursd = eval(items[3])
        param = items[0]
        mystat[param] = curmean


    response.write(str(mystat))

    return response






@login_required
def power(request, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    imei = request.user.profile.imei
    from_date = _date(fdate)
    to_date = _date(tdate)

    header = ['time', 'lat', 'lon', 'curlevel', 'level', 'charging', 'screen', 'events', 'gpstime', 'wifiscan', 'accel', 'acoustictime', 'cpu', 'mem', 'cnet', 'wnet', 'call', 'disconnect', 'delta']

    #header = ['time', 'level', 'screen', 'events', 'gpstime', 'wifiscan', 'accel', 'acoustictime', 'cpu', 'mem', 'cnet', 'wnet', 'call', 'disconnect', 'delta']


    nameMap = {
            'cpu': 'CPU',
            'mem': 'Memory',
            'screen': 'Screen',
            'events': 'Screen',
            'gpstime': 'GPS',
            'wifiscan': 'WiFi',
            'accel': 'Accelerometer',
            'acoustictime': 'Audio',
            'cnet': 'Cell',
            'wnet': 'WiFi',
            'call': 'Call',
            'disconnect': 'Connectivity',
            'delta': 'System'
            }

    orderList = [
            'System', 'Memory', 'WiFi', 'Cell', 'Connectivity',
            'CPU', 'Accelerometer',
            'Screen', 'GPS', 'Audio']

    colorMap = {
            'CPU': 'Crimson',
            'Memory': 'yellow',
            'Screen': 'blue',
            'GPS': 'Maroon',
            'Audio': 'Maroon',
            'WiFi': 'Orange',
            'Accelerometer': 'CornflowerBlue',
            'Cell': 'green',
            'WiFi': 'brown',
            'Call': 'black',
            'Connectivity': 'Coral',
            'System': 'DarkBlue'
            }

    newResponse = HttpResponse(mimetype="text/plain")

    mymodel = {}
    indexes = {}

    powermodel = open('/home/falaki/scripts/models/'+imei+'.model', 'r')
    firstLine = True


    for line in powermodel:
        (param, coef) = line.split(' ')
        coefficient = eval(coef)
#        if param == 'delta' or param == 'level' or param == 'mem':
#            continue

        if firstLine:
            intercept = coefficient
            firstLine = False
#            if coefficient > 0:
#                intercept = coefficient
#            else:
#                intercept = 0
            continue

        if coefficient > 0:
            mymodel[param] = coefficient
        for index, name in enumerate(header):
            if name == param:
                indexes[param] = index

    plotvals = {}
    powervec = []
    plotkeys = []
    basevec = []



    newResponse.write(str(mymodel) + '\n')
    newResponse.write(str(indexes) + '\n')




    deltaHour = datetime.timedelta(hours=-1)

    parseData = parse(request, imei, fdate, tdate, '60')
    records = parseData.content.split('\n')
    records.pop(0)
    for row in  records:
        fields = row.split(', ')
        totalPower = 0.0
        newResponse.write(fields[0] + ': \n')
        if len(fields[0]) > 0:
            plotkeys.append(correct_date(fields[0]) + deltaHour)
            basevec.append(0.0)
            for param in mymodel.keys():
                try:
                    val = eval(fields[indexes[param]])
                    tempPower = mymodel[param]*val
                    if tempPower > 20:
                        tempPower = 0
                    if param == 'delta':
                        tempPower += intercept #For now ignoring delta
                        tempPower = 0

                    totalPower += tempPower
                    if plotvals.has_key(nameMap[param]):
                        if len(plotvals[nameMap[param]]) == len(plotkeys):
                            plotvals[nameMap[param]][len(plotkeys)-1]+= tempPower
                        else:
                            plotvals[nameMap[param]].append(tempPower)

                    else:
                        plotvals[nameMap[param]] = [tempPower]

                    newResponse.write('    ' + param + ' ' +
                            ' (' + fields[indexes[param]] +
                            ')' +
                            str(tempPower) +
                            '\n')
                except:
                    newResponse.write("Key error" + str(sys.exc_info()))
            powervec.append(totalPower)
            newResponse.write('\n')



#    newResponse.write(str(powervec))


    tempparams = plotvals.keys()
    params = []

    for param in orderList:
        if param in tempparams:
            params.append(param)


    #params.reverse();



    fig = Figure(figsize=(13,3.5), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
#    ax = fig.add_subplot(111)
    ax = fig.add_axes(ax_size)





#    ax.plot_date(plotkeys, powervec, color='b', ls='-', marker='None', lw=3)

    pls = []
    for param in params:
        p = ax.bar(plotkeys, plotvals[param], bottom=basevec,
                color=colorMap[param], width=0.043, linewidth=0)
        pls.append(p[0])
        for i in range(0, len(plotkeys)):
            basevec[i] += plotvals[param][i]



    #return newResponse




    ax.legend(pls, params)

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    ax.set_xlim(correct_date(from_date), correct_date(to_date))
    ax.set_ylim(0, max(powervec)*1.2)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Active Discharge/Hour (%)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')


    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def index(request, detail):

    json = request.GET.has_key('json')

    now = datetime.datetime.now()
    difference1 = datetime.timedelta(days=1)
    difference2 = datetime.timedelta(days=-1)
    nextday = now + difference1;
    prevday = now + difference2;
    
    profile = None
    user1 = request.user
    try:
        profile = user1.get_profile()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user1)
    #return profile

    imei_ = profile.imei


    c = RequestContext(request, {
        'year_range': ['2013', '2011', '2012'],
        'day_range': ["%(#)02d" %{"#":i} for i in range(1, 32)],
        'hour_range': ["%(#)02d" %{"#":i} for i in range(0, 24)],
        'minute_range': ["%(#)02d" %{"#":i} for i in range(0, 60)],
        'month_range' : ['Jan', 'Feb', 'Mar', 'Apr',
            'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
            'Nov', 'Dec'],
        'imei' : imei_,
        'user' : request.user.username
        })



    if detail == 'battery':
        t = loader.get_template('battery.html')
    elif detail == 'interaction':
        t = loader.get_template('interaction.html')
    elif detail == 'network':
        t = loader.get_template('network.html')
    elif detail == 'models':
        t = loader.get_template('models.html')
        try:
            interval = request.POST['ininterval']
        except (KeyError):
            interval = '10'
        c.update({'sinterval': interval})
    else:
        t = loader.get_template('main.html')


    try:
        syear = request.POST['syear']
        eyear = request.POST['eyear']
        smonth = request.POST['smonth']
        emonth = request.POST['emonth']
        sday = request.POST['sday']
        eday = request.POST['eday']
        #if len(detail) > 1:
        shour = request.POST['shour']
        ehour = request.POST['ehour']
        sminute = request.POST['sminute']
        eminute = request.POST['eminute']
    except (KeyError):
        syear = str(now.year)
        eyear = str(nextday.year)
        emonth = datetime.datetime.strftime(nextday, "%b")
        eday = "%(#)02d" %{"#": nextday.day}
        if len(detail) > 1:
            sday = "%(#)02d" %{"#": now.day}
            smonth = datetime.datetime.strftime(now, "%b")
        else:
            sday = "%(#)02d" %{"#": prevday.day}
            smonth = datetime.datetime.strftime(prevday, "%b")

        shour = ehour = sminute = eminute = '00'


    months = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
        'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09',
        'Oct':'10', 'Nov':'11', 'Dec':'12'}

    sdate = syear + months[smonth] + sday + shour + sminute
    edate = eyear + months[emonth] + eday + ehour + eminute


    from_date = syear + "-" + months[smonth] + "-" + sday
    to_date = eyear + "-" + months[emonth] + "-" + eday


    netlocation = []

    for each in _query(imei_, from_date + " " + shour + ":" + sminute, to_date + " " + ehour + ":" + eminute, 'netlocation'):
        a = simplejson.loads(each.message)
        netlocation.append(a)

    netlocationjson = simplejson.dumps(netlocation)
    if json:
        return HttpResponse(netlocationjson, mimetype='application/javascript')

    user_query = User_Query(sdate, edate, imei_)
    c.update({'isQuerySet': True,
        'user_query': user_query,
        'cur_sday' : sday,
        'cur_eday' : eday,
        'cur_smonth' : smonth,
        'cur_emonth' : emonth,
        'cur_syear' : syear,
        'cur_eyear' : eyear,
        'cur_shour' : shour,
        'cur_ehour' : ehour,
        'cur_sminute' : sminute,
        'cur_eminute' : eminute,
        'count': _query(imei_, from_date, to_date).count(),})


    return HttpResponse(t.render(c))


def put(request):

    mydebug = open("/tmp/post-log.txt", "a")
    mydebug.write("New set \n")
    one_month = datetime.timedelta(days=30)
    return HttpResponse("put() was called!")
    try:
        data = request.POST['data']
    except (KeyError):
        mydebug.write("Bad request\n")
        return HttpResponseBadRequest()


    try:
        lines = simplejson.loads(data)
    except (ValueError):
        mydebug.write("Bad data\n")
        mydebug.write(data)
        return HttpResponseBadRequest()



    counter = 0

    if len(lines) > 0:
        line = lines[0]
        imei_ = line["user"].upper()
        table_name = check_table(imei_)
        SystemSens._meta.db_table = table_name
    else:
        mydebug.write("Zero lines in data\n")
        return HttpResponse("No records found")


    imei_ = None
    ver = None
    for line in lines:
        if line.has_key("date"):
            counter += 1
            try:
                dt_record_ = line["date"]
                data_type_ = line["type"]
                imei_ = line["user"].upper()
                ver = line["ver"]
                message_ = simplejson.dumps(line)


                r = SystemSens(imei=imei_, dt_record=dt_record_, data_type = data_type_)
                r.message = message_
                r.save()
                mydebug.write(str(counter) + ": " + dt_record_ + "\n")
            except Exception as ex:
                pass
                mydebug.write("Error handling " + str(counter) + "\n")
                mydebug.write(str(ex) + "\n")
                #mydebug.write(str(line) + "\n")



    mydebug.close()
    # update corresponding client object
    if counter > 0:
        Client.update(imei=imei_,
                      version=ver,
                      last_upload=datetime.datetime.now()
        )
    return HttpResponse("Inserted " + str(counter) + " records")


import avro_utils as avro_utils
def handle_avro_request(avro_binary, version):
    # defate the compressed avro binary to LogEntryArray, which is a python object
    obj = avro_utils.parse_binary(avro_binary)
    """ The following code is to transform the data collected by the 4.0 or higher client
        so that it conform to the data format.
    """

    for entry in obj["entries"]:
        # LogEntryArray (i.e. obj) contains various general information of the client
        # such as model name, phone number, etc.
        # we append these information to every collected entry
        for field, value in obj.items():
            if field != "entries":
                entry[field] = value

        # the "entries" field under the entry["data"] should replace the entry["data"] itself
        if "entries" in entry["data"]:
            entry["data"] = entry["data"]["entries"]

        # transform gmt_time_stamp to entry["data"] field
        entry["date"] = \
            str( datetime.datetime.fromtimestamp(
                entry["gmt_time_stamp"] / 1000.0)
            )

        # transform activitylog, servicelog
        if entry["type"] in ['activitylog', 'servicelog']:
            data = {}
            # change format from a list to dict with time_stamp as key
            for sub_entry in entry["data"]:
                data[sub_entry["time_stamp"]] = sub_entry
            entry["data"] = data

        # transform recentapps
        if entry["type"] == "recentapps":
            data = {}
            # change format from a list to dict with time_stamp as key
            for sub_entry in entry["data"]:
                data[sub_entry["taskID"]] = sub_entry
            entry["data"] = data

        # transform cpu entry
        elif entry["type"] == "cpu":
            cpu = {}
            for sub_field in ["freq", "user", "total", "system", "nice"]:
                cpu[sub_field] = entry["data"][sub_field]
            entry["data"]["cpu"] = cpu

        """ Store the transformed data """
        try:
            # point Systemsens model to the table for this IMEI
            imei_ = obj["user"].upper()
            table_name = check_table(imei_)
            SystemSens._meta.db_table = table_name
            # store to db
            r = SystemSens(
                    imei=obj["user"],
                    dt_record=datetime.datetime.fromtimestamp(
                            entry["time_stamp"] / 1000.0
                    ),
                    data_type=entry["type"])
            r.message = simplejson.dumps(entry)
            r.save()
        except:
            pass
    if len(obj["entries"]) > 0:
        Client.update(imei=obj["user"].upper(),
                      version=obj["ver"],
                      last_upload=datetime.datetime.now(),
                      model=obj["model"],
                      phone=obj["phone"])

import threading

def put_binary(request, version):
    if len(request.raw_post_data) > 0:
        # For responsiveness, we create a new thread to handle the request
        t = threading.Thread(target=handle_avro_request,
                             args=[request.raw_post_data, version])
        t.setDaemon(True)
        t.start()
        # we don't do any check here for simplicity.
        return HttpResponse("")

    return HttpResponseBadRequest()

@login_required
def comment(request, imei, fdate, tdate):

    try:
        data = request.POST['comment']
    except (KeyError):
        raise Http400

    now = datetime.datetime.now();
    submit_date_ = "%s-%s-%s %s:%s:%s" %(now.year, now.month, now.day, now.hour, now.minute, now.second)

    newcomment = comments()
    newcomment.imei = imei
    newcomment.submit_date = submit_date_
    newcomment.from_date = fdate
    newcomment.to_date = tdate
    newcomment.text = data

    newcomment.save()


    #return HttpResponseRedirect(reverse('visualization.views.index'))
    return HttpResponseRedirect("http://128.97.93.158/service/viz/")



def get(request, start, end, dtype):

    response = HttpResponse(mimetype='text/plain')


    try:
        user = request.POST['user']
        psword = request.POST['password']
    except (KeyError):
        response.write('Invalid User/Pass')
        return response


    u = authenticate(username=user, password=psword)

    if u is not None:
        imei_ = u.profile.imei
    else:
        response.write('Invalid User/Pass')
        return response



    from_date = _date(start)
    to_date = _date(end)

    data_type_ = dtype.lower()


    q_result = _query(imei_, from_date, to_date, data_type_)


    header = "user, date, type, message\n"
    response.write(header)

    count = q_result.count()

    if count < 3000:
        for i in q_result:
            line = "%s, %s, %s, %s\n" %(i.imei, i.dt_record, i.data_type, i.message)
            response.write(line)
    else:
        for i in q_result.all()[0:3000]:
            line = "%s, %s, %s, %s\n" %(i.imei, i.dt_record, i.data_type, i.message)
            response.write(line)




    return response




def mean(x):
    n = len(x)
    sum = 0.0
    for i in x:
        sum += i

    if n != 0:
        return sum/n
    else:
        return 0.0

@login_required
def parsescreenevents(request):
    response = HttpResponse(mimetype='text/csv')
    visits = simplejson.loads(request.POST['visits'])
    imei = request.user.profile.imei
    header = "date, screenstate, clusterid, visitid\n"
    response.write(header)

    status = 0
    charging = False
    off = False

    for visit in visits:
        from_date = _date(visit['sdate'])
        to_date = _date(visit['edate'])

        q = _query(imei, from_date, to_date)

        for e in q.all():
            record = simplejson.loads(e.message)
            data = record.get("data")
            ts = record.get("time_stamp")
            date = record.get("date")

            if record["type"] == "screen" and not charging:
                if data["status"] == "ON":
                    status = 1
                else:
                    status = 0

                response.write("%s, %s, %s, %s\n" %(ts, status, visit['clusterid'], visit['visitid']))

            if record["type"] == "battery":
                if status == "Charging (AC)" or data["status"] == "Charging (USB)":
                    charging = True
                else:
                    charging = False


    return response

@login_required
def getuserinfo(request):
    response = HttpResponse(mimetype='text/plain')

    imei = request.user.profile.imei
    try:
        user = User.objects.filter(profile__imei__exact=imei)[0]
    except (User.DoesNotExist):
        return response

    username = user.username

    response.write("%s,%s" %(username,imei))

    return response

def checkuser(request, imei):
    response = HttpResponse(mimetype='text/plain')

    try:
        user = User.objects.filter(profile__imei__exact=imei)[0]
    except (IndexError):
        # The user does NOT already exist in the database

        # Write formatted response and return
        response.write("STATUS: User Does Not Exist")
        return response

    # ASSERT: User DOES exist already in the database
    # Get user information from database
    username = user.username
    response.write("%s" %(username))

    return response

def newuser(request, imei, uname, passwd):
    response = HttpResponse(mimetype='text/plain')

    #TODO: validate the submitted values

    #Check if already there is an account with the given IMEI
    try:
        user = User.objects.get(profile__imei__exact=imei)

        # ERROR: User already exists in the database.
        response.write("ERROR: Another User Exists Under Same IMEI")

        return response
    except (User.MultipleObjectsReturned):
        response.write("ERROR: User Exists")
        return response

    except (User.DoesNotExist):
        # Check if account exists under desired username
        try:
            user = User.objects.get(username__exact=uname)

            # ERROR: Username already taken
            response.write("ERROR: Username Already Taken")

            return response

        except (User.DoesNotExist):
            # Now we are ready to create the new user
            newUser = User.objects.create_user(uname, '', passwd)
            newUser.save()
            Profile(user=newUser, imei=imei).save()


            response.write("STATUS: SUCCESS")
            return response


    return response

def changepass(request, uname, oldpasswd, newpasswd):
    response = HttpResponse(mimetype='text/plain')

    #TODO: validate the submitted values? (or handle this on the client-side?)
    try:
        user = User.objects.filter(username__exact=uname)[0]

        if (user.check_password(oldpasswd)):
            user.set_password(newpasswd)
            user.save()
            response.write("STATUS: OK")
        else:
            response.write("STATUS: ERROR BAD PASS")

        return response

    except (User.DoesNotExist):

        response.write("STATUS: ERROR USER_DOES_NOT_EXIST")

    return response




@login_required
def parsevisits(request):

    response = HttpResponse(mimetype='text/csv')
    visits = simplejson.loads(request.POST['visits'])
    interval = request.POST['interval']
    app = request.POST['appname']

    imei = request.user.profile.imei

    header = "date, time, level, screen, events, gps, scan, accel, cpu, mem, crx, ctx, wrx, wtx, call, disconnect, app_user_cpu, app_system_cpu, app_rx, app_tx, delta, clusterid, visitid\n"

    response.write(header)

    for visit in visits:

        from_date = _date(visit['sdate'])
        to_date = _date(visit['edate'])

        q = _query(imei, from_date, to_date)

        INTERVAL = eval(interval)*60
        LONG = 5

        callstart = 0.0

        screenTime = 0.0
        screenCount = 0
        off = True

        voltage = 0.0
        temperature = 0.0


        netDisconnect = 0

        cpuList = []
        memList = []
        levelList = []

        appRx = 0.0
        appTx = 0.0
        rx = []
        tx = []
        firstAppCycle = True

        tempList = []


        totalGps = 0.0
        totalScan = 0.0
        totalAccel = 0.0

        crx = ctx = wrx = wtx = 0.0

        appUserList = []
        appSystemList = []

        callTime = 0
        callstart = 0
        incall = False

        firstCycle = True
        firstAudio = firstAccel = firstWiFiGPS = firstNet = True
        charging = False
        disconnected = False




        for e in q.all():
            record = simplejson.loads(e.message)
            data = record.get("data")
            ts = record.get("time_stamp")
            date = record.get("date")

            pdate = correct_date(date)
            phour = pdate.hour
            pminute = pdate.minute

            phour = phour*60

            ptime = phour+pminute

            if firstCycle:
                firstCycle = False
                lastTime = ts
                continue


            delta = (ts - lastTime)/(1000.0)

            if delta >=  INTERVAL and delta <= LONG*INTERVAL:
                avgCpu = mean(cpuList)
                avgMem = mean(memList)
                avgLevel = mean(levelList)
                avgAppUser = mean(appUserList)
                avgAppSystem = mean(appSystemList)
                totalAppRx = sum(rx)
                totalAppTx = sum(tx)

                response.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" %(date, ptime, avgLevel, screenTime, screenCount, totalGps, totalScan, totalAccel, avgCpu, avgMem, crx, ctx, wrx, wtx, callTime, netDisconnect, avgAppUser, avgAppSystem, totalAppRx, totalAppTx, delta, visit['clusterid'], visit['visitid']))

                screenTime = 0.0
                screenCount = 0
                callTime = 0.0
                netDisconnect = 0
                cpuList = []
                memList = []
                levelList = []

                appUserList = []
                appSystemList = []

                appRx = 0.0
                appTx = 0.0
                rx = []
                tx = []
                firstAppCycle = True

                firstAudio = firstAccel = firstWiFiGPS = firstNet = True
                crx = ctx = wrx = wtx = 0.0
                lastTime = ts

            if delta >  LONG*INTERVAL:
                screenTime = 0.0
                screenCount = 0
                callTime = 0.0
                cpuList = []
                memList = []
                levelList = []

                appUserList = []
                appSystemList = []

                appRx = 0.0
                appTx = 0.0
                rx = []
                tx = []
                firstAppCycle = True

                firstAudio = firstAccel = firstWiFiGPS = firstNet = True
                lastTime = ts
                crx = ctx = wrx = wtx = 0.0


            if record["type"] == "battery":
                level = data["level"]
                temperature = eval(data["temperture"])
                voltage = data["voltage"]
                levelList.append(level)

#            if data["status"] == "Charging (AC)" or data["status"] == "Charging (USB)":
#                charging = True
#            else:
#                charging = False
#



            if record["type"] == "cpu" and not charging:
                if data.has_key('cpu'):
                    cpu = data['cpu']
                    if cpu.has_key('total'):
                        cpuList.append(cpu['total'])



            if record["type"] == "meminfo" and not charging:
                if data.has_key('Active:'):
                    memList.append(int(data['Active:']))


            if record["type"] == "netiflog" and not charging:
                cellrx = data["MobileRxBytes"]
                celltx = data["MobileTxBytes"]
                wifirx = data["TotalRxBytes"] - cellrx
                wifitx = data["TotalTxBytes"] - celltx

                ctxt = crxt = wtxt = wrxt = 0.0

                if not firstNet:
                    if celltx > pcelltx: ctxt = (celltx - pcelltx)/1024.0
                    if cellrx > pcellrx: crxt = (cellrx - pcellrx)/1024.0
                    if wifitx > pwifitx: wtxt = (wifitx - pwifitx)/1024.0
                    if wifirx > pwifirx: wrxt = (wifirx - pwifirx)/1024.0

                else:
                    firstNet = False
                    crx = ctx = wrx = wtx = 0.0

                ctx += ctxt
                crx += crxt
                wtx += wtxt
                wrx += wrxt

                pcelltx = celltx
                pcellrx = cellrx
                pwifitx = wifitx
                pwifirx = wifirx



            if record["type"] == "WiFiGPSLocation" and not charging:
                gpst = data["GPS"]
                wifiscant = data["WiFiScan"]

                if not firstWiFiGPS and pgps <= gpst and pwifiscan <= wifiscant:
                    newGps = (gpst - pgps)
                    newScan = (wifiscant - pwifiscan)
                    totalGps += newGps
                    totalScan += newScan
                else:
                    firstWiFiGPS = False
                    totalGps = totalScan = 0.0

                pgps = gpst
                pwifiscan = wifiscant


            if record["type"] == "AccelService" and not charging:
                accelt = data["Accel"]

                if not firstAccel and paccel < accelt:
                    newAccel = (accelt - paccel)
                    totalAccel += newAccel
                else:
                    totalAccel = 0.0
                    firstAccel = False

                paccel = accelt


            #if record["type"] == 'dataconnection' and not charging:
            #    network = data['network']
            #    if network.find('mobile') != -1:
            #        state = data['state']
            #        if state == 'disconnected' and not disconnected:
            #            disconnected = True
            #            netDisconnect += 1
            #            lastdisc = record["time_stamp"]
            #        elif state == 'connected':
            #            discInterval = ((record["time_stamp"] - lastdisc)/1000.0)
            #            disconnected = False


            if record["type"] == "screen" and not charging:
                if data["status"] == "ON" and off:
                    laston = record["time_stamp"]
                    off = False
                    screenCount += 1
                elif data["status"] == "OFF" and not off:
                    screenInterval = ((record["time_stamp"] - laston)/1000.0)
                    screenTime += screenInterval
                    off = True


            if record["type"] == "call" and not charging:
                if data["state"] == "started" and not incall:
                    callstart = record["time_stamp"]
                    incall = True
                elif data["state"] == "ended" and incall:
                    callLen = ((record["time_stamp"] - callstart)/1000.0)
                    callTime += callLen
                    incall = False

            if record["type"] == "appresource" and not charging:
                uTotal = 0.0
                sTotal = 0.0
                for app_item in data.keys():
                    packageItems = app_item.split('.')
                    appName = packageItems[len(packageItems)-1]
                    if appName.find(':') > 0:
                        nameList = appName.split(':')
                        appName = nameList[0]

                    if appName == app:
                        appUserList.append(data[app_item].get('UserCpu'))
                        appSystemList.append(data[app_item].get('SystemCpu'))

            if record["type"] == "netlog" and not charging:
                for app_item in data.keys():
                    packageItems = app_item.split('.')
                    appName = packageItems[len(packageItems)-1]
                    if appName.find(':') > 0:
                        nameList = appName.split(':')
                        appName = nameList[0]

                    if appName == app:
                        if not firstAppCycle:
                            rx_delta = (data[app_item].get('Rx') - appRx)/1024
                            tx_delta = (data[app_item].get('Tx') - appTx)/1024

                            if (rx_delta < 0):
                                rx.append(0)
                            else:
                                rx.append(rx_delta)

                            if (tx_delta < 0):
                                tx.append(0)
                            else:
                                tx.append(tx_delta)
                            #response.write("Rx difference is %s\nTx difference is %s\n" %(((data[app_item].get('Rx')-appRx)/1024), ((data[app_item].get('Tx')-appTx)/1024)))
                        else:
                            firstAppCycle = False

                        appRx = data[app_item].get('Rx')
                        #response.write("Rx is %s\n" %(appRx))
                        appTx = data[app_item].get('Tx')
                        #response.write("Tx is %s\n" %(appTx))


    return response


def parse(request, imei, fdate, tdate, interval):

    response = HttpResponse(mimetype='text/plain')

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date)

    INTERVAL = eval(interval)*60
    LONG = 5

    callstart = 0.0

    screenTime = 0.0
    screenCount = 0
    off = True

    voltage = 0.0
    temperature = 0.0


    netDisconnect = 0
    discInterval = 0.0
    disconnected = False

    cpuList = []
    memList = []
    levelList = []
    curlevel = 0


    totalGps = 0.0
    totalScan = 0.0
    totalAccel = 0.0
    totalAudio = 0.0
    lat = lon = 0.0

    crx = ctx = wrx = wtx = 0.0


    callTime = 0
    callstart = 0
    incall = False

    firstCycle = True
    firstAudio = firstAccel = firstWiFiGPS = firstNet = True
    charging = False


    header = "time, lat, lon, curlevel, level, charging, screen, events, gpstime, wifiscan, accel, acoustictime, cpu, mem, cnet, wnet, call, disconnect, delta\n"

    response.write(header)



    for e in q.all():
        record = simplejson.loads(e.message)
        data = record.get("data")
        ts = record.get("time_stamp")
        date = record.get("date")
        dtype = record['type']


        if firstCycle:
            firstCycle = False
            lastTime = ts
            continue


        delta = (ts - lastTime)/(1000.0)

        if delta >=  INTERVAL and delta <= LONG*INTERVAL:
            avgCpu = mean(cpuList)
            avgMem = mean(memList)
            #avgLevel = mean(levelList)
            if len(levelList) > 0:
                avgLevel = levelList[len(levelList) - 1] - levelList[0]
            elif len(levelList) == 1:
                avgLevel = curlevel - pcurlevel
            else:
                avgLevel = 0

            response.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" %(date, lat, lon, curlevel, avgLevel, charging, screenTime, screenCount, totalGps, totalScan, totalAccel, totalAudio, avgCpu, avgMem, crx+ctx, wrx+wtx, callTime, netDisconnect, delta))

            screenTime = 0.0
            screenCount = 0
            callTime = 0.0
            netDisconnect = 0
            cpuList = []
            memList = []
            levelList = []

            firstAudio = firstAccel = firstWiFiGPS = firstNet = True
            crx = ctx = wrx = wtx = 0.0
            lastTime = ts

        if delta >  LONG*INTERVAL:
            screenTime = 0.0
            screenCount = 0
            callTime = 0.0
            cpuList = []
            memList = []
            levelList = []
            firstAudio = firstAccel = firstWiFiGPS = firstNet = True
            lastTime = ts
            crx = ctx = wrx = wtx = 0.0


        if dtype == "battery":
            pcurlevel = curlevel
            curlevel = data["level"]
            temperature = eval(data["temperture"])
            voltage = data["voltage"]
            levelList.append(curlevel)
            status = data["status"]

            if status.find("Not") > -1 or status.find("Discharging") > -1:
                charging = False
            else:
                charging = True



        if dtype == "cpu":
            if data.has_key('cpu'):
                cpu = data['cpu']
                if cpu.has_key('total'):
                    cpuList.append(cpu['total'])



        if dtype == "meminfo" and not charging:
            if data.has_key('Active:'):
                memList.append(int(data['Active:']))


        if dtype == "netiflog":
            cellrx = data["MobileRxBytes"]
            celltx = data["MobileTxBytes"]
            wifirx = data["TotalRxBytes"] - cellrx
            wifitx = data["TotalTxBytes"] - celltx

            ctxt = crxt = wtxt = wrxt = 0.0

            if not firstNet:
                if celltx > pcelltx: ctxt = (celltx - pcelltx)/1024.0
                if cellrx > pcellrx: crxt = (cellrx - pcellrx)/1024.0
                if wifitx > pwifitx: wtxt = (wifitx - pwifitx)/1024.0
                if wifirx > pwifirx: wrxt = (wifirx - pwifirx)/1024.0

            else:
                firstNet = False
                crx = ctx = wrx = wtx = 0.0

            ctx += ctxt
            crx += crxt
            wtx += wtxt
            wrx += wrxt

            pcelltx = celltx
            pcellrx = cellrx
            pwifitx = wifitx
            pwifirx = wifirx




        if dtype == "WiFiGPSLocation" or dtype == "LocationTracker":
            if data.has_key('gpstime'):
                gpst = data["gpstime"]
            elif data.has_key("GPS"):
                gpst = data["GPS"]


            #gpst = data["gpstime"]


            if data.has_key("wifiscan"):
                wifiscant = data["wifiscan"]
            elif data.has_key("gpscount"):
                wifiscant = data["gpscount"]
            else:
                wifiscant = 0


            if not firstWiFiGPS and pgps <= gpst and pwifiscan <= wifiscant:
                newGps = (gpst - pgps)
                newScan = (wifiscant - pwifiscan)
                if newGps > 0: totalGps += newGps
                if newScan > 0: totalScan += newScan
            else:
                firstWiFiGPS = False
                totalGps = totalScan = 0.0

            pgps = gpst
            pwifiscan = wifiscant


        if dtype == "AccelService":
            if "Accel" in data:
                accelt = data["Accel"]
            else:
                accelt = data["accel"]

            if not firstAccel and paccel < accelt:
                newAccel = (accelt - paccel)
                totalAccel += newAccel
            else:
                totalAccel = 0.0
                firstAccel = False

            paccel = accelt



        if dtype == "AcousticApp":
            if (data.has_key("acoustictime")):
                audiot = data["acoustictime"]*1.0

                if not firstAudio and paudio < audiot:
                    newAudio = (audiot - paudio)
                    totalAudio += newAudio
                else:
                    totalAudio = 0.0
                    firstAudio = False

                paudio = audiot


        if dtype == 'dataconnection':
            network = data['network']
            if network.find('mobile') != -1:
                state = data['state']
                if state == 'disconnected':
                    netDisconnect += 1


        if dtype == "screen":
            if data["status"] == "ON" and off:
                laston = record["time_stamp"]
                off = False
                screenCount += 1
            elif data["status"] == "OFF" and not off:
                screenInterval = ((record["time_stamp"] - laston)/1000.0)
                screenTime += screenInterval
                off = True


        if dtype == "call":
            if data["state"] == "started" and not incall:
                callstart = record["time_stamp"]
                incall = True
            elif data["state"] == "ended" and incall:
                callLen = ((record["time_stamp"] - callstart)/1000.0)
                callTime += callLen
                incall = False


        if dtype == "netlocation":
            lat = data["Lat"]
            lon = data["Lon"]




    return response



def parse_lme(request, imei, fdate, tdate):

    response = HttpResponse(mimetype='text/plain')

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date)

    LONG = 5*60

    callstart = 0.0
    voltList = []
    lastVoltList = []
    voltage = 0.0
    current = 0.0

    screenTime = 0.0
    screenCount = 0
    off = True


    netDisconnect = 0

    cpuList = []
    memList = []

    tempList = []


    totalGps = 0.0
    totalScan = 0.0
    totalAccel = 0.0

    crx = ctx = wrx = wtx = 0.0
    audiotime = 0.0


    callTime = 0
    callstart = 0
    incall = False

    firstCycle = True
    firstAudio = firstAccel = firstWiFiGPS = firstNet = True
    charging = False

#    temperature = 0.0
#    voltage = 0.0


    header = "day, hour, time, delta, battery, level, current, screen, events, gpstime, wifiscan, accel, acoustictime, cpu, mem, crx, ctx, wrx, wtx, call, disconnect\n"

    response.write(header)


    for e in q.all():
        record = simplejson.loads(e.message)
        data = record.get("data")
        dt = record["date"]
        (day, h) = dt.split()
        hour = h.split(':')[0]
        ts = record.get("time_stamp")
        date = record.get("date")



        if record["type"] == "cpu" and not charging:
            if data.has_key('cpu'):
                cpu = data['cpu']
                if cpu.has_key('total'):
                    cpuList.append(cpu['total'])



        if record["type"] == "meminfo" and not charging:
            if data.has_key('Active:'):
                memList.append(int(data['Active:']))



        if record["type"] == "AccelService" and not charging:
            totalAccel = data["Accel"]

        if record["type"] == "netiflog" and not charging:
            crx = data["MobileRxBytes"]
            ctx = data["MobileTxBytes"]
            wrx = (data["TotalRxBytes"] - crx)
            wtx = (data["TotalTxBytes"] - ctx)

        if record["type"] == "AcousticApp" and not charging:
            if (data.has_key("acoustictime")):
                audiotime = data["acoustictime"]*1.0






        if record["type"] == "LocationTracker" and not charging:
            totalGps = data["gpstime"]
            totalScan = 0
            #totalScan = data["gpscount"]

        if record["type"] == "WiFiGPSLocation" and not charging:
            if data.has_key('gpstime'):
                totalGps = data["gpstime"]
                totalScan = data["wifiscan"]
            elif data.has_key("GPS"):
                totalGps = data["GPS"]
                totalScan = data["WiFiScan"]




        if record["type"] == 'dataconnection' and not charging:
            network = data['network']
            if network.find('mobile') != -1:
                state = data['state']
                if state == 'disconnected':
                    netDisconnect += 1


        if record["type"] == "screen" and not charging:
            if data["status"] == "ON" and off:
                laston = record["time_stamp"]
                off = False
                screenCount += 1
            elif data["status"] == "OFF" and not off:
                screenInterval = ((record["time_stamp"] - laston)/1000.0)
                screenTime += screenInterval
                off = True


        if record["type"] == "call" and not charging:
            if data["state"] == "started" and not incall:
                callstart = record["time_stamp"]
                incall = True
            elif data["state"] == "ended" and incall:
                callLen = ((record["time_stamp"] - callstart)/1000.0)
                callTime += callLen
                incall = False




        if record["type"] == "battery":
            level = data["level"]
            temperature = eval(data["temperture"])
            voltage = data["voltage"]
            if data.has_key('current'):
                current = data["current"]
            else:
                current = 0
            status = data["status"]



            if status == "Charging (AC)" or data["status"] == "Charging (USB)":
                lastBatTime = ts
                screenTime = 0.0
                screenCount = 0
                callTime = 0.0
                netDisconnect = 0
                cpuList = []
                memList = []
                tempList = []
                lastVoltage = voltage
                off = True
                incall = False
                charging = True
                firstAudio = firstAccel = firstWiFiGPS = firstNet = True

            if status == "Not charging" or status == "Discharging":
                if firstCycle:
                    firstCycle = False
                    lastBatTime = ts
                    lastVoltage = voltage
                    continue

                charging = False
                delta = (ts - lastBatTime)/(1000.0)




                if delta <= LONG and delta > 0:
                    discFactor = voltage
                    avgCpu = mean(cpuList)
                    avgMem = mean(memList)
                    avgTemp =  temperature

                    if not off:
                        screenInterval = ((record["time_stamp"] - laston)/1000.0)
                        screenTime += screenInterval

                    if incall:
                        callLen = ((record["time_stamp"] - callstart)/1000.0)
                        callTime += callLen


#                    if (discFactor > 0) and screenTime < INTERVAL * 60:
                    response.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" %(day, hour, ts/1000, delta, discFactor, level, current, screenTime, screenCount, totalGps, totalScan, totalAccel, audiotime, avgCpu, avgMem, crx, ctx, wrx, wtx, callTime, netDisconnect))
                    screenTime = 0.0
                    screenCount = 0
                    callTime = 0.0
                    netDisconnect = 0
                    cpuList = []
                    memList = []
                    tempList = []
                    #crx = ctx = wrx = wtx = 0.0

                    firstAudio = firstAccel = firstWiFiGPS = firstNet = True

                    lastBatLevel = level
                    lastBatTime = ts


                if delta >  LONG:
                    screenTime = 0.0
                    screenCount = 0
                    callTime = 0.0
                    cpuList = []
                    memList = []
                    tempList = []

                    lastVoltage = voltage
                    voltList = []

                    firstAudio = firstAccel = firstWiFiGPS = firstNet = True

                    lastBatLevel = level
                    lastBatTime = ts


                lastVoltage = voltage

    return response






def analysis(request, imei, fdate, tdate, interval):


    response = HttpResponse(mimetype='text/plain')

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date)

    off = True
    charging = False
    laston = 0



    total = 1.0
    good = 0
    bad = 0



    INTERVAL = eval(interval)

    for e in q.all():

        record = simplejson.loads(e.message)
        data = record.get("data")
        ts = record.get("time_stamp")
        date = record.get("date")


        if record["type"] == "battery":
            if data["status"] == "Charging (AC)" or data["status"] == "Charging (USB)":
                charging = True

            if data.get("status") == "Not charging":
                charging = False


        if record["type"] == "netiflog" and not charging:
            total += 1
            if not off:
                good += 1
                #response.write(date + ": on\n")
            elif ts - laston < INTERVAL*1000:
                #response.write(date + ": on\n")
                good += 1
            else:
                #response.write(date + ": off\n")
                bad += 1

        if record["type"] == "screen" and not charging:
            if data["status"] == "ON" and off:
                off = False
            elif data["status"] == "OFF" and not off:
                off = True
                laston = ts

    #response.write("Total: " + str(total) + "\n")
    #response.write("Good: " + str(good) + "\n")
    #response.write("Bad: " + str(bad) + "\n")
    #response.write("-----------------------------\n")
    response.write("Ratio: " + str((good*1.0)/total) + "\n")


    return response




@login_required
def cs219(request):

    now = datetime.datetime.now()
    difference1 = datetime.timedelta(days=1)
    difference2 = datetime.timedelta(days=-1)
    nextday = now + difference1;
    prevday = now + difference2;
    imei_ = request.user.profile.imei


    c = Context({
        'year_range': ['2010', '2011'],
        'day_range': ["%(#)02d" %{"#":i} for i in range(1, 32)],
        'hour_range': ["%(#)02d" %{"#":i} for i in range(0, 24)],
        'minute_range': ["%(#)02d" %{"#":i} for i in range(0, 60)],
        'month_range' : ['Jan', 'Feb', 'Mar', 'Apr',
            'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
            'Nov', 'Dec'],
        'imei' : imei_,
        'user' : request.user.username
        })



    try:
        appname = request.POST['appname']
        resname = request.POST['resname']
        c.update({'appname': appname,
            'resname': resname,
            'isQuerySet': True,
            })
    except (KeyError):
        c.update({ 'isQuerySet': False})


    t = loader.get_template('cs219.html')


    try:
        syear = request.POST['syear']
        eyear = request.POST['eyear']
        smonth = request.POST['smonth']
        emonth = request.POST['emonth']
        sday = request.POST['sday']
        eday = request.POST['eday']
        #if len(detail) > 1:
        shour = request.POST['shour']
        ehour = request.POST['ehour']
        sminute = request.POST['sminute']
        eminute = request.POST['eminute']
    except (KeyError):
        syear = str(now.year)
        eyear = str(nextday.year)
        emonth = datetime.datetime.strftime(nextday, "%b")
        eday = "%(#)02d" %{"#": nextday.day}
        sday = "%(#)02d" %{"#": prevday.day}
        smonth = datetime.datetime.strftime(prevday, "%b")

        shour = ehour = sminute = eminute = '00'


    months = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
        'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09',
        'Oct':'10', 'Nov':'11', 'Dec':'12'}

    sdate = syear + months[smonth] + sday + shour + sminute
    edate = eyear + months[emonth] + eday + ehour + eminute


    from_date = syear + "-" + months[smonth] + "-" + sday
    to_date = eyear + "-" + months[emonth] + "-" + eday



    user_query = User_Query(sdate, edate, imei_)
    c.update({
        'user_query': user_query,
        'cur_sday' : sday,
        'cur_eday' : eday,
        'cur_smonth' : smonth,
        'cur_emonth' : emonth,
        'cur_syear' : syear,
        'cur_eyear' : eyear,
        'cur_shour' : shour,
        'cur_ehour' : ehour,
        'cur_sminute' : sminute,
        'cur_eminute' : eminute })



    return HttpResponse(t.render(c))



@login_required
def appresource(request):

    json = request.GET.has_key('json')

    now = datetime.datetime.now()
    difference1 = datetime.timedelta(days=1)
    difference2 = datetime.timedelta(days=-1)
    nextday = now + difference1;
    prevday = now + difference2;
    imei_ = request.user.profile.imei


    c = RequestContext(request, {
        'year_range': ['2010', '2011'],
        'day_range': ["%(#)02d" %{"#":i} for i in range(1, 32)],
        'hour_range': ["%(#)02d" %{"#":i} for i in range(0, 24)],
        'minute_range': ["%(#)02d" %{"#":i} for i in range(0, 60)],
        'month_range' : ['Jan', 'Feb', 'Mar', 'Apr',
            'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
            'Nov', 'Dec'],
        'imei' : imei_,
        'user' : request.user.username
        })



    try:
        appname = request.POST['appname']
        c.update({'appname': appname,
            'isQuerySet': True,
            })
    except (KeyError):
        c.update({ 'isQuerySet': False})


    t = loader.get_template('appresource.html')


    try:
        syear = request.POST['syear']
        eyear = request.POST['eyear']
        smonth = request.POST['smonth']
        emonth = request.POST['emonth']
        sday = request.POST['sday']
        eday = request.POST['eday']
        #if len(detail) > 1:
        shour = request.POST['shour']
        ehour = request.POST['ehour']
        sminute = request.POST['sminute']
        eminute = request.POST['eminute']
    except (KeyError):
        syear = str(now.year)
        eyear = str(nextday.year)
        emonth = datetime.datetime.strftime(nextday, "%b")
        eday = "%(#)02d" %{"#": nextday.day}
        sday = "%(#)02d" %{"#": prevday.day}
        smonth = datetime.datetime.strftime(prevday, "%b")

        shour = ehour = sminute = eminute = '00'


    months = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
        'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09',
        'Oct':'10', 'Nov':'11', 'Dec':'12'}

    sdate = syear + months[smonth] + sday + shour + sminute
    edate = eyear + months[emonth] + eday + ehour + eminute


    from_date = syear + "-" + months[smonth] + "-" + sday
    to_date = eyear + "-" + months[emonth] + "-" + eday


    appset = set()
    q = _query(imei_, from_date, to_date, 'appresource')
    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        for app_item in data.keys():
            packageItems = app_item.split('.')
            app_name = packageItems[len(packageItems)-1]
            if app_name.find(':') > 0:
                nameList = app_name.split(':')
                app_name = nameList[0]

            appset.add(app_name)

    appnames = []
    for app in appset:
        appnames.append(app)

    appnames.sort()


    if json:
        jsonappnames = []
    for e in appnames:
        jsonappnames.append({'appname':e})
    return HttpResponse(simplejson.dumps(jsonappnames), mimetype='application/javascript')

    user_query = User_Query(sdate, edate, imei_)
    c.update({
        'app_names' : appnames,
        'user_query': user_query,
        'cur_sday' : sday,
        'cur_eday' : eday,
        'cur_smonth' : smonth,
        'cur_emonth' : emonth,
        'cur_syear' : syear,
        'cur_eyear' : eyear,
        'cur_shour' : shour,
        'cur_ehour' : ehour,
        'cur_sminute' : sminute,
        'cur_eminute' : eminute })



    return HttpResponse(t.render(c))



def check_table(imei):

    table_name = "systemsens_" + imei

    cursor = connection.cursor()
    sql_query = "show tables like '" + table_name + "';"
    cursor.execute(sql_query)
    row = cursor.fetchone()
    if row == None:
        create_usertable(imei)

    return table_name

#def check_table2(request, imei):
#    tempresponse = HttpResponse(mimetype='text')
#    table_name = "systemsens_" + imei
#
#    cursor = connection.cursor()
#    sql_query = "show tables like '" + table_name + "';"
#    cursor.execute(sql_query)
#    row = cursor.fetchone()
#
#    tempresponse.write(row)
#
#    return tempresponse
#


def dump():
    print "";



def create_usertable(imei):


    table_name = "`systemsens_" + str(imei) + "`"

    create_head = "CREATE TABLE "

    create_tail = " (`id` int(11) NOT NULL AUTO_INCREMENT, `dt_record` datetime NOT NULL, `data_type` varchar(20) NOT NULL, `imei` varchar(20) NOT NULL, `message` longtext NOT NULL, PRIMARY KEY (`id`), KEY `index_0` (`id`,`dt_record`,`data_type`)) ENGINE=InnoDB;"

    sql_command = create_head + table_name + create_tail

    cursor = connection.cursor()
    cursor.execute(sql_command)
    row = cursor.fetchone()

    return row == None


