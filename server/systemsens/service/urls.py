from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from visualization.models import Client
admin.autodiscover()
admin.site.register(Client)

urlpatterns = patterns('visualization.views',
    # Example:
    # (r'^service/', include('service.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^viz/put/$', 'put'),
    (r'^viz/get_model/$', 'get_model'),
    #(r'^viz/error_report/$', 'error_report'),
    #(r'^viz/request_model/$', 'version_check'),
    (r'^viz/put_binary/(?P<version>[\d\w\.]+)/$', 'put_binary'),
    (r'^viz/cs219/$', 'cs219'),
    (r'^viz/appresource/$', 'appresource'),
    (r'^viz/(?P<detail>\w*)$', 'index'),
    (r'^viz/comment/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'comment'),
    (r'^viz/parse/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<interval>\d+)$', 'parse'),
    (r'^viz/parsevisits/$', 'parsevisits'),
    (r'^viz/newuser/(?P<imei>\w+)/(?P<uname>\w+)/(?P<passwd>\w+)/$', 'newuser'),
    (r'^viz/checkuser/(?P<imei>\w+)/$', 'checkuser'),
    (r'^viz/getuserinfo/$', 'getuserinfo'),
    (r'^viz/changepass/(?P<uname>\w+)/(?P<oldpasswd>\w+)/(?P<newpasswd>\w+)/$', 'changepass'),
    (r'^viz/parsescreenevents/$', 'parsescreenevents'),
    (r'^viz/parse_lme/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'parse_lme'),
    (r'^viz/get/(?P<start>\d+)/(?P<end>\d+)/(?P<dtype>\w+)$', 'get'),
    (r'^viz/analysis/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<interval>\d+)$', 'analysis'),
    (r'^viz/screen_events/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'screen_events'),
    (r'^viz/sleep/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'sleep'),
    (r'^viz/screen_time/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'screen_time'),
    #(r'^viz/metrics/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'metrics'),
    (r'^viz/battery_data/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_data'),
    (r'^viz/battery_level/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_level'),
    (r'^viz/battery_temp/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_temp'),
    (r'^viz/battery_volt/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_volt'),
    (r'^viz/battery_current/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_current'),
    (r'^viz/battery_power/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'battery_power'),
    (r'^viz/cpu_usage/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'cpu_usage'),
    (r'^viz/mem_usage/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'mem_usage'),
    (r'^viz/net_bytes/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'net_bytes'),
    (r'^viz/cell_signal/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'cell_signal'),
    (r'^viz/net_packets/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'net_packets'),
    (r'^viz/gps/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'gps'),
    (r'^viz/audio/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'audio'),
    (r'^viz/resource/(?P<appname>\w+)/(?P<resname>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'resource'),
    (r'^viz/netstate/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'netstate'),
    (r'^viz/net_state/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'net_state'),
    (r'^viz/accelservice/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'accelservice'),
    (r'^viz/wifi_scan/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'wifi_scan'),
    (r'^viz/calls/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'calls'),
    (r'^viz/apps/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'apps'),
    (r'^viz/net_app/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'net_app'),
    (r'^viz/app_cpu/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<app>\w+)/$', 'app_cpu'),
    (r'^viz/app_mem/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<app>\w+)/$', 'app_mem'),
    (r'^viz/app_net/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<app>\w+)/$', 'app_net'),
    (r'^viz/power/(?P<fdate>\d+)/(?P<tdate>\d+)/$', 'power'),
    (r'^viz/model/(?P<imei>\w+)/$', 'model'),
    (r'^viz/stats/(?P<imei>\w+)/$', 'stats'),
    (r'^viz/set_deadline/(?P<imei>\w+)/(?P<fdate>\d+)/(?P<tdate>\d+)/(?P<curlevel>\d+)/$', 'set_deadline'),
    # this is for faisal's data collection
    (r'^viz/dump/', 'dump'),
)



urlpatterns += patterns('',
    (r'^viz/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}),
    (r'^viz/logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html'}),
    (r'^media/SystemSens/$', redirect_to, {'url': 'index.html'}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/opt/systemsens/service/media', 'show_indexes': True}),
)


