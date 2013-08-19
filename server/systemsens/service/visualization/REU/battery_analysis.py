import _mysql
import json
import time
import math

# Class object to hold fetched rows | Pulled out important information to classify and order records
class RowData:
    def __init__(self,stmp,rcd,mes):
        self.time_stamp = stmp
        self.record_type = rcd
        self.message = mes

class BatteryData:
    def __init__(self,timestamp,time,status,level,current,\
                 health,voltage,temp,lolc,tolc,lcl):
        self.timestamp = timestamp
        self.time = time
        self.status = status
        self.level = level
        self.current = current
        self.health = health
        self.voltage = voltage
        self.temp = temp
        self.lolc = lolc
        self.tolc = tolc
        self.lcl = lcl
        self.t2nc = 0
        self.ncd = 0
# EPOCH CONVERSIONS
epochDay = 86400
epochWeek = 604800
epochMonth = 2629743
# Function to convert time stamp reported by Java (millis-since-epoch) to localtime
# Time still reported in seconds. Change conversion rate from epochWeek to epochDay for 00:00 - 24:00
def epoch2daytime(epochtime):
    epochtime = int(epochtime/1000)
    return int(epochtime%epochWeek)

def time2nominal(time):
    intervalHour = 3600
    intervalDay = epochDay
    dayNum = time/intervalDay # day of time
    time = time%intervalDay
    hourNum = time/intervalHour # hour of time
    nominalRep = 'Day ' + str(dayNum) + ' Hour ' + str(hourNum)
    return nominalRep

granularity = 900
gran_type = 'Quarter '

def time2nextNominal(time):
    granNum = int(time/granularity)
    return gran_type + str(granNum)

def feature_generation(user_imei):
    # Connect to database, fetch all table names first.
    colname = 'message'
    db = _mysql.connect('localhost','root','neslrocks!','service')
    #db.query('SHOW TABLES;')

    #alltables = db.store_result()
    #fieldsize = alltables.num_rows()

    tag = 'systemsens_'
    #taglength = len(tag)

    IMEI = user_imei

    # Query for current column of table name
    try:
        db.query('SELECT ' + colname + ' FROM '+ tag + IMEI)
        r = db.store_result()
        tablesize = r.num_rows()
    except _mysql.ProgrammingError:
        return False
    # Preliminary Check, for error management
    if tablesize == 0:
        return False
    # Blind read of table, reformatting to list of RowData objects | Sort by time_stamp on completion.

    print 'Reading full table of ' + str(tablesize) + ' entries. [IMEI: ' + IMEI + ']'

    fetchedRows = []

    for _ in range(tablesize):
        jsontuple = r.fetch_row()
        jsonobj = json.loads(jsontuple[0][0])
        obj_type = jsonobj[u'type']
        # FOR SPEED UP:
        if(obj_type != 'battery'):
            continue
        obj_message = jsonobj[u'data']
        obj_time_stamp = jsonobj[u'time_stamp']
        fetchedRows.append(RowData(obj_time_stamp,obj_type,obj_message))

    # FOLLOWING STATEMENT CAN BE MODIFIED TO DUMP INTO SEPERATE ARRAY
    # USEFUL IF SORTING BY TYPE

    print 'Sorting rows by timestamp.'
    fetchedRows.sort(key=lambda x: x.time_stamp)

    swap_charging_stamp = 0
    swap_charging_disp = 0
    swap_charging_level = 0
    initvalues = True
    charging = True

    print 'Extracting battery data.'
    processedRows = []
    for record in fetchedRows:
        if(record.record_type == 'battery'):        # Determine if record is a battery record
            data = record.message
            timestamp = record.time_stamp
            status = data[u'status']                # Extract all information
            level = data[u'level']
            current = data[u'current']
            health = data[u'health']
            voltage = data[u'voltage']
            temp = data[u'temperture']

            # Check initial case and record battery state switching

            if(initvalues):
                swap_charging_stamp = timestamp
                swap_charging_level = level
                initvalues = False
            elif((not charging) and (status == 'Charging (USB)' or status == 'Charging (AC)')):
                swap_charging_stamp = timestamp
                swap_charging_level = level
                swap_charging_disp = 0
            else:    
                if(charging):
                    swap_charging_disp = timestamp - swap_charging_stamp

            if(status == 'Charging (USB)' or status == 'Charging (AC)'):
                charging = True
            else:
                charging = False
        
            # Convert time since last charge to HOUR format
            processedRows.append(BatteryData(timestamp,epoch2daytime(timestamp),status,level,current,\
            health,voltage,temp,(swap_charging_disp/1000.0),epoch2daytime(swap_charging_stamp),swap_charging_level))

    timeOfNextCharge = processedRows[len(processedRows) - 1].timestamp
    timeOfNextEndCharge = processedRows[len(processedRows) - 1].timestamp
    lastChargingStatus = processedRows[len(processedRows) - 1].status

    print 'Running some extra analysis.'

    maxTimeToNext = 0

    for record in reversed(processedRows):
        if(record.status != 'Not charging'):
            if(lastChargingStatus == 'Not charging'):
                timeOfNextEndCharge = record.timestamp
            lastChargingStatus = record.status
            continue
        if(lastChargingStatus != 'Not charging'):
            timeOfNextCharge = record.timestamp
        lastChargingStatus = record.status
        record.t2nc = (timeOfNextCharge - record.timestamp)/1000.0
        record.ncd = (timeOfNextEndCharge - timeOfNextCharge)/1000.0
        if(maxTimeToNext < record.t2nc):
            maxTimeToNext = record.t2nc
    print 'Writing to ARFF file.'

    # Create WEKA Attribute Relation File Format
    try:
        wekafile = open('/opt/systemsens/service/visualization/REU/wekadata/' + IMEI + '.arff','w')
    except:
        return "File open failure."
    # Setting attribute conditions and types

    wekafile.write('@relation ' + IMEI)

    wekafile.write('\n\n')

    wekafile.write('@attribute timestamp real\n')
    wekafile.write('@attribute time real\n')
    wekafile.write('@attribute period {')

    for day in range(0,7):
        for hour in range(0,24):
            wekafile.write('"Day ' + str(day) + ' Hour ' + str(hour) + '"')
            if (hour != 23 or day != 6):
                wekafile.write(', ')

    wekafile.write('}\n')
    wekafile.write('@attribute status {"Charging (USB)", "Charging (AC)", "Discharging", "Not charging", "Full", "Unknown"}\n')
    wekafile.write('@attribute level real\n')
    #wekafile.write('@attribute current real\n')
    #wekafile.write('@attribute health {Good, Overheat, Dead, Over voltage, Unspecified failure, Health Unknown}\n')
    #wekafile.write('@attribute voltage real\n')
    wekafile.write('@attribute temp real\n')
    wekafile.write('@attribute lengthOfLastCharge real\n')
    wekafile.write('@attribute timeOfLastCharge real\n')
    wekafile.write('@attribute lastChargingLevel real\n')
    wekafile.write('@attribute timeToNextCharge real\n')
    wekafile.write('@attribute timeNextNominal {')

    rangeBarrier = (epochWeek/granularity) + 1
    #int(maxTimeToNext/3600) + 1

    for gran in range(0,rangeBarrier):
        wekafile.write('"' + gran_type + str(gran) + '"')
        if (gran != (rangeBarrier - 1)):
            wekafile.write(', ')

    wekafile.write('}\n')
    wekafile.write('@attribute durationOfNextCharge real\n')
    wekafile.write('\n@data\n')

    #str(record.current), str(record.health), str(record.voltage)

    for record in processedRows:
        wekafile.write(str(record.timestamp) + ', ' + str(record.time) + ', "' + time2nominal(int(record.time)) + '", "' + str(record.status) + '", ' +\
            str(record.level) + ', ' +\
            str(record.temp) + ', ' + str(record.lolc) + ', ' + str(record.tolc) + ', ' + str(record.lcl) + ', ' +\
            str(record.t2nc) + ', "' + time2nextNominal(record.t2nc) + '", ' + str(record.ncd) + '\n')
    wekafile.close()
    return "Successfully wrote file."
