package com.events
{
	//Import Event class
	import flash.events.*;
	
	//FCEvent class extends the Event class
	//We can use the default Event class to track and listen FusionCharts events.
	//But FCEvent class will work here as specific to our component
	public class FCEvent extends Event
	{
		public var param:*;
		
		public function FCEvent(type:String, param:*):void
		{
			super(type);
			this.param=param;
		}
		
		//As we are dealing with custom events with custom event class,
		//overriding the method clone and dispatch the event as FCEvent type.
		override public function clone():Event
		{
            return new FCEvent(type, param);
  		} 

	} 
}