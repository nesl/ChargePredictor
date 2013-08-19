from django.http import HttpResponse, Http404, HttpResponseRedirect
from visualization.models import SystemSens, comments
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import time, calendar, simplejson, datetime


import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import struct
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.cm as cm


hours    = mdates.HourLocator()   # every hour 
days   = mdates.DayLocator()  # every day
hoursFmt = mdates.DateFormatter('%H')
daysFmt = mdates.DateFormatter('%m-%d  .')


class User_Query:
    def __init__(self, start, end):
        self.startdate = start
        self.enddate = end
 

    def set_date(start, end):
        self.startdate = start
        self.enddate = end
 


def _query(imei, fdate, tdate, rtype='any'):
    q = SystemSens.objects.filter(imei__exact=imei)
    q = q.filter(dt_record__gte=fdate)
    q = q.filter(dt_record__lte=tdate)
    if rtype != "any":
        q = q.filter(data_type__exact=rtype)
    q = q.order_by('dt_record')
    return q




def _date(in_date):

    y_str = in_date[:4]
    m_str = in_date[4:6]
    d_str = in_date[-2:]
    return "%s-%s-%s" %(y_str, m_str, d_str)




@login_required
def battery_temp(request, imei, fdate, tdate):
    response = HttpResponse(mimetype='image/png')


    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')

    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        t1 = datetime.datetime.strptime(record["date"], '%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime(t1.year, t1.month + 1, t1.day, t1.hour,
                t1.minute, t1.second)

        plotkeys.append(t1)
        plotvals.append(data["temperture"])



    fig = Figure(figsize=(12,4), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)


    ax.plot_date(plotkeys, plotvals, lw=2, ms=4)#, alpha=0.7, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)


    datemin = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    datemax = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    ax.set_xlim(datemin, datemax)

    ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")
    ax.set_ylabel("Battery Temperature (C)")
    ax.set_xlabel("Time (hour)")
    ax.grid(True)
    ax.grid(True, which='minor')

    fig.autofmt_xdate(bottom=0.25, rotation=90)


    canvas.print_png(response)

    return response





@login_required
def battery_level(request, imei, fdate, tdate):
    response = HttpResponse(mimetype='image/png')

    from_date = _date(fdate)
    to_date = _date(tdate)
    q = _query(imei, from_date, to_date, 'battery')



    plotvals = []
    plotkeys = []

    for e in q.all():
        record = simplejson.loads(e.message)
        data = record["data"]
        t = datetime.datetime.strptime(record["date"], '%Y-%m-%d %H:%M:%S')
        plotkeys.append(t)
        plotvals.append(data["level"])


    fig = Figure(figsize=(12,4), dpi=100, facecolor='white')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)


    ax.plot_date(plotkeys, plotvals, lw=2, ms=4)#, alpha=0.7, mfc='orange')


    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)
    ax.xaxis.labelpad = 1
    #ax.xtick.major.pad = 5


    datemin = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    datemax = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    ax.set_xlim(datemin, datemax)
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
def index(request):

    now = datetime.datetime.now()
    imei_ = request.user.email

    t = loader.get_template('battery.html')
    c = Context({
        'day_range': ["%(#)02d" %{"#":i} for i in range(1, 31)],
        'month_range' : ['Jan', 'Feb', 'Mar', 'Apr', 
            'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
            'Nov', 'Dec'],
        'cur_month' : datetime.datetime.strftime(now, "%b"),
        'imei' : imei_,
        })


    try:
        syear = request.POST['syear']
        eyear = request.POST['eyear']
        smonth = request.POST['smonth']
        emonth = request.POST['emonth']
        sday = request.POST['sday']
        eday = request.POST['eday']
    except (KeyError):
        syear = str(now.year)
        eyear = syear
        smonth = datetime.datetime.strftime(now, "%b")
        emonth = smonth
        sday = "%(#)02d" %{"#": now.day - 1}
        eday = "%(#)02d" %{"#": now.day + 1}


    months = {'Jan':'00', 'Feb':'01', 'Mar':'02', 'Apr':'03', 
        'May':'04', 'Jun':'05', 'Jul':'06', 'Aug':'07', 'Sep':'08', 
        'Oct':'09', 'Nov':'10', 'Dec':'11'}


    sdate = syear + months[smonth] + sday
    edate = eyear + months[emonth] + eday

    from_date = syear + "-" + months[smonth] + "-" + sday
    to_date = eyear + "-" + months[emonth] + "-" + eday


    #imei_ = "354957031725123"

    user_query = User_Query(sdate, edate)
    c.update({'isQuerySet': True, 
        'user_query': user_query,
        'cur_sday' : sday,
        'cur_eday' : eday,
        'count': _query(imei_, from_date, to_date).count(),})

    
    return HttpResponse(t.render(c))

    #num_rec = SystemSens.objects.count()
    #return HttpResponse("Found %s records! " %num_rec)




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


    return HttpResponseRedirect(reverse('visualization.views.index'))

