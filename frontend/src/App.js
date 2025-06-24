import React, { useState } from 'react';
import { MapPin, Calendar, Plane, Navigation } from 'lucide-react';
import MapComponent from './components/MapComponent';
import './App.css';

const ENDPOINT = 'http://localhost:8000';

const App = () => {
  const [formData, setFormData] = useState({ source: '', destination: '', days: 3 });
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState('');
  const [error, setError] = useState(null);
  const [sourceCoords, setSourceCoords] = useState(null);
  const [destinationCoords, setDestinationCoords] = useState(null);
  const [routeData, setRouteData] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'days' ? parseInt(value) || 1 : value
    }));
  };

  const geocodePlace = async (source, destination) => {
    const res = await fetch(`${ENDPOINT}/get_route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_address: source, destination_address: destination }),
    });
    return res.ok ? await res.json() : null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { source, destination, days } = formData;
    if (!source || !destination) return setError('Both source and destination are required.');

    setLoading(true);
    setError(null);
    setItinerary('');
    setRouteData(null);

    try {
      const geo = await geocodePlace(source, destination);
      if (!geo) throw new Error('Geocoding failed');
      setSourceCoords(geo.sourceCoords);
      setDestinationCoords(geo.destinationCoords);
      setRouteData(geo.routeData);

      const res = await fetch(`${ENDPOINT}/plan_trip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, destination, days }),
      });
      const data = await res.json();
      if (!res.ok || !data.final_output) throw new Error(data.detail || 'Itinerary error');
      setItinerary(data.final_output);
    } catch (err) {
      setError(err.message || 'Unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const renderCardLayout = (markdown) => {
    const headers = [...markdown.matchAll(/^Day (\d+):\s*(.*?)$/gm)];
    const days = markdown.split(/^Day \d+:.*$/gm).slice(1);

    return days.map((dayText, index) => {
      const header = headers[index]?.[2]?.trim() || `Day ${index + 1}`;
      const lines = dayText.split(/\n(?=\*\s)/g).map(l => l.trim()).filter(Boolean);

      return (
        <div className="day-container" key={index}>
          <div className="activity-card">
            <div className="day-header">
              <div className="day-number">Day {index + 1}</div>
              <div className="day-info">
                <div className="day-title">{header}</div>
                <div className="day-subtitle">Planned activities</div>
              </div>
            </div>
            <div className="activities-container">
              {lines.map((activity, i) => (
                <div className="activity-title" key={i}>{activity}</div>
              ))}
            </div>
          </div>
        </div>
      );
    });
  };

  return (
    <div className="app-container">
      <div className="background-animations">
        <div className="bg-circle-1"></div>
        <div className="bg-circle-2"></div>
        <div className="bg-circle-3"></div>
      </div>

      <div className="main-content">
        <div className="header">
          <div className="header-icon-container">
            <div className="header-icon">
              <Plane className="w-8 h-8 text-white" />
            </div>
            <h1 className="header-title">AI Travel Planner</h1>
          </div>
          <p className="header-subtitle">Let our AI create the perfect itinerary for your dream destination</p>
        </div>

        <div className="form-container">
          <div className="form-card">
            <form onSubmit={handleSubmit} className="form">
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label"><MapPin /> From</label>
                  <input name="source" value={formData.source} onChange={handleInputChange} placeholder="From" className="form-input focus-teal" required />
                </div>
                <div className="form-group">
                  <label className="form-label"><Navigation /> To</label>
                  <input name="destination" value={formData.destination} onChange={handleInputChange} placeholder="To" className="form-input focus-orange" required />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label"><Calendar /> Days</label>
                <input type="number" name="days" min="1" max="30" value={formData.days} onChange={handleInputChange} className="form-input focus-purple" required />
              </div>
              <button type="submit" disabled={loading} className={`submit-button ${loading ? 'disabled' : 'active'}`}>
                {loading ? (
                  <div className="loading-content">
                    <div className="loading-spinner"></div>
                    AI is crafting your trip...
                  </div>
                ) : 'Generate AI Itinerary'}
              </button>
            </form>
          </div>
        </div>

        {error && <div className="text-red-500 font-medium mt-4">{error}</div>}

        {typeof itinerary === 'string' && (
          <div className="itinerary-container">
            <div className="itinerary-main">
              <div className="itinerary-header">
                <div>
                  <h2 className="itinerary-title">{formData.source} → {formData.destination}</h2>
                  <p className="itinerary-subtitle"><Calendar /> {formData.days} days</p>
                </div>
                <button onClick={() => setItinerary('')} className="new-trip-button">Plan New Trip</button>
              </div>
              <div className="timeline-container">
                <div className="timeline-line"></div>
                {renderCardLayout(itinerary)}
              </div>
            </div>
            <div className="sidebar">
              <div className="sidebar-card">
                <MapComponent sourceCoords={sourceCoords} destinationCoords={destinationCoords} routeGeometry={routeData?.geometry} />
                {routeData && (
                  <div className="mt-4 text-sm text-white">
                    Distance: {routeData.distance_km} km | Duration: {routeData.duration_minutes} minutes
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
