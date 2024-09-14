import os
import sys
import datetime
import requests
import logging
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI


apis_dir = os.path.dirname(os.getcwd())

weather_api_dir = os.path.join(apis_dir, 'WeatherAPI')
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
print(current_dir)
sys.path.insert(0, parent_dir)

# Try to import WeatherAPI

from WeatherAPI.hookup_api import WeatherAPI


# Rest of your code remains the same
class ConnectTodoistAPI:
    def __init__(self):
        self.api_key = os.getenv("td_api_key")
        if not self.api_key:
            raise ValueError("API Key not found. Please check your environment variables.")
        self.api = TodoistAPI(self.api_key)

    def get_projects(self):
        try:
            projects = self.api.get_projects()
            return projects
        except Exception as e:
            logging.error(f"Error getting projects: {e}")
            return []

    def assemble_tasks(self) -> list[dict]:
        try:
            tasks = self.api.get_tasks()
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "content": task.content,
                    "due": task.due,
                    "priority": task.priority,
                    "project_id": task.project_id
                }
                task_list.append(task_dict)
            return task_list
        except Exception as e:
            logging.error(f"Error assembling tasks: {e}")
            return []

    def add_task(self, content="", due_date="", priority=1):
        try:
            task = self.api.add_task(
                content=content,
                due_string=due_date,
                priority=priority
            )
            return task
        except Exception as e:
            logging.error(f"Error adding task: {e}")
            return None

    def mark_task(self, task_id):
        try:
            is_success = self.api.close_task(task_id=task_id)
            print(f"Task {task_id} marked as done: {is_success}")
        except Exception as error:
            print(f"Error marking task {task_id} as done: {error}")

    def update_task(self, task_id, **kwargs):
        try:
            updated_task = self.api.update_task(task_id=task_id, **kwargs)
            return updated_task
        except Exception as e:
            logging.error(f"Error updating task {task_id}: {e}")
            return None

    def put_sunscreens_reminder(self):

        weather = WeatherAPI()
        weather_today = weather.get_air_temperature(os.environ.get('LATITUDE'), os.environ.get('LONGITUDE'))
    #     weather_t = weather_today['data'] 
        try:
            weather_data = weather.get_tomorrow_forecast(os.environ.get('LATITUDE'), os.environ.get('LONGITUDE'))
            if weather_data:
                air_temperature = weather_data['data']['instant']['details']['air_temperature']
                uv = weather_data['data']['instant']['details']['ultraviolet_index_clear_sky']
                uu = weather_data['data']["next_1_hours"]["summary"]["symbol_code"] 
                if air_temperature >= 20:
                    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    task = self.add_task(content="Put on sunscreen", due_date=tomorrow)
                    if task:
                        return f"Task added: {task.content} (due: {task.due.date})"
                    else:
                        return "Failed to add task"
                else:
                    return f"No reminder added. Temperature ({air_temperature}°C) is below threshold."
        except Exception as e:
            logging.error(f"Error in put_sunscreens_reminder: {e}")
            return f"Error occurred: {str(e)}"

if __name__ == '__main__':
    load_dotenv()  # Load environment variables
    api = ConnectTodoistAPI()
    result = api.put_sunscreens_reminder()
    print(result)