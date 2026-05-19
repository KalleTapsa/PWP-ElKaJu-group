import { useState } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { Place } from '../api';

// Fix leaflets broken default icon in Vite (uses a CDN fallback instead of bundled assets)
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = defaultIcon;

// Red circle to show where the rock is being placed
const pendingIcon = L.divIcon({
  className: '',
  html: '<div style="width:22px;height:22px;background:#e94560;border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,0.45);transform:translate(-50%,-50%)"></div>',
  iconSize: [0, 0],
  iconAnchor: [0, 0],
});

// Choosing the position of the rock circle
const ghostIcon = L.divIcon({
  className: '',
  html: '<div style="width:22px;height:22px;background:rgba(233,69,96,0.25);border:2px dashed #e94560;border-radius:50%;transform:translate(-50%,-50%)"></div>',
  iconSize: [0, 0],
  iconAnchor: [0, 0],
});

interface Props {
  places: Place[];
  addingMode: boolean;
  pendingCoords: [number, number] | null;
  onMapClick: (coords: [number, number]) => void;
  onSelectPlace: (place: Place) => void;
}

// Inner component that attaches leaflet map event listeners
// Must live inside <MapContainer> to access the map instance via useMapEvents
function MapEventHandler({ addingMode, onMapClick, onHoverCoords }: {
  addingMode: boolean;
  onMapClick: (coords: [number, number]) => void;
  onHoverCoords: (coords: [number, number] | null) => void;
}) {
  useMapEvents({
    // Confirm pin position on click
    click(e) {
      if (addingMode) onMapClick([e.latlng.lat, e.latlng.lng]);
    },
    // Update the preview position as the cursor moves
    mousemove(e) {
      if (addingMode) onHoverCoords([e.latlng.lat, e.latlng.lng]);
    },
    // Hide the preview when the cursor leaves the map
    mouseout() {
      onHoverCoords(null);
    },
  });
  return null;
}

// Main map component: renders the tile layer, all place markers, and the adding mode overlays
export default function PlaceMap({ places, addingMode, pendingCoords, onMapClick, onSelectPlace }: Props) {
  // Tracks where the cursor is while the user is choosing a pin location
  const [hoverCoords, setHoverCoords] = useState<[number, number] | null>(null);

  return (
    <MapContainer
      center={[62.0, 25.0]} // view centered on finland
      zoom={5}
      style={{ flex: 1, height: '100%', cursor: addingMode ? 'crosshair' : 'grab' }}
    >
      {/* Base map */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapEventHandler
        addingMode={addingMode}
        onMapClick={onMapClick}
        onHoverCoords={setHoverCoords}
      />

      {/* Render one marker per place */}
      {places.map(place => {
        const lat = Number(place.latitude);
        const lng = Number(place.longitude);
        if (isNaN(lat) || isNaN(lng)) return null;
        return (
          <Marker
            key={place.id}
            position={[lat, lng]}
            eventHandlers={{ click: () => onSelectPlace(place) }}
          />
        );
      })}

      {/* Confirmed drop position, after the user clicks to set coordinates */}
      {pendingCoords && (
        <Marker position={pendingCoords} icon={pendingIcon} interactive={false} />
      )}

      {/* Ghost preview, follows the cursor before the user has clicked to confirm */}
      {addingMode && !pendingCoords && hoverCoords && (
        <Marker position={hoverCoords} icon={ghostIcon} interactive={false} />
      )}
    </MapContainer>
  );
}
