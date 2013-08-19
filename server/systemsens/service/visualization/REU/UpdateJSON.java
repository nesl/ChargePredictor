import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import weka.classifiers.Classifier;
import weka.classifiers.trees.RandomTree;
import weka.classifiers.trees.RandomTree.Tree;
import weka.core.Attribute;
import weka.core.Instances;
import weka.core.converters.ArffLoader.ArffReader;


public class UpdateJSON {
	public static void main(String [] args){
		if(args.length == 0){
			System.out.println("Bad arguments");
			System.exit(0);
		}
		try{
		BufferedReader reader = new BufferedReader(
				new InputStreamReader(new FileInputStream(
						"/opt/systemsens/service/visualization/REU/wekadata/modified_" + args[0] + ".arff")));
		ArffReader arff = new ArffReader(reader);
		Instances data = arff.getData();

		/* Setting instance we want to predict */
		data.setClassIndex(data.numAttributes() - 1);
		
		/* Building classifier based on model */
		Classifier cls = (Classifier)new RandomTree();
		cls.buildClassifier(data);

		/* Loading model from file - Recasting to make sure type-issue resolved*/ 
		RandomTree rf = (RandomTree)cls;
		Tree mtree = rf.getTree();
		JSONObject tree_diagram = new JSONObject();
		JSONArray jtree = mtree.toJSON(0);
		tree_diagram.put("tree_diagram", jtree);
		
		Worker wrk = new Worker();
		wrk.readDataBase(args[0], tree_diagram.toString());
		
		}catch(Exception e){
			e.printStackTrace();
		}
	}
}
