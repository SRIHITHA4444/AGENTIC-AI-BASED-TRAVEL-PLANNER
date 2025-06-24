import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const geocodeAddress = async (address) => {
    try {
        const response = await api.get('/geocode', { params: { address } });
        return response.data;
    } catch (error) {
        console.error('Error geocoding:', error);
        throw error;
    }
};

export const getRoute = async (sourceCoords, destCoords, travelMode = 'driving') => {
    try {
        const response = await api.post('/route', { source: sourceCoords, destination: destCoords, mode: travelMode });
        return response.data;
    } catch (error) {
        console.error('Error getting route:', error);
        throw error;
    }
};
