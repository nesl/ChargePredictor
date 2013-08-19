package edu.ucla.cens.systemsens;

import java.util.ArrayList;

import android.R.color;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class SystemAdapter extends ArrayAdapter<Option>{
	
	private final Context context;
	private final ArrayList<Option> data;
	
	public SystemAdapter(Context context, ArrayList<Option> data){
		super(context, R.layout.list_elements, data);
		this.context = context;
		this.data = data;
	}
	
	
	@Override
	public View getView(int position, View convertView, ViewGroup parent){
		
		LayoutInflater inflater = (LayoutInflater) context
				.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		
		View rowView = inflater.inflate(R.layout.list_elements, parent, false);
		TextView feature = (TextView) rowView.findViewById(R.id.feature);
		TextView marquee = (TextView) rowView.findViewById(R.id.marquee);
		
		Option option = data.get(position);
		feature.setText(option.feature);
		marquee.setText(option.marquee);
		
		if(position == 0){
			if(option.feature == context.getString(R.string.enabled_text))
				rowView.setBackgroundResource(color.holo_green_dark);
			else
				rowView.setBackgroundResource(color.holo_red_light);
		}
		
		
		return rowView;
	}
}
