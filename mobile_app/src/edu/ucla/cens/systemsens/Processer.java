package edu.ucla.cens.systemsens;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import android.content.Context;
import android.util.Log;

import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.evaluation.output.prediction.PlainText;
import weka.classifiers.trees.J48;
import weka.core.Attribute;
import weka.core.Debug.Random;
import weka.core.DenseInstance;
import weka.core.FastVector;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ArffLoader.ArffReader;

public class Processer {
	public Processer(){}
	public void go(Context context){
		try{
			BufferedReader reader = new BufferedReader(
					new InputStreamReader(context.getResources().openRawResource(R.raw.template)));
			ArffReader arff = new ArffReader(reader);
			Instances data = arff.getData();
			ArrayList<Attribute> attr = new ArrayList<Attribute>(data.numAttributes());
			for(int i = 0; i < data.numAttributes(); i++){
				attr.add(data.attribute(i));
			}
			/*data.setClassIndex(data.numAttributes() - 12);
			
			int seed = 23123123;
			int folds = 10;
			
			Random rand = new Random(seed);
			Instances randData = new Instances(data);
			randData.randomize(rand);
			
			randData.stratify(folds);
			
			J48 tree = new J48();
			Evaluation eval = new Evaluation(randData);
			StringBuffer output = new StringBuffer();
			PlainText forPredictionsPrinting = new PlainText();
			forPredictionsPrinting.setBuffer(output);
			forPredictionsPrinting.setAttributes("1");
			eval.crossValidateModel(tree, randData, folds, new Random(1), forPredictionsPrinting);
			Log.i("WEKA", "Correct: " + eval.correct());
			*/
			
			// deserialize model
			Classifier cls = (Classifier) weka.core.SerializationHelper.read(context.getResources().openRawResource(R.raw.template));
			//J48 tree = (J48) cls;
			
			// set attributes
			/*List<String> outlookValues = new ArrayList<String>(3);
			outlookValues.add("sunny");
			outlookValues.add("overcast");
			outlookValues.add("rainy");
			
			List<String> tempValues = new ArrayList<String>(3);
			tempValues.add("hot");
			tempValues.add("mild");
			tempValues.add("cool");
			
			List<String> humValues = new ArrayList<String>(2);
			humValues.add("high");
			humValues.add("normal");
			
			List<String> windValues = new ArrayList<String>(2);
			windValues.add("TRUE");
			windValues.add("FALSE");
			
			List<String> playValues = new ArrayList<String>(2);
			playValues.add("yes");
			playValues.add("no");
			
			Attribute outlook = new Attribute("outlook",outlookValues);
			Attribute temp = new Attribute("temperature",tempValues);
			Attribute humidity = new Attribute("humidity",humValues);
			Attribute windy = new Attribute("windy",windValues);
			Attribute play = new Attribute("play",playValues);
			
			ArrayList<Attribute> attr = new ArrayList<Attribute>(4);
			attr.add(outlook);
			attr.add(temp);
			attr.add(humidity);
			attr.add(windy);
			attr.add(play);*/
			
			Instances dataset = new Instances("weather.symbolic",attr,0);
			dataset.setClassIndex(dataset.numAttributes() - 1);
			// generate point
			Instance point = new DenseInstance(dataset.numAttributes());
			point.setDataset(dataset);
			dataset.add(point);
			point.setValue(0, 0);
			point.setValue(1, 0);
			point.setValue(2, 0);
			point.setValue(3, 0);
			point.setMissing(4);
			
			double result = cls.classifyInstance(point);
			Log.i("WEKA","Expected instance = " + result);
			
			
		} catch(Exception e){
			Log.e("WEKA",e.getMessage());
		}
	}
}
