/**
 * SystemSens
 *
 * Copyright (C) 2009 Hossein Falaki
 */

package edu.ucla.cens.systemsens;


import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;


import edu.ucla.cens.systemsens.util.ModelManagerWakeLock;


/**
 * Logs polling sensors.
 *
 * @author      Hossein Falaki
 */
public class ModelUpdateReceiver extends BroadcastReceiver 
{

    private static final String TAG = "ModelUpdateAlarmReceiver";


    @Override
    public void onReceive(Context context, Intent intent)
    {
        // Acquire a lock
    	Log.i(TAG,"Alarm");
        ModelManagerWakeLock.acquireCpuWakeLock(context);

        Intent newIntent = new Intent(context, SystemSens.class);
        newIntent.setAction(SystemSens.UPDATE_ACTION);

        context.startService(newIntent);
    }

}

