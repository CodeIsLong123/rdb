import React, { useEffect, useState } from 'react';
import axios from 'axios';

function NewsService() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/news')
      .then(response => {
        setNews(response.data);
        setLoading(false);
        console.log("News data:", response.data);
      })
      .catch(error => {
        console.error("Error fetching news data:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-gray-800 shadow-md rounded-lg p-6 text-gray-300">
      <h1 className="text-xl font-semibold text-gray-100 mb-4">News</h1>
      {loading ? (
        <p>Loading news data...</p>
      ) : (
        <div>
          {news.map((article, index) => (
            <div key={index} className="mb-4">
              <h2 className="text-lg font-semibold">{article.title}</h2>
              <p className="text-sm text-gray-400">{article.date}</p>
              <p className="mt-2">{article.text_content}</p>
              <a href={article.link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline mt-2 inline-block">Read more</a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default NewsService;