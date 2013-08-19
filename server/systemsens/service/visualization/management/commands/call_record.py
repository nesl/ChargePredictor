from django.core.management.base import BaseCommand, CommandError
from visualization.models import *
from visualization.views import _query
import json
import md5
import csv
from datetime import datetime as dt
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
class Command(BaseCommand):
    args = '<phone_number> <output_file> [<phone #> <phone #>]'
    help = 'Return the phone call record of this phone'

    def handle(self, *args, **options):
        hashedPhone = md5.new(args[0]).hexdigest()
        hashedPhoneOnePrefix = md5.new("1"+args[0]).hexdigest()
	query = Client.objects.filter(phone_num__in=[hashedPhone, hashedPhoneOnePrefix] )
        if len(query) < 1:
            print "No such a phone number"
            return
        imei = query[0].imei
       
        givenHashedPhoneNums = {}
        for i in range(1,len(args)):
              hashed = md5.new(args[i]).hexdigest()
              hashedOnePrefix = md5.new("1"+args[i]).hexdigest()
              givenHashedPhoneNums[hashed] = args[i]
              givenHashedPhoneNums[hashedOnePrefix] = args[i]
        """ Step 1. Call """
        # get all distinct call record
        records = []
        for r in _query(imei, rtype="call"):
            msg = json.loads(r.message)
            # only version 4.1 or higher give us correct phone records
            if float(msg["ver"]) >= 4.1 and "timestamp" in msg["data"]:
                record = {}
                record["callType"] = msg["data"]["callType"]
                record["time"] = dt.fromtimestamp(msg["data"]["timestamp"]/1000.0)
                # Skip duplicate result
                if record["time"] in [r["time"] for r in records]:
                    continue
                record["duration"] = msg["data"]["duration"]
                if msg["data"]["number"] in givenHashedPhoneNums:
                    record["number"] = givenHashedPhoneNums[msg["data"]["number"]]
                else:
                    record["number"] = "(hashed#)" + msg["data"]["number"]
                records.append(record)
         # Output data
        with open(args[1]+"_call.csv",'wb') as OUTPUT:
            dw = csv.DictWriter(OUTPUT, ["callType", "number", "duration", "time"])
            dw.writerow(dict((fn,fn) for fn in dw.fieldnames))
            for r in records:
                dw.writerow(r)
        """ Step 2. SMS """
        # get all distinct call record
        records = []
        for r in _query(imei, rtype="sms"):
            msg = json.loads(r.message)
            # only version 4.1 or higher give us correct phone records
            if float(msg["ver"]) >= 4.1 and "timestamp" in msg["data"]:
                record = {}
                print msg["data"]
                print dt.fromtimestamp(msg["data"]["timestamp"]/1000.0)
		""" SMS TYPE difinition from 
                    http://grepcode.com/file/repository.grepcode.com/java/ext/com.google.android/android/1.5_r4/android/provider/Telephony.java#57
		    public static final int MESSAGE_TYPE_ALL    = 0;
		    public static final int MESSAGE_TYPE_INBOX  = 1;
		    public static final int MESSAGE_TYPE_SENT   = 2;
		    public static final int MESSAGE_TYPE_DRAFT  = 3;
		    public static final int MESSAGE_TYPE_OUTBOX = 4;
		    public static final int MESSAGE_TYPE_FAILED = 5; // for failed outgoing messages
		    public static final int MESSAGE_TYPE_QUEUED = 6; // for messages to send later
		"""
                if msg["data"]["type"] == "1":
                    type = "INCOMMING"
                elif msg["data"]["type"] in ["2","6","4","3"]:
                    # it could be SENT or in the QUEUE if SystemSens 
                    type = "OUTGOING"
                else:
                    print msg
                    continue
                record["smsType"] = type
                record["time"] = dt.fromtimestamp(msg["data"]["timestamp"]/1000.0).isoformat()
                # Skip duplicate result
                if record["time"] in [r["time"] for r in records]:
                    continue
                record["length"] = msg["data"]["length"]
                if msg["data"]["address"] in givenHashedPhoneNums:
                    record["number"] = givenHashedPhoneNums[msg["data"]["address"]]
                else:
                    record["number"] = "(hashed#)" + msg["data"]["address"]
                records.append(record)
         # Output data
        with open(args[1]+"_sms.csv",'wb') as OUTPUT:
            dw = csv.DictWriter(OUTPUT, ["smsType", "number", "length", "time"])
            dw.writerow(dict((fn,fn) for fn in dw.fieldnames))
            for r in records:
                dw.writerow(r)




            
