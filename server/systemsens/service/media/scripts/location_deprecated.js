	function initialize() {
		var messages = {{ netlocationjson|safe }};
		
		// Create array of LatLng objects
		
		var latlng = []; // this might not be necessary for now
		var markerArray = [];
		var minLat = messages[0].data.Lat;
		var minLon = messages[0].data.Lon;
		var maxLat = messages[0].data.Lat;
		var maxLon = messages[0].data.Lon;

		var db_epsilon = 0.2;
		var db_minpts = 10;


		for (var i=0; i < messages.length; i++) {
			
			var currentLat = messages[i].data.Lat;
			var currentLon = messages[i].data.Lon;

			if (messages[i].data.Accuracy > "100") {				
				// Filter out innacurate data points
				messages.splice(i,1);	// Remove the data point, for ease of processing later on
				i--; // Make sure the correct next point is evaluated	
			} else {				
				latlng.push(new google.maps.LatLng(currentLat,currentLon));
				if (currentLat > maxLat) {maxLat = currentLat;}
				if (currentLon > maxLon) {maxLon = currentLon;}
				if (currentLat < minLat) {minLat = currentLat;}
				if (currentLon < minLon) {minLon = currentLon;}
			}
		}
	
		// Divide LatLng's into clusters
		if (typeof(Number.prototype.toRad) === "undefined") {
  				Number.prototype.toRad = function() {
    				return this * Math.PI / 180;
  			}
		}

		// Function determines distance, in kilometers, between two google.maps.LatLng objects
		function db_dist(latlng1,latlng2) {
			var R = 6371; // km
			var dLat = (latlng2.lat()-latlng1.lat()).toRad();
			var dLon = (latlng2.lng()-latlng1.lng()).toRad();
			var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
				Math.cos(latlng1.lat().toRad()) * Math.cos(latlng2.lat().toRad()) *
				Math.sin(dLon/2) * Math.sin(dLon/2);
			var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
			var d = R * c;
			
			return d; // in kilometers
		}
		
		var myOptions = {
      			zoom: 15,
      			center: latlng[0],
			//center: new google.maps.LatLng((maxLat+minLat)/2,(maxLon+minLon)/2),
      			mapTypeId: google.maps.MapTypeId.ROADMAP
    		};
    	
		var map = new google.maps.Map(document.getElementById("map_canvas"),
        		myOptions);

		var polylatlng = []; // 2D array of latlng coordinates, each array is one cluster

		var cluster = [];
		var cluster_sdate;
		var cluster_edate;
		var sdate;
		var edate;

		for (var k = 1; k < latlng.length; k++) {
			if ((db_dist(latlng[k],latlng[k-1]) < db_epsilon) || cluster == []) {
				if (k-1 == 0) {
					// Push the google.maps.LatLng object to cluster array
					cluster.push(latlng[0]);
					
					// Initialize the start date/time for first cluster	
					var datetime = messages[0].date.split(' ');
					var date = datetime[0].split('-');
					var time = datetime[1].split(':');
					sdate = new Date(date[0], date[1], date[2], time[0],time[1],time[2]);
					edate = cluster_sdate;
					
					cluster_sdate = messages[0].date;	
					cluster_sdate = cluster_sdate.substr(0, cluster_sdate.lastIndexOf(':'));
					cluster_sdate = cluster_sdate.replace(/-|:| /g,'');
				}
				
				// Push the google.maps.LatLng object to cluster array
				cluster.push(latlng[k]);
	
				// Update the end date/time
				var datetime = messages[k].date.split(' ');
				var date = datetime[0].split('-');
				var time = datetime[1].split(':');
			
				edate = new Date(date[0], date[1], date[2], time[0],time[1],time[2]);
				
				cluster_edate = messages[k].date;
				cluster_edate = cluster_edate.substr(0, cluster_edate.lastIndexOf(':'));
				cluster_edate = cluster_edate.replace(/-|:| /g,'');
				
			} else {
				// If the cluster is large enough
				if (cluster.length > db_minpts) {
					// Add the cluster to the polygon latlng array
					polylatlng.push({
						sdate: sdate,
						edate: edate,
						cluster_sdate: cluster_sdate,
						cluster_edate: cluster_edate,
						cluster: cluster
					});
					//k++;
				}
				cluster = [];	// reset the cluster array to empty
				
				// ASSERT: k is the start of the next cluster
				var datetime = messages[k].date.split(' ');
				var date = datetime[0].split('-');
				var time = datetime[1].split(':');
				
				// Initialize the start date/time for next cluster
				sdate = new Date(date[0], date[1], date[2], time[0], time[1], time[2]);
				
				cluster_sdate = messages[k].date;
				cluster_sdate = cluster_sdate.substr(0, cluster_sdate.lastIndexOf(':'));
				cluster_sdate = cluster_sdate.replace(/-|:| /g,'');
			}
		}

		console.log(polylatlng);
		
		
		// Helper function to maintain closure for addListener() calls
		function updateInfoWindow(contentString, j) {
			return function() {
				infowindow.setContent(contentString);
				infowindow.setPosition(polylatlng[j].cluster[0]);
				infowindow.open(map);
			}
		}

		var polygonArray = [];

		// Initialize the InfoWindow
		var contentString = '';
		var infowindow = new google.maps.InfoWindow();

		// Populate the Polygon array
		for (var i=0; i < polylatlng.length; i++) {
			polygonArray.push(new google.maps.Polygon({
				paths: getConvexHullPoints(polylatlng[i].cluster),
				map: map,
				strokeColor: "#FF0000",
				strokeOpacity: 0.8,
				strokeWeight: 2,
				fillColor: "#FF0000",
				fillOpacity: 0.35
			}));
			
			// Determine the start date/time and end date/time of this polygon
		
			var poly = polylatlng[i];
	
			contentString = '<b>Start Date: </b>' + poly.sdate.toLocaleString() + '<br>' +
					'<b>End Date: </b>' + poly.edate.toLocaleString() + '<br>' +
					'<img src="http://systemsens.cens.ucla.edu/william/viz/screen_events/{{imei}}/' +
					poly.cluster_sdate + '/' + poly.cluster_edate
					+ '/\" height=100% width=100%></img>';
//			contentString = 'From ' + polylatlng[i].sdate + ' to ' + polylatlng[i].edate;
			google.maps.event.addListener(polygonArray[i], 'click', updateInfoWindow(contentString, i));
		}		
		
		// Populate the Marker array
		for (var i=0; i < messages.length; i++) {
		
    			markerArray.push(new google.maps.Marker({
						position: latlng[i],
						title: "Latitude: "+messages[i].data.Lat+" Longitude: "+messages[i].data.Lon,
						map: map,
						animation: google.maps.Animation.DROP
					}));
			
		/*	contentString = '<b>Latitude:</b> ' + messages[i].data.Lat
					+ '<br><b>Longitude:</b> ' + messages[i].data.Lon
					+ '<br><b>Accuracy:</b> ' + messages[i].data.Accuracy + ' ft'
					+ '<br><br><b>Date:</b> ' + messages[i].date;			
		*/
		//	google.maps.event.addListener(markerArray[i], 'click', updateInfoWindow(contentString, i));


		}

		// Close the InfoWindow upon click of map
		google.maps.event.addListener(map, 'click', function () {
				infowindow.close();
		});

  	}	
