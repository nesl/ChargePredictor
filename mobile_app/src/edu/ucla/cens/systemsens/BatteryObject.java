/**
 * BatteryObject class, holds relevant attribute information.
 * No methods, just a container/structure.
 */
package edu.ucla.cens.systemsens;

public class BatteryObject {
	public static final int CHARGING_USB = 0;
	public static final int CHARGING_AC = 1;
	public static final int NOT_CHARGING = 3;
	
	public long time_stamp;
	public int charging_status;
	public int current_level;
	public long time_of_last_charge;
	public long length_of_last_charge;
	public int last_level;
	public int prediction_quarter;
	public String status_string;
	
	
	public BatteryObject(long time_stamp, int charging_status, int current_level, long time_of_last_charge, 
			long length_of_last_charge, int last_level, String status_string){
		this.charging_status = charging_status;
		this.time_stamp = time_stamp;
		this.time_of_last_charge = time_of_last_charge; //convertToWeekTime(time_of_last_charge);
		this.length_of_last_charge = length_of_last_charge;
		this.last_level = last_level;
		this.current_level = current_level;
		this.status_string = status_string;
	}
}
