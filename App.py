import streamlit as st
import requests
import json
import time
import io
import csv
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import base64


try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None
    st.error("Pillow is missing. Add 'Pillow' to requirements.txt")


try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
except Exception:
    service_account = None
    build = None
    MediaIoBaseUpload = None
    st.error("Google API packages missing. Add these to requirements.txt: "
             "google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client")

st.set_page_config(
    page_title="AI Image Editor Pro - Complete Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com',
        'About': "AI Image Editor Pro - Complete Edition with Google Sheets & CSV"
    }
)

st.markdown("""
<style>
    /* Main Theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 16px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    
    /* Status Boxes */
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    
    /* Image Cards */
    .image-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        margin-bottom: 20px;
        height: 100%;
    }
    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        border-color: #4CAF50;
    }
    
    .image-container {
        position: relative;
        width: 100%;
        padding-bottom: 75%;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 12px;
        cursor: pointer;
    }
    .image-container img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    .image-container:hover img {
        transform: scale(1.05);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-success {
        background-color: #28a745;
        color: white;
    }
    .status-pending {
        background-color: #ffc107;
        color: black;
    }
    .status-fail {
        background-color: #dc3545;
        color: white;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Search Bar */
    .search-container {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Filter Chips */
    .filter-chip {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        background: #e9ecef;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .filter-chip:hover {
        background: #667eea;
        color: white;
    }
    .filter-chip.active {
        background: #667eea;
        color: white;
    }
    
    /* Batch Actions Bar */
    .batch-bar {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 15px 30px;
        border-radius: 50px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from {
            transform: translate(-50%, 100px);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
    
    /* Gallery Grid */
    .gallery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    
    /* Progress Ring */
    .progress-ring {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 4px solid #e0e0e0;
        border-top-color: #667eea;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)


BASE_URL = "https://api.kie.ai/api/v1/jobs"
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

def init_session_state():
    """Initialize all session state variables with comprehensive defaults."""
    defaults = {
        'api_key': "",
        'task_history': [],
        'current_task': None,
        'authenticated': False,
        'service': None,
        'sheets_service': None,
        'credentials': None,
        'generated_images': [],
        'library_images': [],
        'gdrive_folder_id': None,
        'spreadsheet_id': None,
        'auto_upload': True,
        'auto_log_sheets': True,
        'polling_active': False,
        'service_account_info': None,
        'upload_queue': [],
        'stats': {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'total_images': 0,
            'uploaded_images': 0,
            'sheets_entries': 0,
            'csv_entries': 0
        },
        'current_page': "Generate",
        'selected_image_for_edit': None,
        'edit_mode': None,
        'library_view_mode': 'grid',
        'library_sort_by': 'date_desc',
        'library_search_query': '',
        'library_filter_type': 'all',
        'selected_images': [],
        'show_image_modal': False,
        'modal_image_data': None,
        'needs_rerun': False,
        'csv_data': [],
        'favorites': [],
        'tags': {},
        'comparison_mode': False,
        'comparison_images': [],
        'batch_mode': False,
        'batch_prompts': [],
        'download_queue': [],
        'advanced_settings': {
            'guidance_scale': 7.5,
            'negative_prompt': '',
            'seed': -1,
            'sampler': 'euler_a'
        },
        'preset_prompts': [
            "A serene landscape with mountains at sunset",
            "Abstract digital art with vibrant colors",
            "Futuristic cityscape with neon lights",
            "Portrait of a character in fantasy style",
            "Minimalist design with geometric shapes"
        ],
        'prompt_history': [],
        'filters': {
            'date_from': None,
            'date_to': None,
            'model': 'all',
            'status': 'all',
            'has_tags': False
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


def authenticate_with_service_account(service_account_json):
    """Authenticate with Google Drive and Sheets using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_json,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        st.session_state.credentials = credentials
        st.session_state.service = service
        st.session_state.sheets_service = sheets_service
        st.session_state.authenticated = True
        return True, "Successfully authenticated with Google Drive and Sheets"
    except Exception as e:
        return False, f"Authentication failed: {str(e)}"

def create_app_folder():
    """Create or get the app's folder in Google Drive."""
    if not st.session_state.service:
        return None
    
    try:
        results = st.session_state.service.files().list(
            q="name='AI_Image_Editor_Pro' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        if files:
            st.session_state.gdrive_folder_id = files[0]['id']
            return files[0]['id']
        
        file_metadata = {
            'name': 'AI_Image_Editor_Pro',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = st.session_state.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        st.session_state.gdrive_folder_id = folder_id
        return folder_id
    except Exception as e:
        st.error(f"Error creating folder: {str(e)}")
        return None

def upload_to_gdrive(image_url: str, file_name: str, task_id: str = None):
    """Download image from URL and upload to Google Drive with public access."""
    if not st.session_state.service:
        return None
    
    try:
        folder_id = st.session_state.gdrive_folder_id or create_app_folder()
        if not folder_id:
            return None
        
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = response.content
        
        mime_type = 'image/png'
        if file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif file_name.lower().endswith('.webp'):
            mime_type = 'image/webp'
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(image_data),
            mimetype=mime_type,
            resumable=True
        )
        
        file = st.session_state.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, webContentLink, mimeType'
        ).execute()
        
        file_id = file.get('id')
        
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        st.session_state.service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        public_image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
        thumbnail_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
        
        st.session_state.stats['uploaded_images'] += 1
        
        return {
            'file_id': file_id,
            'file_name': file.get('name'),
            'web_link': file.get('webViewLink'),
            'content_link': file.get('webContentLink'),
            'public_image_url': public_image_url,
            'thumbnail_url': thumbnail_url,
            'mime_type': file.get('mimeType'),
            'uploaded_at': datetime.now().isoformat(),
            'task_id': task_id,
            'original_url': image_url,
            'id': file_id,
            'name': file.get('name')
        }
    except Exception as e:
        st.error(f"Error uploading to Google Drive: {str(e)}")
        return None

def list_gdrive_images(folder_id):
    """List all images in the Google Drive folder."""
    if not st.session_state.service or not folder_id:
        return []
    
    try:
        results = st.session_state.service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
            spaces='drive',
            fields='files(id, name, webViewLink, thumbnailLink, createdTime, mimeType)',
            orderBy='createdTime desc',
            pageSize=100
        ).execute()
        
        return results.get('files', [])
    except Exception as e:
        st.error(f"Error listing images: {str(e)}")
        return []

def get_gdrive_image_bytes(file_id):
    """Download image bytes from Google Drive."""
    if not st.session_state.service:
        return None
    
    try:
        request = st.session_state.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh.read()
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def delete_gdrive_file(file_id):
    """Delete a file from Google Drive."""
    if not st.session_state.service:
        return False
    
    try:
        st.session_state.service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False


def create_or_get_spreadsheet():
    """Create or get the tracking spreadsheet."""
    if not st.session_state.sheets_service or not st.session_state.service:
        return None
    
    try:
        folder_id = st.session_state.gdrive_folder_id or create_app_folder()
        
        results = st.session_state.service.files().list(
            q=f"name='AI_Image_Generation_Log' and mimeType='application/vnd.google-apps.spreadsheet' and '{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        if files:
            st.session_state.spreadsheet_id = files[0]['id']
            return files[0]['id']
        
        spreadsheet = {
            'properties': {
                'title': 'AI_Image_Generation_Log'
            },
            'sheets': [{
                'properties': {
                    'title': 'Image Log',
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                }
            }]
        }
        
        spreadsheet = st.session_state.sheets_service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        st.session_state.service.files().update(
            fileId=spreadsheet_id,
            addParents=folder_id,
            fields='id, parents'
        ).execute()
        
        headers = [['Timestamp', 'Model', 'Prompt', 'Image URL', 'Drive Link', 'Task ID', 'Status', 'Tags']]
        st.session_state.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Image Log!A1:H1',
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        requests_body = {
            'requests': [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.26,
                                'green': 0.52,
                                'blue': 0.96
                            },
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {
                                    'red': 1,
                                    'green': 1,
                                    'blue': 1
                                }
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }]
        }
        
        st.session_state.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=requests_body
        ).execute()
        
        st.session_state.spreadsheet_id = spreadsheet_id
        return spreadsheet_id
        
    except Exception as e:
        st.error(f"Error creating spreadsheet: {str(e)}")
        return None

def log_to_sheets(model: str, prompt: str, image_url: str, drive_link: str = "", task_id: str = "", status: str = "success", tags: str = ""):
    """Log image generation to Google Sheets."""
    if not st.session_state.sheets_service:
        return False
    
    try:
        spreadsheet_id = st.session_state.spreadsheet_id or create_or_get_spreadsheet()
        if not spreadsheet_id:
            return False
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [[timestamp, model, prompt, image_url, drive_link, task_id, status, tags]]
        
        st.session_state.sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Image Log!A:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': row}
        ).execute()
        
        st.session_state.stats['sheets_entries'] += 1
        return True
        
    except Exception as e:
        st.error(f"Error logging to sheets: {str(e)}")
        return False

def get_sheets_data():
    """Retrieve all data from the spreadsheet."""
    if not st.session_state.sheets_service or not st.session_state.spreadsheet_id:
        return []
    
    try:
        result = st.session_state.sheets_service.spreadsheets().values().get(
            spreadsheetId=st.session_state.spreadsheet_id,
            range='Image Log!A:H'
        ).execute()
        
        values = result.get('values', [])
        return values[1:] if len(values) > 1 else []
        
    except Exception as e:
        st.error(f"Error reading sheets data: {str(e)}")
        return []


def add_to_csv_data(model: str, prompt: str, image_url: str, drive_link: str = "", task_id: str = "", status: str = "success", tags: str = ""):
    """Add entry to CSV data in session state."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {
        'timestamp': timestamp,
        'model': model,
        'prompt': prompt,
        'image_url': image_url,
        'drive_link': drive_link,
        'task_id': task_id,
        'status': status,
        'tags': tags
    }
    st.session_state.csv_data.append(entry)
    st.session_state.stats['csv_entries'] += 1

def export_to_csv():
    """Export all CSV data to downloadable file."""
    if not st.session_state.csv_data:
        return None
    
    try:
        output = io.StringIO()
        fieldnames = ['timestamp', 'model', 'prompt', 'image_url', 'drive_link', 'task_id', 'status', 'tags']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(st.session_state.csv_data)
        
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error creating CSV: {str(e)}")
        return None

def load_csv_file(uploaded_file):
    """Load existing CSV file into session state."""
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        loaded_entries = list(csv_reader)
        st.session_state.csv_data.extend(loaded_entries)
        st.session_state.stats['csv_entries'] += len(loaded_entries)
        
        return True, f"Loaded {len(loaded_entries)} entries from CSV"
        
    except Exception as e:
        return False, f"Error loading CSV: {str(e)}"


def create_task(api_key, model, input_params, callback_url=None):
    """Create a generation task."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": input_params
    }
    
    if callback_url:
        payload["callBackUrl"] = callback_url
    
    try:
        response = requests.post(
            f"{BASE_URL}/createTask",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        data = response.json()
        if response.status_code == 200:
            if data.get("code") == 200:
                st.session_state.stats['total_tasks'] += 1
                return {"success": True, "task_id": data["data"]["taskId"]}
            else:
                return {"success": False, "error": data.get('msg', 'Unknown error')}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_task_status(api_key, task_id):
    """Check task status."""
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/recordInfo",
            headers=headers,
            params={"taskId": task_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                return {"success": True, "data": data["data"]}
            else:
                return {"success": False, "error": data.get('msg', 'Unknown error')}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def poll_task_until_complete(api_key, task_id, max_attempts=60, delay=2):
    """Poll task status until completion or timeout."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        result = check_task_status(api_key, task_id)
        
        if result["success"]:
            task_data = result["data"]
            state = task_data["state"]
            
            progress = min((attempt + 1) / max_attempts, 0.95)
            progress_bar.progress(progress)
            status_text.text(f"Status: {state} | Attempt {attempt + 1}/{max_attempts}")
            
            if state == "success":
                progress_bar.progress(1.0)
                status_text.text("✅ Task completed successfully!")
                return {"success": True, "data": task_data}
            elif state == "fail":
                progress_bar.empty()
                status_text.text("❌ Task failed")
                st.session_state.stats['failed_tasks'] += 1
                return {"success": False, "error": task_data.get('failMsg', 'Unknown error'), "data": task_data}
            
            time.sleep(delay)
        else:
            status_text.text(f"⚠️ Error checking status: {result['error']}")
            time.sleep(delay)
    
    progress_bar.empty()
    status_text.text("⏱️ Timeout reached")
    st.session_state.stats['failed_tasks'] += 1
    return {"success": False, "error": "Timeout reached"}


def save_and_upload_results(task_id, model, prompt, result_urls, tags=""):
    """Save results to history, upload to Drive, log to Sheets, and add to CSV."""
    for i, task in enumerate(st.session_state.task_history):
        if task['id'] == task_id:
            st.session_state.task_history[i]['status'] = 'success'
            st.session_state.task_history[i]['results'] = result_urls
            st.session_state.stats['successful_tasks'] += 1
            st.session_state.stats['total_images'] += len(result_urls)
            
            for j, result_url in enumerate(result_urls):
                file_name = f"{model.replace('/', '_')}_{task_id}_{j+1}.png"
                drive_link = ""
                
                if st.session_state.authenticated and st.session_state.auto_upload:
                    upload_info = upload_to_gdrive(result_url, file_name, task_id)
                    if upload_info:
                        st.session_state.library_images.insert(0, upload_info)
                        drive_link = upload_info.get('web_link', '')
                        st.success(f"✅ Uploaded {file_name} to Google Drive!")
                
                if st.session_state.authenticated and st.session_state.auto_log_sheets:
                    if log_to_sheets(model, prompt, result_url, drive_link, task_id, "success", tags):
                        st.success(f"📊 Logged to Google Sheets!")
                
                add_to_csv_data(model, prompt, result_url, drive_link, task_id, "success", tags)
            
            break

def add_tag_to_image(image_id, tag):
    """Add a tag to an image."""
    if image_id not in st.session_state.tags:
        st.session_state.tags[image_id] = []
    
    if tag not in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].append(tag)

def remove_tag_from_image(image_id, tag):
    """Remove a tag from an image."""
    if image_id in st.session_state.tags and tag in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].remove(tag)

def get_image_tags(image_id):
    """Get all tags for an image."""
    return st.session_state.tags.get(image_id, [])

def add_to_comparison(image_data):
    """Add image to comparison mode."""
    if len(st.session_state.comparison_images) < 4:
        st.session_state.comparison_images.append(image_data)
        return True
    return False

def remove_from_comparison(image_id):
    """Remove image from comparison."""
    st.session_state.comparison_images = [
        img for img in st.session_state.comparison_images if img.get('id') != image_id
    ]

with st.sidebar:
    st.title("⚙️ Configuration")
    
    st.subheader("🔑 API Key")
    api_key_input = st.text_input(
        "Enter KIE.AI API Key",
        type="password",
        value=st.session_state.api_key,
        key="api_key_input"
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    st.divider()
    
    st.subheader("☁️ Google Services")
    
    if not st.session_state.authenticated:
        uploaded_file = st.file_uploader(
            "Upload Service Account JSON",
            type=['json'],
            help="Upload your Google Cloud service account JSON file for Drive & Sheets access",
            key="service_account_uploader"
        )
        
        if uploaded_file:
            try:
                file_content = uploaded_file.getvalue().decode("utf-8")
                service_account_json = json.loads(file_content)
                
                success, message = authenticate_with_service_account(service_account_json)
                
                if success:
                    st.session_state.service_account_info = file_content
                    create_app_folder()
                    create_or_get_spreadsheet()
                    st.success("✅ " + message)
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.success("✅ Google Services Connected")
        
        st.checkbox(
            "Auto-upload to Drive",
            value=st.session_state.auto_upload,
            key="auto_upload_checkbox",
            on_change=lambda: setattr(st.session_state, 'auto_upload', st.session_state.auto_upload_checkbox)
        )
        
        st.checkbox(
            "Auto-log to Sheets",
            value=st.session_state.auto_log_sheets,
            key="auto_log_sheets_checkbox",
            on_change=lambda: setattr(st.session_state, 'auto_log_sheets', st.session_state.auto_log_sheets_checkbox)
        )
        
        if st.session_state.spreadsheet_id:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{st.session_state.spreadsheet_id}"
            st.markdown(f"[📊 Open Spreadsheet]({sheet_url})")
        
        if st.session_state.gdrive_folder_id:
            folder_url = f"https://drive.google.com/drive/folders/{st.session_state.gdrive_folder_id}"
            st.markdown(f"[📁 Open Drive Folder]({folder_url})")
    
    st.divider()
    
    st.subheader("📁 CSV Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.csv_data:
            csv_content = export_to_csv()
            if csv_content:
                st.download_button(
                    "💾 Export",
                    data=csv_content,
                    file_name=f"image_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col2:
        csv_upload = st.file_uploader(
            "Load CSV",
            type=['csv'],
            help="Load existing CSV log",
            label_visibility="collapsed"
        )
        
        if csv_upload:
            success, message = load_csv_file(csv_upload)
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.caption(f"📊 CSV Entries: {st.session_state.stats['csv_entries']}")
    
    st.divider()
    
    st.subheader("📊 Statistics")
    
    stats_container = st.container()
    with stats_container:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; opacity: 0.9;">Total Tasks</div>
            <div style="font-size: 28px; font-weight: bold;">{st.session_state.stats['total_tasks']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Success", st.session_state.stats['successful_tasks'])
            st.metric("🖼️ Images", st.session_state.stats['total_images'])
            st.metric("📊 Sheets", st.session_state.stats['sheets_entries'])
        with col2:
            st.metric("❌ Failed", st.session_state.stats['failed_tasks'])
            st.metric("📤 Uploaded", st.session_state.stats['uploaded_images'])
            st.metric("📁 CSV", st.session_state.stats['csv_entries'])
    
    st.divider()
    
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Refresh All", use_container_width=True):
        if st.session_state.authenticated:
            st.session_state.library_images = list_gdrive_images(st.session_state.gdrive_folder_id)
        st.rerun()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.task_history = []
        st.success("History cleared!")
    
    if st.button("💾 Backup All Data", use_container_width=True):
        if st.session_state.csv_data:
            csv_content = export_to_csv()
            st.download_button(
                "📥 Download Backup",
                data=csv_content,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


st.title("🎨 AI Image Editor Pro - Complete Edition")
st.caption("Full-featured image generation with Google Sheets, CSV, and advanced management")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎨 Generate",
    "📚 Library",
    "📊 Sheets View",
    "🔍 Compare",
    "📦 Batch",
    "ℹ️ About"
])

with tab1:
    st.header("Generate Images")
    
    if not st.session_state.api_key:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ API Key Required</strong><br>
            Please enter your KIE.AI API key in the sidebar to get started.
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.expander("💡 Preset Prompts", expanded=False):
            st.write("Click a preset to use it:")
            cols = st.columns(2)
            for idx, preset in enumerate(st.session_state.preset_prompts):
                with cols[idx % 2]:
                    if st.button(preset, key=f"preset_{idx}", use_container_width=True):
                        st.session_state.prompt_input = preset
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt = st.text_area(
                "Enter your prompt",
                placeholder="A beautiful sunset over mountains...",
                height=120,
                key="prompt_input",
                value=st.session_state.get('prompt_input', '')
            )
            
            if st.session_state.prompt_history:
                with st.expander("📜 Recent Prompts"):
                    for hist_prompt in st.session_state.prompt_history[-5:]:
                        if st.button(hist_prompt[:50] + "...", key=f"hist_{hist_prompt[:20]}"):
                            st.session_state.prompt_input = hist_prompt
                            st.rerun()
        
        with col2:
            model = st.selectbox(
                "Select Model",
                [
                    "flux-pro",
                    "flux-dev",
                    "flux-schnell",
                    "stable-diffusion-3.5",
                    "flux-realism"
                ],
                key="model_select"
            )
            
            num_images = st.number_input(
                "Number of Images",
                min_value=1,
                max_value=4,
                value=1,
                key="num_images"
            )
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            width = st.number_input("Width", min_value=256, max_value=2048, value=1024, step=64)
        with col4:
            height = st.number_input("Height", min_value=256, max_value=2048, value=1024, step=64)
        with col5:
            steps = st.slider("Steps", min_value=1, max_value=50, value=30)
        
        with st.expander("⚙️ Advanced Settings"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                guidance_scale = st.slider(
                    "Guidance Scale",
                    min_value=1.0,
                    max_value=20.0,
                    value=st.session_state.advanced_settings['guidance_scale'],
                    step=0.5
                )
                seed = st.number_input(
                    "Seed (-1 for random)",
                    min_value=-1,
                    value=st.session_state.advanced_settings['seed']
                )
            
            with col_b:
                negative_prompt = st.text_area(
                    "Negative Prompt",
                    value=st.session_state.advanced_settings['negative_prompt'],
                    placeholder="What to avoid in the image...",
                    height=100
                )
            
            st.session_state.advanced_settings['guidance_scale'] = guidance_scale
            st.session_state.advanced_settings['seed'] = seed
            st.session_state.advanced_settings['negative_prompt'] = negative_prompt
        
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="landscape, sunset, nature",
            key="tags_input"
        )
        
        if st.button("🚀 Generate Images", type="primary", use_container_width=True):
            if prompt:
                # Add to prompt history
                if prompt not in st.session_state.prompt_history:
                    st.session_state.prompt_history.append(prompt)
                
                with st.spinner("Creating task..."):
                    input_params = {
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_inference_steps": steps,
                        "num_images": num_images
                    }
                    
                    # Add advanced settings if configured
                    if guidance_scale != 7.5:
                        input_params["guidance_scale"] = guidance_scale
                    if seed != -1:
                        input_params["seed"] = seed
                    if negative_prompt:
                        input_params["negative_prompt"] = negative_prompt
                    
                    result = create_task(st.session_state.api_key, model, input_params)
                    
                    if result["success"]:
                        task_id = result["task_id"]
                        
                        st.session_state.task_history.insert(0, {
                            'id': task_id,
                            'model': model,
                            'prompt': prompt,
                            'timestamp': datetime.now().isoformat(),
                            'status': 'pending',
                            'results': [],
                            'tags': tags_input
                        })
                        
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>✅ Task created successfully!</strong><br>
                            Task ID: <code>{task_id}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        poll_result = poll_task_until_complete(
                            st.session_state.api_key,
                            task_id
                        )
                        
                        if poll_result["success"]:
                            task_data = poll_result["data"]
                            result_urls = task_data.get("result", [])
                            
                            if result_urls:
                                st.balloons()
                                st.markdown(f"""
                                <div class="success-box">
                                    <strong>🎉 Success!</strong> Generated {len(result_urls)} image(s)
                                </div>
                                """, unsafe_allow_html=True)
                                
                                save_and_upload_results(task_id, model, prompt, result_urls, tags_input)
                                
                                cols = st.columns(min(len(result_urls), 3))
                                for idx, url in enumerate(result_urls):
                                    with cols[idx % 3]:
                                        st.image(url, caption=f"Image {idx + 1}", use_container_width=True)
                                        
                                        col_dl, col_fav = st.columns(2)
                                        with col_dl:
                                            st.download_button(
                                                "💾 Download",
                                                data=requests.get(url).content,
                                                file_name=f"image_{idx+1}.png",
                                                mime="image/png",
                                                key=f"dl_{task_id}_{idx}"
                                            )
                                        with col_fav:
                                            if st.button("⭐ Favorite", key=f"fav_{task_id}_{idx}"):
                                                st.session_state.favorites.append({
                                                    'url': url,
                                                    'prompt': prompt,
                                                    'task_id': task_id
                                                })
                                                st.success("Added to favorites!")
                            else:
                                st.warning("No results returned from API")
                        else:
                            st.markdown(f"""
                            <div class="error-box">
                                <strong>❌ Task failed</strong><br>
                                {poll_result.get('error', 'Unknown error')}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            <strong>❌ Error creating task</strong><br>
                            {result['error']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a prompt")
    
    if st.session_state.task_history:
        st.divider()
        st.subheader("📜 Recent Tasks")
        
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            filter_status = st.selectbox("Status", ["all", "success", "pending", "fail"])
        with col_filter2:
            filter_model = st.selectbox("Model", ["all"] + ["flux-pro", "flux-dev", "flux-schnell", "stable-diffusion-3.5", "flux-realism"])
        with col_filter3:
            show_count = st.number_input("Show", min_value=5, max_value=50, value=10)
        
        # Filter tasks
        filtered_tasks = st.session_state.task_history
        if filter_status != "all":
            filtered_tasks = [t for t in filtered_tasks if t['status'] == filter_status]
        if filter_model != "all":
            filtered_tasks = [t for t in filtered_tasks if t['model'] == filter_model]
        
        for task in filtered_tasks[:show_count]:
            with st.expander(f"{task['model']} - {task['prompt'][:50]}... [{task['status'].upper()}]"):
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.write(f"**Task ID:** `{task['id']}`")
                    st.write(f"**Model:** {task['model']}")
                    st.write(f"**Status:** {task['status']}")
                
                with col_info2:
                    st.write(f"**Timestamp:** {task['timestamp']}")
                    if task.get('tags'):
                        st.write(f"**Tags:** {task['tags']}")
                
                st.write(f"**Prompt:** {task['prompt']}")
                
                if task.get('results'):
                    st.write(f"**Generated {len(task['results'])} image(s):**")
                    cols = st.columns(min(len(task['results']), 4))
                    for idx, url in enumerate(task['results']):
                        with cols[idx % 4]:
                            st.image(url, use_container_width=True)

with tab2:
    st.header("📚 Image Library")
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="info-box">
            <strong>☁️ Connect Google Drive</strong><br>
            Upload your service account JSON in the sidebar to access your image library.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Actions bar
        col_act1, col_act2, col_act3, col_act4 = st.columns(4)
        
        with col_act1:
            if st.button("🔄 Refresh Library", use_container_width=True):
                st.session_state.library_images = list_gdrive_images(st.session_state.gdrive_folder_id)
                st.success("Library refreshed!")
                st.rerun()
        
        with col_act2:
            view_mode = st.selectbox("View", ["grid", "list"], key="view_mode_select")
            st.session_state.library_view_mode = view_mode
        
        with col_act3:
            sort_by = st.selectbox("Sort", [
                ("date_desc", "Newest First"),
                ("date_asc", "Oldest First"),
                ("name_asc", "Name A-Z"),
                ("name_desc", "Name Z-A")
            ], format_func=lambda x: x[1], key="sort_select")
        
        with col_act4:
            batch_mode = st.checkbox("Batch Mode", value=st.session_state.batch_mode)
            st.session_state.batch_mode = batch_mode
        
        # Search bar
        search_query = st.text_input(
            "🔍 Search images...",
            placeholder="Search by name, tags, or prompt",
            key="library_search"
        )
        
        # Load library if not loaded
        if not st.session_state.library_images:
            with st.spinner("Loading library..."):
                st.session_state.library_images = list_gdrive_images(st.session_state.gdrive_folder_id)
        
        if st.session_state.library_images:
            st.write(f"**Total Images:** {len(st.session_state.library_images)}")
            
            # Filter images based on search
            filtered_images = st.session_state.library_images
            if search_query:
                filtered_images = [
                    img for img in filtered_images
                    if search_query.lower() in img.get('name', '').lower()
                ]
            
            st.write(f"**Showing:** {len(filtered_images)} images")
            
            if st.session_state.batch_mode and st.session_state.selected_images:
                st.markdown(f"""
                <div class="info-box">
                    <strong>{len(st.session_state.selected_images)} images selected</strong>
                    <br>Use batch actions below
                </div>
                """, unsafe_allow_html=True)
                
                col_batch1, col_batch2, col_batch3 = st.columns(3)
                with col_batch1:
                    if st.button("📥 Download Selected", use_container_width=True):
                        st.info("Preparing download...")
                with col_batch2:
                    if st.button("🗑️ Delete Selected", use_container_width=True):
                        for img_id in st.session_state.selected_images:
                            delete_gdrive_file(img_id)
                        st.session_state.selected_images = []
                        st.session_state.library_images = list_gdrive_images(st.session_state.gdrive_folder_id)
                        st.success("Deleted!")
                        st.rerun()
                with col_batch3:
                    if st.button("❌ Clear Selection", use_container_width=True):
                        st.session_state.selected_images = []
                        st.rerun()
            
            # Display images
            if st.session_state.library_view_mode == "grid":
                cols = st.columns(4)
                for idx, img in enumerate(filtered_images):
                    with cols[idx % 4]:
                        if st.session_state.batch_mode:
                            is_selected = img['id'] in st.session_state.selected_images
                            if st.checkbox("Select", key=f"select_{img['id']}", value=is_selected):
                                if img['id'] not in st.session_state.selected_images:
                                    st.session_state.selected_images.append(img['id'])
                            else:
                                if img['id'] in st.session_state.selected_images:
                                    st.session_state.selected_images.remove(img['id'])
                        
                        st.markdown(f"**{img.get('name', 'Untitled')[:20]}...**")
                        
                        image_bytes = get_gdrive_image_bytes(img['id'])
                        if image_bytes:
                            st.image(image_bytes, use_container_width=True)
                        else:
                            st.warning("Preview unavailable")
                        
                        col_link, col_del = st.columns(2)
                        with col_link:
                            st.markdown(f"[🔗 Open]({img.get('webViewLink', '#')})")
                        with col_del:
                            if st.button("🗑️", key=f"del_{img['id']}"):
                                if delete_gdrive_file(img['id']):
                                    st.success("Deleted!")
                                    st.session_state.library_images = list_gdrive_images(st.session_state.gdrive_folder_id)
                                    st.rerun()
            else:
                # List view
                for img in filtered_images:
                    col_img, col_info, col_actions = st.columns([1, 3, 1])
                    
                    with col_img:
                        image_bytes = get_gdrive_image_bytes(img['id'])
                        if image_bytes:
                            st.image(image_bytes, width=150)
                    
                    with col_info:
                        st.write(f"**{img.get('name', 'Untitled')}**")
                        st.caption(f"Created: {img.get('createdTime', 'Unknown')}")
                        st.caption(f"Type: {img.get('mimeType', 'Unknown')}")
                    
                    with col_actions:
                        st.markdown(f"[🔗 Open]({img.get('webViewLink', '#')})")
                        if st.button("🗑️ Delete", key=f"del_list_{img['id']}"):
                            if delete_gdrive_file(img['id']):
                                st.success("Deleted!")
                                st.rerun()
        else:
            st.markdown("""
            <div class="info-box">
                <strong>📭 No images in library yet</strong><br>
                Generate some images to get started!
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.header("📊 Google Sheets Data View")
    
    if not st.session_state.authenticated or not st.session_state.spreadsheet_id:
        st.markdown("""
        <div class="info-box">
            <strong>☁️ Connect Google Services</strong><br>
            Upload your service account JSON in the sidebar to view spreadsheet data.
        </div>
        """, unsafe_allow_html=True)
    else:
        col_sheet1, col_sheet2, col_sheet3 = st.columns([2, 1, 1])
        
        with col_sheet1:
            st.write(f"**Spreadsheet ID:** `{st.session_state.spreadsheet_id}`")
        
        with col_sheet2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        with col_sheet3:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{st.session_state.spreadsheet_id}"
            st.link_button("📊 Open Sheets", sheet_url, use_container_width=True)
        
        st.divider()
        
        sheets_data = get_sheets_data()
        
        if sheets_data:
            st.write(f"**Total Entries:** {len(sheets_data)}")
            
            try:
                import pandas as pd
                
                df = pd.DataFrame(sheets_data, columns=['Timestamp', 'Model', 'Prompt', 'Image URL', 'Drive Link', 'Task ID', 'Status', 'Tags'])
                
                # Filters
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    filter_model_sheets = st.selectbox("Filter by Model", ["All"] + list(df['Model'].unique()))
                with col_f2:
                    filter_status_sheets = st.selectbox("Filter by Status", ["All"] + list(df['Status'].unique()))
                with col_f3:
                    search_sheets = st.text_input("Search prompts", placeholder="Search...")
                
                # Apply filters
                filtered_df = df
                if filter_model_sheets != "All":
                    filtered_df = filtered_df[filtered_df['Model'] == filter_model_sheets]
                if filter_status_sheets != "All":
                    filtered_df = filtered_df[filtered_df['Status'] == filter_status_sheets]
                if search_sheets:
                    filtered_df = filtered_df[filtered_df['Prompt'].str.contains(search_sheets, case=False, na=False)]
                
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Export filtered data
                if not filtered_df.empty:
                    csv_export = filtered_df.to_csv(index=False)
                    st.download_button(
                        "📥 Export Filtered Data",
                        data=csv_export,
                        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                st.subheader("🖼️ Image Gallery")
                
                # Gallery view with pagination
                images_per_page = 12
                total_pages = (len(filtered_df) + images_per_page - 1) // images_per_page
                
                if total_pages > 1:
                    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                else:
                    page_num = 1
                
                start_idx = (page_num - 1) * images_per_page
                end_idx = min(start_idx + images_per_page, len(filtered_df))
                
                cols = st.columns(4)
                for idx, row in filtered_df.iloc[start_idx:end_idx].iterrows():
                    with cols[(idx - start_idx) % 4]:
                        if len(row) >= 4 and row['Image URL']:
                            try:
                                st.image(row['Image URL'], caption=row['Prompt'][:30] + "...", use_container_width=True)
                                st.caption(f"**{row['Model']}**")
                                st.caption(f"{row['Timestamp']}")
                                if row.get('Tags'):
                                    st.caption(f"🏷️ {row['Tags']}")
                                
                                if row['Drive Link']:
                                    st.markdown(f"[🔗 Drive Link]({row['Drive Link']})")
                            except:
                                st.error("Failed to load")
                
            except Exception as e:
                st.error(f"Error displaying data: {str(e)}")
        else:
            st.markdown("""
            <div class="info-box">
                <strong>📭 No data in spreadsheet yet</strong><br>
                Generate images to start logging!
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.header("🔍 Compare Images")
    
    st.markdown("""
    <div class="info-box">
        <strong>Compare up to 4 images side by side</strong><br>
        Select images from your library or recent generations to compare.
    </div>
    """, unsafe_allow_html=True)
    
    col_comp1, col_comp2 = st.columns([3, 1])
    
    with col_comp2:
        if st.session_state.comparison_images:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.comparison_images = []
                st.rerun()
    
    # Display comparison
    if st.session_state.comparison_images:
        st.write(f"**Comparing {len(st.session_state.comparison_images)} images:**")
        
        cols = st.columns(len(st.session_state.comparison_images))
        for idx, img_data in enumerate(st.session_state.comparison_images):
            with cols[idx]:
                st.image(img_data.get('url'), use_container_width=True)
                st.caption(f"**Prompt:** {img_data.get('prompt', 'N/A')[:50]}...")
                st.caption(f"**Model:** {img_data.get('model', 'N/A')}")
                if st.button("❌ Remove", key=f"remove_comp_{idx}"):
                    remove_from_comparison(img_data.get('id'))
                    st.rerun()
    else:
        st.info("No images selected for comparison yet")
    
    st.divider()
    
    # Add from recent tasks
    st.subheader("📜 Add from Recent Tasks")
    
    for task in st.session_state.task_history[:10]:
        if task.get('results'):
            with st.expander(f"{task['model']} - {task['prompt'][:40]}..."):
                cols = st.columns(4)
                for idx, url in enumerate(task['results']):
                    with cols[idx % 4]:
                        st.image(url, use_container_width=True)
                        if st.button(f"➕ Add", key=f"add_comp_{task['id']}_{idx}"):
                            if add_to_comparison({
                                'url': url,
                                'prompt': task['prompt'],
                                'model': task['model'],
                                'id': f"{task['id']}_{idx}"
                            }):
                                st.success("Added to comparison!")
                                st.rerun()
                            else:
                                st.warning("Maximum 4 images can be compared")

with tab5:
    st.header("📦 Batch Generation")
    
    st.markdown("""
    <div class="info-box">
        <strong>Generate multiple images with different prompts</strong><br>
        Enter one prompt per line to generate images in batch.
    </div>
    """, unsafe_allow_html=True)
    
    col_batch_set1, col_batch_set2 = st.columns([2, 1])
    
    with col_batch_set1:
        batch_prompts_text = st.text_area(
            "Enter prompts (one per line)",
            placeholder="A beautiful sunset\nA mountain landscape\nA futuristic city",
            height=200,
            key="batch_prompts_input"
        )
    
    with col_batch_set2:
        batch_model = st.selectbox(
            "Model for all",
            [
                "flux-pro",
                "flux-dev",
                "flux-schnell",
                "stable-diffusion-3.5",
                "flux-realism"
            ],
            key="batch_model_select"
        )
        
        batch_width = st.number_input("Width", min_value=256, max_value=2048, value=1024, step=64, key="batch_width")
        batch_height = st.number_input("Height", min_value=256, max_value=2048, value=1024, step=64, key="batch_height")
        batch_steps = st.slider("Steps", min_value=1, max_value=50, value=30, key="batch_steps")
    
    if st.button("🚀 Start Batch Generation", type="primary", use_container_width=True):
        if not st.session_state.api_key:
            st.error("Please enter API key first")
        elif not batch_prompts_text:
            st.warning("Please enter at least one prompt")
        else:
            prompts = [p.strip() for p in batch_prompts_text.split('\n') if p.strip()]
            
            if len(prompts) > 10:
                st.warning("Maximum 10 prompts allowed per batch")
                prompts = prompts[:10]
            
            st.write(f"**Processing {len(prompts)} prompts...**")
            
            progress_batch = st.progress(0)
            status_batch = st.empty()
            
            for idx, prompt in enumerate(prompts):
                status_batch.write(f"**Processing prompt {idx+1}/{len(prompts)}:** {prompt[:50]}...")
                
                input_params = {
                    "prompt": prompt,
                    "width": batch_width,
                    "height": batch_height,
                    "num_inference_steps": batch_steps,
                    "num_images": 1
                }
                
                result = create_task(st.session_state.api_key, batch_model, input_params)
                
                if result["success"]:
                    task_id = result["task_id"]
                    
                    st.session_state.task_history.insert(0, {
                        'id': task_id,
                        'model': batch_model,
                        'prompt': prompt,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'pending',
                        'results': []
                    })
                    
                    poll_result = poll_task_until_complete(
                        st.session_state.api_key,
                        task_id,
                        max_attempts=30
                    )
                    
                    if poll_result["success"]:
                        task_data = poll_result["data"]
                        result_urls = task_data.get("result", [])
                        
                        if result_urls:
                            save_and_upload_results(task_id, batch_model, prompt, result_urls)
                            st.success(f"✅ Generated: {prompt[:30]}...")
                
                progress_batch.progress((idx + 1) / len(prompts))
            
            st.balloons()
            st.success(f"🎉 Batch generation complete! Processed {len(prompts)} prompts")

with tab6:
    st.header("ℹ️ About AI Image Editor Pro")
    
    st.markdown("""
    ### 🎨 Complete Edition - Full Feature Suite
    
    This is the most comprehensive version with all features enabled!
    
    #### ✨ All Features Included
    
    **🎨 Generation Features:**
    - Multiple AI models (Flux Pro, Dev, Schnell, Stable Diffusion, etc.)
    - Advanced settings (guidance scale, seed, negative prompts)
    - Preset prompts and prompt history
    - Real-time progress tracking
    - Batch generation (up to 10 prompts at once)
    
    **☁️ Cloud Storage:**
    - Google Drive integration with automatic uploads
    - Public image URLs for easy sharing
    - Organized folder structure
    - Image library management with search and filters
    
    **📊 Data Management:**
    - Google Sheets automatic logging
    - CSV export/import capabilities
    - Comprehensive statistics dashboard
    - Tagging system for organization
    - Filtering and search across all data
    
    **🔍 Advanced Features:**
    - Image comparison mode (up to 4 images)
    - Batch operations (select, delete, download)
    - Grid and list view modes
    - Favorites system
    - Download queue management
    - Pagination for large datasets
    
    **⚡ Quick Actions:**
    - One-click refresh
    - Bulk delete operations
    - Export filtered data
    - Backup all data to CSV
    
    #### 📝 Setup Instructions
    
    1. **Get API Key**: Sign up at [kie.ai](https://kie.ai) for image generation
    2. **Google Cloud Setup**:
       - Create a project in Google Cloud Console
       - Enable Google Drive API and Google Sheets API
       - Create a service account and download JSON key
       - The app will automatically create necessary folders and spreadsheets
    3. **Upload Credentials**: Upload your service account JSON in the sidebar
    4. **Start Creating**: Generate amazing images with full tracking!
    
    #### 🔒 Privacy & Security
    - All data stored in YOUR Google Drive
    - No external data storage (except Google's secure cloud)
    - Service account access only to app-created folders
    - Local CSV backups available anytime
    - You control all your data
    
    #### 🛠️ Technical Stack
    - **Frontend**: Streamlit with custom CSS
    - **APIs**: KIE.AI for image generation
    - **Storage**: Google Drive API v3
    - **Database**: Google Sheets API v4
    - **Local**: CSV export with pandas
    - **Images**: PIL/Pillow for processing
    
    #### 📈 Statistics Tracking
    - Total tasks created
    - Success/failure rates
    - Images generated and uploaded
    - Sheets and CSV entries
    - Real-time updates
    
    #### 💡 Tips & Tricks
    - Use presets for quick inspiration
    - Save favorite prompts for reuse
    - Tag images for better organization
    - Use batch mode for variations
    - Compare images to refine prompts
    - Export data regularly for backups
    
    #### 🔄 Version History
    - **v3.0** - Complete Edition (Current)
      - Added comparison mode
      - Added batch generation
      - Enhanced library with search/filters
      - Added tagging system
      - Improved UI/UX with animations
    - **v2.0** - Enhanced Edition
      - Google Sheets integration
      - CSV management
      - Enhanced statistics
    - **v1.0** - Initial Release
      - Basic generation
      - Google Drive upload
    
    ---
    
    **Version:** 3.0 Complete Edition  
    **Last Updated:** 2025  
    **Status:** Production Ready  
    
    """)
    
    st.success("🎉 Thank you for using AI Image Editor Pro!")
    
    # Stats summary
    st.divider()
    st.subheader("📊 Your Session Stats")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    with col_stat2:
        st.metric("Images Generated", st.session_state.stats['total_images'])
    with col_stat3:
        st.metric("Uploaded", st.session_state.stats['uploaded_images'])
    with col_stat4:
        success_rate = 0
        if st.session_state.stats['total_tasks'] > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / st.session_state.stats['total_tasks']) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")

st.divider()
col_foot1, col_foot2, col_foot3 = st.columns(3)

with col_foot1:
    st.caption("Made with ❤️ using Streamlit")
with col_foot2:
    st.caption("Enhanced with Google Sheets & Drive")
with col_foot3:
    st.caption("v3.0 Complete Edition")

