/**
 * ModelManager.java - Prashanth Swaminathan - July 2013
 * 
 * Helper class that is periodically called through SystemSens service.
 * SystemSens runs ModelManager as separate thread, and will not wait
 * for response. ModelManager will send requests to Apache server's get_model
 * and wait until model is retrieved. Model processing will be processed
 * depending on the RANDOM_TREE settings:
 * 		- true: processing will be handed to TreeManager class.
 * 		- false: processing will be done with Weka's classifier.
 * 
 * ModelManager can also be requested for classifications of BatteryObjects.
 */
package edu.ucla.cens.systemsens;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Scanner;

import weka.classifiers.Classifier;
import weka.core.Attribute;
import weka.core.DenseInstance;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ArffLoader.ArffReader;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Environment;
import android.util.Log;

public class ModelManager{
	private static final boolean RANDOM_TREE = true;
	private static final String TAG = "Model Manager";
	private static final String CUSTOM_URL = "http://128.97.93.158/service/viz/get_model/";
	private static final int FAIL_COUNT = 100;
	private final int SECONDS_IN_WEEK = 604800;
	private final double ERROR_THRESHOLD;
	private static String IMEI;
	private static String MODEL_WRITTEN = "Model Written.";
	private Classifier wekaClassifier;
	private Instances dataset;
	private ArrayList<Attribute> attributeList;
	private ArrayList<BatteryObject> day_data;
	private ArrayList<BatteryObject> unclass;
	private int version = 0;
	private File model_file;
	private Context context;
	private ConnectivityManager connManager;
	private NetworkInfo mWifi;
	private boolean file_written = false;
	private TreeManager tree_manager;
	private String global_tree;
	
	public ModelManager(Context context, double error, String imei){
		this.context = context;
		connManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
		ERROR_THRESHOLD = error;
		IMEI = imei;
		wekaClassifier = null;
		dataset = null;
		model_file = Environment.getExternalStorageDirectory();
		model_file = new File(model_file.getAbsolutePath() + "/model");
		model_file.mkdir();
		model_file = new File(model_file, "model_" + imei + ".model");
	}
	
	/** 
	 * Data gathered over the week and unclassified data is cloned for analysis.
	 * Get prediction error and only request model from server if threshold is
	 * passed, and then return model update status. Status will be used to determine
	 * whether to flush data from SystemSens.
	 */
	
	@SuppressWarnings("unchecked")
	public boolean startUpdate(ArrayList<BatteryObject> day_data, ArrayList<BatteryObject> general_unclass){
		
		this.day_data = (ArrayList<BatteryObject>)day_data.clone();
		this.unclass = (ArrayList<BatteryObject>)general_unclass.clone();
		
		if(day_data == null || day_data.size() == 0 || unclass == null)
			return false;
		
		double error = getPredictionError();
		Log.i(TAG,"Error: " + error);
		
		if(error > ERROR_THRESHOLD)
			return attemptUpdate(false);
		return false;
	}
	
	/**
	 * Helper function, can be called from UI to update model without
	 * checking if ERROR_THRESHOLD was met.
	 * @return
	 */
	
	public boolean forceUpdateModel(){
		Log.i(TAG,"Forcing update.");
		return attemptUpdate(true);
	}
	
	/**
	 * If model has been received, known attributes are packaged into
	 * DenseInstance and classified. Whether classifier exists must be
	 * checked first. If RandomTree/tree-based models are used, classification
	 * is given to the TreeManager.
	 */
	
	public int getClassification(BatteryObject instance){
		if(RANDOM_TREE){
			if(tree_manager != null){
				int res = tree_manager.classify(instance);
				Log.i(TAG,"Instance( time = " + instance.time_stamp + "; charging_status = " + instance.charging_status
						+ "; current_level = " + instance.current_level + "; length_of_last_charge = " + instance.length_of_last_charge
						+ "; time_of_last_charge = " + instance.time_of_last_charge + "; last_level = " + instance.last_level
						+ "\nClassified as: " + res);
				return res;
			}
			return -1;
		}
		
		if(wekaClassifier == null || dataset == null)
			initializeClassificationScheme();
		if(wekaClassifier == null){
			Log.i(TAG,"Classifier still null.");
			return -1;
		}
		// Clear dataset of any previous dense instances
		dataset.delete();
		
		// Create new instance to classify
		Instance point = new DenseInstance(dataset.numAttributes());
		point.setDataset(dataset);
		dataset.add(point);
		
		// Set attribute values (in the order as they appear in the header)
		// Define the missing point (you should also say 'dataset.setClassIndex(dataset.numAttributes() - 1)'
		point.setValue(0, instance.time_stamp);
		point.setValue(1, instance.charging_status);
		point.setValue(2, instance.current_level);
		point.setValue(3, instance.length_of_last_charge);
		point.setValue(4, instance.time_of_last_charge);
		point.setValue(5, instance.last_level);
		point.setMissing(6);
		
		// Attempt to classify using Weka model.
		int result = -1;
		try {
			result = (int)wekaClassifier.classifyInstance(point);
		} catch (Exception e) {
			e.printStackTrace();
		}
		Log.i(TAG,"Instance( time = " + instance.time_stamp + "; charging_status = " + instance.charging_status
				+ "; current_level = " + instance.current_level + "; length_of_last_charge = " + instance.length_of_last_charge
				+ "; time_of_last_charge = " + instance.time_of_last_charge + "; last_level = " + instance.last_level
				+ "\nClassified as: " + result);
		return result;
	}
	
	/**
	 * Determines prediction error of data collected today. (Passed through array)
	 * Checks that battery prediction matches ground truth.
	 * THIS METHOD IS A VERY NAIVE CHECK. It does not account for the ability of the model
	 * to correct to changing behavior. A more intelligent check would be to see whether
	 * the predictions before the charging session changed to match.
	 * Returns percentage error of predictions.
	 */
	
	private double getPredictionError(){
		if(day_data.size() == 0){			// return 100% error if not initialized.
			return 1.0;
		}
		
		int data_size = day_data.size();
		int time = 0;
		
		int[] predicted_quarters = new int[data_size];
		int quartersInWeek = 4*24*7;
		boolean[] quarterCharge = new boolean[quartersInWeek];
		BatteryObject inst;
		
		for(int data = 0; data < data_size; data++){
			inst = day_data.get(data);
			predicted_quarters[data] = inst.prediction_quarter;
			if(inst.charging_status == BatteryObject.CHARGING_AC || inst.charging_status == BatteryObject.CHARGING_USB){
				time = convertToWeekTime(inst.time_stamp)/900;
				quarterCharge[time] = true;
			}
		}
		
		int unclass_size = unclass.size();
		for(int data = 0; data < unclass_size; data++){
			inst = unclass.get(data);
			if(inst.charging_status == BatteryObject.CHARGING_AC || inst.charging_status == BatteryObject.CHARGING_USB){
				time = convertToWeekTime(inst.time_stamp)/900;
				quarterCharge[time] = true;
			}
		}
		
		int correctlyClassified = 0;
		for(int data = 0; data < data_size; data++){
			if(quarterCharge[predicted_quarters[data]])
				correctlyClassified++;
		}
		
		double error_absolute = 1 - (((double)correctlyClassified)/data_size);
		
		return error_absolute;
	}
	
	/**
	 * Connection method to update model. "force" makes model update
	 * regardless of error. Sends request for model then POSTs every few seconds
	 * until model is returned.
	 */
	
	private boolean attemptUpdate(boolean force){
		int fail = 0;
		int version_reported = version;
		
		if(force)
			version_reported = 0;
		
		int mode = (RANDOM_TREE) ? 1 : 0;
		
		String postContent = "imei=" + IMEI + "&version=" + version_reported + "&tree=" + mode;
		String response;
		int interval = 5000;
		boolean success = false;
		
		while(!handleWifi() && fail < FAIL_COUNT){
			try{
				Thread.sleep(interval);
			}catch(Exception e){}
			fail++;
		}
		if(fail == FAIL_COUNT){
			Log.i(TAG, "Hit fail count.");
			return false;
		}
		fail = 0;
		while(fail < FAIL_COUNT){
			Log.i(TAG,"Attempting connection");
			response = serverPost(postContent,CUSTOM_URL);
			Log.i(TAG,response);
			if(response == MODEL_WRITTEN){
				if(!RANDOM_TREE)
					wekaClassifier = retrieveClassifier();
				version = (force) ? version : version + 1;
				success = true;
				break;
			}
			try {
				Thread.sleep(interval);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			fail++;
		}
		if(!success)
			Log.i(TAG,"Exceeded max attempts, will resume later.");
		return success;
	}
	
	/**
	 * Sends POST request to server. Handles the various expected responses.
	 */
	
	private String serverPost(String content, String dest){
		int respCode;
		HttpURLConnection con;
		URL url;
		try {
			url = new URL(dest);
		} catch (MalformedURLException e) {
			return "Failed.";
		}

		try {
			con = (HttpURLConnection) url.openConnection();
		} catch (IOException e) {
			return "Failed.";
		}

		try {
			con.setRequestMethod("POST");
		} catch (java.net.ProtocolException e) {
			return "Failed.";
		}
		con.setUseCaches(false);
		con.setDoOutput(true);
		con.setDoInput(true);
		con.setRequestProperty("Content-type",
				"text/plain");

		try {
			con.connect();
			OutputStreamWriter osw = new OutputStreamWriter(con.getOutputStream());
			osw.write(content);
			osw.flush();
			
			respCode = con.getResponseCode();
			InputStream input = con.getInputStream();
			Scanner scan = new Scanner(input).useDelimiter("\\A");
			String line = "";
			Log.i(TAG,"Successful post. " + respCode);
			// If response code is 200 or 202, just read the message. If 204, parse the attachment.
			if(respCode == HttpURLConnection.HTTP_ACCEPTED || respCode == HttpURLConnection.HTTP_OK){
				String mesg = (scan.hasNext()) ? scan.next() : "";
				return mesg;
				
			} else if(respCode == HttpURLConnection.HTTP_CREATED){
				
				Log.i(TAG,model_file.getAbsolutePath());
				
				// If it is a tree, read the returned JSON and hand it to TreeManager for processing
				if(RANDOM_TREE){
					FileWriter localWriter = new FileWriter(model_file);
					global_tree = (scan.hasNext()) ? scan.next() : "";
					BufferedReader reader = new BufferedReader(new InputStreamReader(input));
					line = "";
					while ((line = reader.readLine()) != null) {global_tree += line;}
					localWriter.write(global_tree);
					localWriter.close();
					tree_manager = new TreeManager(global_tree);
				}
				// Else, read the model file atttachment.
				else{
					OutputStream output = new FileOutputStream(model_file);
					int read = 0;
					byte[] bytes = new byte[1024];
		 
					while ((read = input.read(bytes)) != -1) {
						output.write(bytes, 0, read);
					}
					output.close();
				}
				file_written = true;
				return MODEL_WRITTEN;
			}
			
		} catch (IOException e) {
			e.printStackTrace();
			con.disconnect();
			return "Failed.";
		}
		con.disconnect();
		return "Unknown Response.";

	}
	
	/**
	 * Loads classifier from model file (which is serialized Java Object).
	 * This method will not work for certain models due to Serial Version UID
	 * mismatch when model is built on different platforms. (JVM >> Dalvik)
	 */
	
	private Classifier retrieveClassifier(){
		InputStream is;
		Classifier cls = null;
		Log.i(TAG,"Loading classifier.");
		// Attempt to deserialize the model.
		try {
			if(file_written){
				is = new FileInputStream(model_file);
				cls = (Classifier) weka.core.SerializationHelper.read(is);
			}
			else{
				Log.i(TAG,"File does not exist.");
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		Log.i(TAG,"Classifier loading finished? ");
		return cls;
	}
	
	/**
	 * Sets up necessary variables for classification. Use of the template.arff here is
	 * required. It provides the necessary header information to enable the use of
	 * DenseInstances on classification.
	 */
	
	private void initializeClassificationScheme(){
		wekaClassifier = retrieveClassifier();
		try{
			// Read header from template file, use it to define instances list.
			BufferedReader reader = new BufferedReader(
					new InputStreamReader(context.getResources().openRawResource(R.raw.template)));
			ArffReader arff = new ArffReader(reader);
			Instances data = arff.getData();
			attributeList = new ArrayList<Attribute>(data.numAttributes());
			for(int attribute = 0; attribute < data.numAttributes(); attribute++){
				attributeList.add(data.attribute(attribute));
			}
		}catch(Exception e){e.printStackTrace();}
		dataset = new Instances("IMEI", attributeList, 0);
		dataset.setClassIndex(dataset.numAttributes() - 1);
	}
	
	/**
	 * Checks whether WiFi is on, if it is, sets it to the preferred connection.
	 * A simple method of avoiding use of their cellular network.
	 */
	
	private boolean handleWifi(){
		mWifi = connManager.getNetworkInfo(ConnectivityManager.TYPE_WIFI);
		if(!mWifi.isConnected())
			return false;
		Log.i("PRASHANTH","Connected! Setting preference to WIFI");
		connManager.setNetworkPreference(ConnectivityManager.TYPE_WIFI);
		return true;
	}
	
	/**
	 * Helper method, converts epoch time stamp in milliseconds to the seconds
	 * since the beginning of the week.
	 */
	
	public int convertToWeekTime(long time){
		return ((int) (time/1000)) % SECONDS_IN_WEEK;
	}
}
