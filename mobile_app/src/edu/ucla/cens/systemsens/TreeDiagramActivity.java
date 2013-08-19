package edu.ucla.cens.systemsens;

import java.util.ArrayList;

import edu.ucla.cens.systemsens.SystemSens.LocalBinder;
import android.R.color;
import android.app.AlertDialog;
import android.app.ListActivity;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.ListView;
import android.widget.Toast;

public class TreeDiagramActivity extends ListActivity {

	private static ArrayList<Option> OPTIONS = new ArrayList<Option>(2);

	private Intent mIntent;
	private SystemSens mService;
	private boolean serviceActive;
	private static final String PREF_FILE = "SystemSens_Preferences";
	private static final String SERVICE_STATE = "SERVICE_STATE";
	private static final String FIRST_RUN = "FIRST_RUN";
	private static final String VERSION = "1.01";
	private SharedPreferences settings;
	private SharedPreferences.Editor settingsEditor;
	private SystemAdapter sysadap;
	private boolean firstrun;
	
	public int bindCall = 0;
	private static final int FORCE_UPLOAD = 0;
	private static final int FETCH_SIZE = 1;
	private static final int UPDATE_MODEL = 2;
	private static final int WRITE_TO_FILE = 3;
	
	private AlertDialog alertDialog;
	public AlertDialog recordDialog;
	private Context context;

	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		requestWindowFeature(Window.FEATURE_INDETERMINATE_PROGRESS);
		
		setTitle("Tree Diagram Options - " + VERSION);
		sysadap = new SystemAdapter(this, OPTIONS);
		setListAdapter(sysadap);
		
		context = getApplicationContext();
		
		AlertDialog.Builder adb = new AlertDialog.Builder(this)
			.setTitle("Service Disabled")
			.setMessage("This action cannot be completed while the service is disabled.")
			.setPositiveButton("Cancel", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog,int id) {
					}
				});
		alertDialog = adb.create();
		
		AlertDialog.Builder records = new AlertDialog.Builder(this)
		.setTitle("Database Report")
		.setPositiveButton("Cancel", new DialogInterface.OnClickListener() {
				public void onClick(DialogInterface dialog,int id) {
				}
			});
		
		recordDialog = records.create();
		
		mIntent = new Intent(this, SystemSens.class);
		mIntent.setAction(SystemSens.POLLSENSORS_ACTION);
		
		settings = this.getSharedPreferences(PREF_FILE,0);
		settingsEditor = settings.edit();
		
		firstrun = settings.getBoolean(FIRST_RUN, true);
		Log.i("PRASHANTH","First run: " + firstrun);
		if(firstrun){
			addShortcut(getApplicationContext());
			firstrun = false;
		}
	}
	
	private void addShortcut(Context context) {
	    Intent shortcutIntent = new Intent(context,TreeDiagramActivity.class);
	    shortcutIntent.setAction(Intent.ACTION_MAIN);
	 
	    Intent addIntent = new Intent();
	    addIntent.putExtra(Intent.EXTRA_SHORTCUT_INTENT, shortcutIntent);
	    addIntent.putExtra(Intent.EXTRA_SHORTCUT_NAME, context.getString(R.string.app_name));
	    addIntent.putExtra(Intent.EXTRA_SHORTCUT_ICON_RESOURCE,
	            Intent.ShortcutIconResource.fromContext(context,R.drawable.ss));
	    addIntent.setAction("com.android.launcher.action.INSTALL_SHORTCUT");
	    addIntent.putExtra("duplicate", false);
	    
	    context.sendBroadcast(addIntent);
	}
	
	public void createList(){
		OPTIONS.clear();
		if(serviceActive)
			OPTIONS.add(new Option(context.getString(R.string.enabled_text), context.getString(R.string.enabled_marq)));
		else
			OPTIONS.add(new Option(context.getString(R.string.disabled_text), context.getString(R.string.disabled_marq)));
		
		OPTIONS.add(new Option("Force Upload", "Ignores charging state and uploads stored data."));
		OPTIONS.add(new Option("Existing Holds","Checks database size and returns entry count."));
		OPTIONS.add(new Option("Update Model","Experimental method to display prediction model."));
		OPTIONS.add(new Option("Flush Unclassifieds","Write unclassified instances to file."));
		OPTIONS.add(new Option("Test Classifier","Try random classification to test."));
	}

	@Override
	protected void onListItemClick(ListView l, View v, int position, long id) {

		if (position == 0) { /* TOGGLE SYSTEMSENS SERVICE */
			if (serviceActive) {
				Toast.makeText(this, "Stopping SystemSens.", Toast.LENGTH_SHORT).show();
				stopService(mIntent);
				toggleEnableText();
			} else {
				Toast.makeText(this, "Starting SystemSens.", Toast.LENGTH_SHORT).show();
				startService(mIntent);
				toggleEnableText();
			}
			serviceActive = !serviceActive;
			settingsEditor.putBoolean(SERVICE_STATE, serviceActive);
			settingsEditor.commit();
		} else if(position == 1) {
			if(serviceActive){
				setIndeterminatePB(true);
				bindCall = FORCE_UPLOAD;
				bindService(mIntent, mConnection, Context.BIND_AUTO_CREATE);
				Toast.makeText(this, "Forcing upload of records to NESL Server.", Toast.LENGTH_SHORT).show();
				Log.i("PRASHANTH","Binding to service.");
			}
			else{
				alertDialog.show();
			}
		} else if(position == 2) {
			if(serviceActive){
				setIndeterminatePB(true);
				bindCall = FETCH_SIZE;
				bindService(mIntent, mConnection, Context.BIND_AUTO_CREATE);
				Log.i("PRASHANTH","Binding to service.");
			}
			else{
				alertDialog.show();
			}
		}
		else if(position == 3){
			//this.startActivity(new Intent(this, ViewActivity.class));
			if(serviceActive){
				setIndeterminatePB(true);
				bindCall = UPDATE_MODEL;
				bindService(mIntent, mConnection, Context.BIND_AUTO_CREATE);
				Log.i("PRASHANTH","Binding to service.");
			}
			else{
				alertDialog.show();
			}
		}
		else if(position == 4){
			if(serviceActive){
				setIndeterminatePB(true);
				bindCall = WRITE_TO_FILE;
				bindService(mIntent, mConnection, Context.BIND_AUTO_CREATE);
				Log.i("PRASHANTH","Binding to service.");
			}
			else{
				alertDialog.show();
			}
		}
		else if(position == 5){
			if(serviceActive){
				bindCall = 4;
				bindService(mIntent, mConnection, Context.BIND_AUTO_CREATE);
				Log.i("PRASHANTH","Binding to service.");
			}
			else{
				alertDialog.show();
			}
		}
	}
	
	@Override
	protected void onStart() {
		super.onStart();
		
		serviceActive = settings.getBoolean(SERVICE_STATE, false);
		
		Log.i("PRASHANTH","onStart() was called, with service state " + serviceActive);
		
		createList();
	};
	
	@Override
	protected void onStop() {
		super.onStop();
		settingsEditor.clear();
		settingsEditor.putBoolean(FIRST_RUN, firstrun);
		settingsEditor.putBoolean(SERVICE_STATE, serviceActive);
		settingsEditor.apply();
	}

	ServiceConnection mConnection = new ServiceConnection() {

		@Override
		public void onServiceDisconnected(ComponentName name) {
			serviceActive = false;
			mService = null;
		}

		@Override
		public void onServiceConnected(ComponentName name, IBinder service) {
			serviceActive = true;
			LocalBinder mLocalBinder = (LocalBinder) service;
			mService = mLocalBinder.getService();
			Log.i("PRASHANTH","Service Connected. Retrieved Service.");
			
			switch(bindCall){
			case FORCE_UPLOAD:
				mService.callupload();
				Log.i("PRASHANTH","Upload called, unbinding from service.");
				break;
			case FETCH_SIZE:
				recordDialog.setMessage("Records: " + mService.getDataBaseSize() + "\nLast recording time: " + mService.getLastRecordTime());
				recordDialog.show();
				//Toast.makeText(getApplicationContext(), "Database entries: " + mService.getDataBaseSize(), Toast.LENGTH_SHORT).show();
				Log.i("PRASHANTH","DB Size fetched, unbinding from service.");
				break;
			case UPDATE_MODEL:
				mService.updateModel();
				Toast.makeText(getApplicationContext(), "Trying to get model.", Toast.LENGTH_SHORT).show();
				Log.i("PRASHANTH","Update called, unbinding from service.");
				break;
			case WRITE_TO_FILE:
				mService.writeToFile();
				Toast.makeText(getApplicationContext(), "Flushing unclassifieds.", Toast.LENGTH_SHORT).show();
				Log.i("PRASHANTH","Update called, unbinding from service.");
				break;
			case 4:
				Toast.makeText(getApplicationContext(), "Classify: " + mService.tryClassify(), Toast.LENGTH_LONG).show();
				Log.i("PRASHANTH","Update called, unbinding from service.");
				break;
			}
			
			unbindService(mConnection);
			Log.i("PRASHANTH","Service unbound.");
			
			setIndeterminatePB(false);
		}
	};
	
	public void toggleEnableText(){
		// If it is CURRENTLY active >> meaning transitioning into disabled state
		if(serviceActive){
			OPTIONS.get(0).feature = context.getString(R.string.disabled_text);
			OPTIONS.get(0).marquee = context.getString(R.string.disabled_marq);
		}
		else{
			OPTIONS.get(0).feature = context.getString(R.string.enabled_text);
			OPTIONS.get(0).marquee = context.getString(R.string.enabled_marq);
		}
		sysadap.notifyDataSetChanged();
	}
	
	/* Accessor method for service connection */
	public void setIndeterminatePB(boolean visible){
		setProgressBarIndeterminate(visible);
		setProgressBarIndeterminateVisibility(visible);
	}
}