var map;
var lastWindow;

var tableid = 831071;
var center_lat = 58.58;
var center_lon = 25.1;
var zoom = 7;
var radius = 5000;

var center = new google.maps.LatLng(center_lat, center_lon);

var markersArray = [];

var zoomMap = new Array();
zoomMap[5000] = 12;
zoomMap[10000] = 11;
zoomMap[15000] = 10;

function initialize() {

  map = new google.maps.Map(document.getElementById('map'), {
//    center: center,
//    zoom: zoom,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    streetViewControl: false,
    panControlOptions: {
        position: google.maps.ControlPosition.LEFT_BOTTOM
    },
    zoomControlOptions: {
        style: google.maps.ZoomControlStyle.LARGE,
        position: google.maps.ControlPosition.LEFT_BOTTOM
    },
  });
  
  circle = new google.maps.Circle({
//    center: center,
//    radius: radius,
    map: map,
    fillOpacity: 0.2,
    fillColor: "#FF0000",    
    strokeOpacity: 0.5,
    strokeWeight: 1,
    clickable: false,
    zIndex: 0
  });

  getDataAll();
}

function getDataAll() {
  query = new google.visualization.Query('http://www.google.com/fusiontables/gvizdata?tq=' + encodeURIComponent("SELECT id, date, type, description, geometry, category, lat, lon FROM " + tableid));
  query.send(prepareData);
  map.setCenter(center);
  map.setZoom(zoom);
  circle.setMap();
}

function getDataAddress() {

  var geocoder = new google.maps.Geocoder();
  var new_radius = document.getElementById("form-select").value;
  
  geocoder.geocode( { 
      'address': document.getElementById("form-address").value,
      'region' : 'ee',
      'language' : 'et'
    }, function(results, status) {
    
    if (status == google.maps.GeocoderStatus.OK) {
      
      location_address = results[0].geometry.location;
      
      clearMarkers();
      
      query = new google.visualization.Query('http://www.google.com/fusiontables/gvizdata?tq=' + encodeURIComponent("SELECT id, date, type, description, geometry, category, lat, lon FROM " + tableid + " WHERE ST_INTERSECTS(geometry, CIRCLE(LATLNG" + location_address + "," + radius + "))"));
      query.send(prepareData);
      
      map.setCenter(location_address);
      map.setZoom(zoomMap[new_radius]);
      circle.setCenter(location_address);
      circle.setMap(map);
      circle.setRadius(parseInt(new_radius));
      
    } 
  });

}

function prepareData(response) {

  numRows = response.getDataTable().getNumberOfRows();
  numCols = response.getDataTable().getNumberOfColumns();
 
  for (i = 0; i < numRows; i++) {
    var row = [];
    for (j = 0; j < numCols; j++) {
      row.push(response.getDataTable().getValue(i, j));
    }
    drawMarkers(row);
  }  
  if (markersArray) {
    var markerCluster = new MarkerClusterer(map, markersArray, {
      gridSize: 3, 
      styles: [
      {
        height: 53,
        url: "images/marker_53x53.png",
        width: 53
      },
      {
        height: 56,
        url: "images/marker_56x56.png",
        width: 56
      },
      {
        height: 66,
        url: "images/marker_66x66.png",
        width: 66
      },
      {
        height: 78,
        url: "images/marker_78x78.png",
        width: 78
      },
      {
        height: 90,
        url: "images/marker_90x90.png",
        width: 90
      },      
      ]
    });
  }
}

function drawMarkers(row) {
  
      var marker_coordinate  = new google.maps.LatLng(row[6],row[7]);
  
      var marker = new google.maps.Marker({
          map: map, 
          position: marker_coordinate,
          icon: new google.maps.MarkerImage("images/marker_16x16.png"),
          zIndex: 1
      });
        
      markersArray.push(marker);
      
      google.maps.event.addListener(marker, 'click', function(event) {

        content = 
           "<h2>" + row[5] + "</h2>" +
           "<div class='description'>" + row[3].substring(0, 325) + "...</div>" +
           "<a href='http://www.ametlikudteadaanded.ee/index.php?act=1&teade="  + 
           row[0] + 
           "' target='_BLANK'>Vaata &rarr;</a>";

        if(lastWindow) lastWindow.close(); 
        
        lastWindow = new google.maps.InfoWindow( { 
          position: marker_coordinate,
          content: content,
          maxWidth: 300
        });
        lastWindow.open(map);
      });

}

function clearMarkers() {
  if (markersArray) {
    for (i in markersArray) {
      markersArray[i].setMap(null);
    }
  }
}

window.onkeypress = enterSubmit;
function enterSubmit() {
  if(event.keyCode==13) {
    getDataAddress();
  }
}