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

# Import pandas and plotly for analytics
try:
    import pandas as pd
    import plotly.express as px
except ImportError:
    pd = None
    px = None
    st.warning("Pandas and Plotly are missing. Install them for enhanced analytics: `pip install pandas plotly`")


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
    page_title="AI Image Studio Pro - Ultimate Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.kie.ai',
        'Report a bug': 'https://github.com',
        'About': "AI Image Studio Pro - Ultimate Edition with Complete Features"
    }
)

# Enhanced CSS Styling
st.markdown("""
<style>
    /* Modern Theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 0 24px;
        border-radius: 10px;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 28px;
        border-radius: 18px;
        margin: 12px 0;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.25);
    }
    
    /* Status Boxes with Animations */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 12px 0;
        animation: slideIn 0.5s ease;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 12px 0;
        animation: slideIn 0.5s ease;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
        margin: 12px 0;
        animation: slideIn 0.5s ease;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 12px 0;
        animation: slideIn 0.5s ease;
    }
    
    /* Task Card Styling */
    .task-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .task-card:hover {
        border-color: #667eea;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Image Gallery Grid */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    
    .image-item {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .image-item:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    
    /* Progress Indicators */
    .progress-ring {
        animation: rotate 2s linear infinite;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    
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
    
    /* Button Enhancements */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 4px;
    }
    
    .badge-success { background-color: #28a745; color: white; }
    .badge-danger { background-color: #dc3545; color: white; }
    .badge-warning { background-color: #ffc107; color: #212529; }
    .badge-info { background-color: #17a2b8; color: white; }
    .badge-primary { background-color: #667eea; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        # Authentication
        'authenticated': False,
        'service': None,
        'drive_service': None,
        'sheets_service': None,
        'app_folder_id': None,
        'spreadsheet_id': None,
        
        # Image Library & Data
        'gdrive_images': [],
        'gdrive_images_cache': {},  # Cache for image bytes
        'last_library_refresh': None,
        'csv_data': [],
        
        # Task Management
        'task_queue': [],
        'active_tasks': [],
        'task_history': [],
        'completed_tasks': [],
        'failed_tasks': [],
        
        # Statistics
        'stats': {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'total_images': 0,
            'uploaded_images': 0,
            'total_api_calls': 0,
            'models_used': {},
            'tags_used': {},
            'daily_usage': {},
            'hourly_usage': {},
            'cost_tracking': {},
        },
        
        # User Preferences
        'favorites': [],
        'tags': {},
        'collections': {},
        'comparison_list': [],
        'projects': {},
        
        # UI State
        'selected_tab': 'Generate',
        'current_page': 1,
        'items_per_page': 12,
        'search_query': '',
        'filter_tag': 'All',
        'view_mode': 'grid',
        'theme': 'dark',
        
        # Generation Settings
        'last_prompt': '',
        'last_model': 'flux-1.1-pro',
        'generation_presets': {},
        'auto_upload_enabled': True,
        'prompt_templates': {},
        'style_presets': {},
        
        # Advanced Features
        'batch_mode': False,
        'batch_prompts': [],
        'comparison_mode': False,
        'analytics_period': 7,
        'workflows': {},
        'scheduled_tasks': [],
        'api_usage_limit': 1000,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# GOOGLE SERVICES AUTHENTICATION
# ============================================================================

def authenticate_with_service_account(service_account_json):
    """Authenticate with Google services using service account"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(service_account_json),
            scopes=[
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
        )
        
        drive_service = build('drive', 'v3', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        st.session_state.authenticated = True
        st.session_state.drive_service = drive_service
        st.session_state.sheets_service = sheets_service
        
        return True, "Successfully authenticated with Google services!"
    except Exception as e:
        return False, f"Authentication failed: {str(e)}"

# ============================================================================
# GOOGLE DRIVE FUNCTIONS
# ============================================================================

def create_app_folder():
    """Create or get the AI Image Editor folder in Google Drive"""
    try:
        # Search for existing folder
        query = "name='AI_Image_Editor_Pro' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = st.session_state.drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            st.session_state.app_folder_id = folders[0]['id']
            return folders[0]['id']
        
        # Create new folder
        file_metadata = {
            'name': 'AI_Image_Editor_Pro',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = st.session_state.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        st.session_state.app_folder_id = folder.get('id')
        return folder.get('id')
        
    except Exception as e:
        st.error(f"Failed to create folder: {str(e)}")
        return None

def upload_to_gdrive(image_url: str, file_name: str, task_id: str = None):
    """Upload image to Google Drive from URL"""
    try:
        if not st.session_state.get('authenticated'):
            return None, "Not authenticated with Google Drive"
        
        # Download image from URL
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return None, f"Failed to download image: HTTP {response.status_code}"
        
        image_bytes = io.BytesIO(response.content)
        
        # Ensure app folder exists
        if not st.session_state.get('app_folder_id'):
            create_app_folder()
        
        # Prepare metadata
        file_metadata = {
            'name': file_name,
            'parents': [st.session_state.app_folder_id],
            'description': f"Generated by AI Image Studio Pro | Task ID: {task_id or 'N/A'}"
        }
        
        # Determine mime type
        mime_type = 'image/png'
        if file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif file_name.lower().endswith('.webp'):
            mime_type = 'image/webp'
        
        media = MediaIoBaseUpload(image_bytes, mimetype=mime_type, resumable=True)
        
        # Upload file
        file = st.session_state.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, size, createdTime'
        ).execute()
        
        # Update statistics
        st.session_state.stats['uploaded_images'] += 1
        st.session_state.stats['total_images'] += 1
        
        return file, None
        
    except Exception as e:
        return None, f"Upload failed: {str(e)}"

def list_gdrive_images(folder_id=None, force_refresh=False):
    """List all images in the Google Drive folder with caching"""
    try:
        if not st.session_state.get('authenticated'):
            return []
        
        # Check cache timing
        last_refresh = st.session_state.get('last_library_refresh')
        if not force_refresh and last_refresh:
            time_diff = (datetime.now() - last_refresh).total_seconds()
            if time_diff < 30:  # Cache for 30 seconds
                return st.session_state.gdrive_images
        
        folder_id = folder_id or st.session_state.get('app_folder_id')
        if not folder_id:
            return []
        
        # Query for image files
        query = f"'{folder_id}' in parents and trashed=false and (mimeType contains 'image/')"
        
        results = st.session_state.drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, webViewLink, size, createdTime, description, thumbnailLink)',
            orderBy='createdTime desc',
            pageSize=1000
        ).execute()
        
        images = results.get('files', [])
        
        # Update session state
        st.session_state.gdrive_images = images
        st.session_state.last_library_refresh = datetime.now()
        
        return images
        
    except Exception as e:
        st.error(f"Failed to list images: {str(e)}")
        return []

def get_gdrive_image_bytes(file_id):
    """Get image bytes from Google Drive with caching"""
    try:
        # Check cache first
        if file_id in st.session_state.gdrive_images_cache:
            return st.session_state.gdrive_images_cache[file_id]
        
        # Download from Drive
        request = st.session_state.drive_service.files().get_media(fileId=file_id)
        image_bytes = io.BytesIO()
        downloader = MediaIoBaseDownload(image_bytes, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        image_bytes.seek(0)
        image_data = image_bytes.read()
        
        # Cache the result
        st.session_state.gdrive_images_cache[file_id] = image_data
        
        return image_data
        
    except Exception as e:
        st.error(f"Failed to get image: {str(e)}")
        return None

def delete_gdrive_file(file_id):
    """Delete a file from Google Drive"""
    try:
        st.session_state.drive_service.files().delete(fileId=file_id).execute()
        
        # Clear from cache
        if file_id in st.session_state.gdrive_images_cache:
            del st.session_state.gdrive_images_cache[file_id]
        
        # Remove from session state list and refresh
        st.session_state.gdrive_images = [img for img in st.session_state.gdrive_images if img['id'] != file_id]
        
        return True, "File deleted successfully"
    except Exception as e:
        return False, f"Delete failed: {str(e)}"

# ============================================================================
# GOOGLE SHEETS FUNCTIONS
# ============================================================================

def create_or_get_spreadsheet():
    """Create or get the tracking spreadsheet"""
    try:
        # Search for existing spreadsheet
        query = "name='AI_Image_Editor_Pro_Log' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        results = st.session_state.drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        sheets = results.get('files', [])
        
        if sheets:
            st.session_state.spreadsheet_id = sheets[0]['id']
            return sheets[0]['id']
        
        # Create new spreadsheet
        spreadsheet = {
            'properties': {'title': 'AI_Image_Editor_Pro_Log'},
            'sheets': [{
                'properties': {'title': 'Generation_Log'},
                'data': [{
                    'rowData': [{
                        'values': [
                            {'userEnteredValue': {'stringValue': 'Timestamp'}},
                            {'userEnteredValue': {'stringValue': 'Model'}},
                            {'userEnteredValue': {'stringValue': 'Prompt'}},
                            {'userEnteredValue': {'stringValue': 'Image URL'}},
                            {'userEnteredValue': {'stringValue': 'Drive Link'}},
                            {'userEnteredValue': {'stringValue': 'Task ID'}},
                            {'userEnteredValue': {'stringValue': 'Status'}},
                            {'userEnteredValue': {'stringValue': 'Tags'}},
                            {'userEnteredValue': {'stringValue': 'File ID'}},
                        ]
                    }]
                }]
            }]
        }
        
        sheet = st.session_state.sheets_service.spreadsheets().create(
            body=spreadsheet
        ).execute()
        
        spreadsheet_id = sheet.get('spreadsheetId')
        
        # Move to app folder
        if st.session_state.get('app_folder_id'):
            st.session_state.drive_service.files().update(
                fileId=spreadsheet_id,
                addParents=st.session_state.app_folder_id,
                fields='id, parents'
            ).execute()
        
        st.session_state.spreadsheet_id = spreadsheet_id
        return spreadsheet_id
        
    except Exception as e:
        st.error(f"Failed to create spreadsheet: {str(e)}")
        return None

def log_to_sheets(model: str, prompt: str, image_url: str, drive_link: str = "", 
                  task_id: str = "", status: str = "success", tags: str = "", file_id: str = ""):
    """Log generation data to Google Sheets"""
    try:
        if not st.session_state.get('spreadsheet_id'):
            create_or_get_spreadsheet()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        values = [[timestamp, model, prompt, image_url, drive_link, task_id, status, tags, file_id]]
        
        body = {'values': values}
        
        st.session_state.sheets_service.spreadsheets().values().append(
            spreadsheetId=st.session_state.spreadsheet_id,
            range='Generation_Log!A:I',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Failed to log to sheets: {str(e)}")
        return False

def get_sheets_data():
    """Get all data from Google Sheets"""
    try:
        if not st.session_state.get('spreadsheet_id'):
            return []
        
        result = st.session_state.sheets_service.spreadsheets().values().get(
            spreadsheetId=st.session_state.spreadsheet_id,
            range='Generation_Log!A:I'
        ).execute()
        
        values = result.get('values', [])
        return values[1:] if len(values) > 1 else []  # Skip header
        
    except Exception as e:
        st.error(f"Failed to get sheets data: {str(e)}")
        return []

# ============================================================================
# CSV DATA FUNCTIONS
# ============================================================================

def add_to_csv_data(model: str, prompt: str, image_url: str, drive_link: str = "", 
                    task_id: str = "", status: str = "success", tags: str = "", file_id: str = ""):
    """Add entry to CSV data in session state"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = {
        'timestamp': timestamp,
        'model': model,
        'prompt': prompt,
        'image_url': image_url,
        'drive_link': drive_link,
        'task_id': task_id,
        'status': status,
        'tags': tags,
        'file_id': file_id
    }
    
    st.session_state.csv_data.append(entry)

def export_to_csv():
    """Export CSV data to downloadable file"""
    if not st.session_state.csv_data:
        return None
    
    output = io.StringIO()
    fieldnames = ['timestamp', 'model', 'prompt', 'image_url', 'drive_link', 'task_id', 'status', 'tags', 'file_id']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(st.session_state.csv_data)
    
    return output.getvalue()

def load_csv_file(uploaded_file):
    """Load CSV file into session state"""
    try:
        content = uploaded_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        loaded_data = list(reader)
        st.session_state.csv_data.extend(loaded_data)
        
        return True, len(loaded_data)
    except Exception as e:
        return False, str(e)

# ============================================================================
# KIE.AI API FUNCTIONS
# ============================================================================

def create_task(api_key, model, input_params, callback_url=None):
    """Create a new task using KIE.ai API"""
    url = "https://api.kie.ai/v1/tasks"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": input_params
    }
    
    if callback_url:
        payload["callback_url"] = callback_url
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            task_data = response.json()
            
            # Update stats
            st.session_state.stats['total_tasks'] += 1
            st.session_state.stats['total_api_calls'] += 1
            
            model_name = model.split('/')[-1]
            st.session_state.stats['models_used'][model_name] = st.session_state.stats['models_used'].get(model_name, 0) + 1
            
            # Track daily usage
            today = datetime.now().strftime("%Y-%m-%d")
            st.session_state.stats['daily_usage'][today] = st.session_state.stats['daily_usage'].get(today, 0) + 1
            
            # Track hourly usage
            now = datetime.now()
            st.session_state.stats['hourly_usage'][now.strftime("%Y-%m-%d %H")] = st.session_state.stats['hourly_usage'].get(now.strftime("%Y-%m-%d %H"), 0) + 1

            # Basic cost tracking (assuming fixed cost per task for now)
            # More sophisticated tracking would depend on model/parameters
            cost_per_task = 0.04 # Example cost, replace with actual model pricing if available
            st.session_state.stats['cost_tracking'][model_name] = st.session_state.stats['cost_tracking'].get(model_name, 0) + cost_per_task
            
            return task_data, None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"

def check_task_status(api_key, task_id):
    """Check the status of a task"""
    url = f"https://api.kie.ai/v1/tasks/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Status check failed: {response.status_code}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"

def poll_task_until_complete(api_key, task_id, max_attempts=60, delay=2):
    """Poll task status until completion"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        status_text.text(f"⏳ Checking task status... (Attempt {attempt + 1}/{max_attempts})")
        
        task_status, error = check_task_status(api_key, task_id)
        
        if error:
            progress_bar.empty()
            status_text.empty()
            return None, error
        
        status = task_status.get('status')
        
        if status == 'succeeded':
            progress_bar.progress(100)
            status_text.text("✅ Task completed successfully!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Update stats
            st.session_state.stats['successful_tasks'] += 1
            
            return task_status, None
            
        elif status == 'failed':
            progress_bar.empty()
            status_text.empty()
            
            # Update stats
            st.session_state.stats['failed_tasks'] += 1
            
            error_msg = task_status.get('error', 'Unknown error')
            return None, f"Task failed: {error_msg}"
        
        # Update progress
        progress = int((attempt + 1) / max_attempts * 100)
        progress_bar.progress(min(progress, 95))
        
        time.sleep(delay)
    
    progress_bar.empty()
    status_text.empty()
    
    # Timeout - mark as failed
    st.session_state.stats['failed_tasks'] += 1
    
    return None, "Task timed out"

def save_and_upload_results(task_id, model, prompt, result_urls, tags=""):
    """Save results and automatically upload to Drive"""
    uploaded_files = []
    
    for idx, image_url in enumerate(result_urls):
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{model.replace('/', '_')}_{timestamp}_{idx+1}.png"
            
            # Upload to Drive if authenticated
            drive_link = ""
            file_id = ""
            
            if st.session_state.get('authenticated') and st.session_state.get('auto_upload_enabled', True):
                file_info, error = upload_to_gdrive(image_url, file_name, task_id)
                
                if file_info:
                    drive_link = file_info.get('webViewLink', '')
                    file_id = file_info.get('id', '')
                    uploaded_files.append(file_info)
                    
                    # Update stats (already incremented in upload_to_gdrive)
                    
                    # Log to Sheets
                    log_to_sheets(model, prompt, image_url, drive_link, task_id, "success", tags, file_id)
            
            # Always add to CSV
            add_to_csv_data(model, prompt, image_url, drive_link, task_id, "success", tags, file_id)
            
        except Exception as e:
            st.error(f"Failed to process image {idx+1}: {str(e)}")
    
    # Force refresh library to show new images
    if uploaded_files:
        list_gdrive_images(force_refresh=True)
    
    return uploaded_files

# ============================================================================
# TAG AND COLLECTION MANAGEMENT
# ============================================================================

def add_tag_to_image(image_id, tag):
    """Add a tag to an image"""
    if image_id not in st.session_state.tags:
        st.session_state.tags[image_id] = []
    
    if tag not in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].append(tag)
        st.session_state.stats['tags_used'][tag] = st.session_state.stats['tags_used'].get(tag, 0) + 1

def remove_tag_from_image(image_id, tag):
    """Remove a tag from an image"""
    if image_id in st.session_state.tags and tag in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].remove(tag)

def get_image_tags(image_id):
    """Get all tags for an image"""
    return st.session_state.tags.get(image_id, [])

def add_to_comparison(image_data):
    """Add image to comparison list"""
    if len(st.session_state.comparison_list) < 4:
        if image_data not in st.session_state.comparison_list:
            st.session_state.comparison_list.append(image_data)
            return True
    return False

def remove_from_comparison(image_id):
    """Remove image from comparison list"""
    st.session_state.comparison_list = [
        img for img in st.session_state.comparison_list 
        if img.get('id') != image_id
    ]

# ============================================================================
# PAGE: TEXT-TO-IMAGE GENERATION
# ============================================================================

def display_generate_page():
    """Display the text-to-image generation page"""
    st.title("🎨 AI Image Generation")
    st.markdown("Create stunning images using advanced AI models")
    
    # API Key Input
    # Use st.secrets for API keys if available, otherwise use text_input
    api_key = st.text_input(
        "🔑 KIE.ai API Key",
        type="password",
        value=st.secrets.get("KIE_API_KEY", ""),
        help="Enter your KIE.ai API key from https://kie.ai"
    )
    
    if not api_key:
        st.info("👆 Please enter your KIE.ai API key to start generating images")
        st.markdown("""
        ### Quick Start Guide:
        1. Get your API key from [KIE.ai](https://kie.ai)
        2. Enter it above
        3. Choose a model and write your prompt
        4. Click Generate!
        
        All generated images will automatically upload to Google Drive when authenticated.
        """)
        return
    
    st.divider()
    
    # Model Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_options = {
            "FLUX 1.1 Pro (Fastest, Best Quality)": "black-forest-labs/flux-1.1-pro",
            "FLUX Pro (High Quality)": "black-forest-labs/flux-pro",
            "FLUX Dev (Balanced)": "black-forest-labs/flux-dev",
            "FLUX Schnell (Speed)": "black-forest-labs/flux-schnell",
            "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
            "Stable Diffusion 3.5 Large Turbo": "stabilityai/stable-diffusion-3.5-large-turbo",
            "Stable Diffusion 3.5 Medium": "stabilityai/stable-diffusion-3.5-medium",
            "Playground v3": "playground/playground-v3",
            "Recraft V3": "recraft-ai/recraft-v3",
        }
        
        selected_model_name = st.selectbox(
            "🤖 Select AI Model",
            options=list(model_options.keys()),
            help="Different models offer different styles and speeds"
        )
        
        selected_model = model_options[selected_model_name]
        st.session_state.last_model = selected_model
    
    with col2:
        st.metric("Model Type", "Text-to-Image")
        st.caption(f"Using: {selected_model.split('/')[-1]}")
    
    # Prompt Input
    st.markdown("### ✍️ Describe Your Image")
    
    # Prompt presets
    preset_prompts = {
        "Custom": "",
        "Photorealistic Portrait": "A photorealistic portrait of a person, professional lighting, 8k resolution, highly detailed",
        "Fantasy Landscape": "A breathtaking fantasy landscape with mountains, magical forests, and ethereal lighting, concept art style",
        "Cyberpunk City": "A futuristic cyberpunk city at night, neon lights, rain-soaked streets, dramatic atmosphere",
        "Abstract Art": "Abstract geometric art with vibrant colors, modern minimalist style, high contrast",
        "Product Photography": "Professional product photography, white background, studio lighting, commercial quality",
    }
    
    col_preset1, col_preset2 = st.columns([1, 3])
    
    with col_preset1:
        selected_preset = st.selectbox("Quick Preset", list(preset_prompts.keys()))
    
    with col_preset2:
        if selected_preset != "Custom" and preset_prompts[selected_preset]:
            prompt = st.text_area(
                "Image Prompt",
                value=preset_prompts[selected_preset],
                height=120,
                help="Describe what you want to see in the image"
            )
        else:
            prompt = st.text_area(
                "Image Prompt",
                value=st.session_state.get('last_prompt', ''),
                height=120,
                placeholder="Example: A serene mountain landscape at sunset with vibrant colors...",
                help="Be specific and descriptive for best results"
            )
    
    st.session_state.last_prompt = prompt
    
    # Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["1:1", "16:9", "9:16", "4:3", "3:4"],
                help="Image dimensions"
            )
            
            # Map aspect ratios to image sizes
            aspect_to_size = {
                "1:1": "square_hd",
                "16:9": "landscape_16_9",
                "9:16": "portrait_9_16",
                "4:3": "landscape_4_3",
                "3:4": "portrait_3_4",
            }
            image_size = aspect_to_size.get(aspect_ratio, "square_hd")
        
        with col_adv2:
            num_images = st.slider("Number of Images", 1, 4, 1)
        
        with col_adv3:
            seed = st.number_input("Seed (0 for random)", 0, 999999, 0)
        
        # Tags
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="landscape, sunset, mountains",
            help="Add tags to organize your images"
        )
    
    # Auto-upload toggle
    auto_upload = st.checkbox(
        "🔄 Auto-upload to Google Drive",
        value=st.session_state.get('auto_upload_enabled', True),
        help="Automatically upload generated images to your Google Drive"
    )
    st.session_state.auto_upload_enabled = auto_upload
    
    # Generate Button
    st.divider()
    
    col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
    
    with col_gen1:
        generate_btn = st.button("🚀 Generate Image", type="primary", use_container_width=True)
    
    with col_gen2:
        if st.button("💾 Save Prompt", use_container_width=True):
            if prompt:
                if 'saved_prompts' not in st.session_state:
                    st.session_state.saved_prompts = []
                st.session_state.saved_prompts.append({
                    'prompt': prompt,
                    'model': selected_model,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Prompt saved!")
    
    with col_gen3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.last_prompt = ""
            st.rerun()
    
    # Generation Logic
    if generate_btn:
        if not prompt.strip():
            st.error("❌ Please enter a prompt to generate an image")
            return
        
        with st.spinner("🎨 Creating your masterpiece..."):
            # Prepare input parameters
            input_params = {
                "prompt": prompt,
                "image_size": image_size,
                "num_outputs": num_images,
            }
            
            if seed > 0:
                input_params["seed"] = seed
            
            # Create task
            task_data, error = create_task(api_key, selected_model, input_params)
            
            if error:
                st.error(f"❌ Generation failed: {error}")
                return
            
            task_id = task_data.get('id')
            
            st.success(f"✅ Task created! ID: `{task_id}`")
            
            # Add to active tasks and history
            task_info = {
                'id': task_id,
                'model': selected_model,
                'prompt': prompt,
                'status': 'processing',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'tags': tags_input
            }
            st.session_state.active_tasks.append(task_info)
            st.session_state.task_history.append(task_info)
            
            # Poll for completion
            result, error = poll_task_until_complete(api_key, task_id)
            
            if error:
                st.error(f"❌ {error}")
                task_info['status'] = 'failed'
                # Update history with failed status
                for t in st.session_state.task_history:
                    if t['id'] == task_id:
                        t['status'] = 'failed'
                        break
                st.session_state.failed_tasks.append(task_info) # Add to failed list
                # Remove from active tasks
                st.session_state.active_tasks = [t for t in st.session_state.active_tasks if t['id'] != task_id]
                return
            
            # Get result URLs
            output = result.get('output', {})
            result_urls = output.get('images', [])
            
            if not result_urls:
                st.error("❌ No images generated")
                task_info['status'] = 'failed' # Mark as failed if no images
                # Update history with failed status
                for t in st.session_state.task_history:
                    if t['id'] == task_id:
                        t['status'] = 'failed'
                        break
                st.session_state.failed_tasks.append(task_info)
                st.session_state.active_tasks = [t for t in st.session_state.active_tasks if t['id'] != task_id]
                return
            
            # Update task status and lists
            task_info['status'] = 'completed'
            task_info['result_urls'] = result_urls
            for t in st.session_state.task_history:
                if t['id'] == task_id:
                    t.update(task_info) # Update in history
                    break
            st.session_state.completed_tasks.append(task_info)
            
            # Remove from active tasks
            st.session_state.active_tasks = [
                t for t in st.session_state.active_tasks if t['id'] != task_id
            ]
            
            st.success(f"🎉 Generated {len(result_urls)} image(s)!")
            
            # Save and upload results
            uploaded_files = save_and_upload_results(
                task_id, selected_model, prompt, result_urls, tags_input
            )
            
            # Display results
            st.markdown("### 🖼️ Generated Images")
            
            cols = st.columns(min(len(result_urls), 3))
            
            for idx, image_url in enumerate(result_urls):
                with cols[idx % 3]:
                    st.image(image_url, caption=f"Image {idx + 1}", use_container_width=True)
                    
                    # Download button
                    try:
                        img_response = requests.get(image_url, timeout=30)
                        if img_response.status_code == 200:
                            st.download_button(
                                label="💾 Download",
                                data=img_response.content,
                                file_name=f"generated_{idx+1}.png",
                                mime="image/png",
                                key=f"download_{task_id}_{idx}"
                            )
                    except Exception as e:
                        st.error(f"Download failed: {e}")
            
            # Show upload status
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} image(s) uploaded to Google Drive!")
                
                with st.expander("📁 View Drive Links"):
                    for file_info in uploaded_files:
                        st.markdown(f"- [{file_info['name']}]({file_info['webViewLink']})")

# ============================================================================
# PAGE: IMAGE EDITING (SEEDREAM)
# ============================================================================

def display_edit_page():
    """Display the image editing page (Seedream)"""
    st.title("✏️ AI Image Editing")
    st.markdown("Edit and transform existing images using AI")
    
    # API Key
    api_key = st.text_input(
        "🔑 KIE.ai API Key",
        type="password",
        key="edit_api_key",
        value=st.secrets.get("KIE_API_KEY", ""),
    )
    
    if not api_key:
        st.info("👆 Please enter your KIE.ai API key to start editing images")
        return
    
    st.divider()
    
    # Model Selection for Editing
    edit_model_options = {
        "Seedream v4 (Edit)": "bytedance/seedream-v4-edit",
        "Qwen VL-Plus": "qwen/qwen-vl-plus",
    }
    
    selected_edit_model_name = st.selectbox(
        "🤖 Select Editing Model",
        options=list(edit_model_options.keys())
    )
    
    selected_edit_model = edit_model_options[selected_edit_model_name]
    
    # Image Source Selection
    st.markdown("### 📸 Select Source Image")
    
    image_source = st.radio(
        "Choose image source:",
        ["Upload from Computer", "Select from Google Drive Library"],
        horizontal=True
    )
    
    source_image_url = None
    original_image_pil = None # Store PIL image for display
    
    if image_source == "Upload from Computer":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload the image you want to edit"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = PILImage.open(uploaded_file)
            original_image_pil = image # Store for later display
            st.image(image, caption="Uploaded Image", width=300)
            
            # For editing, we need to upload to a temporary location or use base64
            # For simplicity, we'll convert to base64 data URL
            buffered = io.BytesIO()
            image.save(buffered, format="PNG") # Save as PNG for consistent format
            img_str = base64.b64encode(buffered.getvalue()).decode()
            source_image_url = f"data:image/png;base64,{img_str}"
    
    else:  # Select from Drive
        if not st.session_state.get('authenticated'):
            st.warning("⚠️ Please authenticate with Google Drive in the Settings tab first")
        else:
            # Load library images
            images = list_gdrive_images()
            
            if not images:
                st.info("No images in library. Generate some first!")
            else:
                # Create selection dropdown
                library_options = {f"{img['name']} ({img['createdTime'][:10]})": img for img in images}
                
                selected_image_name = st.selectbox(
                    "Choose an image from your library:",
                    options=list(library_options.keys())
                )
                
                if selected_image_name:
                    selected_image_info = library_options[selected_image_name]
                    
                    # Display selected image
                    if display_gdrive_image(selected_image_info, caption="Selected Image", width=300):
                        # Get direct link for API
                        file_id = selected_image_info['id']
                        source_image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                        # Store PIL image for later display
                        image_bytes = get_gdrive_image_bytes(file_id)
                        if image_bytes:
                            original_image_pil = PILImage.open(io.BytesIO(image_bytes))
    
    # Editing Prompt
    st.markdown("### ✏️ Describe Your Edit")
    
    edit_prompt = st.text_area(
        "Edit Instructions",
        placeholder="Example: Change background into a beach scene, make the sky purple, add sunglasses...",
        height=100,
        help="Describe what changes you want to make to the image"
    )
    
    # Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            edit_strength = st.slider(
                "Edit Strength",
                0.1, 1.0, 0.7,
                help="How much to change the image (higher = more changes)"
            )
        
        with col_e2:
            edit_resolution = st.selectbox(
                "Output Resolution",
                ["1K", "2K", "4K"],
                index=0
            )
        
        edit_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="edited, portrait, background-change",
            key="edit_tags"
        )
    
    # Edit Button
    st.divider()
    
    edit_btn = st.button("✨ Apply Edits", type="primary", use_container_width=True)
    
    if edit_btn:
        if not source_image_url:
            st.error("❌ Please select or upload a source image")
            return
        
        if not edit_prompt.strip():
            st.error("❌ Please describe the edits you want to make")
            return
        
        with st.spinner("✨ Applying edits to your image..."):
            # Prepare input for Seedream
            input_params = {
                "prompt": edit_prompt,
                "image_urls": [source_image_url],
                "image_size": "square_hd", # Seedream might have fixed sizes, adjust if needed
                "image_resolution": edit_resolution,
                "max_images": 1,
                "strength": edit_strength # Pass strength if model supports it
            }
            
            # Create task
            task_data, error = create_task(api_key, selected_edit_model, input_params)
            
            if error:
                st.error(f"❌ Editing failed: {error}")
                return
            
            task_id = task_data.get('id')
            st.success(f"✅ Edit task created! ID: `{task_id}`")
            
            # Poll for completion
            result, error = poll_task_until_complete(api_key, task_id, max_attempts=90, delay=3)
            
            if error:
                st.error(f"❌ {error}")
                return
            
            # Get result URLs
            output = result.get('output', {})
            result_urls = output.get('images', [])
            
            if not result_urls:
                st.error("❌ No edited images generated")
                return
            
            st.success("🎉 Image edited successfully!")
            
            # Save and upload results
            uploaded_files = save_and_upload_results(
                task_id, selected_edit_model, edit_prompt, result_urls, edit_tags
            )
            
            # Display results
            st.markdown("### 🖼️ Edited Image")
            
            col_before, col_after = st.columns(2)
            
            with col_before:
                st.markdown("**Before**")
                if original_image_pil:
                    st.image(original_image_pil, use_container_width=True)
            
            with col_after:
                st.markdown("**After**")
                st.image(result_urls[0], use_container_width=True)
                
                # Download button
                try:
                    img_response = requests.get(result_urls[0], timeout=30)
                    if img_response.status_code == 200:
                        st.download_button(
                            label="💾 Download Edited Image",
                            data=img_response.content,
                            file_name="edited_image.png",
                            mime="image/png"
                        )
                except Exception as e:
                    st.error(f"Download failed: {e}")
            
            if uploaded_files:
                st.success(f"✅ Edited image uploaded to Google Drive!")

# ============================================================================
# PAGE: LIBRARY
# ============================================================================

def display_library_page():
    """Display the image library from Google Drive"""
    st.title("📚 Image Library")
    st.markdown("Browse and manage your generated images")
    
    if not st.session_state.get('authenticated'):
        st.warning("⚠️ Please authenticate with Google Drive in the Settings tab to view your library")
        return
    
    # Toolbar
    col_tool1, col_tool2, col_tool3, col_tool4 = st.columns([1, 1, 1, 1])
    
    with col_tool1:
        if st.button("🔄 Refresh Library", use_container_width=True):
            list_gdrive_images(force_refresh=True)
            st.rerun()
    
    with col_tool2:
        view_mode = st.selectbox("View", ["Grid", "List"], key="lib_view_mode")
        st.session_state.view_mode = view_mode.lower()
    
    with col_tool3:
        sort_by = st.selectbox("Sort By", ["Newest", "Oldest", "Name"])
    
    with col_tool4:
        items_per_page = st.selectbox("Per Page", [12, 24, 48, 96])
        st.session_state.items_per_page = items_per_page
    
    # Search and Filter
    col_search1, col_search2 = st.columns([3, 1])
    
    with col_search1:
        search_query = st.text_input(
            "🔍 Search images",
            placeholder="Search by name, tags, or prompt...",
            key="lib_search"
        )
        st.session_state.search_query = search_query
    
    with col_search2:
        # Get all unique tags
        all_tags = set()
        for tags_list in st.session_state.tags.values():
            all_tags.update(tags_list)
        
        tag_options = ["All"] + sorted(list(all_tags))
        filter_tag = st.selectbox("Filter by Tag", tag_options)
        st.session_state.filter_tag = filter_tag
    
    st.divider()
    
    # Load images
    images = list_gdrive_images()
    
    if not images:
        st.info("📭 Your library is empty. Start generating images in the Generate tab!")
        return
    
    # Filter images
    filtered_images = images
    
    if search_query:
        # Search in name and description (if available)
        filtered_images = [
            img for img in filtered_images
            if search_query.lower() in img.get('name', '').lower() or \
               search_query.lower() in img.get('description', '').lower()
        ]
    
    if filter_tag != "All":
        filtered_images = [
            img for img in filtered_images
            if filter_tag in get_image_tags(img.get('id')) # Use .get for safety
        ]
    
    # Sort images
    if sort_by == "Oldest":
        filtered_images = sorted(filtered_images, key=lambda x: x.get('createdTime', ''))
    elif sort_by == "Name":
        filtered_images = sorted(filtered_images, key=lambda x: x.get('name', ''))
    # Newest is already the default order
    
    # Pagination
    total_images = len(filtered_images)
    items_per_page = st.session_state.items_per_page # Use value from session state
    total_pages = (total_images + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
        
        with col_page1:
            if st.button("◀️ Previous", disabled=st.session_state.current_page <= 1):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col_page2:
            st.markdown(f"<div style='text-align: center'>Page {st.session_state.current_page} of {total_pages} ({total_images} images)</div>", unsafe_allow_html=True)
        
        with col_page3:
            if st.button("Next ▶️", disabled=st.session_state.current_page >= total_pages):
                st.session_state.current_page += 1
                st.rerun()
    else:
        st.caption(f"Showing {total_images} image(s)")
    
    # Paginate images
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_images = filtered_images[start_idx:end_idx]
    
    # Display images
    if st.session_state.view_mode == "grid":
        # Grid view
        cols_per_row = 4
        rows = (len(page_images) + cols_per_row - 1) // cols_per_row
        
        for row_idx in range(rows):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                img_idx = row_idx * cols_per_row + col_idx
                
                if img_idx < len(page_images):
                    img = page_images[img_idx]
                    
                    with cols[col_idx]:
                        # Display image
                        if display_gdrive_image(img, width=250):
                            st.caption(f"**{img['name'][:30]}...**" if len(img['name']) > 30 else img.get('name', 'Untitled'))
                            st.caption(f"📅 {img.get('createdTime', 'N/A')[:10]}")
                            
                            # Action buttons
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            
                            with col_btn1:
                                if st.button("🔗", key=f"link_{img['id']}", help="Open in Drive"):
                                    st.markdown(f"[View in Drive]({img.get('webViewLink', '#')})")
                            
                            with col_btn2:
                                is_fav = img['id'] in st.session_state.favorites
                                if st.button("❤️" if is_fav else "🤍", key=f"fav_{img['id']}", help="Favorite"):
                                    if is_fav:
                                        st.session_state.favorites.remove(img['id'])
                                    else:
                                        st.session_state.favorites.append(img['id'])
                                    st.rerun()
                            
                            with col_btn3:
                                if st.button("🗑️", key=f"del_{img['id']}", help="Delete"):
                                    success, msg = delete_gdrive_file(img['id'])
                                    if success:
                                        # No need to force_refresh if delete_gdrive_file already updates session state
                                        # list_gdrive_images(force_refresh=True) 
                                        st.success("Image deleted.")
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            
                            # Tags
                            img_tags = get_image_tags(img.get('id'))
                            if img_tags:
                                st.markdown(" ".join([f"`{tag}`" for tag in img_tags]))
    
    else:
        # List view
        for img in page_images:
            with st.container():
                col_img, col_info = st.columns([1, 3])
                
                with col_img:
                    display_gdrive_image(img, width=150)
                
                with col_info:
                    st.markdown(f"### {img.get('name', 'Untitled')}")
                    st.caption(f"📅 Created: {img.get('createdTime', 'N/A')}")
                    st.caption(f"📦 Size: {int(img.get('size', 0)) / 1024:.1f} KB")
                    
                    # Tags
                    img_tags = get_image_tags(img.get('id'))
                    if img_tags:
                        st.markdown("🏷️ Tags: " + " ".join([f"`{tag}`" for tag in img_tags]))
                    
                    # Actions
                    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
                    
                    with col_act1:
                        st.link_button("🔗 View in Drive", img.get('webViewLink', '#'))
                    
                    with col_act2:
                        is_fav = img['id'] in st.session_state.favorites
                        if st.button("❤️ Unfavorite" if is_fav else "🤍 Favorite", key=f"fav_list_{img['id']}"):
                            if is_fav:
                                st.session_state.favorites.remove(img['id'])
                            else:
                                st.session_state.favorites.append(img['id'])
                            st.rerun()
                    
                    with col_act3:
                        if st.button("➕ Compare", key=f"cmp_list_{img['id']}"):
                            if add_to_comparison(img):
                                st.success("Added to comparison!")
                            else:
                                st.warning("Comparison list is full (max 4 images).")
                    
                    with col_act4:
                        if st.button("🗑️ Delete", key=f"del_list_{img['id']}"):
                            success, msg = delete_gdrive_file(img['id'])
                            if success:
                                st.success("Image deleted.")
                                st.rerun()
                            else:
                                st.error(msg)
                
                st.divider()

# ============================================================================
# PAGE: TASK MANAGEMENT
# ============================================================================

def display_task_management_page():
    """Display comprehensive task management page"""
    st.title("📋 Task Management Center")
    st.markdown("Monitor and manage all your AI generation tasks")
    
    # Summary Stats
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
    
    with col_stat1:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    
    with col_stat2:
        st.metric("Successful", st.session_state.stats['successful_tasks'], 
                  delta=None, delta_color="off")
    
    with col_stat3:
        st.metric("Failed", st.session_state.stats['failed_tasks'])
    
    with col_stat4:
        st.metric("Active", len(st.session_state.active_tasks))
    
    with col_stat5:
        success_rate = 0
        if st.session_state.stats['total_tasks'] > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / st.session_state.stats['total_tasks']) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.divider()
    
    # Active Tasks Section
    if st.session_state.active_tasks:
        st.markdown("### 🔄 Active Tasks")
        
        for task in st.session_state.active_tasks:
            with st.expander(f"🔄 {task['prompt'][:50]}... - {task.get('created_at', 'N/A')}"):
                col_t1, col_t2 = st.columns([3, 1])
                
                with col_t1:
                    st.write(f"**Task ID:** `{task['id']}`")
                    st.write(f"**Model:** {task['model']}")
                    st.write(f"**Prompt:** {task['prompt']}")
                    st.write(f"**Status:** {task.get('status', 'processing').upper()}")
                
                with col_t2:
                    if st.button("🔍 Check Status", key=f"check_{task['id']}"):
                        st.info("Status checking would require API key and polling...")
                        # In a real app, you'd poll check_task_status here
        
        st.divider()
    
    # Task History with Filters
    st.markdown("### 📜 Task History")
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Completed", "Failed", "Processing"]
        )
    
    with col_filter2:
        model_options_history = ["All"] + sorted(list(st.session_state.stats['models_used'].keys()))
        model_filter = st.selectbox(
            "Filter by Model",
            model_options_history
        )
    
    with col_filter3:
        date_filter = st.selectbox(
            "Filter by Date",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days"]
        )
    
    # Apply filters
    filtered_history = st.session_state.task_history.copy()
    
    if status_filter != "All":
        filtered_history = [
            t for t in filtered_history 
            if t.get('status', '').lower() == status_filter.lower()
        ]
    
    if model_filter != "All":
        filtered_history = [
            t for t in filtered_history 
            if model_filter in t.get('model', '')
        ]
    
    if date_filter != "All Time":
        today = datetime.now()
        if date_filter == "Today":
            filter_date_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "Last 7 Days":
            filter_date_start = today - timedelta(days=7)
        else:  # Last 30 Days
            filter_date_start = today - timedelta(days=30)
        
        filtered_history = [
            t for t in filtered_history
            if datetime.strptime(t.get('created_at', '1970-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S") >= filter_date_start
        ]
    
    st.caption(f"Showing {len(filtered_history)} task(s)")
    
    # Display task history
    if not filtered_history:
        st.info("No tasks found matching the filters")
    else:
        # Sort by date descending (newest first)
        filtered_history_sorted = sorted(filtered_history, key=lambda x: x.get('created_at', '1970-01-01 00:00:00'), reverse=True)

        for task in filtered_history_sorted[:50]:  # Show last 50 tasks
            status_emoji = {
                'completed': '✅',
                'failed': '❌',
                'processing': '🔄'
            }.get(task.get('status', 'processing').lower(), '❓')
            
            with st.expander(f"{status_emoji} {task.get('prompt', 'No prompt')[:60]}... - {task.get('created_at', 'N/A')}"):
                col_h1, col_h2 = st.columns([2, 1])
                
                with col_h1:
                    st.write(f"**Task ID:** `{task.get('id', 'N/A')}`")
                    st.write(f"**Model:** {task.get('model', 'N/A')}")
                    st.write(f"**Prompt:** {task.get('prompt', 'N/A')}")
                    st.write(f"**Status:** {task.get('status', 'unknown').upper()}")
                    st.write(f"**Created:** {task.get('created_at', 'N/A')}")
                    
                    if task.get('tags'):
                        st.write(f"**Tags:** {task.get('tags')}")
                
                with col_h2:
                    status = task.get('status', 'info').lower()
                    badge_class = "badge-success" if status == "completed" else "badge-danger" if status == "failed" else "badge-warning" if status == "processing" else "badge-info"
                    st.markdown(f"<div class='badge {badge_class}'>{status.upper()}</div>", unsafe_allow_html=True)
                    
                    # Show result images if available
                    if task.get('result_urls'):
                        st.caption(f"🖼️ {len(task['result_urls'])} image(s) generated")
                        
                        with st.expander("View Results", expanded=False):
                            for i, url in enumerate(task['result_urls']):
                                st.image(url, caption=f"Result {i+1}")
                                try:
                                    img_response = requests.get(url, timeout=10)
                                    if img_response.status_code == 200:
                                        st.download_button(
                                            label=f"Download Result {i+1}",
                                            data=img_response.content,
                                            file_name=f"task_{task.get('id', 'result')}_img_{i+1}.png",
                                            mime="image/png",
                                            key=f"download_task_{task.get('id')}_{i}"
                                        )
                                except Exception as e:
                                    st.error(f"Failed to download result {i+1}: {e}")

# ============================================================================
# PAGE: MODEL COMPARISON
# ============================================================================

def display_model_comparison_page():
    """Display model comparison and benchmarking page"""
    st.title("🔬 Model Comparison Lab")
    st.markdown("Compare different AI models side-by-side with the same prompts")
    
    tab1, tab2, tab3 = st.tabs(["⚖️ Compare Models", "📊 Performance", "💰 Cost Analysis"])
    
    with tab1:
        st.markdown("### Compare Generation Results")
        
        col_models1, col_models2 = st.columns(2)
        
        # Predefined model options for comparison
        comparison_models = {
            "FLUX 1.1 Pro": "black-forest-labs/flux-1.1-pro",
            "FLUX Pro": "black-forest-labs/flux-pro",
            "FLUX Dev": "black-forest-labs/flux-dev",
            "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
            "Stable Diffusion 3.5 Medium": "stabilityai/stable-diffusion-3.5-medium",
        }
        
        with col_models1:
            model1_name = st.selectbox("Model 1", list(comparison_models.keys()), key="compare_model1_name")
            model1_id = comparison_models[model1_name]
        
        with col_models2:
            model2_name = st.selectbox("Model 2", list(comparison_models.keys()), index=1, key="compare_model2_name")
            model2_id = comparison_models[model2_name]
        
        comparison_prompt = st.text_area(
            "Comparison Prompt",
            height=100,
            placeholder="Enter a prompt to test both models..."
        )
        
        col_size1, col_size2 = st.columns(2)
        
        with col_size1:
            image_size = st.selectbox("Image Size", ["square_hd", "square", "portrait", "landscape"])
        
        with col_size2:
            seed = st.number_input("Seed (0 for random)", 0, 999999, 0)
        
        if st.button("🚀 Run Comparison", type="primary"):
            if not comparison_prompt:
                st.error("Please enter a prompt")
                return
            
            api_key = st.secrets.get("KIE_API_KEY") # Use secrets for API key
            if not api_key:
                st.error("KIE.ai API key not found. Please enter it in the text input or set it in secrets.toml")
                return
            
            col_result1, col_result2 = st.columns(2)
            
            # Generate with Model 1
            with col_result1:
                st.markdown(f"### {model1_name}")
                with st.spinner("Generating with Model 1..."):
                    input_params = {
                        "prompt": comparison_prompt,
                        "image_size": image_size,
                        "num_outputs": 1,
                    }
                    if seed > 0:
                        input_params["seed"] = seed
                    
                    task_data1, error1 = create_task(api_key, model1_id, input_params)
                    
                    if not error1 and task_data1:
                        result1, error1 = poll_task_until_complete(api_key, task_data1.get('id'))
                        if result1:
                            urls1 = result1.get('output', {}).get('images', [])
                            if urls1:
                                st.image(urls1[0], use_container_width=True)
                                st.caption(f"✅ Generated by {model1_name}")
                    
                    if error1:
                        st.error(f"❌ Model 1 Error: {error1}")
            
            # Generate with Model 2
            with col_result2:
                st.markdown(f"### {model2_name}")
                with st.spinner("Generating with Model 2..."):
                    input_params = {
                        "prompt": comparison_prompt,
                        "image_size": image_size,
                        "num_outputs": 1,
                    }
                    if seed > 0:
                        input_params["seed"] = seed
                    
                    task_data2, error2 = create_task(api_key, model2_id, input_params)
                    
                    if not error2 and task_data2:
                        result2, error2 = poll_task_until_complete(api_key, task_data2.get('id'))
                        if result2:
                            urls2 = result2.get('output', {}).get('images', [])
                            if urls2:
                                st.image(urls2[0], use_container_width=True)
                                st.caption(f"✅ Generated by {model2_name}")
                    
                    if error2:
                        st.error(f"❌ Model 2 Error: {error2}")
    
    with tab2:
        st.markdown("### Model Performance Metrics")
        
        if not pd or not px:
            st.error("Please install pandas and plotly: `pip install pandas plotly`")
            return
        
        if st.session_state.stats['models_used']:
            model_stats = []
            
            # Summing up counts from history to get total usage per model
            aggregated_model_usage = {}
            for task in st.session_state.task_history:
                model_key = task.get('model', '').split('/')[-1] # Extract model name
                if model_key:
                    aggregated_model_usage[model_key] = aggregated_model_usage.get(model_key, 0) + 1

            for model, count in sorted(aggregated_model_usage.items(), key=lambda item: item[1], reverse=True):
                total_tasks = st.session_state.stats['total_tasks']
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                model_stats.append({
                    'Model': model,
                    'Uses': count,
                    'Percentage': f"{percentage:.1f}%"
                })
            
            df = pd.DataFrame(model_stats)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### Usage Distribution")
            fig = px.pie(df, values='Uses', names='Model', title='Model Usage Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No model usage data yet. Start generating images!")
    
    with tab3:
        st.markdown("### Cost Analysis by Model")
        
        st.info("This feature provides an estimated cost based on KIE.ai API usage. Actual costs may vary.")
        
        # Estimated costs per model (example values - these should be verified with KIE.ai pricing)
        model_costs_per_image = {
            'flux-1.1-pro': 0.04,
            'flux-pro': 0.055,
            'flux-dev': 0.025,
            'flux-schnell': 0.03,
            'stable-diffusion-3.5-large': 0.065,
            'stable-diffusion-3.5-large-turbo': 0.07,
            'stable-diffusion-3.5-medium': 0.035,
            'playground-v3': 0.045,
            'recraft-v3': 0.05,
        }
        
        if aggregated_model_usage: # Use the aggregated data from previous tab
            cost_data = []
            total_estimated_cost = 0
            
            for model_key, count in aggregated_model_usage.items():
                # Extract base model name if it's like 'black-forest-labs/flux-1.1-pro'
                model_name_base = model_key.split('/')[-1] if '/' in model_key else model_key
                
                cost_per_image = model_costs_per_image.get(model_name_base, 0.04) # Default to 0.04 if not found
                model_total_cost = count * cost_per_image
                total_estimated_cost += model_total_cost
                
                cost_data.append({
                    'Model': model_key,
                    'Images Generated': count,
                    'Cost Per Image ($)': f"${cost_per_image:.3f}",
                    'Estimated Cost ($)': f"${model_total_cost:.2f}"
                })
            
            df_cost = pd.DataFrame(cost_data)
            st.dataframe(df_cost, use_container_width=True)
            
            st.metric("Total Estimated Cost ($)", f"{total_estimated_cost:.2f}")
        else:
            st.info("No cost data available yet. Generate some images first!")

# ============================================================================
# PAGE: WORKFLOWS & AUTOMATION
# ============================================================================

def display_workflows_page():
    """Display automated workflows and batch processing"""
    st.title("⚙️ Workflows & Automation")
    st.markdown("Create and manage automated image generation workflows")
    
    tab1, tab2, tab3 = st.tabs(["🔧 Create Workflow", "📋 My Workflows", "⏰ Schedule"])
    
    with tab1:
        st.markdown("### Create New Workflow")
        
        workflow_name = st.text_input("Workflow Name", placeholder="e.g., Product Photography Batch")
        workflow_description = st.text_area(
            "Description",
            placeholder="Describe what this workflow does..."
        )
        
        st.markdown("#### Workflow Steps")
        
        # Use session state to manage dynamic number of steps
        if 'workflow_steps_count' not in st.session_state:
            st.session_state.workflow_steps_count = 1

        if st.button("➕ Add Step"):
            st.session_state.workflow_steps_count += 1

        workflow_steps_list = []
        for i in range(st.session_state.workflow_steps_count):
            with st.expander(f"Step {i+1} Configuration", expanded=True):
                step_type = st.selectbox(
                    "Step Type",
                    ["Generate Image", "Edit Image", "Apply Style", "Upload to Drive", "Post-processing"],
                    key=f"step_type_{i}"
                )
                
                step_config = {'type': step_type}
                
                if step_type == "Generate Image":
                    model_options_gen = {
                        "FLUX 1.1 Pro": "black-forest-labs/flux-1.1-pro",
                        "FLUX Pro": "black-forest-labs/flux-pro",
                        "FLUX Dev": "black-forest-labs/flux-dev",
                        "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
                    }
                    model_name = st.selectbox(
                        "Model",
                        list(model_options_gen.keys()),
                        key=f"model_gen_{i}"
                    )
                    model_id = model_options_gen[model_name]
                    
                    prompt_template = st.text_area(
                        "Prompt Template",
                        placeholder="Use {variable} for dynamic inputs",
                        height=80,
                        key=f"prompt_template_{i}"
                    )
                    
                    step_config.update({
                        'model_name': model_name,
                        'model_id': model_id,
                        'prompt_template': prompt_template
                    })
                
                elif step_type == "Edit Image":
                    edit_model_options_edit = {
                        "Seedream v4 (Edit)": "bytedance/seedream-v4-edit",
                        "Qwen VL-Plus": "qwen/qwen-vl-plus",
                    }
                    edit_model_name = st.selectbox(
                        "Editing Model",
                        list(edit_model_options_edit.keys()),
                        key=f"edit_model_{i}"
                    )
                    edit_model_id = edit_model_options_edit[edit_model_name]
                    
                    edit_instructions = st.text_area(
                        "Edit Instructions",
                        placeholder="Describe edits...",
                        height=60,
                        key=f"edit_instructions_{i}"
                    )
                    edit_strength = st.slider("Edit Strength", 0.1, 1.0, 0.7, key=f"edit_strength_{i}")
                    
                    step_config.update({
                        'edit_model_name': edit_model_name,
                        'edit_model_id': edit_model_id,
                        'edit_instructions': edit_instructions,
                        'edit_strength': edit_strength
                    })

                elif step_type == "Apply Style":
                    style_preset = st.selectbox(
                        "Style Preset",
                        ["Photorealistic", "Fantasy Art", "Cyberpunk", "Abstract", "Anime"],
                        key=f"style_preset_{i}"
                    )
                    step_config['style_preset'] = style_preset
                
                elif step_type == "Upload to Drive":
                    step_config['upload_enabled'] = st.checkbox("Enable Upload to Drive", value=True, key=f"upload_drive_{i}")

                elif step_type == "Post-processing":
                    resolution = st.selectbox(
                        "Output Resolution",
                        ["1K", "2K", "4K"],
                        key=f"post_res_{i}"
                    )
                    step_config['resolution'] = resolution

                workflow_steps_list.append(step_config)

        if st.button("💾 Save Workflow", type="primary"):
            if workflow_name:
                # Generate a unique ID for the workflow
                workflow_id = f"workflow_{int(time.time())}_{len(st.session_state.workflows) + 1}" 
                st.session_state.workflows[workflow_id] = {
                    'name': workflow_name,
                    'description': workflow_description,
                    'steps': workflow_steps_list,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success(f"✅ Workflow '{workflow_name}' saved!")
                # Optionally reset the step count or clear form
                st.session_state.workflow_steps_count = 1 
                st.rerun()
            else:
                st.error("Please enter a workflow name")
    
    with tab2:
        st.markdown("### Saved Workflows")
        
        if st.session_state.workflows:
            for wf_id, workflow in st.session_state.workflows.items():
                with st.expander(f"📋 {workflow['name']}"):
                    st.markdown(f"**Description:** {workflow['description']}")
                    st.markdown(f"**Steps:** {len(workflow['steps'])}")
                    st.markdown(f"**Created:** {workflow['created_at']}")
                    
                    col_run, col_edit, col_delete = st.columns([1, 1, 1])
                    
                    with col_run:
                        if st.button("▶️ Run", key=f"run_{wf_id}"):
                            st.info("Workflow execution is currently under development and will be available soon!")
                    
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_{wf_id}"):
                            st.info("Editing workflows is under development!")
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_{wf_id}"):
                            if st.button("Confirm Delete", key=f"confirm_delete_{wf_id}"):
                                del st.session_state.workflows[wf_id]
                                st.success("Workflow deleted.")
                                st.rerun()
        else:
            st.info("No workflows created yet. Create one in the 'Create Workflow' tab!")
    
    with tab3:
        st.markdown("### Scheduled Tasks")
        
        st.info("Schedule workflows to run automatically at specific times or intervals.")
        
        if not st.session_state.workflows:
            st.warning("You need to create at least one workflow before scheduling.")
        else:
            workflow_options = {wf['name']: wf_id for wf_id, wf in st.session_state.workflows.items()}
            
            schedule_workflow_name = st.selectbox(
                "Select Workflow to Schedule",
                list(workflow_options.keys())
            )
            
            selected_workflow_id = workflow_options[schedule_workflow_name]
            
            col_date, col_time = st.columns(2)
            
            with col_date:
                schedule_date = st.date_input("Execution Date", min_value=datetime.now().date())
            
            with col_time:
                schedule_time = st.time_input("Execution Time")
            
            repeat_option = st.selectbox(
                "Repeat",
                ["Once", "Daily", "Weekly", "Monthly"]
            )
            
            # Placeholder for dynamic inputs if workflow needs them
            dynamic_inputs_section = st.empty()
            if workflow_steps_list: # Check if any steps were defined
                 with dynamic_inputs_section.expander("Dynamic Inputs (Optional)", expanded=False):
                     st.write("Provide values for variables used in your workflow's prompt templates or instructions.")
                     # Logic to parse variables from templates and create inputs would go here

            if st.button("⏰ Schedule Workflow"):
                if schedule_workflow_name and selected_workflow_id:
                    scheduled_task = {
                        'id': f"schedule_{int(time.time())}",
                        'workflow_id': selected_workflow_id,
                        'workflow_name': schedule_workflow_name,
                        'date': str(schedule_date),
                        'time': str(schedule_time.strftime("%H:%M:%S")), # Format time
                        'repeat': repeat_option,
                        'status': 'scheduled',
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.scheduled_tasks.append(scheduled_task)
                    st.success("✅ Workflow scheduled successfully!")
                    st.rerun()
                else:
                    st.error("Please select a workflow to schedule")

# ============================================================================
# PAGE: PROJECTS
# ============================================================================

def display_projects_page():
    """Display project management for organizing related images"""
    st.title("📁 Projects")
    st.markdown("Organize your AI generations into projects")
    
    # Initialize projects state if not exists
    if 'projects' not in st.session_state:
        st.session_state.projects = {}
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None # No project selected initially

    tab1, tab2 = st.tabs(["📂 My Projects", "➕ New Project"])
    
    with tab1:
        st.subheader("Your Projects")
        if st.session_state.projects:
            # Use columns for a grid layout of projects
            col_count = 3
            cols = st.columns(col_count)
            
            project_ids = list(st.session_state.projects.keys())
            
            for idx, project_id in enumerate(project_ids):
                project = st.session_state.projects[project_id]
                current_col = cols[idx % col_count]
                
                with current_col:
                    with st.container(border=True):
                        st.markdown(f"### {project['name']}")
                        st.caption(project['description'])
                        
                        st.metric("Images Assigned", project.get('image_count', 0))
                        st.caption(f"Created: {project['created_at']}")
                        
                        if st.button("View", key=f"view_project_{project_id}"):
                            st.session_state.selected_project = project_id
                            st.success(f"Viewing project: {project['name']}")
                            # Optionally, navigate to a dedicated project view or filter library
                            # For now, just show a success message and allow reruns for potential future navigation
                        
                        if st.button("Delete", key=f"delete_project_{project_id}"):
                            # Confirmation step
                            if st.button("Confirm Delete", key=f"confirm_delete_project_{project_id}"):
                                del st.session_state.projects[project_id]
                                if st.session_state.selected_project == project_id:
                                    st.session_state.selected_project = None # Deselect if deleted
                                st.success("Project deleted.")
                                st.rerun()
        else:
            st.info("No projects created yet. Click on 'New Project' to get started!")
    
    with tab2:
        st.subheader("Create New Project")
        
        project_name = st.text_input("Project Name", placeholder="e.g., Product Launch 2024")
        project_description = st.text_area(
            "Description",
            placeholder="Describe your project and its goals..."
        )
        project_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., product, marketing, campaign"
        )
        
        if st.button("🎨 Create Project", type="primary"):
            if project_name:
                # Generate a unique project ID
                project_id = f"project_{int(time.time())}_{len(st.session_state.projects) + 1}"
                st.session_state.projects[project_id] = {
                    'name': project_name,
                    'description': project_description,
                    'tags': [tag.strip() for tag in project_tags.split(',') if tag.strip()],
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'image_count': 0, # Initialize image count
                    'images': [] # List to store assigned image IDs or info
                }
                st.success(f"✅ Project '{project_name}' created!")
                st.rerun() # Rerun to clear form and update UI
            else:
                st.error("Please enter a project name")

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

def display_analytics_page():
    """Display analytics and statistics"""
    st.title("📊 Analytics Dashboard")
    st.markdown("Insights into your AI image generation activity")
    
    if not pd or not px:
        st.error("Please install pandas and plotly for analytics: `pip install pandas plotly`")
        return

    # Overall Statistics
    st.markdown("### 📈 Overall Statistics")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    
    with col_stat2:
        st.metric("Images Generated", st.session_state.stats['total_images'])
    
    with col_stat3:
        st.metric("Uploaded to Drive", st.session_state.stats['uploaded_images'])
    
    with col_stat4:
        st.metric("API Calls", st.session_state.stats['total_api_calls'])
    
    st.divider()
    
    # Model Usage
    st.markdown("### 🤖 Model Usage")
    
    # Re-aggregate model usage from task history for accuracy
    aggregated_model_usage = {}
    for task in st.session_state.task_history:
        model_key = task.get('model', '').split('/')[-1] # Extract base model name
        if model_key:
            aggregated_model_usage[model_key] = aggregated_model_usage.get(model_key, 0) + 1

    if aggregated_model_usage:
        model_stats_list = []
        for model, count in sorted(aggregated_model_usage.items(), key=lambda item: item[1], reverse=True):
            model_stats_list.append({'Model': model, 'Uses': count})
        
        df_models = pd.DataFrame(model_stats_list)

        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("**Usage by Model:**")
            st.dataframe(df_models, use_container_width=True)
        
        with col_m2:
            st.markdown("### Usage Distribution")
            fig_models = px.pie(df_models, values='Uses', names='Model', title='Model Usage Distribution')
            st.plotly_chart(fig_models, use_container_width=True)
            
            if df_models.shape[0] > 0:
                 most_used = df_models.iloc[0]
                 st.metric("Most Used Model", most_used['Model'], f"{most_used['Uses']} uses")

    else:
        st.info("No model usage data yet. Start generating images!")
    
    st.divider()
    
    # Tag Analytics
    st.markdown("### 🏷️ Tag Analytics")
    
    if st.session_state.stats['tags_used']:
        tag_data = st.session_state.stats['tags_used']
        
        tag_stats_list = []
        for tag, count in sorted(tag_data.items(), key=lambda item: item[1], reverse=True):
            tag_stats_list.append({'Tag': tag, 'Count': count})
        
        df_tags = pd.DataFrame(tag_stats_list)
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("**Top Tags:**")
            st.dataframe(df_tags.head(10), use_container_width=True)
        
        with col_t2:
            st.metric("Total Unique Tags", len(tag_data))
            st.metric("Total Tagged Images", sum(tag_data.values()))
            
            st.markdown("### Tag Usage Distribution")
            fig_tags = px.bar(df_tags.head(15), x='Tag', y='Count', title='Top 15 Tag Usage')
            st.plotly_chart(fig_tags, use_container_width=True)

    else:
        st.info("No tag data yet. Add tags to your images!")
    
    st.divider()
    
    # Daily Usage
    st.markdown("### 📅 Daily Usage")
    
    if st.session_state.stats['daily_usage']:
        daily_data = st.session_state.stats['daily_usage']
        
        # Prepare data for plotting
        days = sorted(daily_data.keys())
        counts = [daily_data[day] for day in days]
        
        df_daily = pd.DataFrame({'Date': days, 'Generations': counts})
        df_daily['Date'] = pd.to_datetime(df_daily['Date']) # Ensure date format for plotting
        
        st.markdown("**Generations per Day:**")
        fig_daily = px.line(df_daily, x='Date', y='Generations', title='Daily Generation Trends')
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Show recent activity
        st.markdown("**Recent Activity:**")
        sorted_days = sorted(daily_data.items(), key=lambda item: item[0], reverse=True)[:7]
        for date, count in sorted_days:
            st.write(f"- **{date}:** {count} generations")
    else:
        st.info("No daily usage data yet")
    
    st.divider()
    
    # Hourly Usage
    st.markdown("### ⏰ Hourly Usage")
    if st.session_state.stats['hourly_usage']:
        hourly_data = st.session_state.stats['hourly_usage']
        
        # Prepare data for plotting
        hours = sorted(hourly_data.keys())
        counts = [hourly_data[hour] for hour in hours]
        
        df_hourly = pd.DataFrame({'Hour': hours, 'Generations': counts})
        df_hourly['Hour_dt'] = pd.to_datetime(df_hourly['Hour']) # Convert to datetime for sorting
        
        st.markdown("**Generations per Hour of Day:**")
        fig_hourly = px.line(df_hourly.sort_values('Hour_dt'), x='Hour_dt', y='Generations', title='Hourly Generation Patterns')
        st.plotly_chart(fig_hourly, use_container_width=True)
    else:
        st.info("No hourly usage data yet.")

    st.divider()

    # Success/Failure Analysis
    st.markdown("### ✅ Success Rate Analysis")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.metric("Successful Tasks", st.session_state.stats['successful_tasks'])
    
    with col_s2:
        st.metric("Failed Tasks", st.session_state.stats['failed_tasks'])
    
    with col_s3:
        total_tasks = st.session_state.stats['total_tasks']
        if total_tasks > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / total_tasks) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")

# ============================================================================
# PAGE: DATA EXPORT/IMPORT
# ============================================================================

def display_data_page():
    """Display data management page"""
    st.title("💾 Data Management")
    st.markdown("Export, import, and manage your generation data")
    
    tab1, tab2, tab3 = st.tabs(["📤 Export", "📥 Import", "🗑️ Clear Data"])
    
    with tab1:
        st.markdown("### Export Your Data")
        
        # CSV Export
        st.markdown("#### 📄 CSV Export")
        
        csv_data_string = export_to_csv()
        
        if csv_data_string:
            st.download_button(
                label="💾 Download CSV",
                data=csv_data_string,
                file_name=f"ai_image_studio_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download all your generation data as CSV"
            )
            
            st.caption(f"Total entries in CSV data: {len(st.session_state.csv_data)}")
        else:
            st.info("No CSV data to export yet")
        
        st.divider()
        
        # JSON Export (Complete Backup)
        st.markdown("#### 📋 JSON Export (Complete Backup)")
        
        full_data = {
            'csv_data': st.session_state.csv_data,
            'stats': st.session_state.stats,
            'tags': st.session_state.tags,
            'favorites': st.session_state.favorites,
            'task_history': st.session_state.task_history,
            'projects': st.session_state.projects,
            'workflows': st.session_state.workflows,
            'scheduled_tasks': st.session_state.scheduled_tasks,
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        json_data_string = json.dumps(full_data, indent=2)
        
        st.download_button(
            label="💾 Download Complete Backup (JSON)",
            data=json_data_string,
            file_name=f"ai_image_studio_backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            help="Download complete backup including stats, tags, history, projects, workflows, and schedules"
        )
    
    with tab2:
        st.markdown("### Import Data")
        
        # CSV Import
        st.markdown("#### 📄 Import CSV")
        
        csv_file_upload = st.file_uploader("Upload CSV file", type=['csv'], key="csv_import")
        
        if csv_file_upload:
            if st.button("Import CSV Data"):
                try:
                    success, result = load_csv_file(csv_file_upload)
                    if success:
                        st.success(f"✅ Imported {result} entries from CSV!")
                    else:
                        st.error(f"❌ Import failed: {result}")
                except Exception as e:
                    st.error(f"Error during CSV import: {str(e)}")
        
        st.divider()
        
        # JSON Import
        st.markdown("#### 📋 Import JSON Backup")
        
        json_file_upload = st.file_uploader("Upload JSON backup file", type=['json'], key="json_import")
        
        if json_file_upload:
            if st.button("Import JSON Backup"):
                try:
                    backup_data = json.load(json_file_upload)
                    
                    # Restore data - append and update to avoid overwriting existing unique data
                    if 'csv_data' in backup_data and isinstance(backup_data['csv_data'], list):
                        st.session_state.csv_data.extend(backup_data['csv_data'])
                    
                    if 'stats' in backup_data and isinstance(backup_data['stats'], dict):
                        for key, value in backup_data['stats'].items():
                            if key in st.session_state.stats:
                                if isinstance(value, dict):
                                    st.session_state.stats[key].update(value) # Merge dictionaries
                                elif isinstance(st.session_state.stats[key], (int, float)) and isinstance(value, (int, float)):
                                    st.session_state.stats[key] += value # Sum numbers
                                else:
                                    st.session_state.stats[key] = value # Overwrite if types differ or not dict/number
                    
                    if 'tags' in backup_data and isinstance(backup_data['tags'], dict):
                        st.session_state.tags.update(backup_data['tags'])
                    
                    if 'favorites' in backup_data and isinstance(backup_data['favorites'], list):
                        st.session_state.favorites.extend(backup_data['favorites'])
                        # Ensure unique favorites
                        st.session_state.favorites = list(set(st.session_state.favorites))

                    if 'task_history' in backup_data and isinstance(backup_data['task_history'], list):
                        st.session_state.task_history.extend(backup_data['task_history'])
                    
                    if 'projects' in backup_data and isinstance(backup_data['projects'], dict):
                        st.session_state.projects.update(backup_data['projects'])

                    if 'workflows' in backup_data and isinstance(backup_data['workflows'], dict):
                        st.session_state.workflows.update(backup_data['workflows'])

                    if 'scheduled_tasks' in backup_data and isinstance(backup_data['scheduled_tasks'], list):
                        st.session_state.scheduled_tasks.extend(backup_data['scheduled_tasks'])
                    
                    st.success("✅ Backup restored successfully!")
                    st.rerun() # Rerun to reflect changes
                    
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file. Please ensure it's a valid backup.")
                except Exception as e:
                    st.error(f"❌ Import failed: {str(e)}")
    
    with tab3:
        st.markdown("### Clear Data")
        st.warning("⚠️ These actions cannot be undone!")
        
        col_clear1, col_clear2 = st.columns(2)
        
        with col_clear1:
            if st.button("🗑️ Clear CSV Data Entries", type="secondary"):
                if st.button("Confirm Clear CSV", key="confirm_clear_csv"):
                    st.session_state.csv_data = []
                    st.success("CSV data cleared")
                    st.rerun()
        
        with col_clear2:
            if st.button("🗑️ Clear Statistics", type="secondary"):
                 if st.button("Confirm Clear Stats", key="confirm_clear_stats"):
                    # Reset specific stats keys, not the whole session state
                    st.session_state.stats = {
                        'total_tasks': 0,
                        'successful_tasks': 0,
                        'failed_tasks': 0,
                        'total_images': 0,
                        'uploaded_images': 0,
                        'total_api_calls': 0,
                        'models_used': {},
                        'tags_used': {},
                        'daily_usage': {},
                        'hourly_usage': {},
                        'cost_tracking': {},
                    }
                    st.session_state.task_history = [] # Clear history as well for accurate stats
                    st.session_state.completed_tasks = []
                    st.session_state.failed_tasks = []
                    st.session_state.active_tasks = []
                    st.success("Statistics and task history cleared.")
                    st.rerun()
        
        st.divider()
        
        if st.button("⚠️ Clear ALL App Data (Reset to Defaults)", type="secondary", help="This will clear all session state and reset the app."):
            if st.button("Confirm Full Reset", key="confirm_full_reset"):
                # Clear all keys from session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Re-initialize with defaults
                init_session_state() 
                st.success("All app data cleared. App reset to defaults.")
                st.rerun()

# ============================================================================
# PAGE: SETTINGS
# ============================================================================

def display_settings_page():
    """Display settings and configuration page"""
    st.title("⚙️ Settings & Configuration")
    st.markdown("Manage your Google Drive integration and app preferences")
    
    # Google Authentication Section
    st.markdown("### 🔐 Google Services Authentication")
    
    if st.session_state.get('authenticated'):
        st.success("✅ Successfully authenticated with Google services!")
        
        col_auth1, col_auth2, col_auth3 = st.columns(3)
        
        with col_auth1:
            st.metric("Drive Status", "Connected" if st.session_state.drive_service else "Not Connected")
        
        with col_auth2:
            st.metric("Sheets Status", "Connected" if st.session_state.sheets_service else "Not Connected")
        
        with col_auth3:
            folder_id = st.session_state.get('app_folder_id', 'N/A')
            st.metric("App Folder ID", folder_id[:20] + "..." if isinstance(folder_id, str) and len(folder_id) > 20 else folder_id)
        
        if st.button("🔄 Re-authenticate"):
            st.session_state.authenticated = False
            st.session_state.drive_service = None
            st.session_state.sheets_service = None
            st.session_state.app_folder_id = None
            st.session_state.spreadsheet_id = None
            st.rerun()
    
    else:
        st.info("👇 Enter your Google Service Account JSON or upload the file to connect with Google Drive and Sheets")
        
        service_account_json = st.text_area(
            "Service Account JSON",
            height=200,
            help="Paste your Google Cloud service account JSON here",
            placeholder='{\n  "type": "service_account",\n  "project_id": "...",\n  ...\n}'
        )
        
        # Add file uploader for service account JSON
        uploaded_file = st.file_uploader(
            "Upload Service Account JSON File",
            type=['json'],
            help="Alternatively, upload your Google Cloud service account JSON file",
            key="settings_auth_upload"
        )
        
        if st.button("🔐 Authenticate", type="primary"):
            json_to_use = None
            if service_account_json.strip():
                json_to_use = service_account_json
            elif uploaded_file:
                try:
                    json_to_use = uploaded_file.read().decode('utf-8')
                except Exception as e:
                    st.error(f"Error reading uploaded file: {str(e)}")
                    json_to_use = None
            
            if json_to_use:
                with st.spinner("Authenticating..."):
                    success, message = authenticate_with_service_account(json_to_use)
                    
                    if success:
                        st.success(message)
                        
                        # Create app folder and spreadsheet in background if auth is successful
                        with st.spinner("Setting up Google Drive folder and spreadsheet..."):
                            folder_id = create_app_folder()
                            if folder_id:
                                st.success(f"✅ App folder created/found in Drive.")
                            else:
                                st.warning("Could not create/find app folder. Check permissions.")
                            
                            spreadsheet_id = create_or_get_spreadsheet()
                            if spreadsheet_id:
                                st.success(f"✅ Tracking spreadsheet ready.")
                            else:
                                st.warning("Could not create/find tracking spreadsheet. Check permissions.")
                        
                        time.sleep(1) # Give time for spinners to show
                        st.rerun() # Rerun to update status
                    else:
                        st.error(message)
            else:
                st.error("Please enter your service account JSON or upload the file")
        
        with st.expander("ℹ️ How to get Service Account JSON"):
            st.markdown("""
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select an existing one.
            3. Enable **Google Drive API** and **Google Sheets API** for your project.
            4. Navigate to **IAM & Admin** > **Service Accounts**.
            5. Click **+ CREATE SERVICE ACCOUNT**. Give it a name and description.
            6. Grant it the roles: `Drive Editor` and `Sheets Editor`.
            7. Click **Done**. Then, click on the created service account, go to the **Keys** tab.
            8. Click **ADD KEY** > **Create new key**. Choose **JSON** and click **Create**.
            9. The JSON file will download. Copy its content and paste it into the text area above, or upload the file.
            10. Ensure the service account email also has access (e.g., `Editor` role) to the Google Drive folder where you want to store files.
            """)
    
    st.divider()
    
    # App Preferences
    st.markdown("### 🎨 App Preferences")
    
    col_pref1, col_pref2 = st.columns(2)
    
    with col_pref1:
        auto_upload = st.checkbox(
            "Auto-upload to Drive",
            value=st.session_state.get('auto_upload_enabled', True),
            help="Automatically upload all generated images to Google Drive"
        )
        st.session_state.auto_upload_enabled = auto_upload
    
    with col_pref2:
        # Use slider for items per page, ensure it's in session state
        items_per_page_slider = st.slider(
            "Library items per page",
            12, 96, st.session_state.get('items_per_page', 12), 12,
            help="Number of items to display per page in the library"
        )
        st.session_state.items_per_page = items_per_page_slider
    
    # Theme selection
    theme = st.radio(
        "Select Theme",
        ["Light", "Dark", "System"],
        index=["Light", "Dark", "System"].index(st.session_state.get('theme', 'dark').capitalize()),
        horizontal=True,
        key="theme_selector"
    )
    st.session_state.theme = theme.lower() # Store theme in session state

    st.divider()
    
    # System Information
    st.markdown("### 📊 System Information")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    
    with col_info2:
        st.metric("Images in Library", len(st.session_state.gdrive_images))
    
    with col_info3:
        st.metric("CSV Entries", len(st.session_state.csv_data))
    
    st.divider()
    
    # About
    st.markdown("### ℹ️ About")
    st.markdown("""
    **AI Image Studio Pro - Ultimate Edition**
    
    A comprehensive AI image generation and management platform with:
    - Multiple AI models (FLUX, Stable Diffusion, Seedream, and more)
    - Google Drive & Sheets integration
    - Task management and tracking
    - Advanced analytics and cost estimation
    - Workflow automation and scheduling
    - Project organization
    - Complete data export/import
    
    Powered by [KIE.ai](https://kie.ai) API
    """)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()

    # Apply theme
    if st.session_state.theme == 'dark':
        st.markdown("<style>body {background-color: #1e1e1e; color: white;}</style>", unsafe_allow_html=True)
    elif st.session_state.theme == 'light':
        st.markdown("<style>body {background-color: white; color: black;}</style>", unsafe_allow_html=True)
    # System theme is handled by Streamlit's default behavior or can be further customized

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=AI+Image+Studio+Pro", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 🔐 Google Auth")
        
        if not st.session_state.get('authenticated'):
            with st.expander("📤 Upload Service File", expanded=False):
                uploaded_file = st.file_uploader(
                    "Service Account JSON",
                    type=['json'],
                    help="Upload your Google Cloud service account JSON file",
                    key="sidebar_auth_upload"
                )
                
                if uploaded_file:
                    try:
                        service_json = uploaded_file.read().decode('utf-8')
                        
                        if st.button("🔓 Authenticate Now", type="primary"):
                            with st.spinner("Authenticating..."):
                                success, message = authenticate_with_service_account(service_json)
                                
                                if success:
                                    # Create app folder and spreadsheet if authentication succeeds
                                    with st.spinner("Setting up Drive folder and spreadsheet..."):
                                        folder_id = create_app_folder()
                                        spreadsheet_id = create_or_get_spreadsheet()
                                    
                                    st.success("✅ Connected to Google Services!")
                                    time.sleep(1) # Short delay for spinner
                                    st.rerun()
                                else:
                                    st.error(message)
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
                
                st.caption("Or paste JSON in Settings page")
        else:
            st.success("✅ Drive Connected")
            if st.button("🔄 Disconnect"):
                st.session_state.authenticated = False
                st.session_state.drive_service = None
                st.session_state.sheets_service = None
                st.session_state.app_folder_id = None
                st.session_state.spreadsheet_id = None
                st.rerun()
        
        st.markdown("---")
        
        # Navigation
        selected_page = st.radio(
            "Navigation",
            [
                "🎨 Generate", 
                "✏️ Edit", 
                "📚 Library", 
                "📋 Tasks", 
                "🔬 Compare", 
                "⚙️ Workflows",
                "📁 Projects",
                "📊 Analytics", 
                "💾 Data", 
                "⚙️ Settings"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
        st.metric("Images", st.session_state.stats['total_images'])
        success_rate = (st.session_state.stats['successful_tasks'] / max(st.session_state.stats['total_tasks'], 1) * 100)
        st.metric("Success Rate", f"{success_rate:.1f}%")
        
        if st.session_state.active_tasks:
            st.markdown("---")
            st.warning(f"⚡ {len(st.session_state.active_tasks)} Active Task(s)")
        
        st.markdown("---")
        
        # Authentication Status
        if st.session_state.get('authenticated'):
            st.success("✅ Google Drive Connected")
            if st.session_state.app_folder_id:
                st.caption(f"Folder: {st.session_state.app_folder_id[:20]}...") # Show truncated folder ID
        else:
            st.warning("⚠️ Drive Not Connected")
        
        st.markdown("---")
        
        st.caption("v4.0 Ultimate Pro Edition")
        st.caption("Powered by KIE.ai")
    
    # Main content area
    if selected_page == "🎨 Generate":
        display_generate_page()
    elif selected_page == "✏️ Edit":
        display_edit_page()
    elif selected_page == "📚 Library":
        display_library_page()
    elif selected_page == "📋 Tasks":
        display_task_management_page()
    elif selected_page == "🔬 Compare":
        display_model_comparison_page()
    elif selected_page == "⚙️ Workflows":
        display_workflows_page()
    elif selected_page == "📁 Projects":
        display_projects_page()
    elif selected_page == "📊 Analytics":
        display_analytics_page()
    elif selected_page == "💾 Data":
        display_data_page()
    elif selected_page == "⚙️ Settings":
        display_settings_page()
    
    # Footer
    st.markdown("---")
    
    col_footer1, col_footer2, col_footer3, col_footer4 = st.columns(4)
    
    with col_footer1:
        st.caption(f"📊 {st.session_state.stats['total_tasks']} Total Tasks")
    
    with col_footer2:
        st.caption(f"🖼️ {st.session_state.stats['total_images']} Images Generated")
    
    with col_footer3:
        st.caption(f"✅ {st.session_state.stats['successful_tasks']} Successful")
    
    with col_footer4:
        st.caption(f"⚡ {len(st.session_state.active_tasks)} Active Now")

if __name__ == "__main__":
    main()
