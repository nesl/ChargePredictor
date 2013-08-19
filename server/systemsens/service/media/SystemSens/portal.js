/**
 * @class Ext.app.Portal
 * @extends Object
 * A sample portal layout application class.
 */
// TODO: Fill in the content panel -- no AccordionLayout at the moment
// TODO: Fix container drag/scroll support (waiting on Ext.lib.Anim)
// TODO: Fix Ext.Tool scope being set to the panel header
// TODO: Drag/drop does not cause a refresh of scroll overflow when needed
// TODO: Grid portlet throws errors on destroy (grid bug)
// TODO: Z-index issues during drag

Ext.define('Ext.app.Portal', {

    extend: 'Ext.container.Viewport',

    uses: ['Ext.app.PortalPanel', 'Ext.app.PortalColumn', 'Ext.app.GridPortlet', 'Ext.app.ChartPortlet'],

    getTools: function(){
        return [{
            xtype: 'tool',
            type: 'gear',
            handler: function(e, target, panelHeader, tool){
                var portlet = panelHeader.ownerCt;
		portlet.setLoading('Working...');
                Ext.defer(function() {
                    portlet.setLoading(false);
                }, 2000);
            }
        }];
    },

    initComponent: function(){

    
        var yesterday = new Date();
   	    var tomorrow = new Date();
    	yesterday.setDate(yesterday.getDate()-1);
    	tomorrow.setDate(tomorrow.getDate()+1);

    	var map_canvas = Ext.create('Ext.Window', {
		    width:400,
		    height: 300	
	    });

        // Get the user information from the server (IMEI and Username)
        Ext.Ajax.request({
            url:'http://128.97.93.158/service/viz/getuserinfo/',
            method:'POST',
            success: function (result, request) {
                var resultArr = result.responseText.split(',');
                var html = resultArr[0] +'<br>('+resultArr[1] +')<br><br><a href="http://128.97.93.158/service/viz/logout/">logout</a>' 
                
                // Update the Ext container w/ the dynamically generated HTML
                Ext.getCmp('logoutBox').update(html);
            },
            failure: function (result, request) {
                var html = '<a href="http://128.97.93.158/service/viz/logout/">logout</a>' 
                Ext.getCmp('logoutBox').update(html);
            }

        });
    	Ext.define('clusterVisits', {
		extend: 'Ext.data.Model',
		fields: [
			{name: 'clusterid', type: 'int'},
			{name: 'visitid', type: 'int'},
			{name: 'stringid', type: 'string'},
			{name: 'sdate', type: 'date'},
			{name: 'edate', type: 'date'}		
		],
    	});
	
	Ext.define('appNames', {
		extend: 'Ext.data.Model',
		fields: [ {name: 'appname', type: 'string'} ]
	});

    	var clusterVisits = Ext.create('Ext.data.Store', {
		model: 'clusterVisits',
		storeId: 'clusterVisits',
    	});
	
	var appNames = Ext.create('Ext.data.Store', {
		model: 'appNames',
		proxy: {
			type: 'ajax',
			url: '/service/viz/appresource/?json',
			reader: {
				type: 'json'
			}
		},
		autoLoad: true,
		storeId: 'appNames'
	});
    
    Ext.apply(this, {
            id: 'app-viewport',
            layout: {
                type: 'border',
                padding: '0 5 5 5' // pad the layout from the window edges
            },
            items: [
            { 
                id: 'app-topnav', 
                xtype: 'container', 
                region: 'north', 
                items: [
		{ 
                    xtype: 'container', 
                    layout: { 
                        type: 'hbox', 
                        align: 'middle' 
                    }, 
                    items: [{ 
                        id: 'app-header', 
                            xtype: 'box', 
                            html: 'SystemSens' 
                           },
                            // Start Date Controls
                           {
				xtype: 'tbspacer',
				flex: 1
			},{
				xtype: 'fieldset',
				height: 75,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Start Date',
                                        labelAlign: 'left',
                                        labelPad: 0,
                                        labelWidth: 70,
                                        anchor: '100%',
                                        value: yesterday,
                                        id: 'startDate'
                                    },
                                    {
                                        xtype: 'timefield',
                                        fieldLabel: 'Start Time',
                                        labelAlign: 'left',
                                        labelPad: 0,
                                        labelWidth: 70,
                                        anchor: '100%',
                                        value: new Date(0,0,0,0,0,0),
					id: 'startTime'
                                    }
                                ]
                            },

                            {xtype: 'tbspacer', width: 30},


                            // End Date Controls
                            {
				xtype: 'fieldset',
                                height: 75,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'End Date',
                                        labelAlign: 'left',
                                        labelPad: 0,
                                        labelWidth: 70,
                                        anchor: '100%',
                                        value: tomorrow,
                                        id: 'endDate'
                                    },
                                    {
                                        xtype: 'timefield',
                                        fieldLabel: 'End Time',
                                        labelAlign: 'left',
                                        labelPad: 0,
                                        labelWidth: 70,
                                        anchor: '100%',
                                        value: new Date(0,0,0,0,0,0),
					id: 'endTime'
                                    }
                                ]
                            },


                            {xtype: 'tbspacer', width: 30},
                            // Button
                            {
				xtype: 'container',
				border: true,
				height: 75,
				layout: { type: 'vbox', pack: 'center' },
				defaults: {
					width: 100
				},
				items: [{
                               		xtype: 'button',
                               		text: 'Apply Date Filter',
                               		id: 'go_button',
                               		scope: this,
                            },{
					xtype: 'button',
					baseCls: 'x-btn',
					text: 'Collapse Charts',
					id: 'collapse_all',
					scope: this,
					hidden: true,
					enableToggle: true
                           }]
			},{ 
                            xtype: 'tbspacer', 
                                   width: 40 
                           },
                           { 
                                xtype: 'box', 
                                id: 'logoutBox',
                                html: '<a href="http://128.97.93.158/service/viz/logout/">logout</a>' 
                           }

                     ] 
                }] },










               {
                xtype: 'container',
                region: 'center',
                layout: 'border',

                items: [

                    {
                    id: 'app-portal',
                    xtype: 'portalpanel',
                    region: 'center',
                    items: [{
                        id: 'col-1',
                        items: [
                        
                            //TODO

                   {

                    id: 'app-options',
                    title: 'Location Filters',
                    // TODO: Disable location filters for summer HS
                    // interns

                    hidden: false,
                    tools: [{
			type: 'save',
			handler: function() {
				var postdata = [];

				clusterVisits.each(function(record) {
					var startDate = record.get('sdate');
					var endDate = record.get('edate');
		
					var smonths = (startDate.getMonth() < 9) ? '0' + (startDate.getMonth()+1) : startDate.getMonth()+1; 
                                	var sdays = (startDate.getDate() < 10) ? '0' + startDate.getDate() : startDate.getDate();
                                	var shours = (startDate.getHours() < 10) ? '0' + startDate.getHours() : startDate.getHours();
                                	var sminutes = (startDate.getMinutes() < 10) ? '0' + startDate.getMinutes() : startDate.getMinutes();       
                                	var sstring = '' + startDate.getFullYear() + 
                                                smonths + sdays + shours + sminutes;                                            
        
                                	var emonths = (endDate.getMonth() < 9) ? '0' + (endDate.getMonth()+1) : endDate.getMonth()+1;        
                                	var edays = (endDate.getDate() < 10) ? '0' + endDate.getDate() : endDate.getDate();
                                	var ehours = (endDate.getHours() < 10) ? '0' + endDate.getHours() : endDate.getHours();
                                	var eminutes = (endDate.getMinutes() < 10) ? '0' + endDate.getMinutes() : endDate.getMinutes();       
                                	var estring = '' + endDate.getFullYear() + 
                                                emonths + edays + ehours + eminutes;

					postdata.push({
						clusterid: record.get('clusterid'),
						visitid: record.get('visitid'),
						sdate: sstring,
						edate: estring
					});
				});

				var viewport = this.ownerCt.ownerCt.ownerCt.ownerCt.ownerCt.ownerCt;
				
				var resultsWindow = Ext.create('Ext.window.Window', {
					title: 'Export Results',
					height: viewport.getHeight()*0.667,
					width: viewport.getWidth()*0.9,
					border: false,
					constrain: true,
					maximizable: true,
					modal: true,
					layout: 'fit',
					items: [{
						xtype: 'textareafield',
						border: false,
						id: 'results_text',
						//value: response.responseText
					}]
				}).show();



				Ext.Msg.prompt('Input Required', 'Please enter application name:', function(btn,text){
					if (btn == 'ok'){
						var appname = text;
						console.log("Application name is "+appname);

						resultsWindow.center();	
						Ext.getCmp('results_text').setLoading("Exporting data to CSV. Please wait...");
	
						Ext.Ajax.request({
							url: '/service/viz/parsevisits/',
							timeout: 3000000, // Timeout after 3000 seconds
							params: {
								visits: JSON.stringify(postdata),
								interval: 10,
								appname: appname
							},
							success: function(response) {
								Ext.getCmp('results_text').setValue(response.responseText);
								Ext.getCmp('results_text').setLoading(false);
							}
						});	
					} else {
						resultsWindow.close();

					}
				});
					


			}
		    },{
		    	type: 'pin',
			handler: function () {
				// Disable loading of charts
				window.chartLoadEnabled = 0;

			}
		    },{
			type: 'save',
			tooltip: 'Export Screen Events to CSV',
			handler: function() {
				var postdata = [];
				clusterVisits.each(function(record) {
					var startDate = record.get('sdate');
					var endDate = record.get('edate');
		
					var smonths = (startDate.getMonth() < 9) ? '0' + (startDate.getMonth()+1) : startDate.getMonth()+1; 
                                	var sdays = (startDate.getDate() < 10) ? '0' + startDate.getDate() : startDate.getDate();
                                	var shours = (startDate.getHours() < 10) ? '0' + startDate.getHours() : startDate.getHours();
                                	var sminutes = (startDate.getMinutes() < 10) ? '0' + startDate.getMinutes() : startDate.getMinutes();       
                                	var sstring = '' + startDate.getFullYear() + 
                                                smonths + sdays + shours + sminutes;                                            
        
                                	var emonths = (endDate.getMonth() < 9) ? '0' + (endDate.getMonth()+1) : endDate.getMonth()+1;        
                                	var edays = (endDate.getDate() < 10) ? '0' + endDate.getDate() : endDate.getDate();
                                	var ehours = (endDate.getHours() < 10) ? '0' + endDate.getHours() : endDate.getHours();
                                	var eminutes = (endDate.getMinutes() < 10) ? '0' + endDate.getMinutes() : endDate.getMinutes();       
                                	var estring = '' + endDate.getFullYear() + 
                                                emonths + edays + ehours + eminutes;

					postdata.push({
						clusterid: record.get('clusterid'),
						visitid: record.get('visitid'),
						sdate: sstring,
						edate: estring
					});
				});

				var viewport = this.ownerCt.ownerCt.ownerCt.ownerCt.ownerCt.ownerCt;
				
				var resultsWindow = Ext.create('Ext.window.Window', {
					title: 'Export Results',
					height: viewport.getHeight()*0.667,
					width: viewport.getWidth()*0.9,
					border: false,
					constrain: true,
					maximizable: true,
					modal: true,
					layout: 'fit',
					items: [{
						xtype: 'textareafield',
						border: false,
						id: 'results_text',
						//value: response.responseText
					}]
				}).show();

				resultsWindow.center();	
				Ext.getCmp('results_text').setLoading("Exporting data to CSV. Please wait...");
	
				Ext.Ajax.request({
					url: '/service/viz/parsescreenevents/',
					timeout: 3000000, // Timeout after 3000 seconds
					params: {
						visits: JSON.stringify(postdata),
						interval: 10,
					},
					success: function(response) {
						Ext.getCmp('results_text').setValue(response.responseText);
						Ext.getCmp('results_text').setLoading(false);
					}
				});	
			}
		    }],
                    region: 'north',
                    height: 300,    
        	    split: true,
                    layout: 'fit',
                    layoutConfig:{
                        animate: true
                    },
                items: [
                    {
                    	xtype: 'panel',
			autoShow: true,
			id: 'filterPanel',
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			flex: 10,
			items: [
            {
				xtype: 'panel',
				id: 'map_panel',
				flex: 6.5,
				margin: '0 0 0 0',
			},
            {
				layout: {type: 'vbox', align: 'stretch'},
				flex: 2.5,
				items: [{
						margin: '5',
						xtype: 'fieldset',
						id: 'visit_details',
						title: 'Visit Details',
						layout: 'anchor',
						defaults: {
							anchor: '100%',
							readOnly: true
						},
						defaultType: 'textfield',
						items: [{
							xtype: 'combo',
							fieldLabel: 'Choose Visit #',
							store: Ext.data.StoreManager.lookup('clusterVisits'),
							displayField: 'stringid',
							queryMode: 'local',
							valueField: 'clusterid',
							readOnly: false,
							id: 'choose_visit',
							lastQuery: '',
						},{
							fieldLabel: 'Start Date',
							id: 'start_date'
						},{
							fieldLabel: 'End Date',
							id: 'end_date'
						},{
							fieldLabel: 'Duration',
							id: 'duration'
						}

                        ,{
							fieldLabel: 'Approx. Address',
							id: 'address1',
							hidden: true
						}
                        ,{
							id: 'address2',
							fieldLabel: 'City ',
							labelSeparator: '',
							hidden: true
						}

                        ]
					}]
			}]
		    }]
                },  /* end of HS disabled map */
                        
                            //TODO
                        
                        {
                            	title: 'Interactions',
                            	tools: this.getTools(),
			    	height: '400px',
				//width: '100px',
				items: [
				{
					xtype: 'tabpanel',
					tabPosition: 'bottom',
					deferredRender: false,
					items: [
						{
							title: 'Screen',
							id: 'container_screen',
							html: '<div id="portlet_screen"></div>',
						},{
							title: 'Applications',
							id: 'container_apps',
							html: '<div id="portlet_apps"></div>'
						}
					]
				}],
			    	listeners: {
                                	'close': Ext.bind(this.onPortletClose, this)
                            	}
                        },
                        {
				title: 'Battery',
				tools: this.getTools(),
				height: '400px',
				//width: '100px',
				items: [{
					xtype: 'tabpanel',
					tabPosition: 'bottom',
					deferredRender: false,
					items: [
					{
						title: 'Level',
						id: 'container_battery',
						html: '<div id="portlet_battery"></div>',
					},{
						title: 'Voltage',
						id: 'container_volt',
						html: '<div id="portlet_volt"></div>'
					},{	
						title: 'Current',
						id: 'container_curr',
						html: '<div id="portlet_curr"></div>'
					},{	
						title: 'Temperature',
						id: 'container_temp',
						html: '<div id="portlet_temp"></div>'
					},{

						title: 'Power',
						id: 'container_power',
						html: '<div id="portlet_power"></div>'
					}]

				}],
				listeners: {
					'close': Ext.bind(this.onPortletClose, this)
				}
			},
                        {
                                title: 'Network',
                                tools: this.getTools(),
                                height: '400px',
				//width: '100px',
				items: [{
					xtype: 'tabpanel',
					tabPosition: 'bottom',
					deferredRender: false,
					items: [{
						title: 'Bytes',
						id: 'container_bytes',
                                		html: '<div id="portlet_bytes"></div>'
					},{
						title: 'WiFi APs ID',
						id: 'container_wifiscan',
                                		html: '<div id="portlet_wifiscan"></div>'
					},{
						title: 'Packets',
						id: 'container_packets',
						html: '<div id="portlet_packets"></div>'
					},{
						title: 'State',
						id: 'container_netstate',
						html: '<div id="portlet_netstate"></div>'
                    } ,{
						title: 'Signal',
						id: 'container_cellsignal',
						html: '<div id="portlet_cellsignal"></div>'
					} ]

				}],
                                listeners: {
                                        'close': Ext.bind(this.onPortletClose, this)
                                }
                        },{
				title: 'Resources',
				tools: this.getTools(),
				height: '450px',
				//width: '100px',
				items: [{
					xtype: 'tabpanel',
					tabPosition: 'bottom',
					deferredRender: false,
					activeTab: 0,
					layoutOnTabChange: true,
					items: [{
						title: 'CPU Usage',
						id: 'container_cpu',
						html: '<div id="portlet_cpu"></div>'
					},{
						title: 'Memory Usage',
						id: 'container_memory',
                                		html: '<div id="portlet_memory"></div>'
					},{
						title: 'GPS Usage',
						id: 'container_gps',
                                		html: '<div id="portlet_gps"></div>'
					},{
						title: 'Audio Usage',
						id: 'container_audio',
                                		html: '<div id="portlet_audio"></div>'
					},{
						title: 'Accelerometer Usage',
						id: 'container_accel',
                                		html: '<div id="portlet_accel"></div>'

					},{
						xtype: 'container',
						hideMode: 'offsets',
						width: 400,
						height: 400,
						layout: { type: 'vbox', align: 'stretch' },
						title: 'Applications',
						items: [{
							xtype: 'toolbar',
							border: false,
							height: 30,
							items: [{
								xtype: 'combo',
								fieldLabel: 'Choose Application',
								store: Ext.data.StoreManager.lookup('appNames'),
								displayField: 'appname',
								labelWidth: 105,
								queryMode: 'local',
								valueField: 'appname',
								id: 'choose_application',
								lastQuery: ''
							},' ','-',{
								xtype: 'button',
								text: 'CPU Usage',
								id: 'appresource_cpu',
								disabled: true,
								allowDepress: true,
								enableToggle: true,
							},'-',{
								xtype: 'button',
								text: 'Network Usage',
								id: 'appresource_network',
								disabled: true,
								allowDepress: true,
								enableToggle: true,
							},'-',{
								xtype: 'button',
								text: 'Memory Usage',
								id: 'appresource_memory',
								disabled: true,
								allowDepress: true,
								enableToggle: true,
							},'-']
						},{
							xtype: 'container',
							id: 'container_appresource',
							flex: 1,
							border: false,
							autoShow: true,
							items: [{
								xtype: 'box',
								html: '<div id="portlet_appresource"></div>'	
							//	html: '<img src="http://systemsens.cens.ucla.edu/service/viz/app_cpu/201105120000/201105140000/gapps/"></img>'
							}]

						}


							/*{
								xtype: 'container',
								flex: 1,
								html: '<img src="http://systemsens.cens.ucla.edu/service/viz/net_bytes/201105120000/201105140000/"></img>'
								//html: '<div id="portlet_appresource"></div>'
							},{
								xtype: 'container',
								layout: 'hbox',
								height: 30,
								items: [{ xtype: 'tbspacer', width: 190 },{
									xtype: 'toolbar',
									height: 30,
									width: 210,
									items: [{
										xtype: 'combo',
										fieldLabel: 'Choose',
										store: Ext.data.StoreManager.lookup('clusterVisits'),
										displayField: 'visitid',
										labelWidth: 45,
										queryMode: 'local',
										valueField: 'clusterid',
										id: 'choose_application',
										lastQuery: ''
									}]
								}]	
						}*/]

					}]
				}],
				listeners: {
					'close': Ext.bind(this.onPortletClose, this)
				}
			}]
                    }/*,{
                        id: 'col-2',
                        items: [{
                            id: 'portlet-3',
                            title: 'Portlet 3',
                            tools: this.getTools(),
                            html: '<div class="portlet-content">'+Ext.example.bogusMarkup+'</div>',
                            listeners: {
                                'close': Ext.bind(this.onPortletClose, this)
                            }
                        }]
                    },{
                        id: 'col-3',
                        items: [{
                            id: 'portlet-4',
                            title: 'Stock Portlet',
                            tools: this.getTools(),
                            items: Ext.create('Ext.app.ChartPortlet'),
                            listeners: {
                                'close': Ext.bind(this.onPortletClose, this)
                            }
                        }]
                    }*/]
                }]
            }]
	});



	
        this.callParent(arguments);
    },

    onPortletClose: function(portlet) {
        this.showMsg('"' + portlet.title + '" was removed');
    },

    showMsg: function(msg) {
        var el = Ext.get('app-msg'),
            msgId = Ext.id();

        this.msgId = msgId;
        el.update(msg).show();

        Ext.defer(this.clearMsg, 3000, this, [msgId]);
    },

    clearMsg: function(msgId) {
        if (msgId === this.msgId) {
            Ext.get('app-msg').hide();
        }
    }
});
