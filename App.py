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
        },
        
        # User Preferences
        'favorites': [],
        'tags': {},
        'collections': {},
        'comparison_list': [],
        
        # UI State
        'selected_tab': 'Generate',
        'current_page': 1,
        'items_per_page': 12,
        'search_query': '',
        'filter_tag': 'All',
        'view_mode': 'grid',
        
        # Generation Settings
        'last_prompt': '',
        'last_model': 'flux-1.1-pro',
        'generation_presets': {},
        'auto_upload_enabled': True,
        
        # Advanced Features
        'batch_mode': False,
        'batch_prompts': [],
        'comparison_mode': False,
        'analytics_period': 7,
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
                    
                    st.session_state.stats['total_images'] += 1
                    
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
# DISPLAY FUNCTIONS
# ============================================================================

def display_gdrive_image(file_info, caption="", width=200):
    """Display a Google Drive image with enhanced styling"""
    try:
        file_id = file_info['id']
        image_bytes = get_gdrive_image_bytes(file_id)
        
        if image_bytes and PILImage:
            image = PILImage.open(io.BytesIO(image_bytes))
            st.image(image, caption=caption, width=width)
            return True
        else:
            st.error("Failed to load image")
            return False
            
    except Exception as e:
        st.error(f"Display error: {str(e)}")
        return False

# ============================================================================
# PAGE: TEXT-TO-IMAGE GENERATION
# ============================================================================

def display_generate_page():
    """Display the text-to-image generation page"""
    st.title("🎨 AI Image Generation")
    st.markdown("Create stunning images using advanced AI models")
    
    # API Key Input
    api_key = st.text_input(
        "🔑 KIE.ai API Key",
        type="password",
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
            
            # Add to active tasks
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
                st.session_state.failed_tasks.append(task_info)
                return
            
            # Get result URLs
            output = result.get('output', {})
            result_urls = output.get('images', [])
            
            if not result_urls:
                st.error("❌ No images generated")
                task_info['status'] = 'failed'
                return
            
            # Update task status
            task_info['status'] = 'completed'
            task_info['result_urls'] = result_urls
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
                    except:
                        pass
            
            # Show upload status
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} image(s) uploaded to Google Drive!")
                
                with st.expander("📁 View Drive Links"):
                    for file_info in uploaded_files:
                        st.markdown(f"[{file_info['name']}]({file_info['webViewLink']})")

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
        key="edit_api_key"
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
    
    if image_source == "Upload from Computer":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload the image you want to edit"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = PILImage.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width=300)
            
            # For editing, we need to upload to a temporary location or use base64
            # For simplicity, we'll convert to base64 data URL
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
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
                    selected_image = library_options[selected_image_name]
                    
                    # Display selected image
                    display_gdrive_image(selected_image, caption="Selected Image", width=300)
                    
                    # Get direct link for API
                    file_id = selected_image['id']
                    source_image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    
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
                "image_size": "square_hd",
                "image_resolution": edit_resolution,
                "max_images": 1,
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
                if image_source == "Upload from Computer" and uploaded_file:
                    st.image(image, use_container_width=True)
                elif selected_image_name:
                    display_gdrive_image(selected_image, width=400)
            
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
                except:
                    pass
            
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
        filtered_images = [
            img for img in filtered_images
            if search_query.lower() in img['name'].lower()
        ]
    
    if filter_tag != "All":
        filtered_images = [
            img for img in filtered_images
            if filter_tag in get_image_tags(img['id'])
        ]
    
    # Sort images
    if sort_by == "Oldest":
        filtered_images = sorted(filtered_images, key=lambda x: x.get('createdTime', ''))
    elif sort_by == "Name":
        filtered_images = sorted(filtered_images, key=lambda x: x.get('name', ''))
    # Newest is already the default order
    
    # Pagination
    total_images = len(filtered_images)
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
                            st.caption(f"**{img['name'][:30]}...**" if len(img['name']) > 30 else img['name'])
                            st.caption(f"📅 {img.get('createdTime', 'N/A')[:10]}")
                            
                            # Action buttons
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            
                            with col_btn1:
                                if st.button("🔗", key=f"link_{img['id']}", help="Open in Drive"):
                                    st.markdown(f"[View in Drive]({img['webViewLink']})")
                            
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
                                        list_gdrive_images(force_refresh=True)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            
                            # Tags
                            img_tags = get_image_tags(img['id'])
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
                    st.markdown(f"### {img['name']}")
                    st.caption(f"📅 Created: {img.get('createdTime', 'N/A')}")
                    st.caption(f"📦 Size: {int(img.get('size', 0)) / 1024:.1f} KB")
                    
                    # Tags
                    img_tags = get_image_tags(img['id'])
                    if img_tags:
                        st.markdown("🏷️ Tags: " + " ".join([f"`{tag}`" for tag in img_tags]))
                    
                    # Actions
                    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
                    
                    with col_act1:
                        st.link_button("🔗 View in Drive", img['webViewLink'])
                    
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
                            add_to_comparison(img)
                            st.success("Added to comparison!")
                    
                    with col_act4:
                        if st.button("🗑️ Delete", key=f"del_list_{img['id']}"):
                            success, msg = delete_gdrive_file(img['id'])
                            if success:
                                list_gdrive_images(force_refresh=True)
                                st.rerun()
                
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
                        st.info("Status checking would require API key...")
        
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
        model_filter = st.selectbox(
            "Filter by Model",
            ["All"] + list(st.session_state.stats['models_used'].keys())
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
            filter_date = today
        elif date_filter == "Last 7 Days":
            filter_date = today - timedelta(days=7)
        else:  # Last 30 Days
            filter_date = today - timedelta(days=30)
        
        filtered_history = [
            t for t in filtered_history
            if datetime.strptime(t.get('created_at', ''), "%Y-%m-%d %H:%M:%S") >= filter_date
        ]
    
    st.caption(f"Showing {len(filtered_history)} task(s)")
    
    # Display task history
    if not filtered_history:
        st.info("No tasks found matching the filters")
    else:
        for task in reversed(filtered_history[-50:]):  # Show last 50 tasks
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
                    st.markdown(f"<div class='badge badge-{task.get('status', 'info')}'>{task.get('status', 'unknown').upper()}</div>", unsafe_allow_html=True)
                    
                    # Show result images if available
                    if task.get('result_urls'):
                        st.caption(f"🖼️ {len(task['result_urls'])} image(s) generated")

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

def display_analytics_page():
    """Display analytics and statistics"""
    st.title("📊 Analytics Dashboard")
    st.markdown("Insights into your AI image generation activity")
    
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
    
    if st.session_state.stats['models_used']:
        model_data = st.session_state.stats['models_used']
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            # Model usage table
            st.markdown("**Usage by Model:**")
            for model, count in sorted(model_data.items(), key=lambda x: x[1], reverse=True):
                st.write(f"- **{model}:** {count} generations")
        
        with col_m2:
            # Most used model
            most_used = max(model_data.items(), key=lambda x: x[1])
            st.metric("Most Used Model", most_used[0], f"{most_used[1]} uses")
    else:
        st.info("No model usage data yet. Start generating images!")
    
    st.divider()
    
    # Tag Analytics
    st.markdown("### 🏷️ Tag Analytics")
    
    if st.session_state.stats['tags_used']:
        tag_data = st.session_state.stats['tags_used']
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("**Top Tags:**")
            top_tags = sorted(tag_data.items(), key=lambda x: x[1], reverse=True)[:10]
            for tag, count in top_tags:
                st.write(f"- **{tag}:** {count} images")
        
        with col_t2:
            st.metric("Total Unique Tags", len(tag_data))
            st.metric("Total Tagged Images", sum(tag_data.values()))
    else:
        st.info("No tag data yet. Add tags to your images!")
    
    st.divider()
    
    # Daily Usage
    st.markdown("### 📅 Daily Usage")
    
    if st.session_state.stats['daily_usage']:
        daily_data = st.session_state.stats['daily_usage']
        
        # Show last 30 days
        sorted_days = sorted(daily_data.items(), reverse=True)[:30]
        
        st.markdown("**Recent Activity:**")
        for date, count in sorted_days:
            st.write(f"- **{date}:** {count} generations")
    else:
        st.info("No daily usage data yet")
    
    st.divider()
    
    # Success/Failure Analysis
    st.markdown("### ✅ Success Rate Analysis")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.metric("Successful Tasks", st.session_state.stats['successful_tasks'])
    
    with col_s2:
        st.metric("Failed Tasks", st.session_state.stats['failed_tasks'])
    
    with col_s3:
        if st.session_state.stats['total_tasks'] > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / st.session_state.stats['total_tasks']) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")

# ============================================================================
# PAGE: DATA EXPORT
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
        
        csv_data = export_to_csv()
        
        if csv_data:
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"ai_image_studio_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download all your generation data as CSV"
            )
            
            st.caption(f"Total entries: {len(st.session_state.csv_data)}")
        else:
            st.info("No data to export yet")
        
        st.divider()
        
        # JSON Export
        st.markdown("#### 📋 JSON Export (Complete Backup)")
        
        full_data = {
            'csv_data': st.session_state.csv_data,
            'stats': st.session_state.stats,
            'tags': st.session_state.tags,
            'favorites': st.session_state.favorites,
            'task_history': st.session_state.task_history,
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        json_data = json.dumps(full_data, indent=2)
        
        st.download_button(
            label="💾 Download Complete Backup (JSON)",
            data=json_data,
            file_name=f"ai_image_studio_backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            help="Download complete backup including stats, tags, and history"
        )
    
    with tab2:
        st.markdown("### Import Data")
        
        # CSV Import
        st.markdown("#### 📄 Import CSV")
        
        csv_file = st.file_uploader("Upload CSV file", type=['csv'], key="csv_import")
        
        if csv_file:
            if st.button("Import CSV Data"):
                success, result = load_csv_file(csv_file)
                
                if success:
                    st.success(f"✅ Imported {result} entries from CSV!")
                else:
                    st.error(f"❌ Import failed: {result}")
        
        st.divider()
        
        # JSON Import
        st.markdown("#### 📋 Import JSON Backup")
        
        json_file = st.file_uploader("Upload JSON backup file", type=['json'], key="json_import")
        
        if json_file:
            if st.button("Import JSON Backup"):
                try:
                    backup_data = json.load(json_file)
                    
                    # Restore data
                    if 'csv_data' in backup_data:
                        st.session_state.csv_data.extend(backup_data['csv_data'])
                    
                    if 'stats' in backup_data:
                        # Merge stats
                        for key, value in backup_data['stats'].items():
                            if isinstance(value, dict):
                                st.session_state.stats[key].update(value)
                            else:
                                st.session_state.stats[key] += value
                    
                    if 'tags' in backup_data:
                        st.session_state.tags.update(backup_data['tags'])
                    
                    if 'favorites' in backup_data:
                        st.session_state.favorites.extend(backup_data['favorites'])
                    
                    if 'task_history' in backup_data:
                        st.session_state.task_history.extend(backup_data['task_history'])
                    
                    st.success("✅ Backup restored successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Import failed: {str(e)}")
    
    with tab3:
        st.markdown("### Clear Data")
        st.warning("⚠️ These actions cannot be undone!")
        
        col_clear1, col_clear2 = st.columns(2)
        
        with col_clear1:
            if st.button("🗑️ Clear CSV Data", type="secondary"):
                st.session_state.csv_data = []
                st.success("CSV data cleared")
        
        with col_clear2:
            if st.button("🗑️ Clear Statistics", type="secondary"):
                init_session_state()
                st.success("Statistics reset")
        
        st.divider()
        
        if st.button("⚠️ Clear ALL Data (Reset App)", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.success("All data cleared. App reset.")
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
            st.metric("Folder ID", "✓" if st.session_state.app_folder_id else "Not Created")
        
        if st.button("🔄 Re-authenticate"):
            st.session_state.authenticated = False
            st.rerun()
    
    else:
        st.info("👇 Enter your Google Service Account JSON to connect with Google Drive and Sheets")
        
        service_account_json = st.text_area(
            "Service Account JSON",
            height=200,
            help="Paste your Google Cloud service account JSON here",
            placeholder='{\n  "type": "service_account",\n  "project_id": "...",\n  ...\n}'
        )
        
        if st.button("🔐 Authenticate", type="primary"):
            if service_account_json.strip():
                with st.spinner("Authenticating..."):
                    success, message = authenticate_with_service_account(service_account_json)
                    
                    if success:
                        st.success(message)
                        
                        # Create app folder
                        with st.spinner("Setting up Drive folder..."):
                            folder_id = create_app_folder()
                            if folder_id:
                                st.success(f"✅ App folder created/found: {folder_id}")
                            
                            # Create spreadsheet
                            spreadsheet_id = create_or_get_spreadsheet()
                            if spreadsheet_id:
                                st.success(f"✅ Spreadsheet ready: {spreadsheet_id}")
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("❌ Please enter your service account JSON")
        
        with st.expander("ℹ️ How to get Service Account JSON"):
            st.markdown("""
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing one
            3. Enable **Google Drive API** and **Google Sheets API**
            4. Create a **Service Account** under IAM & Admin
            5. Generate and download the JSON key
            6. Copy and paste the JSON content above
            7. (Optional) Share your Drive folder with the service account email
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
        items_per_page = st.slider(
            "Library items per page",
            12, 96, st.session_state.get('items_per_page', 12), 12
        )
        st.session_state.items_per_page = items_per_page
    
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
    - Advanced analytics
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
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=AI+Image+Studio+Pro", use_container_width=True)
        
        st.markdown("---")
        
        # Navigation
        selected_page = st.radio(
            "Navigation",
            ["🎨 Generate", "✏️ Edit", "📚 Library", "📋 Tasks", "📊 Analytics", "💾 Data", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
        st.metric("Images", st.session_state.stats['total_images'])
        st.metric("Success Rate", 
                  f"{(st.session_state.stats['successful_tasks'] / max(st.session_state.stats['total_tasks'], 1) * 100):.1f}%")
        
        st.markdown("---")
        
        # Authentication Status
        if st.session_state.get('authenticated'):
            st.success("✅ Google Drive Connected")
        else:
            st.warning("⚠️ Drive Not Connected")
        
        st.markdown("---")
        
        st.caption("v3.5 Ultimate Edition")
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
    elif selected_page == "📊 Analytics":
        display_analytics_page()
    elif selected_page == "💾 Data":
        display_data_page()
    elif selected_page == "⚙️ Settings":
        display_settings_page()
    
    # Footer
    st.markdown("---")
    
    st.success("🎉 Thank you for using AI Image Studio Pro!")
    
    # Stats summary in footer
    st.divider()
    st.subheader("📊 Your Session Stats")
    
    col_foot_stat1, col_foot_stat2, col_foot_stat3, col_foot_stat4 = st.columns(4)
    
    with col_foot_stat1:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    with col_foot_stat2:
        st.metric("Images Generated", st.session_state.stats['total_images'])
    with col_foot_stat3:
        st.metric("Uploaded", st.session_state.stats['uploaded_images'])
    with col_foot_stat4:
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
        st.caption("v3.5 Ultimate Edition")

if __name__ == "__main__":
    main()
