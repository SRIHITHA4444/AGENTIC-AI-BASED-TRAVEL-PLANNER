import React, { useRef, useEffect } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const DEFAULT_CENTER = [78.9629, 20.5937];
const DEFAULT_ZOOM = 4;

const MapComponent = ({ sourceCoords, destinationCoords, routeGeometry }) => {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);

  const center = (sourceCoords && sourceCoords.lat && sourceCoords.lon)
    ? [sourceCoords.lon, sourceCoords.lat]
    : DEFAULT_CENTER;

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = new maplibregl.Map({
        container: mapContainer.current,
        style: 'https://demotiles.maplibre.org/style.json',
        center: center,
        zoom: DEFAULT_ZOOM,
      });
    } else {
      mapRef.current.flyTo({ center, zoom: DEFAULT_ZOOM });
    }

    if (mapRef.current._sourceMarker) {
      mapRef.current._sourceMarker.remove();
      mapRef.current._sourceMarker = null;
    }
    if (mapRef.current._destMarker) {
      mapRef.current._destMarker.remove();
      mapRef.current._destMarker = null;
    }

    if (sourceCoords && sourceCoords.lat && sourceCoords.lon) {
      mapRef.current._sourceMarker = new maplibregl.Marker({ color: 'green' })
        .setLngLat([sourceCoords.lon, sourceCoords.lat])
        .addTo(mapRef.current);
    }

    if (destinationCoords && destinationCoords.lat && destinationCoords.lon) {
      mapRef.current._destMarker = new maplibregl.Marker({ color: 'red' })
        .setLngLat([destinationCoords.lon, destinationCoords.lat])
        .addTo(mapRef.current);
    }

    if (mapRef.current.getLayer('route')) {
      mapRef.current.removeLayer('route');
    }
    if (mapRef.current.getSource('route')) {
      mapRef.current.removeSource('route');
    }

        if (routeGeometry && routeGeometry.coordinates) {
      mapRef.current.once('styledata', () => {
        if (mapRef.current.getLayer('route')) {
          mapRef.current.removeLayer('route');
        }
        if (mapRef.current.getSource('route')) {
          mapRef.current.removeSource('route');
        }

        mapRef.current.addSource('route', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: routeGeometry,
          },
        });
        mapRef.current.addLayer({
          id: 'route',
          type: 'line',
          source: 'route',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: { 'line-color': '#1e40af', 'line-width': 4 },
        });
      });
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [sourceCoords, destinationCoords, routeGeometry]);

  return (
    <div
      ref={mapContainer}
      style={{
        height: '400px',
        width: '100%',
        borderRadius: '8px',
        overflow: 'hidden',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    />
  );
};

export default MapComponent;
