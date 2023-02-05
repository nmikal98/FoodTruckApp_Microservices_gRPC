import React from "react";
import ReactDOM from "react-dom";
import Sidebar from "./components/Sidebar";

// setting up mapbox
mapboxgl.accessToken =
  "pk.eyJ1Ijoibm1pa2FsMDEiLCJhIjoiY2xibTM4YnRnMGRjcDNwbXZ2a2N3MmNmbSJ9.Hoaznn3N4ac-03Cle_Up9g";

var map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/nmikal01/cl8bl2lrw00au15qvq311gojb",
  center: [-122.44, 37.77],
  zoom: 12,
});

ReactDOM.render(<Sidebar map={map} />, document.getElementById("sidebar"));

function formatHTMLforMarker(props) {
  var { name, hours, address } = props;
  var html =
    '<div class="marker-title">' +
    name +
    "</div>" +
    "<h4>Operating Hours</h4>" +
    "<span>" +
    hours +
    "</span>" +
    "<h4>Address</h4>" +
    "<span>" +
    address +
    "</span>";
  return html;
}

// setup popup display on the marker
map.on("click", function (e) {
  var features = map.queryRenderedFeatures(
    e.point, 
    { layers: ['trucks', 'trucks-highlight'], radius: 10, includeGeometry: true }
  );

  if (!features.length) return;

  var feature = features[0];

  new mapboxgl.Popup()
    .setLngLat(feature.geometry.coordinates)
    .setHTML(formatHTMLforMarker(feature.properties))
    .addTo(map);
});
