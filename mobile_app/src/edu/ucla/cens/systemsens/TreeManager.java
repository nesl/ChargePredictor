package edu.ucla.cens.systemsens;

import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import android.util.Log;

public class TreeManager {
	
	private final String TAG = "Tree Manager";
	private final int SECONDS_IN_WEEK = 604800;
	public TreeNode root_scheme;
	
	public TreeManager(String tree_description){
		init(tree_description);
		Log.i(TAG,"Model intialized!");
	}
	
	/**
	 * Parses JSON String as JSON object.
	 */
	
	protected void init(String tree){
		JSONObject tree_model = null;
		try {
			tree_model = (JSONObject)new JSONParser().parse(tree);
		} catch (ParseException e) {
			e.printStackTrace();
			return;
		}
		JSONArray phys_tree = (JSONArray)tree_model.get("tree_diagram");
		root_scheme = new TreeNode();
		buildTree(phys_tree,root_scheme);
	}
	
	/**
	 * Recursive method to build tree.
	 */
	
	protected void buildTree(JSONArray level, TreeNode relativeRoot){
		int elements = level.size();
		JSONObject split;
		JSONArray sub_trees;
		for(int node = 0; node < elements; node++){
			TreeNode create = new TreeNode();
			split = (JSONObject)(level.get(node));
			create.type = (String)split.get("type");
			create.attribute = (String)split.get("attribute");
			create.operator = (String)split.get("operator");
			if(create.type.compareTo("node") == 0){
				create.nom_value = (String)split.get("value");
				create.children = null;
				relativeRoot.children.add(create);
				return;
			}
			
			if(create.type.compareTo("nominal") == 0)
				create.nom_value = (String)split.get("value");
			else if(create.type.compareTo("numerical") == 0)
				create.num_value = Double.parseDouble((String)split.get("value"));
			
			sub_trees = (JSONArray)split.get("subtree");
			buildTree(sub_trees,create);
			relativeRoot.children.add(create);
		}
	}
	
	/**
	 * Recursive method (similar to buildTree) that uses the instance to reach
	 * the appropriate node.
	 */
	
	protected String binaryClassify(JSONObject instance, TreeNode relativeRoot){
		ArrayList<TreeNode> subtree = relativeRoot.children;
		int treeSize = subtree.size();
		TreeNode subroot;
		for(int node = 0; node < treeSize; node++){
			subroot = subtree.get(node);
			if(subroot.isNode()){
				return subroot.nom_value;
			}
			else{
				Object comparator = instance.get(subroot.attribute);
				String compare = comparator.toString();
				if(subroot.match(compare)){
					return binaryClassify(instance, subroot);
				}
			}
		}
		return "";
	}
	
	/**
	 * Takes BatteryObject to classify and converts it into a JSON object.
	 * This form makes it easier to classify with binaryClassify.
	 * This method also does error checking and returns the count of how many
	 * quarters there are until the next charging time.
	 */
	@SuppressWarnings("unchecked")
	public int classify(BatteryObject instance){
		JSONObject create_inst = new JSONObject();
		create_inst.put("time", convertToWeekTime(instance.time_stamp));
		create_inst.put("lastChargingLevel", instance.last_level);
		create_inst.put("timeOfLastCharge", convertToWeekTime(instance.time_of_last_charge));
		create_inst.put("level",instance.current_level);
		create_inst.put("status",instance.status_string);
		create_inst.put("lengthOfLastCharge", instance.length_of_last_charge);
		
		String result = binaryClassify(create_inst,root_scheme);
		String quarter_number = result.substring(result.indexOf(' ') + 1).trim();
		
		if(quarter_number.compareTo("") == 0){
			Log.i(TAG,"No tree path was found.");
			return -1;
		}
		return Integer.parseInt(quarter_number);
	}
	
	public int convertToWeekTime(long time){
		return ((int) (time/1000)) % SECONDS_IN_WEEK;
	}
}

/**
 * TreeNode class that holds node attribute information,
 * as well as a list of children. Note that there is no
 * left/right node. This is because tree models can include
 * a varying number of children.
 */

class TreeNode {
	String type;
	String attribute;
	double num_value;
	String nom_value;
	String operator;
	ArrayList<TreeNode> children;
	
	TreeNode(){
		children = new ArrayList<TreeNode>();
	}
	
	boolean match(String value){
		if(type.compareTo("numerical") == 0){
			double val = Double.parseDouble(value);
			if(operator.compareTo("<") == 0 && val < num_value){
				return true;
			}
			else if(operator.compareTo(">=") == 0 && val >= num_value){
				return true;
			}
			return false;
		}
		else{
			return (nom_value.compareTo(value) == 0);
		}
	}
	
	boolean isNode(){
		return (type.compareTo("node") == 0);
	}
}