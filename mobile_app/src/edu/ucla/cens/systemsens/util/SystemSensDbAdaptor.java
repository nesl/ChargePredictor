/**
 * SystemSensDbADaptor
 *
 * Copyright (C) 2009 Hossein Falaki
 */
package edu.ucla.cens.systemsens.util;


import org.json.JSONObject;
import org.json.JSONException;

import java.text.SimpleDateFormat;
import java.util.Locale;
import java.util.Calendar;
import java.util.HashSet;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.SQLException;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteStatement;
import android.os.PowerManager;


//import android.util.Log;
import edu.ucla.cens.systemlog.Log;

import edu.ucla.cens.systemsens.SystemSens;

/**
 * Simple  database access helper class. 
 * Interfaces with the SQLite database to store system information.
 * Written based on sample code provided by Google.
 *
 * @author Hossein Falaki
 */
public class SystemSensDbAdaptor 
{


    private static final String VER = SystemSens.VER;
    private static final String IMEI = SystemSens.IMEI;

    public static final String KEY_DATARECORD = "datarecord";
    public static final String KEY_ROWID = "_id";
    public static final String KEY_TYPE = "recordtype";
    public static final String KEY_TIME = "recordtime";


    private static final String TAG = "SystemSensDbAdapter";
    private DatabaseHelper mDbHelper;
    private SQLiteDatabase mDb;

    private long mDbBirthDate;
    
    /** Database creation sql statement */
    private static final String DATABASE_CREATE =
            "create table systemsens (_id integer primary key "
           + "autoincrement, recordtime text not null, " 
           + "recordtype text not null, datarecord text not null);";


    private static final String DATABASE_DROP = 
        "DROP TABLE IF EXISTS systemsens";
    
    
    private static final String DATABASE_NAME = "data";
    private static final String DATABASE_TABLE = "systemsens";
    private static final int DATABASE_VERSION = 4;

    private static final long ONE_MINUTE = 1000 * 60;
    private static final long ONE_HOUR = 60 * ONE_MINUTE;
    private static final long ONE_DAY = 24 * ONE_HOUR;

    private static final long MIN_TICKLE_INTERVAL = ONE_HOUR;



    private SimpleDateFormat mSDF;

    private HashSet<ContentValues> mBuffer;
    private HashSet<ContentValues> tempBuffer;

    private boolean mOpenLock = false;
    private boolean mFlushLock = false;


    //private final Context mCtx;
    private final PowerManager.WakeLock mWL;
    private final SystemSens mSystemSens;

    private static class DatabaseHelper extends SQLiteOpenHelper 
    {

        DatabaseHelper(Context context) 
        {
            super(context, DATABASE_NAME, null, DATABASE_VERSION);
        }

        @Override
        public void onCreate(SQLiteDatabase db) 
        {
            db.execSQL(DATABASE_CREATE);
        }

        @Override
        public void onUpgrade(SQLiteDatabase db, int oldVersion, 
                int newVersion) 
        {
            Log.w(TAG, "Upgrading database from version " 
                    + oldVersion + " to "
                    + newVersion + ", which will destroy all old data");

            db.execSQL(DATABASE_DROP);
            onCreate(db);
        }
    }

    /**
     * Constructor - takes the context to allow the database to be
     * opened/created
     * 
     * @param   systesens   SystemSens object
     */
    public SystemSensDbAdaptor(SystemSens systemsens) 
    {
        //this.mCtx = systemsens;
        this.mSystemSens = systemsens;
        mBuffer = new HashSet<ContentValues>(); 

        PowerManager pm = (PowerManager)
            mSystemSens.getSystemService(Context.POWER_SERVICE);

        mWL = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
                TAG);
        mWL.setReferenceCounted(false);

        mSDF = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US);


        mDbBirthDate = 0L;

    }

    /**
     * Open the database.
     * If it cannot be opened, try to create a new instance of the
     * database. If it cannot be created, throw an exception to signal
     * the failure.
     * 
     * @return this         (self reference, allowing this to be
     *                      chained in an initialization call)
     * @throws SQLException if the database could be neither opened or
     *                      created
     */
    public synchronized SystemSensDbAdaptor open() throws SQLException 
    {
        if (!mFlushLock)
        {
            mDbHelper = new DatabaseHelper(mSystemSens);
            mDb = mDbHelper.getWritableDatabase();
        }
        mOpenLock = true;
        return this;
    }
    
    /**
      * Closes the database.
      */
    public synchronized void close() 
    {
        if (!mFlushLock)
        {
            mDb.close();
            mDbHelper.close();
        }
        mOpenLock = false;
    }


    /**
      * Cause the database adaptor to drop the table and clreate it
      * again. This hack is necessary to prevent the index values from
      * getting too large. When the DB is created the index starts
      * from 0.
      * This method assumes that the database has been opened.
      */
    public synchronized void tickle()
    {

        if (!mOpenLock)
            return;


        long curTime = Calendar.getInstance().getTimeInMillis();
        
        if (curTime - mDbBirthDate < MIN_TICKLE_INTERVAL)
            return;


        SQLiteStatement countQuery = mDb.compileStatement(
                "SELECT COUNT (*) FROM " + DATABASE_TABLE + ";");

        long count = countQuery.simpleQueryForLong();

        if (count == 0)
        {
            Log.i(TAG, "Dropping the table.");
            mDb.execSQL(DATABASE_DROP);

            Log.i(TAG, "Creating a new table.");
            mDb.execSQL(DATABASE_CREATE);

            mDbBirthDate = curTime;
        }
    }


    /**
     * Create a new entry using the datarecord provided. 
     * If the entry is successfully created returns the new rowId for
     * that entry, otherwise returns a -1 to indicate failure.
     * 
     * @param datarecord        datarecord for the entry
     */
    public synchronized void createEntry(JSONObject data, String type) 
    {

        JSONObject dataRecord = new JSONObject();

        // First thing, get the current time
        Calendar cal = Calendar.getInstance();

        String timeStr = mSDF.format(cal.getTime());



        try
        {
            dataRecord.put("date", timeStr);
            dataRecord.put("time_stamp", cal.getTimeInMillis());
            dataRecord.put("user", IMEI);
            dataRecord.put("type", type);
            dataRecord.put("ver", VER);
            dataRecord.put("data", data);
        }
        catch (JSONException e)
        {
            Log.e(TAG, "Exception", e);
        }


        String recordStr = dataRecord.toString();

        ContentValues initialValues = new ContentValues();
        initialValues.put(KEY_TIME, timeStr);
        initialValues.put(KEY_TYPE, type);
        initialValues.put(KEY_DATARECORD, recordStr );

        mBuffer.add(initialValues);

        if (mSystemSens.hasContextReceivers())
            mSystemSens.broadcast(recordStr);

        //android.util.Log.i(TAG, dataRecord.toString());

    }


    public synchronized void flushDb()
    {
       tempBuffer = mBuffer;
       mBuffer = new HashSet<ContentValues>(); 

        Thread flushThread = new Thread()
        {
            public void run()
            {
                mWL.acquire();

                if (!mOpenLock)
                {
                    try
                    {
                        mDbHelper = new DatabaseHelper(mSystemSens);
                        mDb = mDbHelper.getWritableDatabase();
                    }
                    catch (SQLException se)
                    {
                        Log.e(TAG, "Could not open DB helper", se);

                    }
                }
                mFlushLock = true;


                Log.i(TAG, "Flushing " 
                        + tempBuffer.size() + " records.");

                try
                {
                    for (ContentValues value : tempBuffer)
                    {
                        mDb.insert(DATABASE_TABLE, null, value);
                    }
                }
                catch (IllegalStateException ilse)
                {
                    Log.e(TAG, "Exception inserting. Trying later.",
                            ilse);
                    mBuffer = tempBuffer;
                }


                if (!mOpenLock)
                {
                    mDb.close();
                    mDbHelper.close();
                }

                mFlushLock = false;
                mWL.release();
            }
        };

        flushThread.start();

    }

    /**
     * Deletes the entry with the given rowId
     * 
     * @param rowId         id of datarecord to delete
     * @return              true if deleted, false otherwise
     */
    public synchronized boolean deleteEntry(long rowId) 
    {
        return mDb.delete(DATABASE_TABLE, KEY_ROWID 
                + "=" + rowId, null) > 0;
    }


    /**
     * Deletes the entries in a range.
     * 
     * @param fromId         id of first datarecord to delete
     * @param toId           id of last datarecord to delete
     * @return              true if deleted, false otherwise
     */
    public synchronized boolean deleteRange(long fromId, long toId) 
    {
        return mDb.delete(DATABASE_TABLE, KEY_ROWID 
                + " BETWEEN " 
                + fromId
                + " AND " 
                + toId, null) > 0;
    }


    /**
     * Returns a Cursor over the list of all datarecords in the database
     * 
     * @return              Cursor over all notes
     */
    public Cursor fetchAllEntries() 
    {

        return mDb.query(DATABASE_TABLE, new String[] {KEY_ROWID,
                KEY_TIME, KEY_TYPE, KEY_DATARECORD}, 
                null, null, null, null, null);
    }

    /**
     * Returns a Cursor positioned at the record that matches the
     * given rowId.
     * 
     * @param  rowId        id of note to retrieve
     * @return              Cursor positioned to matching note, if found
     * @throws SQLException if note could not be found/retrieved
     */
    public Cursor fetchEntry(long rowId) throws SQLException 
    {

        Cursor mCursor = mDb.query(true, DATABASE_TABLE, new String[]
                {KEY_ROWID, KEY_TIME, KEY_TYPE, KEY_DATARECORD}, 
                KEY_ROWID + "=" + rowId,
                null, null, null, null, null);
        if (mCursor != null) {
            mCursor.moveToFirst();
        }
        return mCursor;

    }


}
