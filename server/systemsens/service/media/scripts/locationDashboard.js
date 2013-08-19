Ext.require('Ext.chart.*');
Ext.require(['Ext.Window', 'Ext.fx.target.Sprite', 'Ext.layout.container.Fit']);

Ext.onReady(function () {
    var yesterday = new Date();
    var tomorrow = new Date();
    yesterday.setDate(yesterday.getDate()-1);
    tomorrow.setDate(tomorrow.getDate()+1);

    var initializeDashboard = this.initializeDashboard;
    Ext.define('rawString', {
	extend: 'Ext.data.Model',
	fields: [
		{name: 'date', type: 'string'},
		{name: 'value', type: 'int'}
	]
    });

    Ext.define('clusterVisits', {
	extend: 'Ext.data.Model',
	fields: [
		{name: 'clusterid', type: 'int'},
		{name: 'sdate', type: 'date'},
		{name: 'edate', type: 'date'}		
	],
    });

    var clusterVisits = Ext.create('Ext.data.Store', {
		model: 'clusterVisits',
		storeId: 'clusterVisits',
    });

    Ext.define('Interactions', {
	extend: 'Ext.data.Model',
	fields: [
		{name: 'date', type: 'date'},
		{name: 'events', type: 'int'}
	]
    });

    this.rawStore = Ext.create('Ext.data.JsonStore', {
	proxy: {
		type: 'ajax',
		reader: {
			type: 'json'
		}
	},
	model: 'rawString'
    });

    var testStore = new Ext.data.Store({
	model: 'Interactions',
	storeId: 'testStore',
	sorters: [{
		property: 'date',
		direction: 'ASC'
	}]
    });

    var interactionStore = new Ext.data.Store({
	model: 'Interactions',
	storeId: 'interactionStore',
	sorters: [{
		property: 'date',
		direction: 'ASC'
	}],
	/*data: [{
		date: longago, events: 1 
	},{
		date: longago2, events: 1	

	}]*/
    });

//	interactionStore.load();

    var map_canvas = Ext.create('Ext.Window', {
	width:400,
	height: 300	
	});


    var lineChart = Ext.create('Ext.chart.Chart', {
	flex: 0.6,
	height: 200, // to prevent bug in ExtJS
	width: 300, // to prevent bug in ExtJS
	animate: true,
	hideMode: 'offsets',
	id: 'linechart',
	disabled: true,
	store: interactionStore,
	shadow: true,
	theme: 'Category1',
	legend: {
		position: 'right'
	},
	axes: [/*{
		type: 'Time',
		grid: true,
		position: 'bottom',
		title: 'Date',
		fields: 'date'



	}*/{
		type: 'Time',
		grid: true,
		position: 'bottom',
		dateFormat: 'M d gA',
		title: 'Date',
		fields: 'date',
		aggregateOp: 'sum',
		groupBy: 'year,month,day,hour',
		fromDate: new Date(2007,1,1)
	},{
		type: 'Numeric',
		grid: true,
		fields: 'events',
		position: 'left',
		minimum: 0,
		title: '# of Interactions'
	}],
	series: [{
		type: 'line',
		axis: 'left',
		id: 'line_series',
		xField: 'date',
		yField: 'events',
		fill: true,
		/*style: {
			fill: '#38B8BF',
			stroke: '#38B8BF',
			'stroke-width': 3


		},
		markerConfig: {
			type: 'circle',
			size: 4,
			radius: 4,
			'stroke-width': 0,
			fill: '#38B8BF',
			stroke: '#38B8BF'

		},*/
		showInLegend: false
	}/*,{
		type: 'column',
		axis: 'left',
		highlight: true,
		xField: 'date',
		yField: 'events'

	}*/]
    });

    var gridForm = Ext.create('Ext.form.Panel', {
	title: 'Location Dashboard',
	frame: true,
	bodyPadding: 5,
	width: 1024,
	height: 750,
	id: 'gridForm',

	fieldDefaults: {
		labelAlign: 'left',
		msgTarget: 'side'
	},

	layout: {
		type: 'vbox',
		align: 'stretch'
	},

	items: [{
		height: 30,
		layout: 'fit',
		margin: '0 0 3 0',
		items: [{
			xtype: 'toolbar',
			border: 0,
			id: 'topBar',
			shadow: false,
			defaults: {
				margin: '0 3 0 3'
			},
			items: [{
				xtype: 'datefield',
				fieldLabel: 'Start Date',
				labelAlign: 'left',
				labelPad: 0,
				labelWidth: 60,
				value: yesterday,
				id: 'startDate'
			},{
				xtype: 'timefield',
				id: 'startTime',
				fieldLabel: 'Start Time',
				labelAlign: 'left',
				labelPad: 0,
				labelWidth: 60,
				value: new Date(0,0,0,0,0,0),
			},'-',' ','-',{
				xtype: 'datefield',
				fieldLabel: 'End Date',
				id: 'endDate',
				labelAlign: 'left',
				labelPad: 0,
				labelWidth: 60,
				value: tomorrow
			},{
				xtype: 'timefield',
				id: 'endTime',
				fieldLabel: 'End Time',
				labelAlign: 'left',
				labelPad: 0,
				labelWidth: 60,
				value: new Date(0,0,0,0,0,0)
			},'-',{
				xtype: 'button',
				border: 1,
				text: 'Go!',
				scope: this,
				handler: function() {
				/*		
				*/
					var startdate = Ext.getCmp('startDate').getValue();
					var starttime = Ext.getCmp('startTime').getValue();
					var enddate = Ext.getCmp('endDate').getValue();
					var endtime = Ext.getCmp('endTime').getValue();

					startdate.setHours(starttime.getHours());
					startdate.setMinutes(starttime.getMinutes());
					enddate.setHours(endtime.getHours());
					enddate.setMinutes(endtime.getMinutes());					
					if (enddate <= startdate) {	
						Ext.Msg.show({
							title: 'Date Range Error',
							msg: 'Please enter a valid date and time range.',
							buttons: Ext.Msg.OK,
							animateTarget: 'topBar'
						});
					} else {
						this.initializeDashboard(startdate,enddate);				
					}
				}
			},'-']
		}]
	   },{
		height: 300,
		id: 'map_canvas',
		margin: '0 0 3 0',
		items: [map_canvas]
	   		
	   },{
		height: 30,
		layout: 'fit',
		margin: '0 0 3 0',
		items: [{
			xtype: 'toolbar',
			border: '0 0 0 0',
			items: [{
	
					xtype: 'combo',
					fieldLabel: 'Choose Visit',
					store: Ext.data.StoreManager.lookup('clusterVisits'),
					displayField: 'sdate',
					queryMode: 'local',
					valueField: 'clusterid',
					readOnly: false,
					id: 'choose_visit',
					lastQuery: '',
					labelWidth: 70,
					width: 355
			   },'-','-',{
				xtype: 'splitbutton',
				text: 'Interactions',
				menu: Ext.create('Ext.menu.Menu', {
					items: [{
						text: 'Screen',
						id: 'menu_screen'
					},{
						text: 'Applications',
						id: 'menu_apps'
					}]
				})
			   },'-',{
				xtype: 'splitbutton',
				text: 'Battery',
				menu: Ext.create('Ext.menu.Menu', {
					items: [{
						text: 'Level',
						id: 'menu_level'
					},{
						text: 'Charging Rate',
						id: 'menu_chargerate'
					},{
						text: 'Voltage',
						id: 'menu_voltage'
					},{
						text: 'Temperature',
						id: 'menu_temp'
					}]
				})
			   },'-',{
				xtype: 'splitbutton',
				text: 'Network',	
				menu: Ext.create('Ext.menu.Menu', {
					items: [{
						text: 'Bytes',
						id: 'menu_bytes'
					},{
						text: 'WiFi APs ID',
						id: 'menu_wifiscan'
					},{
						text: 'Packets',
						id: 'menu_packets'
					},{
						text: 'Network State',
						id: 'menu_netstate'
					},{
						text: 'Applications',
						id: 'menu_netapps'
					}]
				})
			   },'-',{
				xtype: 'button',
				text: 'CPU & Memory',
				menu: Ext.create('Ext.menu.Menu', {
					items: [{
						text: 'CPU Usage',
						id: 'menu_cpu'
					},{
						text: 'Memory Usage',
						id: 'menu_mem'
					}]
				})
			},'->','-','-',{
				xtype: 'splitbutton',
				text: 'Select Overlay(s)',
				disabled: true,
				menu: Ext.create('Ext.menu.Menu', {
				items: [{
						text: 'Clusters',
						checked: true,
						id: 'clusterCheckbox',
						checkHandler: function(item, checked) {
							(checked) ? showPolygons() : hidePolygons();
						}
					},{
						text: 'Markers',
						checked: false,
						id: 'markerCheckbox',
						checkHandler: function(item, checked) {
							(checked) ? showMarkers() : hideMarkers();
						}
	
					}]
				})

			}]	
			
		    }]
	   },{
		layout: {type: 'hbox', align: 'stretch'},
		margin: '0 0 3 0',
		flex: 3,
		items: [{
			flex: 0.35,
			border: false,
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			items: [{
				margin: '5',
				xtype: 'fieldset',
				flex: 1,
				id: 'visit_details',
				title: 'Visit Details',
				defaults: {
					width: 310,
					labelWidth: 120,
					readOnly: true
				},
			
				defaultType: 'textfield',
				items: [/*{
					xtype: 'combo',
					fieldLabel: 'Choose Visit',
					store: Ext.data.StoreManager.lookup('clusterVisits'),
					displayField: 'sdate',
					queryMode: 'local',
					valueField: 'clusterid',
					readOnly: false,
					id: 'choose_visit',
					lastQuery: ''
				},*/{
					fieldLabel: 'Start Date',
					id: 'start_date'
				},{
					fieldLabel: 'End Date',
					id: 'end_date'
				},{
					fieldLabel: 'Duration',
					id: 'duration'
				},{
					fieldLabel: 'Approx. Address',
					id: 'address'
				}
				]
			}]
			
			},{
				xtype: 'panel',
				flex: 0.6,
				width: 400,
				height: 600,
				id: 'chartPanel',
				autoShow: true,
				html: '<img id="dashboard_chart" style="height: 100%; width: 100%;" onload="Ext.getCmp(\'chartPanel\').setLoading(false)" src="http://systemsens.cens.ucla.edu/william/media/ext/welcome/css/blank.gif">'

	}]
	   }
	],

	
	renderTo: 'map_canvas'
	});

});
