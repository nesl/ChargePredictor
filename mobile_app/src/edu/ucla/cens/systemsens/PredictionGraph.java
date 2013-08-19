package edu.ucla.cens.systemsens;

import java.util.Calendar;

import android.app.Activity;
import android.os.Bundle;

public class PredictionGraph extends Activity{

	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.prediction_table);
		setTitle("Prediction Table - " + Calendar.DAY_OF_WEEK + ", " + Calendar.MONTH + "/" + Calendar.DATE);
		
		
	}
}
