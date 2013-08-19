/**
 * SystemSens
 *
 * Copyright (C) 2009 Hossein Falaki
 */
package edu.ucla.cens.systemsens.util;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.database.SQLException;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import java.lang.ProcessBuilder;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.Calendar;
import java.util.Scanner;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.File;
import java.io.PrintWriter;
import java.io.FileNotFoundException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.io.BufferedInputStream;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.StringWriter;

import org.apache.http.util.EntityUtils;

//import android.util.Log;
import edu.ucla.cens.systemlog.Log;

import edu.ucla.cens.systemsens.SystemSens;

/**
 * This class implements mechanisms to upload data collected by SystemSens to
 * Sensorbase (or any other repository). It is passed a pointer to a Database
 * Adaptor object upon creation. Each time the upload() method is called a new
 * thread is spawned. The new thread will read all the records in the database
 * and uploaded and then delete them.
 * 
 * @author Hossein Falaki
 */
public class Uploader {
	/** Tag used for log messages */
	private static final String TAG = "SystemSensUploader";
	private static int count = 0;

	/** Database adaptor object */
	private SystemSensDbAdaptor mDbAdaptor;
	
	private Context context;
	private ConnectivityManager connManager;
	private NetworkInfo mWifi;
	private Scanner scan;
	private InputStream input;

	/**
	 * Maximum number of records that will be read and deleted at a time
	 */
	private static final int MAX_UPLOAD_SIZE = 200;

	/** After this number of failures upload will abort */
	private static final int MAX_FAIL_COUNT = 50;

	/** Upload location of the SystemSens server */
	private static final String CUSTOM_URL = "http://128.97.93.158/service/viz/put/";

	private static final String IMEI = SystemSens.IMEI;

	private static final String mTableName = "systemsens";
	
	
	/**
	 * Constructor - creates an Uploader object with access to the given
	 * database adaptor object.
	 * 
	 * @param dbAdaptor
	 *            database adaptor object
	 */
	public Uploader(SystemSensDbAdaptor dbAdaptor, Context context) {
		this.mDbAdaptor = dbAdaptor;
		this.context = context;
		connManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
	}

	public void tryUpload(boolean isForced) {

		Log.i(TAG, "tryUpload started");
		Cursor c = null;
		boolean postResult = false;
		boolean noError = true;

		try {
			mDbAdaptor.open();

			c = mDbAdaptor.fetchAllEntries();
			int dataIndex = c
					.getColumnIndex(SystemSensDbAdaptor.KEY_DATARECORD);
			int idIndex = c.getColumnIndex(SystemSensDbAdaptor.KEY_ROWID);
			int timeIndex = c.getColumnIndex(SystemSensDbAdaptor.KEY_TIME);
			int typeIndex = c.getColumnIndex(SystemSensDbAdaptor.KEY_TYPE);

			Integer id, pId;
			HashSet<Integer> keySet = new HashSet<Integer>();
			String newRecord, newType, newTime;
			String line;
			ArrayList<String> content;

			int failCount = 0;
			int dbSize = c.getCount();
			int readCount = 0;
			
			c.moveToFirst();
			Log.i(TAG, "Forced? " + isForced);
			
			/** Confirm all data transfers are through WiFi only **/
			if(!handleWifi())
				return;
			
			while ((dbSize > 0) && (SystemSens.isPlugged() || isForced) && noError) {

				Log.i(TAG, "Total DB size is: " + dbSize);
				int maxCount = (MAX_UPLOAD_SIZE > dbSize) ? dbSize
						: MAX_UPLOAD_SIZE;
				
				content = new ArrayList<String>();
				pId = -1;

				for (int i = 0; i < maxCount; i++) {

					id = c.getInt(idIndex);
					if ((pId != -1) && (id != (pId + 1))) {
						Log.i(TAG, "Cursor jumped.");
						noError = false;
						break;
					}
					newRecord = c.getString(dataIndex);

					content.add(URLEncoder.encode(newRecord));
					keySet.add(id);
					readCount++;
					pId = id;

					c.moveToNext();

				}

				dbSize -= readCount;	// Shouldn't this just be c.getCount()?
				//dbSize = c.getCount();
				
				do {
					postResult = doPost("data=" + content.toString(),
							CUSTOM_URL);
					if (postResult) {
						failCount = 0;
						long fromId = Collections.min(keySet);
						long toId = Collections.max(keySet);
						Log.i(TAG, "Deleting [" + fromId + ", " + toId + "]");

						if (!mDbAdaptor.deleteRange(fromId, toId)) {
							Log.e(TAG, "Error deleting rows");
						}

					} else {
						Log.e(TAG, "Post failed");
						failCount++;
					}
					keySet.clear();
				} while ((!postResult) && (failCount < MAX_FAIL_COUNT));
				
				if (failCount > MAX_FAIL_COUNT) {
					Log.e(TAG, "Too many post failures. "
							+ "Will try at another time");
					c.close();
					mDbAdaptor.close();
					return;
				}

			}

			c.close();

			// Tickle the DB
			mDbAdaptor.tickle();
			mDbAdaptor.close();

		} catch (Exception e) {
			Log.e(TAG, "Exception", e);
			Log.i(TAG, "Will resume upload later");

			if (c != null) {
				c.close();
			}
			mDbAdaptor.close();
		}
		connManager.setNetworkPreference(ConnectivityManager.DEFAULT_NETWORK_PREFERENCE);

	}

	private boolean doPost(String content, String dest) {
		OutputStream out;
		byte[] buff;
		int respCode;
		String respMsg = "";
		HttpURLConnection con;
		URL url;
		try {
			url = new URL(dest);
		} catch (MalformedURLException e) {
			Log.e(TAG, "Exception", e);
			return false;
		}

		try {
			con = (HttpURLConnection) url.openConnection();
		} catch (IOException e) {
			Log.e(TAG, "Exception", e);
			return false;
		}

		try {
			con.setRequestMethod("POST");
		} catch (java.net.ProtocolException e) {
			Log.e(TAG, "Exception", e);
			return false;
		}
		con.setUseCaches(false);
		con.setDoOutput(true);
		con.setDoInput(true);
		con.setRequestProperty("Content-type",
				"application/x-www-form-urlencoded");

		try {
			con.connect();
			out = con.getOutputStream();
			buff = content.getBytes("UTF8");
			out.write(buff);
			out.flush();
			
			respMsg = con.getResponseMessage();
			respCode = con.getResponseCode();
			
			/* Grabs string from Django HttpResponse. */
			
			input = con.getInputStream();
			scan = new Scanner(input).useDelimiter("\\A");
			String mesg = (scan.hasNext()) ? scan.next() : "";
			Log.i("Django", "Message recieved from Django (" + respCode + "): " + mesg);
			
		} catch (IOException e) {
			Log.e(TAG, "Exception", e);
			con.disconnect();
			return false;
		}

		if (respCode == HttpURLConnection.HTTP_OK) {
			con.disconnect();
			return true;
		} else {
			Log.e(TAG, "post failed with error: " + respMsg);
			con.disconnect();
			return false;
		}
	}
	
	/**
	 * Returns state of Wi-Fi connection, with network preference forced on Wi-Fi.
	 * This does not explicitly guarantee that no data will be sent over cell network.
	 **/
	private boolean handleWifi(){
		mWifi = connManager.getNetworkInfo(ConnectivityManager.TYPE_WIFI);
		if(!mWifi.isConnected())
			return false;
		Log.i("PRASHANTH","Connected! Setting preference to WIFI");
		connManager.setNetworkPreference(ConnectivityManager.TYPE_WIFI);
		return true;
	}
}

