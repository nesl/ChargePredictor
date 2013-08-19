/**
 * SystemSens
 *
 * Copyright (C) 2009 Hossein Falaki
 */

package edu.ucla.cens.systemsens.util;


import android.content.Context;
import android.os.PowerManager;
import android.util.Log;

/**
 * Manages a static WakeLock to gaurantee that the phone
 * does not go to sleep before SystemSens Service is started
 * by the Alarm BroadcastReceiver.
 * 
 *
 * @author      Hossein Falaki
 */
public class ModelManagerWakeLock 
{

    private static final String TAG = "ModelManagerWakeLock";

    private static PowerManager.WakeLock sCpuWakeLock;


    public static void acquireCpuWakeLock(Context context)
    {
        Log.i(TAG, "Acquiring cpu wake lock");

        if (sCpuWakeLock != null)
            return;


        PowerManager pm = (PowerManager) context.getSystemService(
                Context.POWER_SERVICE);
        sCpuWakeLock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK, 
                "ModelManagerLock");

        sCpuWakeLock.acquire();

    }


    public static void releaseCpuLock()
    {
        Log.i(TAG, "Releaseing cpu wake lock");

        if (sCpuWakeLock != null)
        {
            sCpuWakeLock.release();
            sCpuWakeLock = null;
        }
    }




}

