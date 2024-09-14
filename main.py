
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from APIs.TodoistAPI.hookup_api import ConnectTodoistAPI
from APIs.NotionAPI.hookup_api import ConnectNotionAPI
from APIs.WeatherAPI.hookup_api import WeatherAPI
from APIs.NewsAPI.fetch_news import TagesSchaueClient
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os 
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Wetter(BaseModel):
    temperature: float
    unit: str = "°C"  
    todays_suggestion: str = "No suggestion available"
    tomorrows_suggestion: str = "No suggestion available"

class News(BaseModel):
    title: str
    date: str
    description: str
    url: str

class Task(BaseModel):
    id: int
    task: str = "No task available"
    priority: int
    project_id: int 
    
class NotionEvent(BaseModel):
    id: int
    event_name: str
    event_date: str
    description: str
    

############## Todoist API ##############

@app.get("/api/tasks", response_model=list[Task])
def get_todoist_tasks():
    api = ConnectTodoistAPI()
    tasks = api.assemble_tasks()
    print(tasks)
    task_list = []
    for task in tasks:
        task_list.append(Task(id=task['id'],  # Use task['id'] for the correct ID
                                task=task['content'], 
                                priority=task['priority'], 
                                project_id=task['project_id']))
    return task_list

@app.post("/api/todoist/remove/{task_id}")
def remove_task(task_id: int):
    print(f"Received task_id: {task_id}")  # Log the received task_id
    api = ConnectTodoistAPI()
    api.mark_task(task_id=task_id)
    return {"message": f"Task {task_id} removed successfully"}

        

@app.post("/api/todoist/add")
def add_task(task: Task):
    api = ConnectTodoistAPI()
    api.add_task(task.task, priority = task.priority)

    return {"message": "Task added successfully"}



############## Weather API ##############
@app.get("/api/weather", response_model=Wetter)
def get_weather():
    api = WeatherAPI()
    latitude = os.environ.get('LATITUDE', '52.5200')  # Standardwert für Berlin
    longitude = os.environ.get('LONGITUDE', '13.4050')  # Standardwert für Berlin
    temperature = api.get_air_temperature(latitude, longitude)

    suggestion = api.suggest_clothing(latitude, longitude)
    tmrw_suggestion = api.suggest_clothing_for_tomorrow(latitude, longitude)
    return Wetter(temperature=temperature, unit="°C", todays_suggestion=suggestion, tomorrows_suggestion=tmrw_suggestion)

############## Notion API ##############
@app.get("/api/events", response_model=list[NotionEvent])
def get_notion_events():
    api = ConnectNotionAPI()
    try:
        # Fetch data from Notion API
        pages = api.get_pages()
        event_names = api.extract_event_name(pages)
        event_dates = api.extract_event_date(pages)
        descriptions = api.extract_description(pages)

        event_list = []
        
        # Safely iterate over event names, dates, and descriptions
        for i, (event_name, event_date, description) in enumerate(zip(event_names, event_dates, descriptions)):
            # Handle different date formats (e.g., when start and end dates differ)
            if len(event_date) == 3:
                event_date_str = f"{event_date[0]} {event_date[1]} - {event_date[2]}"
            elif len(event_date) == 4:
                event_date_str = f"{event_date[0]} {event_date[1]} to {event_date[2]} {event_date[3]}"
            else:
                event_date_str = "Invalid date format"
            

            if not description:
                description = "No description available"
            
            # Append the event to the list
            event_list.append(
                NotionEvent(
                    id=i,
                    event_name=event_name, 
                    event_date=event_date_str,  # Pass the formatted string here
                    description=description
                )
            )
        
        return event_list

    except Exception as e:
        # Catch and log any unexpected errors
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")



DATABASE_NAME = "news.db"

def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        title TEXT,
        date TEXT,
        text_content TEXT,
        link TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_update (
        id INTEGER PRIMARY KEY,
        timestamp TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_articles(articles):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")  # Alte Artikel löschen
    for article in articles:
        cursor.execute('''
        INSERT INTO articles (title, date, text_content, link)
        VALUES (?, ?, ?, ?)
        ''', (article['title'], article['date'], article['text_content'], article['link']))
    cursor.execute("DELETE FROM last_update")
    cursor.execute("INSERT INTO last_update (timestamp) VALUES (?)", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

def get_cached_articles():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, date, text_content, link FROM articles")
    articles = [{"title": row[0], "date": row[1], "text_content": row[2], "link": row[3]} for row in cursor.fetchall()]
    conn.close()
    return articles

def is_update_needed():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM last_update")
    result = cursor.fetchone()
    conn.close()
    if not result:
        return True
    last_update = datetime.fromisoformat(result[0])
    return datetime.now() - last_update > timedelta(days=1)

def fetch_and_update_news():
    try:
        api = TagesSchaueClient()
        articles = api.get_articles()
        cleaned_articles = api.cleanup_articles(articles)
        insert_articles(cleaned_articles)
        print("News database updated successfully")
    except Exception as e:
        print(f"Error updating news database: {e}")

@app.on_event("startup")
def startup_event():
    create_database()
    if is_update_needed():
        fetch_and_update_news()
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_update_news, 'cron', hour=8)  # Jeden Tag um Mitternacht ausführen
    scheduler.start()

# Aktualisierter News API-Endpunkt
@app.get("/api/news")
def show_the_news():
    if is_update_needed():
        fetch_and_update_news()
    return get_cached_articles()



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)