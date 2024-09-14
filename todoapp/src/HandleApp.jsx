import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, List, BookOpen, Cloud, FileText } from 'react-feather';
import Todoist from './components/Todoist';
import Notion from './components/Notion';

const WeatherService = () => {
  const [weatherData, setWeatherData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/weather')
      .then(response => response.json())
      .then(data => setWeatherData(data))
      .catch(error => console.error('Error fetching weather data:', error));
  }, []);

  if (!weatherData) return <div className="animate-pulse">Loading weather...</div>;

  return (
    <div className="text-gray-200">
      <div className="flex items-center justify-between mb-4">
        <span className="text-5xl font-bold">{weatherData.temperature}°C</span>
        <Cloud className="text-blue-400" size={48} />
      </div>
      <div className="space-y-2">
        <p className="text-sm opacity-80">{weatherData.todays_suggestion}</p>
        <p className="text-sm opacity-80 mt-2">{weatherData.tomorrows_suggestion}</p>
      </div>
    </div>
  );
};

const NewsService = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/news')
      .then(response => response.json())
      .then(data => {
        setNews(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching news data:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="animate-pulse">Loading news...</div>;

  return (
    <div className="text-gray-200 space-y-4">
      {news.map((article, index) => (
        <div key={index} className="border-b border-gray-700 pb-2 last:border-b-0">
          <h2 className="text-lg font-semibold">{article.title}</h2>
          <p className="text-xs text-gray-400 mt-1">{article.date}</p>
          <p className="mt-2 text-sm line-clamp-2 opacity-80">{article.text_content}</p>
          <a href={article.link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline mt-2 inline-block text-sm">Read more</a>
        </div>
      ))}
    </div>
  );
};

const DashboardItem = ({ children, title, icon: Icon }) => {
  return (
    <motion.div
      className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg overflow-hidden"
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="bg-opacity-50 bg-gray-700 p-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-100 flex items-center">
          <Icon className="mr-2" /> {title}
        </h2>
      </div>
      <div className="p-4 overflow-y-auto max-h-[400px]">
        {children}
      </div>
    </motion.div>
  );
};

const ThemeToggle = ({ isDark, toggleTheme }) => (
  <button
    onClick={toggleTheme}
    className="fixed top-4 right-4 p-2 rounded-full bg-opacity-50 bg-gray-700 text-gray-200 hover:bg-opacity-75 focus:outline-none transition-all duration-300"
  >
    {isDark ? <Sun size={20} /> : <Moon size={20} />}
  </button>
);
function HandleApp() {
  const [isDark, setIsDark] = useState(true);
  const toggleTheme = () => setIsDark(!isDark);

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-gray-200' : 'bg-gray-100 text-gray-800'} transition-colors duration-500`}>
      <ThemeToggle isDark={isDark} toggleTheme={toggleTheme} />
      <div className="p-6">
        <h1 className="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
          Personal Dashboard
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <DashboardItem title="Todoist" icon={List}>
            <Todoist />
          </DashboardItem>
          <DashboardItem title="Notion" icon={BookOpen}>
            <Notion />
          </DashboardItem>
          <DashboardItem title="Weather" icon={Cloud}>
            <WeatherService />
          </DashboardItem>
          <DashboardItem title="News" icon={FileText}>
            <NewsService />
          </DashboardItem>
        </div>
      </div>
      <footer className={`${isDark ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600'} text-center p-4 transition-colors duration-500`}>
        <p>&copy; {new Date().getFullYear()} Personal Dashboard</p>
      </footer>
    </div>
  );
}

export default HandleApp;