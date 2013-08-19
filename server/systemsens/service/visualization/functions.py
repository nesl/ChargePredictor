import _mysql
import sys
sys.path.insert(0,'/opt/systemsens/service/visualization/REU')

# START REU SUMMER CODE
import battery_analysis as analyze
import subprocess
import mimetypes
import os.path
from threading import Thread

UPDATE_MODEL_RESP = 0
IN_ERR_RANGE_RESP = 1
NO_MODEL_EXT_RESP = 2
NO_NEW_MODEL_RESP = 3
MODEL_UDPATING_RESP = 4

def uni2ascii(send):
    send = send.decode('utf-8')
    send = send.encode('ascii','ignore')
    return send

def error_report(request):
    try:
        imei = request.POST['imei']
        error = request.POST['err']
    except (KeyError):
        return HttpResponseBadRequest()
    
    # Parse ASCII representations of IMEI and reported model error
    imei = uni2ascii(imei)
    error = float(uni2ascii(error))
    #return HttpResponse('Hello')
    # Open database connection
    model_db = _mysql.connect('localhost','root','neslrocks!','service')
    model_db.query('SELECT * FROM user_models WHERE imei=' + imei)
    raw = model_db.store_result()
    table_size = raw.num_rows()

    # Assuming no repeated IMEIs   
    #return HttpResponse("Hello") 
    if table_size != 0:
        user_data = raw.fetch_row()[0]
        user_imei = user_data[0]

        if(user_imei == imei):
            model_exists = True
            user_error_threshold = user_data[1]
            user_version = user_data[2]
            if(error > user_error_threshold):
                # Start asynch task to generate, inform user that it is being done
    #            generate = Thread(target=generate_model, args=(user_imei,user_version,model_db,))
    #            generate.start()
    #            generate_model(user_imei,user_version,model_db)
                return HttpResponse(UPDATE_MODEL_RESP)
            else:
                return HttpResponse(IN_ERR_RANGE_RESP)
    else:
        model_db.query('INSERT INTO user_models (imei,vers) VALUES(' + imei + ',0);')
        generate_model(user_imei,0,model_db)
        #generate = Thread(target=generate_model, args=(user_imei,0,model_db))
        #generate.start()
        return HttpResponse("Is this right.")

def request_model(request, imei):
    current_version = request.POST['version']
    # Open database connection
    model_db = _mysql.connect('localhost','root','neslrocks!','service')
    model_db.query('SELECT * FROM user_models')
    raw = model_db.store_result()
    table_size = raw.num_rows()
    
    model_exists = False
    # row return format (,(imei,error_threshold,version,model,updating))
    for _ in range(table_size):
        user_data = raw.fetch_row()[0]
        user_imei = user_data[0]
        if(user_imei == imei):
            model_exists = True
            model_version = user_data[2]
            model_update = user_data[4]
            if(model_update == 1):
                return HttpResponse(MODEL_UPDATING_RESP) # something to indic
            elif(model_version > current_version):
                #user_model = user_data[3]
                return send_model(imei)
            else:
                return HttpResponse(NO_NEW_MODEL_RESP)
    return HttpResponse("No model found.")

def send_model(imei):
    mimetypes.init()
    try:
        file_path = '/opt/systemsens/service/visualization/REU/models/' + imei + '.model'
        fsock = open(file_path,'rb')
        file_name = os.path.basename(file_path)
        mimetype_guess = mimetypes.guess_type(file_name)
        if mimetype_guess is not None:
            response = HttpResponse(fsock, mimetype=mimetype_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' + file_name
    except IOError:
        return HttpResponseNotFound()
    return response
# not a clean way to do this, will be updated later

def update_db(imei,update_var,update_val,database):
    value = str(update_val)
    try:
        int(update_val)
    except ValueError:
        value = "'" + value + "'"
    database.query("UPDATE user_models SET " + update_var + "=" + value + " WHERE imei='" + imei + "';")

def generate_model(imei,version,database):
    # move python files to a more local place and have them run analysis every night
    # when models need to be generated, access file based on IMEI and channel through WEKA
    # retrieve WEKA model and create a JSON object that holds the 'tweaking' factors
    # find location in database and put model in there, update error thresholds and version number
    # Set updating flag
    #update_db(imei,'updating',1,database)
    # Run file to generate ARFF, then call weka classifier.
    #analyze.feature_generation(imei)
    # Call WEKA classification and update server file
    #subprocess.call(['./REU/run_model.sh',imei])
    # Unset updating flag, update version/error_threshold (doing this here for speed)
    version += 1
    #update_db(imei,'version',version,database)
    #update_db(imei,'updating',0,database)
# END REU SUMMER CODE
