from notion_client import Client
import os 
from dotenv import load_dotenv
import requests
import json 
import re 
from itertools import zip_longest
load_dotenv()
class ConnectNotionAPI:
    ## For no this has calendar and other tasks, 
    # but in the future it will be
    # split into different classes
    def __init__(self):
        self.token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('NOTION_DB_TOKE')
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json", 
            "Notion-Version": "2022-06-28"
        }
        self.client = Client(auth=self.token)
        
    def get_pages(self):

        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        payload = {"page_size": 100}  
        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()
        return data['results']


    def extract_event_name(self, page):
        
        list_content = []   
        for item in page:   
            content = item['properties']["Action"]['title'] 
            if content == []:
                print("skipped empty")

                continue
            
            else :
                list_content.append(content[0]['plain_text'])
    
        return list_content
    
    def extract_event_date(self, page):
        list_of_dates = [] 
        try: 
            for item in page:
                # Check if 'Date' field exists
                content = item.get('properties', {}).get('Date', {}).get('date', None)
                if content is None:
                    print("skipped empty")
                    continue
                
                # Extract start date and time
                start_content = content.get('start', '')
                start_date = re.search(r'\d{4}-\d{2}-\d{2}', start_content)
                start_time = re.search(r'\d{2}:\d{2}', start_content)
                
                # Set default times if not present
                start_time = start_time.group(0) if start_time else "00:00"
                
                # Extract end date and time
                end_content = content.get('end', '')
                end_date = re.search(r'\d{4}-\d{2}-\d{2}', end_content)
                end_time = re.search(r'\d{2}:\d{2}', end_content)
                
                # Set default end time
                end_time = end_time.group(0) if end_time else "23:59"
                
                # Handle case where start and end dates are the same or different
                if start_date and end_date and start_date.group(0) == end_date.group(0):
                    list_of_dates.append((start_date.group(0), start_time, end_time))
                elif start_date and end_date:
                    list_of_dates.append((start_date.group(0), start_time, end_date.group(0), end_time))
                else:
                    print(f"Invalid date format in item: {item}")
                    
            return list_of_dates
        except Exception as e:
            print(f"Error extracting event dates: {e}")
            return None
        
    
    def extract_description(self, page):
        list_of_descriptions = []
        for item in page:
            content = item['properties']['Description']['rich_text']
            if content == []:
            
                list_of_descriptions.append("No description available")
                continue
            else:
                list_of_descriptions.append(content[0]['plain_text'])
        return list_of_descriptions
    
            
            
    def creare_dict(self, event_name, event_date, description):
        # Initialize the dictionary
        event_dict = {}

        # Use zip_longest to handle mismatched lengths
        for name, date, desc in zip_longest(event_name, event_date, description, fillvalue="No information"):
                
            if not desc or len(desc) == 0:
                desc = "No description available"
            
            # Create the dictionary entry
            event_dict[name] = {
                "date": date,
                "description": desc
            }

        return event_dict

if __name__ == '__main__':
    
    napi = ConnectNotionAPI()
    pages = napi.get_pages()
    content = napi.extract_event_name(pages)
    date= napi.extract_event_date(pages)
    description = napi.extract_description(pages)   
    event_dict = napi.creare_dict(content, date, description)   
    
    
    
    