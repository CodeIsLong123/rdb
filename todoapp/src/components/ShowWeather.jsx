import React, { useEffect, useState } from 'react';
import axios from 'axios';

function WeatherService() {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://127.0.0.1:8000/api/weather')
            .then(response => {
                setWeather(response.data);
                setLoading(false);
                console.log("Weather data:", response.data);
            })
            .catch(error => {
                console.error("Error fetching weather data:", error);
                setLoading(false);
            });
    }, []);

    return (
        <div className="bg-gray-800 shadow-md rounded-lg p-6 text-gray-300">
            <h1 className="text-xl font-semibold text-gray-100 mb-4">Weather</h1>
            {loading ? (
                <p>Loading weather data...</p>
            ) : (
                <div>
                    <p>Temperature: {weather.temperature}°C</p>
                    <br/>
                    <p>Todays Weather: {weather.todays_suggestion}</p>
                    <br/>
                    <p>Tomorrows Wather: {weather.tomorrows_suggestion} m/s</p> 
                </div>
            )}
        </div>
    );
}

export default WeatherService;
