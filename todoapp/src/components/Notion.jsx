import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Info } from 'react-feather';

const NotionEvent = ({ event, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="bg-gray-800 rounded-lg p-4 mb-4 hover:shadow-lg transition-shadow duration-300"
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-100">{event.event_name}</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-400 hover:text-gray-200 transition-colors duration-200"
        >
          {isExpanded ? 'Less' : 'More'}
        </button>
      </div>
      <div className="flex items-center text-gray-400 text-sm mt-2">
        <Calendar size={14} className="mr-2" />
        <span>{event.event_date}</span>
      </div>
      <motion.div
        initial={false}
        animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <p className="text-gray-300 mt-2 text-sm">{event.description}</p>
      </motion.div>
    </motion.div>
  );
};

const Notion = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/events')
      .then(response => response.json())
      .then(data => {
        setEvents(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching Notion events:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-100">Upcoming Events</h2>
        <span className="text-sm text-gray-400">{events.length} events</span>
      </div>
      <div className="overflow-y-auto max-h-[400px] pr-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800">
        {events.map((event, index) => (
          <NotionEvent key={event.id} event={event} index={index} />
        ))}
      </div>
    </div>
  );
};

export default Notion;