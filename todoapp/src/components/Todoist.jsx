import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Circle, Flag, Calendar, X } from 'react-feather';

const priorityColors = {
  1: 'text-gray-400',
  2: 'text-blue-400',
  3: 'text-yellow-400',
  4: 'text-red-400'
};

const TaskItem = ({ task, onComplete, onDelete }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-gray-800 rounded-lg p-3 mb-2 flex items-center justify-between"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center">
        <button onClick={() => onComplete(task.id)} className="mr-3">
          {task.completed ? 
            <CheckCircle className="text-green-400" size={20} /> : 
            <Circle className="text-gray-400 hover:text-gray-200" size={20} />
          }
        </button>
        <div>
          <p className={`text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-200'}`}>
            {task}
          </p>
          {task.due && (
            <div className="flex items-center text-xs text-gray-400 mt-1">
              <Calendar size={12} className="mr-1" />
              {new Date(task.due.date).toLocaleDateString()}
            </div>
          )}
        </div>
      </div>
      <div className="flex items-center">
        <Flag className={`${priorityColors[task.priority]} mr-2`} size={16} />
        <AnimatePresence>
          {isHovered && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={() => onDelete(task.id)}
              className="text-gray-400 hover:text-red-400 transition-colors duration-200"
            >
              <X size={16} />
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const Todoist = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/tasks')
      .then(response => response.json())
      .then(data => {
        setTasks(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching Todoist tasks:', error);
        setLoading(false);
      });
  }, []);

  const handleComplete = (taskId) => {
    fetch(`http://localhost:8000/api/todoist/remove/${taskId}`, { method: 'POST' })
      .then(() => {
        setTasks(tasks.map(task => 
          task.id === taskId ? { ...task, completed: true } : task
        ));
      })
      .catch(error => console.error('Error completing task:', error));
  };

  const handleDelete = (taskId) => {
    // Assuming your API supports task deletion
    fetch(`http://localhost:8000/api/todoist/delete/${taskId}`, { method: 'DELETE' })
      .then(() => {
        setTasks(tasks.filter(task => task.id !== taskId));
      })
      .catch(error => console.error('Error deleting task:', error));
  };
  const handleRefresh = () => {
    setLoading(true);
    fetch('http://localhost:8000/api/tasks')
      .then(response => response.json())
      .then(data => {
        setTasks(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching Todoist tasks:', error);
        setLoading(false);
      });
  };
  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        
        <h2 className="text-xl font-bold text-gray-100">Tasks</h2>
        <button 
          onClick={handleRefresh} 
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm rounded-md transition-colors duration-200 flex items-center"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        <span className="text-sm text-gray-400">{tasks.length} tasks</span>
      </div>

        <AnimatePresence>
          {tasks.map(task => (
            <TaskItem 
              key={task.id} 
              task={task.task} 
              onComplete={handleComplete}
              onDelete={handleDelete}
            />
          ))}
        </AnimatePresence>

    </div>
  );
};

export default Todoist;