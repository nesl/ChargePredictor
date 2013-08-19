/**
 * SystemSensLite
 *
 * Copyright (C) 2009 Hossein Falaki
 */

package edu.ucla.cens.systemsens;


import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;



/**
 * Starts the SystemSens Service at boot time.
 *
 * @author      Hossein Falaki
 */
public class SystemSensStartup extends BroadcastReceiver 
{

    private static final String TAG = "SystemSensStartup";
    public static final String PREF_FILE = "SystemSens_Preferences";

    @Override
    public void onReceive(Context context, Intent intent)
    {
    	SharedPreferences settings = context.getSharedPreferences(PREF_FILE, 0);
    	boolean serviceActive = settings.getBoolean("SERVICE_STATE", false);
    	//Log.i("PRASHANTH","" + settings.getBoolean("BIND STATE", true));
        //context.startService(new Intent(context, 
        //            SystemSens.class));
    	
    	if(serviceActive){
    		context.startService(new Intent(context,SystemSens.class));
    		Log.i(TAG, "Started SystemSens");
    	}
    }
}

