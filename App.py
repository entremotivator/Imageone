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
        'service': None, # Not actually used, but kept for potential future use
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
        'task_queue': [], # Not actively used, but kept for structure
        'active_tasks': [],
        'task_history': [],
        'completed_tasks': [], # Not actively used, but kept for structure
        'failed_tasks': [], # Not actively used, but kept for structure
        
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
        'tags': {}, # Key: image_id, Value: list of tags
        'collections': {}, # Not actively used, kept for future
        'comparison_list': [],
        'projects': {}, # Key: project_id, Value: project_data
        
        # UI State
        'selected_tab': 'Generate', # Not actively used, kept for structure
        'current_page': 1,
        'items_per_page': 12,
        'search_query': '',
        'filter_tag': 'All',
        'view_mode': 'grid',
        'theme': 'dark', # Default theme
        'selected_image_for_edit': None, # To store image selected from library for editing
        
        # Generation Settings
        'last_prompt': '',
        'last_model': 'black-forest-labs/flux-1.1-pro', # Default model
        'generation_presets': {}, # Not actively used
        'auto_upload_enabled': True,
        'prompt_templates': {}, # Not actively used
        'style_presets': {}, # Not actively used
        
        # Advanced Features
        'batch_mode': False, # Not actively used
        'batch_prompts': [], # Not actively used
        'comparison_mode': False, # Not actively used
        'analytics_period': 7, # Not actively used
        'workflows': {}, # Key: workflow_id, Value: workflow_data
        'scheduled_tasks': [], # List of scheduled task dicts
        'api_usage_limit': 1000, # Placeholder, not actively enforced
        'workflow_steps_count': 1, # For workflow creation UI
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
        st.session_state.service = credentials # Store credentials as 'service'
        
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
            folder_id = folders[0]['id']
            st.session_state.app_folder_id = folder_id
            return folder_id
        
        # Create new folder
        file_metadata = {
            'name': 'AI_Image_Editor_Pro',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = st.session_state.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        st.session_state.app_folder_id = folder_id
        return folder_id
        
    except Exception as e:
        st.error(f"Failed to create or find app folder: {str(e)}")
        return None

def list_gdrive_images(folder_id=None, force_refresh=False):
    """List all images in the Google Drive folder with caching and better error handling"""
    try:
        if not st.session_state.get('authenticated') or not st.session_state.get('drive_service'):
            return []
        
        # Check cache timing
        last_refresh = st.session_state.get('last_library_refresh')
        if not force_refresh and last_refresh:
            time_diff = (datetime.now() - last_refresh).total_seconds()
            if time_diff < 30:  # Cache for 30 seconds
                return st.session_state.gdrive_images
        
        folder_id = folder_id or st.session_state.get('app_folder_id')
        if not folder_id:
            # Try to create/get folder if not found
            folder_id = create_app_folder()
            if not folder_id:
                st.error("App folder not found or could not be created. Cannot list images.")
                return []
        
        # Query for image files with retry logic for SSL errors
        query = f"'{folder_id}' in parents and trashed=false and (mimeType contains 'image/')"
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                results = st.session_state.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name, webViewLink, size, createdTime, description, thumbnailLink)',
                    orderBy='createdTime desc',
                    pageSize=100
                ).execute()
                
                images = results.get('files', [])
                
                # Update session state
                st.session_state.gdrive_images = images
                st.session_state.last_library_refresh = datetime.now()
                
                return images
            
            except Exception as retry_error:
                retry_count += 1
                error_msg = str(retry_error).lower()
                
                # Check for SSL-related errors
                if 'ssl' in error_msg or 'decryption' in error_msg:
                    if retry_count < max_retries:
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        st.error(f"SSL connection error after {max_retries} attempts. Please check your internet connection and try again.")
                        return []
                else:
                    # Other errors, don't retry
                    raise retry_error
        
        return []
        
    except Exception as e:
        st.error(f"Failed to list images: {str(e)}")
        return []

def upload_to_gdrive(image_url: str, file_name: str, task_id: str = None):
    """Upload image to Google Drive from URL"""
    try:
        if not st.session_state.get('authenticated') or not st.session_state.get('drive_service'):
            return None, "Not authenticated with Google Drive"
        
        # Download image from URL
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return None, f"Failed to download image: HTTP {response.status_code}"
        
        image_bytes = io.BytesIO(response.content)
        
        # Ensure app folder exists
        if not st.session_state.get('app_folder_id'):
            create_app_folder()
            if not st.session_state.get('app_folder_id'): # Check again if folder creation failed
                return None, "App folder not found or could not be created"
        
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

def get_gdrive_image_bytes(file_id):
    """Get image bytes from Google Drive with caching"""
    try:
        # Check cache first
        if file_id in st.session_state.gdrive_images_cache:
            return st.session_state.gdrive_images_cache[file_id]
        
        if not st.session_state.get('authenticated') or not st.session_state.get('drive_service'):
            return None
        
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
        st.error(f"Failed to get image bytes for {file_id}: {str(e)}")
        return None

def display_gdrive_image(file_info, caption="", width=150):
    """Display an image from Google Drive with error handling"""
    try:
        if not st.session_state.drive_service or not file_info or not file_info.get('id'):
            st.warning("Unable to display image - missing file info or Drive service")
            return False
        
        image_bytes = get_gdrive_image_bytes(file_info['id'])
        if image_bytes:
            try:
                st.image(image_bytes, caption=caption, use_container_width=True, width=width)
                return True
            except Exception as img_err:
                st.error(f"Image display error: {str(img_err)}")
                return False
        else:
            st.warning("Image preview unavailable")
            return False
    except Exception as e:
        st.error(f"Display error: {str(e)}")
        return False

def delete_gdrive_file(file_id):
    """Delete a file from Google Drive"""
    try:
        if not st.session_state.get('authenticated') or not st.session_state.get('drive_service'):
            return False, "Not authenticated with Google Drive"

        st.session_state.drive_service.files().delete(fileId=file_id).execute()
        
        # Clear from cache
        if file_id in st.session_state.gdrive_images_cache:
            del st.session_state.gdrive_images_cache[file_id]
        
        # Remove from session state list and refresh (list_gdrive_images handles refresh logic)
        st.session_state.gdrive_images = [img for img in st.session_state.gdrive_images if img['id'] != file_id]
        st.session_state.last_library_refresh = None # Force refresh next time
        
        return True, "File deleted successfully"
    except Exception as e:
        return False, f"Delete failed: {str(e)}"

# ============================================================================
# GOOGLE SHEETS FUNCTIONS
# ============================================================================

def create_or_get_spreadsheet():
    """Create or get the tracking spreadsheet"""
    try:
        if not st.session_state.get('authenticated') or not st.session_state.get('drive_service') or not st.session_state.get('sheets_service'):
            return None
            
        # Search for existing spreadsheet
        query = "name='AI_Image_Editor_Pro_Log' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        results = st.session_state.drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        sheets = results.get('files', [])
        
        if sheets:
            spreadsheet_id = sheets[0]['id']
            st.session_state.spreadsheet_id = spreadsheet_id
            return spreadsheet_id
        
        # Create new spreadsheet
        spreadsheet_body = {
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
            body=spreadsheet_body,
            fields='spreadsheetId, spreadsheetUrl'
        ).execute()
        
        spreadsheet_id = sheet.get('spreadsheetId')
        
        # Move to app folder
        if st.session_state.get('app_folder_id'):
            # Ensure the spreadsheet is shared with the service account if it's not the owner
            # This part might need more robust handling depending on the service account setup
            try:
                st.session_state.drive_service.files().update(
                    fileId=spreadsheet_id,
                    addParents=st.session_state.app_folder_id,
                    fields='id, parents'
                ).execute()
            except Exception as move_err:
                st.warning(f"Could not move spreadsheet to app folder: {move_err}")

        st.session_state.spreadsheet_id = spreadsheet_id
        return spreadsheet_id
        
    except Exception as e:
        st.error(f"Failed to create or find spreadsheet: {str(e)}")
        return None

def log_to_sheets(model: str, prompt: str, image_url: str, drive_link: str = "", 
                  task_id: str = "", status: str = "success", tags: str = "", file_id: str = ""):
    """Log generation data to Google Sheets"""
    try:
        spreadsheet_id = st.session_state.get('spreadsheet_id')
        if not spreadsheet_id:
            spreadsheet_id = create_or_get_spreadsheet()
            if not spreadsheet_id:
                st.error("Spreadsheet not available, cannot log to sheets.")
                return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        values = [[timestamp, model, prompt, image_url, drive_link, task_id, status, tags, file_id]]
        body = {'values': values}
        
        st.session_state.sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Generation_Log!A:I',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Failed to log to sheets: {str(e)}")
        return False

def get_sheets_data():
    """Get all data from Google Sheets Generation_Log sheet"""
    try:
        spreadsheet_id = st.session_state.get('spreadsheet_id')
        if not spreadsheet_id:
            st.warning("Spreadsheet ID not found. Cannot retrieve data.")
            return []
        
        result = st.session_state.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Generation_Log!A:I' # Assuming A:I covers all columns
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        # Ensure all rows have the expected number of columns, padding with empty strings if necessary
        # This prevents errors if some rows are shorter due to incomplete logging or manual edits.
        num_columns = len(values[0]) if values else 0
        processed_values = []
        for row in values:
            padded_row = row + [''] * (num_columns - len(row))
            processed_values.append(padded_row)
            
        return processed_values[1:] if len(processed_values) > 1 else []  # Skip header row
        
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
    
    # Add to the global csv_data list in session state
    st.session_state.csv_data.append(entry)

def export_to_csv():
    """Export CSV data to downloadable file"""
    if not st.session_state.csv_data:
        return None
    
    output = io.StringIO()
    # Ensure fieldnames cover all possible keys that might be in csv_data
    fieldnames = ['timestamp', 'model', 'prompt', 'image_url', 'drive_link', 'task_id', 'status', 'tags', 'file_id']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(st.session_state.csv_data)
    
    return output.getvalue()

def load_csv_file(uploaded_file):
    """Load CSV file into session state's csv_data"""
    try:
        content = uploaded_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        loaded_data = list(reader)
        # Append loaded data to existing session state data
        st.session_state.csv_data.extend(loaded_data)
        
        return True, len(loaded_data) # Return success status and number of entries loaded
    except Exception as e:
        return False, str(e) # Return failure status and error message

# ============================================================================
# KIE.AI API FUNCTIONS
# ============================================================================

def create_task(api_key, model, input_params, callback_url=None):
    """Create a new task using KIE.ai API with updated endpoints"""
    
    # Determine which API endpoint to use based on model
    if 'gpt-4o' in model.lower() or 'gpt4o' in model.lower():
        # Use GPT-4o Image API
        url = "https://api.kie.ai/api/v1/gpt4o-image/generate"
        
        # Transform parameters for GPT-4o API format
        payload = {
            "prompt": input_params.get("prompt", ""),
            "size": input_params.get("aspect_ratio", "1:1"),  # Map aspect_ratio to size
            "quality": input_params.get("image_resolution", "standard"),  # hd or standard
            "style": input_params.get("style", "vivid"),  # vivid or natural
            "n": input_params.get("max_images", 1)
        }
    elif 'flux' in model.lower():
        # Use Flux Kontext API
        url = "https://api.kie.ai/api/v1/flux/kontext/generate"
        
        # Transform parameters for Flux API format
        payload = {
            "prompt": input_params.get("prompt", ""),
            "enableTranslation": input_params.get("enable_translation", True),
            "aspectRatio": input_params.get("aspect_ratio", "16:9"),
            "outputFormat": input_params.get("output_format", "jpeg"),
            "promptUpsampling": input_params.get("prompt_upsampling", False),
            "model": model.split('/')[-1] if '/' in model else model
        }
        
        # Add optional seed if provided
        if input_params.get("seed") and input_params["seed"] > 0:
            payload["seed"] = input_params["seed"]
            
        # Add optional safety_tolerance if provided
        if input_params.get("safety_tolerance"):
            payload["safetyTolerance"] = input_params["safety_tolerance"]
    elif 'seedream' in model.lower():
        # Use Seedream API for editing
        url = "https://api.kie.ai/api/v1/seedream/edit" # Example endpoint for Seedream
        payload = {
            "prompt": input_params.get("prompt", ""),
            "image_urls": input_params.get("image_urls", []), # Should be a list of URLs or data URIs
            "image_size": input_params.get("image_size", "square_hd"), # e.g., "square", "square_hd", "portrait_4_3" etc.
            "max_images": input_params.get("max_images", 1),
            "output_format": input_params.get("output_format", "png"),
            "guidance_scale": input_params.get("guidance_scale", 7.5)
        }
        # Seedream specific parameters might be different, this is a hypothetical mapping
        # Ensure input_params['image_urls'] is correctly handled when calling this
    elif 'gpt-4o/image' in model.lower() and 'edit' in input_params.get("prompt", "").lower():
        # Special handling for GPT-4o editing if it supports editing via prompt
        # Assuming it follows a similar structure to general generation, but with editing focus
        url = "https://api.kie.ai/api/v1/gpt4o-image/edit" # Hypothetical edit endpoint
        payload = {
            "prompt": input_params.get("prompt", ""),
            "image_url": input_params.get("image_url"), # For editing, expects a single image URL or data URI
            "aspect_ratio": input_params.get("aspect_ratio", "1:1"),
            "guidance_scale": input_params.get("guidance_scale", 7.5),
            "output_format": input_params.get("output_format", "png")
        }
    else:
        # Fallback to Flux API for unknown models or default behavior
        url = "https://api.kie.ai/api/v1/flux/kontext/generate"
        payload = {
            "prompt": input_params.get("prompt", ""),
            "enableTranslation": True,
            "aspectRatio": input_params.get("aspect_ratio", "16:9"),
            "outputFormat": "jpeg",
            "model": "flux-kontext-pro"
        }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result_data = response.json()
            
            # Create a pseudo-task structure for compatibility
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            task_data = {
                'id': task_id,
                'status': 'succeeded',
                'output': result_data,
                'model': model,
                'created_at': datetime.now().isoformat()
            }
            
            # Update stats
            st.session_state.stats['total_tasks'] += 1
            st.session_state.stats['total_api_calls'] += 1
            st.session_state.stats['successful_tasks'] += 1
            
            # Extract base model name for stats
            model_name_base = model.split('/')[-1] if '/' in model else model
            st.session_state.stats['models_used'][model_name_base] = st.session_state.stats['models_used'].get(model_name_base, 0) + 1
            
            # Track daily usage
            today = datetime.now().strftime("%Y-%m-%d")
            st.session_state.stats['daily_usage'][today] = st.session_state.stats['daily_usage'].get(today, 0) + 1
            
            # Track hourly usage
            now = datetime.now()
            st.session_state.stats['hourly_usage'][now.strftime("%Y-%m-%d %H")] = st.session_state.stats['hourly_usage'].get(now.strftime("%Y-%m-%d %H"), 0) + 1

            # Basic cost tracking
            cost_per_task = 0.04 # Placeholder, should be dynamically determined
            st.session_state.stats['cost_tracking'][model_name_base] = st.session_state.stats['cost_tracking'].get(model_name_base, 0) + cost_per_task
            
            return task_data, None
        else:
            # Log API error for debugging
            try:
                error_details = response.json()
                error_message = f"API Error: {response.status_code} - {error_details.get('error', {}).get('message', response.text)}"
            except json.JSONDecodeError:
                error_message = f"API Error: {response.status_code} - {response.text}"
            
            st.session_state.stats['failed_tasks'] += 1
            
            return None, error_message
            
    except requests.exceptions.RequestException as e:
        st.session_state.stats['failed_tasks'] += 1
        return None, f"Request failed: {str(e)}"
    except Exception as e:
        st.session_state.stats['failed_tasks'] += 1
        return None, f"An unexpected error occurred: {str(e)}"


def check_task_status(api_key, task_id):
    """Check the status of a task - with new API, tasks complete immediately"""
    # With the new API, tasks are synchronous, so we don't need to poll
    # This function is kept for backwards compatibility
    # Return a pre-completed status
    return {
        'id': task_id,
        'status': 'succeeded',
        'message': 'Task completed (synchronous API)'
    }, None


def poll_task_until_complete(api_key, task_id, max_attempts=60, delay=2):
    """Poll task status until completion - simplified for synchronous API"""
    # With new API endpoints, tasks complete immediately
    # Just return success status
    status_text = st.empty()
    status_text.text("✅ Task completed successfully!")
    time.sleep(0.5)
    status_text.empty()
    
    return {
        'id': task_id,
        'status': 'succeeded'
    }, None


def save_and_upload_results(task_id, model, prompt, result_urls, tags=""):
    """Save results and automatically upload to Drive if enabled and authenticated"""
    uploaded_files_info = [] # Stores info about successfully uploaded files

    for idx, image_url in enumerate(result_urls):
        try:
            # Generate filename
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Extract base model name for filename
            model_name_base = model.split('/')[-1] if '/' in model else model
            file_name = f"{model_name_base}_{timestamp_str}_{idx+1}.png"
            
            drive_link = ""
            file_id = ""
            
            # Check if auto-upload is enabled and Google Drive is authenticated
            if st.session_state.get('auto_upload_enabled', False) and \
               st.session_state.get('authenticated') and \
               st.session_state.get('drive_service'):
                
                file_info, error = upload_to_gdrive(image_url, file_name, task_id)
                
                if file_info:
                    drive_link = file_info.get('webViewLink', '')
                    file_id = file_info.get('id', '')
                    uploaded_files_info.append(file_info) # Store info for display later
                    
                    # Log to Sheets if logging is successful
                    log_to_sheets(model, prompt, image_url, drive_link, task_id, "success", tags, file_id)
                else:
                    st.warning(f"Failed to upload image {idx+1} to Google Drive: {error}")
                    # Log to sheets even if Drive upload fails, but mark drive link as N/A
                    log_to_sheets(model, prompt, image_url, drive_link="", task_id=task_id, status="success_no_drive", tags=tags, file_id="")
            else:
                # If auto-upload is off or not authenticated, just add to CSV and log (without Drive link)
                log_to_sheets(model, prompt, image_url, drive_link="", task_id=task_id, status="success_local", tags=tags, file_id="")
            
            # Always add to session state's CSV data
            add_to_csv_data(model, prompt, image_url, drive_link, task_id, "success", tags, file_id)
            
        except Exception as e:
            st.error(f"Failed to process image {idx+1} for saving/uploading: {str(e)}")
            # Log as failed if any part of processing fails
            log_to_sheets(model, prompt, image_url, task_id=task_id, status="failed_processing", tags=tags)
    
    # Force refresh library to show new images immediately if any were uploaded
    if uploaded_files_info:
        list_gdrive_images(force_refresh=True)
    
    return uploaded_files_info # Return list of uploaded file info dictionaries

# ============================================================================
# TAG AND COLLECTION MANAGEMENT
# ============================================================================

def add_tag_to_image(image_id, tag):
    """Add a tag to an image in session state"""
    if not tag: return # Do nothing if tag is empty
    
    if image_id not in st.session_state.tags:
        st.session_state.tags[image_id] = []
    
    tag = tag.strip().lower() # Normalize tag
    if tag and tag not in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].append(tag)
        # Update global tag usage stats
        st.session_state.stats['tags_used'][tag] = st.session_state.stats['tags_used'].get(tag, 0) + 1
        # Update session state to reflect change (important for UI updates)
        st.session_state.tags = st.session_state.tags # This reassign triggers rerun if needed

def remove_tag_from_image(image_id, tag):
    """Remove a tag from an image in session state"""
    if image_id in st.session_state.tags and tag in st.session_state.tags[image_id]:
        st.session_state.tags[image_id].remove(tag)
        # Optional: decrement tag usage count if needed for stats, but might be complex if not tracking precisely
        # For simplicity, we'll just remove it from the image's list.

def get_image_tags(image_id):
    """Get all tags for an image from session state"""
    return st.session_state.tags.get(image_id, [])

def add_to_comparison(image_data):
    """Add image data to the comparison list in session state"""
    # Ensure image_data is a dictionary with at least an 'id' key
    if not isinstance(image_data, dict) or 'id' not in image_data:
        st.warning("Invalid image data provided for comparison.")
        return False
        
    # Limit comparison list size
    if len(st.session_state.comparison_list) >= 4:
        st.warning("Comparison list is full (max 4 images). Remove an image to add a new one.")
        return False
    
    # Check if image is already in the list (based on ID)
    if any(img.get('id') == image_data['id'] for img in st.session_state.comparison_list):
        st.info("Image is already in the comparison list.")
        return False
        
    st.session_state.comparison_list.append(image_data)
    st.session_state.comparison_list = st.session_state.comparison_list # Reassign to trigger potential reruns/updates
    return True

def remove_from_comparison(image_id):
    """Remove image from comparison list by its ID"""
    initial_length = len(st.session_state.comparison_list)
    st.session_state.comparison_list = [
        img for img in st.session_state.comparison_list 
        if img.get('id') != image_id
    ]
    if len(st.session_state.comparison_list) < initial_length:
        st.session_state.comparison_list = st.session_state.comparison_list # Reassign to trigger updates

# ============================================================================
# PAGE: TEXT-TO-IMAGE GENERATION
# ============================================================================

def display_generate_page():
    """Display the text-to-image generation page"""
    st.title("🎨 AI Image Generation")
    st.markdown("Create stunning images using advanced AI models")
    
    # API Key Input
    # Use st.secrets for API keys if available, otherwise use text_input
    # Set a default value from secrets if available
    default_api_key = st.secrets.get("KIE_API_KEY", "") if hasattr(st, 'secrets') and st.secrets else ""
    
    api_key = st.text_input(
        "🔑 KIE.ai API Key",
        type="password",
        value=default_api_key,
        help="Enter your KIE.ai API key from https://kie.ai"
    )
    
    if not api_key:
        st.markdown("""
        <div class="info-box">
            <strong>🔑 API Key Required</strong><br>
            Please enter your KIE.ai API key to start generating images.
            Get your key from <a href="https://kie.ai" target="_blank">kie.ai</a>
        </div>
        """, unsafe_allow_html=True)
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
        # Define model options with user-friendly names and API identifiers
        model_options_dict = {
            "FLUX 1.1 Pro (Fast, High Quality)": "black-forest-labs/flux-1.1-pro",
            "FLUX Pro (Best Quality)": "black-forest-labs/flux-pro",
            "FLUX Dev (Balanced)": "black-forest-labs/flux-dev",
            "FLUX Schnell (Speed Focused)": "black-forest-labs/flux-schnell",
            "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
            "Stable Diffusion 3.5 Large Turbo": "stabilityai/stable-diffusion-3.5-large-turbo",
            "Stable Diffusion 3.5 Medium": "stabilityai/stable-diffusion-3.5-medium",
            "Playground v3": "playground/playground-v3",
            "Recraft V3": "recraft-ai/recraft-v3",
            "GPT-4o Image": "gpt-4o/image", # Added GPT-4o Image model
        }
        
        selected_model_name = st.selectbox(
            "🤖 Select AI Model",
            options=list(model_options_dict.keys()),
            index=list(model_options_dict.keys()).index(next((k for k, v in model_options_dict.items() if v == st.session_state.last_model), list(model_options_dict.keys())[0])), # Preserve last model if possible
            help="Different models offer different styles, speeds, and quality levels."
        )
        
        selected_model = model_options_dict[selected_model_name]
        st.session_state.last_model = selected_model # Update session state with the chosen model
    
    with col2:
        # Display model info in a metric card
        st.metric("Model Type", "Text-to-Image")
        st.caption(f"Using: `{selected_model.split('/')[-1]}`") # Show the API model identifier
    
    # Prompt Input
    st.markdown("### ✍️ Describe Your Image")
    
    # Prompt presets for quick selection
    preset_prompts = {
        "Custom": "",
        "Photorealistic Portrait": "A photorealistic portrait of a young woman, professional studio lighting, 8k resolution, highly detailed skin texture, sharp focus",
        "Fantasy Landscape": "A breathtaking fantasy landscape with snow-capped mountains, a glowing magical waterfall, and an ethereal sky, concept art style, vibrant colors",
        "Cyberpunk City Night": "A futuristic cyberpunk city at night, neon signs reflecting on rain-soaked streets, flying vehicles, dramatic atmosphere, cinematic lighting",
        "Abstract Geometric": "Abstract geometric art with overlapping shapes and vibrant gradients, modern minimalist style, high contrast, smooth textures",
        "Product Photography": "Professional product photography of a sleek smartphone on a clean white background, studio lighting, commercial quality, sharp focus",
        "Whimsical Cartoon": "A whimsical cartoon scene of a cat wearing a wizard hat casting a spell, playful style, bright colors",
    }
    
    col_preset1, col_preset2 = st.columns([1, 3])
    
    with col_preset1:
        selected_preset = st.selectbox("Quick Preset", list(preset_prompts.keys()))
    
    with col_preset2:
        # Use preset prompt if selected and not "Custom", otherwise use last prompt or placeholder
        default_prompt = preset_prompts.get(selected_preset, "") if selected_preset != "Custom" else st.session_state.get('last_prompt', '')
        
        prompt = st.text_area(
            "Image Prompt",
            value=default_prompt,
            height=120,
            placeholder="Example: A serene mountain landscape at sunset with vibrant colors...",
            help="Be specific and descriptive for best results. Use detailed descriptions for better image quality."
        )
    
    st.session_state.last_prompt = prompt # Save the current prompt to session state
    
    # Advanced Settings Expander
    with st.expander("⚙️ Advanced Settings", expanded=False):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)", "4:3 (Landscape)", "3:4 (Portrait)"],
                help="Select the desired aspect ratio for your image."
            )
            
            # Map aspect ratios to known image sizes supported by models
            # Note: GPT-4o expects 'size' parameter in the format 'W:H' or specific keywords
            # Adjusting the mapping for newer APIs
            aspect_to_api_param = {
                "1:1 (Square)": "1:1",
                "16:9 (Landscape)": "16:9",
                "9:16 (Portrait)": "9:16",
                "4:3 (Landscape)": "4:3",
                "3:4 (Portrait)": "3:4",
            }
            # Store the raw aspect ratio string and potentially a mapped value for different APIs
            selected_aspect_ratio_raw = aspect_to_api_param.get(aspect_ratio, "1:1") # Store the string like "16:9"
            
            # Other potential parameters for different models
            image_resolution = st.selectbox(
                "Image Resolution",
                ["Standard", "HD"], # For GPT-4o
                index=0, # Default to Standard
                help="Choose the desired resolution for the generated image."
            )
            
            style = st.selectbox(
                "Style",
                ["Vivid", "Natural"], # For GPT-4o
                index=0,
                help="Choose the artistic style for the generated image."
            )
            
            # Mapping for models like Flux that might use different keys
            input_params_map = {
                "prompt": prompt.strip(),
                "aspect_ratio": selected_aspect_ratio_raw,
                "image_resolution": image_resolution.lower(), # e.g. "hd"
                "style": style.lower(), # e.g. "vivid"
                "max_images": 1, # Default to 1, adjusted later by slider
                "enable_translation": st.checkbox("Enable Translation", value=True, key="enable_translation_gen"),
                "output_format": st.selectbox("Output Format", ["jpeg", "png"], key="output_format_gen"),
                "prompt_upsampling": st.checkbox("Enable Prompt Upsampling", value=False, key="prompt_upsampling_gen"),
                "safety_tolerance": st.slider("Safety Tolerance", 0.0, 1.0, 0.0, 0.1, help="Adjust safety filter sensitivity (lower is more permissive).", key="safety_tolerance_gen")
            }

        with col_adv2:
            num_images = st.slider(
                "Number of Images",
                1, 4, 1, # Min, Max, Default
                help="How many variations of the image to generate."
            )
            input_params_map["max_images"] = num_images # Update the map
        
        with col_adv3:
            seed = st.number_input(
                "Seed (0 for random)",
                min_value=0,
                max_value=999999, # Arbitrary max for seed value
                value=0, # Default to random seed
                step=1,
                help="Use a specific seed for reproducible results. 0 generates a random seed."
            )
            input_params_map["seed"] = seed # Update the map
        
        # Tags input within advanced settings
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., landscape, sunset, mountains",
            help="Add tags to help organize and search your images later."
        )
    
    # Auto-upload toggle
    auto_upload = st.checkbox(
        "🔄 Auto-upload to Google Drive",
        value=st.session_state.get('auto_upload_enabled', True),
        help="If checked and authenticated with Google Drive, generated images will be automatically uploaded to your Google Drive."
    )
    st.session_state.auto_upload_enabled = auto_upload # Update session state immediately
    
    st.divider() # Separator before action buttons
    
    # Generation and Action Buttons
    col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
    
    with col_gen1:
        generate_btn = st.button("🚀 Generate Image", type="primary", use_container_width=True)
    
    with col_gen2:
        if st.button("💾 Save Prompt", use_container_width=True):
            if prompt.strip():
                # Initialize saved_prompts list if it doesn't exist
                if 'saved_prompts' not in st.session_state:
                    st.session_state.saved_prompts = []
                
                # Add new prompt with timestamp and model info
                st.session_state.saved_prompts.append({
                    'prompt': prompt.strip(),
                    'model': selected_model,
                    'model_name': selected_model_name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Prompt saved!")
            else:
                st.warning("No prompt to save.")
    
    with col_gen3:
        if st.button("🗑️ Clear Prompt", use_container_width=True):
            st.session_state.last_prompt = "" # Clear the last prompt
            st.session_state.selected_preset = "Custom" # Reset preset selection
            st.rerun() # Rerun to update the UI with cleared prompt
    
    # Generation Logic - Executed when generate_btn is clicked
    if generate_btn:
        if not prompt.strip():
            st.error("❌ Please enter a prompt to generate an image.")
            return # Stop execution if prompt is empty
        
        if not api_key:
            st.error("❌ Please enter your KIE.ai API key.")
            return # Stop execution if API key is missing
            
        # Start generation process
        with st.spinner("🎨 Creating your masterpiece..."):
            # Prepare input parameters for the KIE.ai API
            # Use the parameters from input_params_map, potentially overriding defaults
            current_input_params = {
                "prompt": prompt.strip(),
                "aspect_ratio": selected_aspect_ratio_raw, # Pass raw aspect ratio string
                "image_resolution": image_resolution.lower(),
                "style": style.lower(),
                "max_images": num_images,
                "seed": seed,
                "enable_translation": st.session_state.get("enable_translation_gen", True),
                "output_format": st.session_state.get("output_format_gen", "jpeg"),
                "prompt_upsampling": st.session_state.get("prompt_upsampling_gen", False),
                "safety_tolerance": st.session_state.get("safety_tolerance_gen", 0.0)
            }
            
            # Create the task using the KIE.ai API
            task_data, error = create_task(api_key, selected_model, current_input_params)
            
            if error:
                st.error(f"❌ Generation failed: {error}")
                return # Stop if task creation failed
            
            # If task creation was successful
            # Note: With the new API, task_data is directly the output, not a task object with status
            # We need to adapt the flow as the new API is synchronous
            
            # The create_task function now returns a pseudo-task_data with status 'succeeded'
            # and output containing the images directly.
            
            if task_data and task_data.get('status') == 'succeeded':
                result_urls = task_data.get('output', {}).get('images', []) # Directly access images from output
                
                if not result_urls:
                    st.error("❌ No images were generated by the model.")
                    return # Stop execution if no images are returned
                
                st.success(f"🎉 Generated {len(result_urls)} image(s)!")
                
                # Log the task and save/upload results
                task_id = task_data.get('id', f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}") # Use pseudo-id
                
                # Add to active tasks and history for monitoring (even if synchronous)
                task_info = {
                    'id': task_id,
                    'model': selected_model,
                    'model_name': selected_model_name, # Store user-friendly name too
                    'prompt': prompt.strip(),
                    'status': 'completed', # Initial status is completed
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'tags': tags_input.strip(), # Store tags
                    'result_urls': result_urls # Store URLs in task info
                }
                st.session_state.task_history.append(task_info)
                st.session_state.completed_tasks.append(task_info) # Add to completed list
                
                # Save results (to CSV) and upload to Google Drive if enabled
                uploaded_files_metadata = save_and_upload_results(
                    task_id, selected_model, prompt.strip(), result_urls, tags_input.strip()
                )
                
                # Display the generated images
                st.markdown("### 🖼️ Generated Images")
                
                # Use columns for displaying images, adjust number based on how many were generated
                num_cols = min(len(result_urls), 4) # Max 4 columns for images
                cols = st.columns(num_cols)
                
                for idx, image_url in enumerate(result_urls):
                    with cols[idx % num_cols]: # Distribute images across columns
                        st.image(image_url, caption=f"Image {idx + 1}", use_container_width=True)
                        
                        # Provide a download button for each image
                        try:
                            # Fetch image content for download button
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                st.download_button(
                                    label="💾 Download",
                                    data=img_response.content,
                                    file_name=f"generated_{selected_model.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx+1}.png",
                                    mime="image/png",
                                    key=f"download_{task_id}_{idx}" # Unique key for each button
                                )
                        except Exception as e:
                            st.error(f"Download button failed: {e}")
                
                # Provide feedback on Google Drive upload status
                if uploaded_files_metadata:
                    st.success(f"✅ {len(uploaded_files_metadata)} image(s) successfully uploaded to Google Drive!")
                    
                    # Display Drive links if upload was successful
                    with st.expander("📁 View Drive Links", expanded=False):
                        for file_info in uploaded_files_metadata:
                            st.markdown(f"- [{file_info.get('name', 'Untitled')}]({file_info.get('webViewLink', '#')})")
                elif st.session_state.get('auto_upload_enabled', False):
                    st.warning("ℹ️ Auto-upload was enabled, but no images were uploaded. Check previous messages for errors.")
            
            else: # If task_data is None or status is not succeeded
                st.error(f"❌ Generation failed: {error or 'Unknown error'}")

# ============================================================================
# PAGE: IMAGE EDITING (SEEDREAM)
# ============================================================================

def display_edit_page():
    """Display the image editing page with proper validation"""
    st.title("✏️ AI Image Editing")
    st.markdown("Edit and transform existing images using AI")
    
    # API Key Input
    default_api_key_edit = st.secrets.get("KIE_API_KEY", "") if hasattr(st, 'secrets') and st.secrets else ""
    api_key = st.text_input(
        "🔑 KIE.ai API Key",
        type="password",
        key="edit_api_key",
        value=default_api_key_edit,
    )
    
    if not api_key:
        st.markdown("""
        <div class="info-box">
            <strong>🔑 API Key Required</strong><br>
            Please enter your KIE.ai API key to start editing images.
            Get your key from <a href="https://kie.ai" target="_blank">kie.ai</a>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.divider()
    
    # Model Selection for Editing
    edit_model_options = {
        "Seedream v4 (Edit)": "bytedance/seedream-v4-edit",
        "GPT-4o Image (Edit)": "gpt-4o/image",
    }
    
    selected_edit_model_name = st.selectbox(
        "🤖 Select Editing Model",
        options=list(edit_model_options.keys()),
        help="Choose an AI model optimized for image editing tasks."
    )
    
    selected_edit_model = edit_model_options[selected_edit_model_name]
    
    # Image Source Selection UI
    st.markdown("### 📸 Select Source Image")
    
    # Check if an image was selected from the library
    if st.session_state.get('selected_image_for_edit'):
        selected_img = st.session_state.selected_image_for_edit
        st.success(f"✅ Using selected image: **{selected_img.get('name', 'Untitled')}**")
        
        # Display the selected image
        with st.expander("Preview Selected Image", expanded=True):
            display_gdrive_image(selected_img, caption=selected_img.get('name', ''))
        
        if st.button("🔄 Choose Different Image"):
            st.session_state.selected_image_for_edit = None
            st.rerun()
        
        # Use the selected image URL
        source_image_url = f"https://drive.google.com/uc?export=view&id={selected_img['id']}"
        has_valid_source = True
    
    else:
        # Image source selection radio buttons
        image_source = st.radio(
            "Choose image source:",
            ["Upload from Computer", "Select from Google Drive Library", "Enter Image URL"],
            horizontal=True,
            key="edit_image_source"
        )
        
        source_image_url = None
        has_valid_source = False
        
        # Handle image upload from computer
        if image_source == "Upload from Computer":
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=['png', 'jpg', 'jpeg', 'webp'],
                help="Upload the image you want to edit",
                key="edit_upload_file"
            )
            
            if uploaded_file:
                try:
                    image = PILImage.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", width=300)
                    
                    # Convert image to base64 for API
                    buffered = io.BytesIO()
                    # Ensure image is in RGB format if needed for certain formats (e.g., PNG)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    source_image_url = f"data:image/png;base64,{img_str}"
                    has_valid_source = True
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
        
        # Handle selection from Google Drive library
        elif image_source == "Select from Google Drive Library":
            if not st.session_state.get('authenticated'):
                st.warning("⚠️ Please authenticate with Google Drive first.")
            else:
                images = list_gdrive_images()
                if images:
                    # Create a dictionary of image options for the selectbox
                    img_options = {img.get('name', f"Image ID: {img.get('id', '')[:8]}"): img for img in images}
                    selected_name = st.selectbox("Select Image", list(img_options.keys()), key="edit_drive_selector")
                    
                    if selected_name:
                        selected_img = img_options[selected_name]
                        display_gdrive_image(selected_img, caption="Selected Image")
                        # For editing APIs, we often need the image data directly.
                        # Google Drive direct download link might not work for all APIs,
                        # so convert to base64 if possible.
                        try:
                            img_bytes = get_gdrive_image_bytes(selected_img['id'])
                            if img_bytes:
                                buffered = io.BytesIO(img_bytes)
                                img_pil = PILImage.open(buffered)
                                if img_pil.mode != 'RGB':
                                    img_pil = img_pil.convert('RGB')
                                img_pil.save(buffered, format="PNG")
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                source_image_url = f"data:image/png;base64,{img_str}"
                                has_valid_source = True
                            else:
                                st.error("Could not retrieve image data from Drive for editing.")
                        except Exception as e:
                            st.error(f"Error preparing image from Drive for editing: {str(e)}")
                else:
                    st.info("No images in library. Generate some first!")
        
        # Handle manual URL input
        elif image_source == "Enter Image URL":
            url_input = st.text_input(
                "Image URL",
                placeholder="https://example.com/image.jpg",
                help="Enter a publicly accessible image URL"
            )
            
            if url_input:
                try:
                    # Validate URL by trying to fetch it
                    response = requests.head(url_input, timeout=5)
                    if response.status_code == 200:
                        st.image(url_input, caption="Image from URL", width=300)
                        source_image_url = url_input
                        has_valid_source = True
                    else:
                        st.error(f"Unable to access image URL (Status: {response.status_code})")
                except Exception as e:
                    st.error(f"Invalid URL: {str(e)}")
    
    st.divider()
    
    # Editing form - only show if we have a valid source
    if not has_valid_source:
        st.markdown("""
        <div class="warning-box">
            <strong>❌ No Source Image Selected</strong><br>
            Please select or upload a source image before applying edits.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Editing parameters
    st.markdown("### ✍️ Describe Your Edit")
    
    edit_prompt = st.text_area(
        "Edit Instructions",
        placeholder="Describe how you want to transform the image...",
        height=100,
        help="Be specific about the changes you want to make"
    )
    
    # Advanced settings in expander
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            if 'seedream' in selected_edit_model.lower():
                image_size = st.selectbox(
                    "Image Size",
                    ["square", "square_hd", "portrait_4_3", "landscape_4_3", "landscape_16_9"],
                    index=1,
                    help="Select the desired output resolution and aspect ratio for Seedream."
                )
                max_images = st.slider("Number of Variations", 1, 4, 1)
            else: # Assuming other models like GPT-4o might use different parameters
                aspect_ratio = st.selectbox(
                    "Aspect Ratio",
                    ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    index=0,
                    help="Select the desired aspect ratio for the output image."
                )
        
        with col2:
            guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5,
                                        help="Controls how strongly the edit prompt influences the output. Higher values mean more adherence to the prompt.")
            output_format = st.selectbox("Output Format", ["png", "jpeg", "webp"])
    
    # Generate button
    if st.button("🎨 Apply Edits", type="primary", use_container_width=True):
        if not edit_prompt:
            st.error("Please provide edit instructions!")
            return
        
        # Prepare parameters based on model
        input_params = {
            "prompt": edit_prompt,
            "max_images": 1 # Typically editing produces one output
        }
        
        if 'seedream' in selected_edit_model.lower():
            input_params.update({
                "image_urls": [source_image_url], # Seedream expects list for image_urls
                "image_size": image_size,
                "max_images": max_images,
                "output_format": output_format
            })
        else: # Assuming GPT-4o or similar models
            input_params.update({
                "image_url": source_image_url, # Other models might expect single URL
                "aspect_ratio": aspect_ratio,
                "guidance_scale": guidance_scale,
                "output_format": output_format
            })
        
        with st.spinner("🎨 Editing your image..."):
            task_data, error = create_task(api_key, selected_edit_model, input_params)
        
        if error:
            st.error(f"❌ Edit failed: {error}")
        elif task_data and task_data.get('status') == 'succeeded':
            st.success("✅ Edit completed successfully!")
            
            # Extract and display results
            output = task_data.get('output', {})
            image_urls = []
            
            # Handle different response formats from KIE.ai API
            if isinstance(output, dict):
                if 'images' in output: # Common format for generation
                    image_urls = output['images']
                elif 'data' in output and isinstance(output['data'], list): # Another possible format
                    image_urls = [item.get('url') for item in output['data'] if item.get('url')]
                elif 'url' in output: # Direct URL in output
                    image_urls = [output['url']]
                elif 'results' in output and isinstance(output['results'], list): # For models returning results array
                    image_urls = [res.get('url') for res in output['results'] if res.get('url')]
            
            if image_urls:
                st.markdown("### 🎨 Edited Results")
                cols = st.columns(min(len(image_urls), 3))
                for idx, url in enumerate(image_urls):
                    with cols[idx % 3]:
                        st.image(url, use_container_width=True)
                        
                        # Download button
                        try:
                            response = requests.get(url, timeout=20) # Add timeout for safety
                            if response.status_code == 200:
                                st.download_button(
                                    "💾 Download",
                                    data=response.content,
                                    file_name=f"edited_{idx+1}.{output_format}",
                                    mime=f"image/{output_format}",
                                    key=f"download_edit_{idx}"
                                )
                            else:
                                st.error(f"Failed to download image {idx+1}: HTTP {response.status_code}")
                        except Exception as e:
                            st.error(f"Failed to create download button for image {idx+1}: {e}")
                
                # Auto-upload to Drive if enabled and authenticated
                if st.session_state.get('authenticated') and st.session_state.get('auto_upload_enabled', True):
                    with st.spinner("Uploading edited image(s) to Google Drive..."):
                        # Save and upload results
                        uploaded_metadata = save_and_upload_results(
                            task_data['id'],
                            selected_edit_model,
                            edit_prompt,
                            image_urls,
                            tags="edited"
                        )
                    if uploaded_metadata:
                        st.success(f"✅ Uploaded {len(uploaded_metadata)} edited image(s) to Google Drive!")
                    else:
                        st.warning("Upload to Google Drive failed or was not completed.")
            else:
                st.warning("No images found in the API response. Please check the model and your prompt.")
        else:
            st.error(f"Editing failed or returned an unknown status: {task_data.get('status', 'unknown')}")


def display_library_page():
    """Display the image library from Google Drive"""
    st.title("📚 Image Library")
    st.markdown("Browse and manage your generated images stored in Google Drive")
    
    # Require Google Drive authentication to view library
    if not st.session_state.get('authenticated') or not st.session_state.get('drive_service'):
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Google Drive Not Connected</strong><br>
            Please authenticate with Google Drive in the sidebar or Settings tab to view your library.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Toolbar for library controls
    toolbar_cols = st.columns([1, 1, 1, 1])
    
    with toolbar_cols[0]:
        if st.button("🔄 Refresh Library", use_container_width=True):
            with st.spinner("Refreshing library..."):
                list_gdrive_images(force_refresh=True)
            st.success("Library refreshed!")
            time.sleep(0.5)
            st.rerun()
    
    with toolbar_cols[1]:
        view_mode = st.selectbox("View", ["Grid", "List"], key="lib_view_mode")
        st.session_state.view_mode = view_mode.lower()
    
    with toolbar_cols[2]:
        sort_by = st.selectbox("Sort By", ["Newest", "Oldest", "Name"])
    
    with toolbar_cols[3]:
        items_per_page_slider = st.slider(
            "Items per Page",
            12, 96, st.session_state.get('items_per_page', 12), 12,
            key="lib_items_per_page_slider",
            help="Number of images to display per page."
        )
        st.session_state.items_per_page = items_per_page_slider
    
    # Search and Filter Section
    search_filter_cols = st.columns([3, 1])
    
    with search_filter_cols[0]:
        search_query = st.text_input(
            "🔍 Search images (by name, description)",
            placeholder="Enter search terms...",
            key="lib_search_query"
        )
        st.session_state.search_query = search_query
    
    with search_filter_cols[1]:
        all_tags_in_session = set()
        for tags_list in st.session_state.tags.values():
            all_tags_in_session.update(tags_list)
        
        tag_options = ["All"] + sorted(list(all_tags_in_session))
        
        filter_tag = st.selectbox(
            "Filter by Tag",
            tag_options,
            key="lib_filter_tag"
        )
        st.session_state.filter_tag = filter_tag
    
    st.divider()
    
    # Load images from Google Drive
    with st.spinner("Loading images from Google Drive..."):
        images = list_gdrive_images()
    
    if not images:
        st.markdown("""
        <div class="info-box">
            <strong>📭 No images found in your Google Drive library</strong><br>
            Start by generating some images! They will automatically upload to Google Drive when authentication is enabled.
            <br><br>
            <strong>Tips:</strong>
            <ul>
                <li>Generate images in the 🎨 Generate tab</li>
                <li>Make sure "Auto Upload to Drive" is enabled in Settings</li>
                <li>Check that you've authenticated with Google Drive</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Apply search filter
    if search_query:
        images = [
            img for img in images
            if search_query.lower() in img.get('name', '').lower() or
               search_query.lower() in img.get('description', '').lower()
        ]
    
    # Apply tag filter
    if filter_tag != "All":
        images = [
            img for img in images
            if img.get('id') in st.session_state.tags and
               filter_tag in st.session_state.tags.get(img['id'], [])
        ]
    
    # Apply sort
    if sort_by == "Newest":
        images = sorted(images, key=lambda x: x.get('createdTime', ''), reverse=True)
    elif sort_by == "Oldest":
        images = sorted(images, key=lambda x: x.get('createdTime', ''))
    elif sort_by == "Name":
        images = sorted(images, key=lambda x: x.get('name', ''))
    
    # Pagination
    total_images = len(images)
    items_per_page = st.session_state.items_per_page
    total_pages = (total_images + items_per_page - 1) // items_per_page if total_images > 0 else 1
    
    if total_images > 0:
        st.markdown(f"**Found {total_images} image(s)** | Page {st.session_state.current_page} of {total_pages}")
        
        # Pagination controls
        if total_pages > 1:
            page_cols = st.columns([1, 3, 1])
            
            with page_cols[0]:
                if st.button("◀ Previous", disabled=(st.session_state.current_page <= 1)):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with page_cols[1]:
                page_number = st.number_input(
                    "Page",
                    min_value=1,
                    max_value=total_pages,
                    value=st.session_state.current_page,
                    key="page_number_input",
                    label_visibility="collapsed"
                )
                if page_number != st.session_state.current_page:
                    st.session_state.current_page = page_number
                    st.rerun()
            
            with page_cols[2]:
                if st.button("Next ▶", disabled=(st.session_state.current_page >= total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()
        
        # Calculate slice indices
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_images)
        page_images = images[start_idx:end_idx]
        
        st.divider()
        
        # Display images
        if st.session_state.view_mode == "grid":
            cols_per_row = 3
            for i in range(0, len(page_images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(page_images):
                        img_info = page_images[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                # Display image
                                display_gdrive_image(img_info, caption=img_info.get('name', 'Untitled'))
                                
                                # Image name and metadata
                                st.markdown(f"**{img_info.get('name', 'Untitled')}**")
                                if img_info.get('createdTime'):
                                    # Parse ISO format, handle potential 'Z' and timezone info
                                    try:
                                        created = datetime.fromisoformat(img_info['createdTime'].replace('Z', '+00:00'))
                                        st.caption(f"📅 {created.strftime('%Y-%m-%d %H:%M')}")
                                    except ValueError:
                                        st.caption(f"📅 Created: {img_info.get('createdTime')}")

                                
                                # Action buttons
                                btn_cols = st.columns(2)
                                with btn_cols[0]:
                                    if st.button("✏️ Edit", key=f"edit_{img_info['id']}", use_container_width=True):
                                        st.session_state.selected_image_for_edit = img_info
                                        st.success("Image selected for editing! Go to the Edit tab.")
                                
                                with btn_cols[1]:
                                    if st.button("🗑️ Delete", key=f"del_{img_info['id']}", use_container_width=True):
                                        success, message = delete_gdrive_file(img_info['id'])
                                        if success:
                                            st.success("Deleted!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error(message)
        else:
            # List view
            for img_info in page_images:
                with st.container(border=True):
                    list_cols = st.columns([1, 3, 2])
                    
                    with list_cols[0]:
                        display_gdrive_image(img_info, width=100)
                    
                    with list_cols[1]:
                        st.markdown(f"### {img_info.get('name', 'Untitled')}")
                        if img_info.get('description'):
                            st.caption(img_info['description'])
                        if img_info.get('createdTime'):
                            try:
                                created = datetime.fromisoformat(img_info['createdTime'].replace('Z', '+00:00'))
                                st.caption(f"📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                            except ValueError:
                                st.caption(f"📅 Created: {img_info.get('createdTime')}")
                        if img_info.get('size'):
                            size_mb = int(img_info['size']) / (1024 * 1024)
                            st.caption(f"💾 Size: {size_mb:.2f} MB")
                    
                    with list_cols[2]:
                        if st.button("✏️ Edit", key=f"edit_list_{img_info['id']}", use_container_width=True):
                            st.session_state.selected_image_for_edit = img_info
                            st.success("Image selected! Go to Edit tab.")
                        
                        if st.button("🗑️ Delete", key=f"del_list_{img_info['id']}", use_container_width=True):
                            success, message = delete_gdrive_file(img_info['id'])
                            if success:
                                st.success("Deleted!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(message)
    else:
        st.info("No images match your search or filter criteria.")

# ============================================================================
# PAGE: TASK MANAGEMENT
# ============================================================================

def display_task_management_page():
    """Display comprehensive task management page"""
    st.title("📋 Task Management Center")
    st.markdown("Monitor and manage all your AI generation tasks")
    
    # Summary Statistics Section
    st.markdown("### 📊 Summary Statistics")
    stats_cols = st.columns(5) # Create 5 columns for metrics
    
    with stats_cols[0]:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    
    with stats_cols[1]:
        st.metric("Successful", st.session_state.stats['successful_tasks'])
    
    with stats_cols[2]:
        st.metric("Failed", st.session_state.stats['failed_tasks'])
    
    with stats_cols[3]:
        st.metric("Active", len(st.session_state.active_tasks)) # Count of currently active tasks
    
    with stats_cols[4]:
        # Calculate success rate, handle division by zero
        total_tasks = st.session_state.stats['total_tasks']
        success_rate = 0
        if total_tasks > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / total_tasks) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.divider() # Separator
    
    # Active Tasks Section
    if st.session_state.active_tasks:
        st.markdown("### 🔄 Active Tasks")
        
        # Display each active task in an expander for details
        for task in st.session_state.active_tasks:
            task_prompt_preview = task.get('prompt', 'No prompt')[:50] + "..." # Truncate prompt for title
            task_created_at = task.get('created_at', 'N/A')
            
            with st.expander(f"🔄 Processing: `{task.get('id', 'N/A')}` - {task_prompt_preview} ({task_created_at})"):
                detail_cols = st.columns([3, 1]) # Columns for details and actions
                
                with detail_cols[0]:
                    st.write(f"**Task ID:** `{task['id']}`")
                    st.write(f"**Model:** {task.get('model_name', task['model'])}") # Use friendly name if available
                    st.write(f"**Prompt:** {task['prompt']}")
                    st.write(f"**Status:** {task.get('status', 'processing').upper()}") # Display status in uppercase
                    st.write(f"**Created:** {task_created_at}")
                
                with detail_cols[1]:
                    # Button to re-check status (requires API key and polling logic)
                    if st.button("🔍 Check Status", key=f"check_{task['id']}"):
                        st.info("Status check functionality requires the KIE.ai API key. Ensure it's entered in the 'Generate' tab.")
                        # In a real implementation, you'd call check_task_status here and update UI
        
        st.divider() # Separator after active tasks
    
    # Task History Section with Filtering and Sorting
    st.markdown("### 📜 Task History")
    
    # Filter controls row
    filter_cols = st.columns(3)
    
    with filter_cols[0]:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Completed", "Failed", "Processing"], # Options for status filtering
            key="task_history_status_filter"
        )
    
    with filter_cols[1]:
        # Generate model filter options from available models used
        # Use keys from aggregated_model_usage if available, otherwise from stats
        available_models = sorted(list(st.session_state.stats.get('models_used', {}).keys()))
        model_options_history = ["All"] + available_models
        model_filter = st.selectbox(
            "Filter by Model",
            model_options_history,
            key="task_history_model_filter"
        )
    
    with filter_cols[2]:
        date_filter = st.selectbox(
            "Filter by Date",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days"], # Date range options
            key="task_history_date_filter"
        )
    
    # Apply filters to task history
    filtered_history = st.session_state.task_history.copy() # Start with a copy
    
    # Filter by status
    if status_filter != "All":
        filtered_history = [
            t for t in filtered_history 
            if t.get('status', '').lower() == status_filter.lower() # Case-insensitive comparison
        ]
    
    # Filter by model
    if model_filter != "All":
        filtered_history = [
            t for t in filtered_history 
            if model_filter in t.get('model', '').split('/')[-1] # Match base model name
        ]
    
    # Filter by date range
    if date_filter != "All Time":
        today = datetime.now()
        if date_filter == "Today":
            filter_date_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "Last 7 Days":
            filter_date_start = today - timedelta(days=7)
        else:  # Last 30 Days
            filter_date_start = today - timedelta(days=30)
        
        # Convert task 'created_at' string to datetime object for comparison
        filtered_history = [
            t for t in filtered_history
            if datetime.strptime(t.get('created_at', '1970-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S") >= filter_date_start
        ]
    
    st.caption(f"Showing {len(filtered_history)} task(s) matching filters.")
    
    # Display task history entries
    if not filtered_history:
        st.info("No tasks found matching the selected filters.")
    else:
        # Sort history by creation date, newest first
        filtered_history_sorted = sorted(
            filtered_history, 
            key=lambda x: datetime.strptime(x.get('created_at', '1970-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S"), 
            reverse=True
        )

        # Display up to a certain number of tasks (e.g., last 50) to avoid overwhelming the UI
        max_tasks_to_display = 50 
        for task in filtered_history_sorted[:max_tasks_to_display]:
            # Determine status emoji and badge class
            status = task.get('status', 'unknown').lower()
            status_emoji = {
                'completed': '✅',
                'failed': '❌',
                'processing': '🔄',
                'unknown': '❓'
            }.get(status, '❓')
            
            badge_class = "badge-success" if status == "completed" else \
                          "badge-danger" if status == "failed" else \
                          "badge-warning" if status == "processing" else \
                          "badge-info"
            
            task_prompt_preview = task.get('prompt', 'No prompt')[:60] + "..." # Truncate prompt
            task_created_at = task.get('created_at', 'N/A')
            
            # Use expander for each task's details
            with st.expander(f"{status_emoji} {task_prompt_preview} - {task_created_at}"):
                detail_cols = st.columns([2, 1]) # Columns for details and summary badge
                
                with detail_cols[0]:
                    st.write(f"**Task ID:** `{task.get('id', 'N/A')}`")
                    st.write(f"**Model:** {task.get('model_name', task.get('model', 'N/A'))}") # Show friendly name if available
                    st.write(f"**Prompt:** {task.get('prompt', 'N/A')}")
                    st.write(f"**Created:** {task_created_at}")
                    
                    # Display tags if they exist for the task
                    if task.get('tags'):
                        st.write(f"**Tags:** {task.get('tags')}")
                
                with detail_cols[1]:
                    # Display status badge
                    st.markdown(f"<div class='badge {badge_class}' style='margin-top: 15px;'>{status.upper()}</div>", unsafe_allow_html=True)
                    
                    # Show result images if available for completed tasks
                    if task.get('result_urls') and status == 'completed':
                        st.caption(f"🖼️ {len(task['result_urls'])} image(s) generated")
                        
                        # Expander to view result images and download buttons
                        with st.expander("View Results", expanded=False):
                            for i, url in enumerate(task['result_urls']):
                                st.image(url, caption=f"Result {i+1}", use_container_width=True)
                                # Download button for each result image
                                try:
                                    img_response = requests.get(url, timeout=20)
                                    if img_response.status_code == 200:
                                        st.download_button(
                                            label=f"Download Result {i+1}",
                                            data=img_response.content,
                                            file_name=f"task_{task.get('id', 'result')}_img_{i+1}.png",
                                            mime="image/png",
                                            key=f"download_task_{task.get('id')}_{i}" # Unique key
                                        )
                                except Exception as e:
                                    st.error(f"Failed to download result {i+1}: {e}")

# ============================================================================
# PAGE: MODEL COMPARISON
# ============================================================================

def display_model_comparison_page():
    """Display model comparison and benchmarking page"""
    st.title("🔬 Model Comparison Lab")
    st.markdown("Compare different AI models side-by-side with the same prompts for quality and style")
    
    # Tabs for different sections of the comparison page
    tab1, tab2, tab3 = st.tabs(["⚖️ Compare Generations", "📊 Performance Metrics", "💰 Estimated Cost"])
    
    with tab1:
        st.markdown("### Compare Generation Results")
        
        # Column layout for model selection
        col_models1, col_models2 = st.columns(2)
        
        # Predefined model options for comparison - ensure these are valid API identifiers
        comparison_models = {
            "FLUX 1.1 Pro": "black-forest-labs/flux-1.1-pro",
            "FLUX Pro": "black-forest-labs/flux-pro",
            "FLUX Dev": "black-forest-labs/flux-dev",
            "FLUX Schnell": "black-forest-labs/flux-schnell",
            "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
            "Stable Diffusion 3.5 Medium": "stabilityai/stable-diffusion-3.5-medium",
            "Playground v3": "playground/playground-v3",
            "GPT-4o Image": "gpt-4o/image", # Added GPT-4o for comparison
        }
        
        with col_models1:
            model1_name = st.selectbox("Model 1", list(comparison_models.keys()), key="compare_model1_name")
            model1_id = comparison_models[model1_name]
        
        with col_models2:
            # Default to the second model in the list for the second selectbox
            default_index_model2 = min(1, len(comparison_models) - 1) # Ensure index is valid
            model2_name = st.selectbox("Model 2", list(comparison_models.keys()), index=default_index_model2, key="compare_model2_name")
            model2_id = comparison_models[model2_name]
        
        # Prompt input for comparison
        comparison_prompt = st.text_area(
            "Comparison Prompt",
            height=100,
            placeholder="Enter a prompt to test both models side-by-side...",
            key="compare_prompt_input"
        )
        
        # Aspect ratio and seed controls
        ratio_seed_cols = st.columns(2)
        
        with ratio_seed_cols[0]:
            # Select aspect ratio, mapped to known sizes
            aspect_ratio_options = ["1:1", "16:9", "9:16", "4:3", "3:4"]
            selected_aspect = st.selectbox("Aspect Ratio", aspect_ratio_options, key="compare_aspect_ratio")
            
            # Map aspect ratio string to model parameter value
            aspect_map = {
                "1:1": "1:1", "16:9": "16:9", "9:16": "9:16",
                "4:3": "4:3", "3:4": "3:4"
            }
            image_size_param = aspect_map.get(selected_aspect, "1:1") # Parameter for the API call
        
        with ratio_seed_cols[1]:
            seed = st.number_input("Seed (0 for random)", 0, 999999, 0, step=1, key="compare_seed")
        
        # Comparison run button
        if st.button("🚀 Run Comparison", type="primary", use_container_width=True):
            if not comparison_prompt.strip():
                st.error("Please enter a prompt to run the comparison.")
                return
            
            # Retrieve API key, preferably from secrets
            api_key = st.secrets.get("KIE_API_KEY") if hasattr(st, 'secrets') and st.secrets else ""
            if not api_key:
                st.error("KIE.ai API key not found. Please enter it in the 'Generate' tab or set it in your secrets.toml file.")
                return
            
            # Layout for displaying comparison results
            col_result1, col_result2 = st.columns(2)
            
            # --- Generate with Model 1 ---
            with col_result1:
                st.markdown(f"### {model1_name}")
                with st.spinner(f"Generating with {model1_name}..."):
                    input_params1 = {
                        "prompt": comparison_prompt.strip(),
                        "aspect_ratio": image_size_param, # Use the selected aspect ratio parameter
                        "num_outputs": 1, # Generate one image for comparison
                        "seed": seed,
                        # Add other parameters if needed for specific models
                    }
                    
                    # Create task for model 1
                    task_data1, error1 = create_task(api_key, model1_id, input_params1)
                    
                    if error1:
                        st.error(f"Error generating with {model1_name}: {error1}")
                    elif task_data1 and task_data1.get('status') == 'succeeded':
                        urls1 = task_data1.get('output', {}).get('images', [])
                        if urls1:
                            st.image(urls1[0], use_container_width=True) # Display the generated image
                            st.caption(f"✅ Generated by {model1_name}")
                            # Optionally save to CSV/Drive here
                        else:
                            st.warning(f"No images generated by {model1_name}.")
                    else:
                        st.error(f"Generation with {model1_name} failed or returned no images.")
            
            # --- Generate with Model 2 ---
            with col_result2:
                st.markdown(f"### {model2_name}")
                with st.spinner(f"Generating with {model2_name}..."):
                    input_params2 = {
                        "prompt": comparison_prompt.strip(),
                        "aspect_ratio": image_size_param, # Use the selected aspect ratio parameter
                        "num_outputs": 1,
                        "seed": seed,
                        # Add other parameters if needed
                    }
                    
                    # Create task for model 2
                    task_data2, error2 = create_task(api_key, model2_id, input_params2)
                    
                    if error2:
                        st.error(f"Error generating with {model2_name}: {error2}")
                    elif task_data2 and task_data2.get('status') == 'succeeded':
                        urls2 = task_data2.get('output', {}).get('images', [])
                        if urls2:
                            st.image(urls2[0], use_container_width=True) # Display the generated image
                            st.caption(f"✅ Generated by {model2_name}")
                            # Optionally save to CSV/Drive here
                        else:
                            st.warning(f"No images generated by {model2_name}.")
                    else:
                        st.error(f"Generation with {model2_name} failed or returned no images.")
    
    with tab2:
        st.markdown("### Model Performance Metrics")
        
        # Check if pandas and plotly are available
        if not pd or not px:
            st.error("Please install pandas and plotly for advanced analytics: `pip install pandas plotly`")
            return
        
        # Use aggregated model usage data (recalculated for accuracy)
        aggregated_model_usage = {}
        for task in st.session_state.task_history:
            model_key = task.get('model', '').split('/')[-1] # Extract base model name
            if model_key:
                aggregated_model_usage[model_key] = aggregated_model_usage.get(model_key, 0) + 1

        if aggregated_model_usage: # If there's data to display
            model_stats_list = []
            # Prepare data for DataFrame
            for model, count in sorted(aggregated_model_usage.items(), key=lambda item: item[1], reverse=True):
                total_tasks = st.session_state.stats['total_tasks']
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                model_stats_list.append({
                    'Model': model,
                    'Uses': count,
                    'Percentage': f"{percentage:.1f}%"
                })
            
            df_models = pd.DataFrame(model_stats_list)
            
            # Display table and pie chart
            col_metrics1, col_metrics2 = st.columns(2)
            
            with col_metrics1:
                st.markdown("**Usage by Model:**")
                st.dataframe(df_models, use_container_width=True)
            
            with col_metrics2:
                st.markdown("### Usage Distribution")
                fig_models = px.pie(df_models, values='Uses', names='Model', title='Model Usage Distribution')
                st.plotly_chart(fig_models, use_container_width=True)
                
                # Display most used model metric
                if not df_models.empty:
                    most_used = df_models.iloc[0]
                    st.metric("Most Used Model", most_used['Model'], f"{most_used['Uses']} uses")

        else:
            st.info("No model usage data recorded yet. Start generating images to see statistics!")
    
    with tab3:
        st.markdown("### Estimated Cost Analysis by Model")
        
        st.info("This section provides an estimated cost based on KIE.ai API usage. Actual costs may vary based on pricing changes and specific model parameters.")
        
        # Example estimated costs per image generation for different models
        # These values should be verified against KIE.ai's official pricing
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
            'seedream-v4-edit': 0.05, # Example cost for editing model
            'gpt-4o/image': 0.03, # Example cost for GPT-4o image generation
        }
        
        # Use the aggregated model usage data from the task history
        aggregated_model_usage = {} # Recalculate for clarity
        for task in st.session_state.task_history:
            model_key = task.get('model', '').split('/')[-1] if '/' in task.get('model', '') else task.get('model', '')
            if model_key:
                aggregated_model_usage[model_key] = aggregated_model_usage.get(model_key, 0) + 1

        if aggregated_model_usage:
            cost_data_list = []
            total_estimated_cost = 0.0
            
            # Calculate costs for each model
            for model_key, count in aggregated_model_usage.items():
                # Look up cost based on the base model name
                cost_per_image = model_costs_per_image.get(model_key, 0.04) # Default cost if model not listed
                model_total_cost = count * cost_per_image
                total_estimated_cost += model_total_cost
                
                cost_data_list.append({
                    'Model': model_key,
                    'Images Generated': count,
                    'Cost Per Image ($)': f"${cost_per_image:.3f}",
                    'Estimated Cost ($)': f"${model_total_cost:.2f}"
                })
            
            # Create DataFrame for cost data
            df_cost = pd.DataFrame(cost_data_list)
            st.dataframe(df_cost, use_container_width=True)
            
            # Display total estimated cost
            st.metric("Total Estimated Cost ($)", f"${total_estimated_cost:.2f}")
        else:
            st.info("No cost data available yet. Generate some images to see cost estimations!")

# ============================================================================
# PAGE: WORKFLOWS & AUTOMATION
# ============================================================================

def display_workflows_page():
    """Display automated workflows and batch processing configuration"""
    st.title("⚙️ Workflows & Automation")
    st.markdown("Create, manage, and schedule automated image generation workflows")
    
    # Tabs for workflow management
    tab1, tab2, tab3 = st.tabs(["🔧 Create Workflow", "📋 My Workflows", "⏰ Schedule Tasks"])
    
    with tab1:
        st.markdown("### Create New Workflow")
        
        # Workflow name and description inputs
        workflow_name = st.text_input("Workflow Name", placeholder="e.g., Product Photography Batch", key="workflow_name_input")
        workflow_description = st.text_area(
            "Description",
            placeholder="Describe what this workflow does and its purpose...",
            key="workflow_desc_input"
        )
        
        st.markdown("#### Workflow Steps")
        
        # Manage number of steps dynamically using session state
        if 'workflow_steps_count' not in st.session_state:
            st.session_state.workflow_steps_count = 1 # Initialize step count

        # Button to add a new step to the workflow
        if st.button("➕ Add Step", key="add_workflow_step"):
            st.session_state.workflow_steps_count += 1
            st.rerun() # Rerun to redraw the UI with the new step

        workflow_steps_config = [] # List to store configuration for each step
        # Loop to create input fields for each workflow step
        for i in range(st.session_state.workflow_steps_count):
            with st.expander(f"Step {i+1}: Configuration", expanded=True):
                step_type = st.selectbox(
                    "Step Type",
                    ["Generate Image", "Edit Image", "Apply Style (Future)", "Upload to Drive", "Post-processing"],
                    key=f"step_type_{i}"
                )
                
                step_config = {'type': step_type} # Store the type of step
                
                # Configuration options based on step type
                if step_type == "Generate Image":
                    # Model selection for generation steps
                    model_options_gen = {
                        "FLUX 1.1 Pro (Fast, High Quality)": "black-forest-labs/flux-1.1-pro",
                        "FLUX Pro (Best Quality)": "black-forest-labs/flux-pro",
                        "FLUX Dev (Balanced)": "black-forest-labs/flux-dev",
                        "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
                        "GPT-4o Image": "gpt-4o/image", # Include GPT-4o here
                    }
                    model_name = st.selectbox(
                        "AI Model",
                        list(model_options_gen.keys()),
                        key=f"model_gen_{i}"
                    )
                    model_id = model_options_gen[model_name]
                    
                    # Prompt template for dynamic generation
                    prompt_template = st.text_area(
                        "Prompt Template",
                        placeholder="Use {variable} syntax for dynamic inputs. Example: 'A {adjective} {object} in {location}'",
                        height=80,
                        key=f"prompt_template_{i}"
                    )
                    
                    # Add more generation specific parameters
                    aspect_ratio_gen = st.selectbox(
                        "Aspect Ratio",
                        ["1:1", "16:9", "9:16", "4:3", "3:4"],
                        key=f"aspect_ratio_gen_{i}"
                    )
                    image_resolution_gen = st.selectbox(
                        "Image Resolution",
                        ["Standard", "HD"],
                        key=f"resolution_gen_{i}"
                    )
                    style_gen = st.selectbox(
                        "Style",
                        ["Vivid", "Natural"],
                        key=f"style_gen_{i}"
                    )
                    seed_gen = st.number_input("Seed (0 for random)", 0, 999999, 0, step=1, key=f"seed_gen_{i}")
                    
                    step_config.update({
                        'model_name': model_name,
                        'model_id': model_id,
                        'prompt_template': prompt_template,
                        'aspect_ratio': aspect_ratio_gen,
                        'image_resolution': image_resolution_gen.lower(),
                        'style': style_gen.lower(),
                        'seed': seed_gen
                    })
                
                elif step_type == "Edit Image":
                    # Model selection for editing steps
                    edit_model_options_edit = {
                        "Seedream v4 (Edit)": "bytedance/seedream-v4-edit",
                        "GPT-4o Image (Edit)": "gpt-4o/image",
                    }
                    edit_model_name = st.selectbox(
                        "Editing Model",
                        list(edit_model_options_edit.keys()),
                        key=f"edit_model_{i}"
                    )
                    edit_model_id = edit_model_options_edit[edit_model_name]
                    
                    # Edit instructions and strength
                    edit_instructions = st.text_area(
                        "Edit Instructions",
                        placeholder="Describe specific edits needed...",
                        height=60,
                        key=f"edit_instructions_{i}"
                    )
                    edit_strength = st.slider(
                        "Edit Strength", 0.1, 1.0, 0.7, # Min, Max, Default
                        key=f"edit_strength_{i}"
                    )
                    # Add other relevant editing parameters if available
                    edit_resolution_edit = st.selectbox(
                        "Output Quality",
                        ["Standard", "HD"],
                        key=f"edit_resolution_{i}"
                    )
                    edit_aspect_ratio_edit = st.selectbox(
                        "Aspect Ratio",
                        ["1:1", "16:9", "9:16", "4:3", "3:4"],
                        key=f"edit_aspect_ratio_{i}"
                    )

                    step_config.update({
                        'edit_model_name': edit_model_name,
                        'edit_model_id': edit_model_id,
                        'edit_instructions': edit_instructions,
                        'edit_strength': edit_strength,
                        'image_resolution': edit_resolution_edit.lower(),
                        'aspect_ratio': edit_aspect_ratio_edit
                    })

                elif step_type == "Apply Style (Future)":
                    # Placeholder for style application step
                    st.info("Apply Style feature is under development.")
                    style_preset = st.selectbox(
                        "Style Preset",
                        ["Photorealistic", "Fantasy Art", "Cyberpunk", "Abstract", "Anime"],
                        key=f"style_preset_{i}",
                        disabled=True # Disable until implemented
                    )
                    step_config['style_preset'] = style_preset
                
                elif step_type == "Upload to Drive":
                    # Checkbox to enable/disable upload for this step
                    upload_enabled = st.checkbox("Enable Upload to Google Drive", value=True, key=f"upload_drive_{i}")
                    step_config['upload_enabled'] = upload_enabled

                elif step_type == "Post-processing":
                    # Post-processing options like resolution enhancement
                    resolution = st.selectbox(
                        "Output Resolution",
                        ["1K", "2K", "4K"],
                        key=f"post_res_{i}"
                    )
                    step_config['resolution'] = resolution

                workflow_steps_config.append(step_config) # Add the configured step

        # Button to save the workflow
        if st.button("💾 Save Workflow", type="primary", key="save_workflow_button"):
            if workflow_name.strip(): # Ensure workflow name is provided
                # Generate a unique ID for the workflow using timestamp and index
                workflow_id = f"wf_{int(time.time())}_{len(st.session_state.workflows) + 1}" 
                st.session_state.workflows[workflow_id] = {
                    'name': workflow_name.strip(),
                    'description': workflow_description.strip(),
                    'steps': workflow_steps_config, # Store the list of step configurations
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success(f"✅ Workflow '{workflow_name.strip()}' saved!")
                # Reset step count and potentially clear form fields after saving
                st.session_state.workflow_steps_count = 1 
                st.rerun() # Rerun to reset UI elements
            else:
                st.error("Please enter a name for the workflow.")
    
    with tab2:
        st.markdown("### My Saved Workflows")
        
        if st.session_state.workflows: # Check if any workflows exist
            # Display each saved workflow
            for wf_id, workflow in st.session_state.workflows.items():
                with st.expander(f"📋 {workflow['name']}"):
                    st.markdown(f"**Description:** {workflow.get('description', 'No description provided.')}")
                    st.markdown(f"**Steps:** {len(workflow.get('steps', []))}") # Count steps
                    st.markdown(f"**Created:** {workflow.get('created_at', 'N/A')}")
                    
                    # Action buttons for each workflow
                    action_cols = st.columns([1, 1, 1])
                    
                    with action_cols[0]:
                        if st.button("▶️ Run Workflow", key=f"run_{wf_id}"):
                            st.info("Workflow execution is currently under development and will be available soon!")
                            # Placeholder for actual workflow execution logic
                    
                    with action_cols[1]:
                        if st.button("✏️ Edit Workflow", key=f"edit_{wf_id}"):
                            st.info("Editing workflows is under development!")
                            # Placeholder for workflow editing logic
                    
                    with action_cols[2]:
                        if st.button("🗑️ Delete Workflow", key=f"delete_{wf_id}"):
                            # Add a confirmation step for deletion
                            if st.button("Confirm Delete", key=f"confirm_delete_{wf_id}"):
                                del st.session_state.workflows[wf_id] # Remove workflow from session state
                                st.success("Workflow deleted.")
                                st.rerun() # Rerun to update the UI
        else:
            st.info("No workflows created yet. Click on the 'Create Workflow' tab to start!")
    
    with tab3:
        st.markdown("### Scheduled Tasks")
        st.info("Schedule your created workflows to run automatically at specific times or intervals.")
        
        # Check if any workflows exist before allowing scheduling
        if not st.session_state.workflows:
            st.warning("You need to create at least one workflow in the 'Create Workflow' tab before you can schedule it.")
        else:
            # Workflow selection for scheduling
            workflow_options = {wf['name']: wf_id for wf_id, wf in st.session_state.workflows.items()}
            
            schedule_workflow_name = st.selectbox(
                "Select Workflow to Schedule",
                list(workflow_options.keys()),
                key="schedule_workflow_select"
            )
            
            selected_workflow_id = workflow_options[schedule_workflow_name] # Get the ID of the selected workflow
            
            # Date and time selection for scheduling
            schedule_date_cols = st.columns(2)
            
            with schedule_date_cols[0]:
                schedule_date = st.date_input("Execution Date", min_value=datetime.now().date(), key="schedule_date_input")
            
            with schedule_date_cols[1]:
                schedule_time = st.time_input("Execution Time", key="schedule_time_input")
            
            # Repeat option for scheduling
            repeat_option = st.selectbox(
                "Repeat Frequency",
                ["Once", "Daily", "Weekly", "Monthly"],
                key="schedule_repeat_select"
            )
            
            # Placeholder for dynamic inputs required by the workflow (e.g., variables in prompts)
            # This section would need logic to parse workflow templates and create corresponding inputs
            dynamic_inputs_section = st.empty() # Use an empty container that can be updated
            # Check if workflow_steps_config exists and has generation steps to parse variables from
            current_workflow_steps = st.session_state.workflows.get(selected_workflow_id, {}).get('steps', [])
            variables_found = False
            if current_workflow_steps:
                 with dynamic_inputs_section.expander("Dynamic Inputs (Optional)", expanded=False):
                     st.write("Provide values for variables used in your workflow's prompt templates or instructions.")
                     # Example: Parse '{variable}' from prompt templates and create text inputs
                     # This is a simplified example; real implementation would need robust parsing
                     dynamic_inputs = {}
                     for i, step in enumerate(current_workflow_steps):
                         if step.get('type') == "Generate Image" and step.get('prompt_template'):
                             # Basic regex to find variables like {variable_name}
                             import re
                             variables = re.findall(r'\{(\w+)\}', step['prompt_template'])
                             for var in set(variables): # Use set to avoid duplicate inputs for the same variable
                                 if var not in dynamic_inputs: # Check if already added from another step
                                    dynamic_inputs[var] = st.text_input(f"Input for '{var}' (Step {i+1})", key=f"dynamic_input_{selected_workflow_id}_{var}")
                                    variables_found = True
            
            # Button to schedule the task
            if st.button("⏰ Schedule Workflow", key="schedule_workflow_button"):
                if schedule_workflow_name and selected_workflow_id:
                    # Construct the scheduled task object
                    scheduled_task = {
                        'id': f"schedule_{int(time.time())}_{len(st.session_state.scheduled_tasks) + 1}", # Unique ID
                        'workflow_id': selected_workflow_id,
                        'workflow_name': schedule_workflow_name,
                        'date': str(schedule_date), # Store date as string
                        'time': schedule_time.strftime("%H:%M:%S"), # Store time as formatted string
                        'repeat': repeat_option,
                        'status': 'scheduled', # Initial status
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        # 'dynamic_inputs': dynamic_inputs # Store any dynamic inputs provided
                    }
                    # Add the scheduled task to session state
                    st.session_state.scheduled_tasks.append(scheduled_task)
                    st.success("✅ Workflow scheduled successfully!")
                    st.rerun() # Rerun to update the UI
                else:
                    st.error("Please select a workflow to schedule.")

# ============================================================================
# PAGE: PROJECTS
# ============================================================================

def display_projects_page():
    """Display project management functionality for organizing related images"""
    st.title("📁 Projects")
    st.markdown("Organize your AI generations and related assets into projects")
    
    # Initialize session state for projects if it doesn't exist
    if 'projects' not in st.session_state:
        st.session_state.projects = {}
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None # No project selected by default

    # Tabs for managing projects
    tab1, tab2 = st.tabs(["📂 My Projects", "➕ New Project"])
    
    with tab1:
        st.subheader("Your Projects")
        if st.session_state.projects: # Check if there are existing projects
            # Use columns for a grid-like display of projects
            col_count = 3 # Number of columns for project cards
            cols = st.columns(col_count)
            
            project_ids = list(st.session_state.projects.keys()) # Get list of project IDs
            
            # Iterate through projects and display them in columns
            for idx, project_id in enumerate(project_ids):
                project = st.session_state.projects[project_id] # Get project data
                current_col_index = idx % col_count # Determine which column this project belongs to
                current_col = cols[current_col_index]
                
                with current_col:
                    # Use a container with a border for each project card
                    with st.container(border=True):
                        st.markdown(f"### {project['name']}")
                        st.caption(project.get('description', 'No description'))
                        
                        # Display metrics like image count
                        st.metric("Images Assigned", project.get('image_count', 0))
                        st.caption(f"Created: {project.get('created_at', 'N/A')}")
                        
                        # Action buttons for each project
                        project_action_cols = st.columns(2)
                        
                        with project_action_cols[0]:
                            if st.button("View", key=f"view_project_{project_id}"):
                                st.session_state.selected_project = project_id # Set selected project
                                st.success(f"Viewing project: '{project['name']}'")
                                # Note: Navigation to a dedicated project view page is not implemented yet.
                                # This action primarily sets the state for potential future use.
                        
                        with project_action_cols[1]:
                            if st.button("Delete", key=f"delete_project_{project_id}"):
                                # Add a confirmation step for deletion
                                if st.button("Confirm Delete", key=f"confirm_delete_project_{project_id}"):
                                    del st.session_state.projects[project_id] # Remove project from session state
                                    # If the deleted project was the selected one, deselect it
                                    if st.session_state.selected_project == project_id:
                                        st.session_state.selected_project = None
                                    st.success("Project deleted.")
                                    st.rerun() # Rerun to update the UI
        else:
            st.info("No projects created yet. Click on the 'New Project' tab to get started!")
    
    with tab2:
        st.subheader("Create New Project")
        
        # Input fields for new project details
        project_name = st.text_input("Project Name", placeholder="e.g., Product Launch 2024", key="new_project_name")
        project_description = st.text_area(
            "Description",
            placeholder="Describe your project and its goals...",
            key="new_project_description"
        )
        project_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., product, marketing, campaign",
            key="new_project_tags"
        )
        
        # Button to create the project
        if st.button("🎨 Create Project", type="primary"):
            if project_name.strip(): # Ensure project name is not empty
                # Generate a unique project ID
                project_id = f"proj_{int(time.time())}_{len(st.session_state.projects) + 1}"
                # Store project data in session state
                st.session_state.projects[project_id] = {
                    'name': project_name.strip(),
                    'description': project_description.strip(),
                    # Parse tags, remove empty ones, and convert to list
                    'tags': [tag.strip() for tag in project_tags.split(',') if tag.strip()], 
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'image_count': 0, # Initialize image count to 0
                    'images': [] # List to store IDs or references of assigned images
                }
                st.success(f"✅ Project '{project_name.strip()}' created!")
                st.rerun() # Rerun to clear the form and update the project list
            else:
                st.error("Please enter a name for the project.")

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

def display_analytics_page():
    """Display analytics dashboard and statistics related to AI image generation"""
    st.title("📊 Analytics Dashboard")
    st.markdown("Gain insights into your AI image generation activity, model usage, and trends")
    
    # Check for required libraries for analytics
    if not pd or not px:
        st.error("Pandas and Plotly are required for the Analytics dashboard. Please install them: `pip install pandas plotly`")
        return

    # --- Section 1: Overall Statistics ---
    st.markdown("### 📈 Overall Statistics")
    stats_cols = st.columns(4) # Create 4 columns for key metrics
    
    with stats_cols[0]:
        st.metric("Total Tasks Created", st.session_state.stats['total_tasks'])
    
    with stats_cols[1]:
        st.metric("Images Generated", st.session_state.stats['total_images'])
    
    with stats_cols[2]:
        st.metric("Uploaded to Drive", st.session_state.stats['uploaded_images'])
    
    with stats_cols[3]:
        st.metric("Total API Calls", st.session_state.stats['total_api_calls'])
    
    st.divider() # Separator
    
    # --- Section 2: Model Usage Analysis ---
    st.markdown("### 🤖 Model Usage")
    
    # Recalculate aggregated model usage from task history for accuracy
    aggregated_model_usage = {}
    for task in st.session_state.task_history:
        model_key = task.get('model', '').split('/')[-1] if '/' in task.get('model', '') else task.get('model', '') # Extract base model name
        if model_key:
            aggregated_model_usage[model_key] = aggregated_model_usage.get(model_key, 0) + 1

    if aggregated_model_usage: # Only display if there is usage data
        model_stats_list = []
        # Prepare data for DataFrame: Model name, number of uses, percentage of total
        for model, count in sorted(aggregated_model_usage.items(), key=lambda item: item[1], reverse=True):
            total_tasks = st.session_state.stats['total_tasks']
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            model_stats_list.append({
                'Model': model,
                'Uses': count,
                'Percentage': f"{percentage:.1f}%"
            })
        
        df_models = pd.DataFrame(model_stats_list)

        # Layout for model usage charts and table
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("**Usage by Model:**")
            st.dataframe(df_models, use_container_width=True)
        
        with col_m2:
            st.markdown("### Usage Distribution")
            # Create a pie chart for model usage distribution
            fig_models = px.pie(df_models, values='Uses', names='Model', title='Model Usage Distribution')
            st.plotly_chart(fig_models, use_container_width=True)
            
            # Display metric for the most used model
            if not df_models.empty:
                 most_used = df_models.iloc[0] # First row is the most used model due to sorting
                 st.metric("Most Used Model", most_used['Model'], f"{most_used['Uses']} uses")

    else:
        st.info("No model usage data recorded yet. Start generating images to populate this section!")
    
    st.divider() # Separator
    
    # --- Section 3: Tag Analytics ---
    st.markdown("### 🏷️ Tag Analytics")
    
    if st.session_state.stats['tags_used']: # Check if any tags have been used
        tag_data = st.session_state.stats['tags_used']
        
        tag_stats_list = []
        # Prepare data for tag statistics, sorted by count
        for tag, count in sorted(tag_data.items(), key=lambda item: item[1], reverse=True):
            tag_stats_list.append({'Tag': tag, 'Count': count})
        
        df_tags = pd.DataFrame(tag_stats_list)
        
        # Layout for tag analytics
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("**Top Tags:**")
            st.dataframe(df_tags.head(10), use_container_width=True) # Display top 10 tags
        
        with col_t2:
            st.metric("Total Unique Tags Used", len(tag_data))
            st.metric("Total Tagged Images (Approx.)", sum(tag_data.values())) # Sum of counts is approx total tag instances
            
            st.markdown("### Tag Usage Distribution")
            # Create a bar chart for top tag usage
            fig_tags = px.bar(df_tags.head(15), x='Tag', y='Count', title='Top 15 Tag Usage') # Limit to top 15 for clarity
            st.plotly_chart(fig_tags, use_container_width=True)

    else:
        st.info("No tag data available yet. Add tags to your generated images to see tag analytics!")
    
    st.divider() # Separator
    
    # --- Section 4: Daily Usage Trends ---
    st.markdown("### 📅 Daily Usage Trends")
    
    if st.session_state.stats['daily_usage']: # Check if daily usage data exists
        daily_data = st.session_state.stats['daily_usage']
        
        # Prepare data for plotting: ensure dates are sorted and in correct format
        days = sorted(daily_data.keys())
        counts = [daily_data[day] for day in days]
        
        df_daily = pd.DataFrame({'Date': days, 'Generations': counts})
        df_daily['Date'] = pd.to_datetime(df_daily['Date']) # Convert to datetime objects for proper plotting
        
        st.markdown("**Generations per Day:**")
        # Create a line chart for daily generation trends
        fig_daily = px.line(df_daily, x='Date', y='Generations', title='Daily Generation Trends Over Time')
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Display recent daily activity
        st.markdown("**Recent Activity:**")
        sorted_days = sorted(daily_data.items(), key=lambda item: item[0], reverse=True)[:7] # Get last 7 days
        for date, count in sorted_days:
            st.write(f"- **{date}:** {count} generations")
    else:
        st.info("No daily usage data recorded yet.")
    
    st.divider() # Separator
    
    # --- Section 5: Hourly Usage Patterns ---
    st.markdown("### ⏰ Hourly Usage Patterns")
    if st.session_state.stats['hourly_usage']: # Check if hourly usage data exists
        hourly_data = st.session_state.stats['hourly_usage']
        
        # Prepare data for plotting
        hours = sorted(hourly_data.keys())
        counts = [hourly_data[hour] for hour in hours]
        
        df_hourly = pd.DataFrame({'Hour': hours, 'Generations': counts})
        df_hourly['Hour_dt'] = pd.to_datetime(df_hourly['Hour']) # Convert to datetime for sorting and plotting
        
        st.markdown("**Generations per Hour of Day:**")
        # Create a line chart for hourly patterns, sorted by time
        fig_hourly = px.line(df_hourly.sort_values('Hour_dt'), x='Hour_dt', y='Generations', title='Hourly Generation Patterns')
        st.plotly_chart(fig_hourly, use_container_width=True)
    else:
        st.info("No hourly usage data recorded yet.")

    st.divider() # Separator
    
    # --- Section 6: Success Rate Analysis ---
    st.markdown("### ✅ Success Rate Analysis")
    
    # Columns for success/failure metrics
    success_cols = st.columns(3)
    
    with success_cols[0]:
        st.metric("Successful Tasks", st.session_state.stats['successful_tasks'])
    
    with success_cols[1]:
        st.metric("Failed Tasks", st.session_state.stats['failed_tasks'])
    
    with success_cols[2]:
        total_tasks = st.session_state.stats['total_tasks']
        if total_tasks > 0:
            success_rate = (st.session_state.stats['successful_tasks'] / total_tasks) * 100
            st.metric("Overall Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Overall Success Rate", "N/A")

# ============================================================================
# PAGE: DATA EXPORT/IMPORT
# ============================================================================

def display_data_page():
    """Display data management page for exporting and importing data"""
    st.title("💾 Data Management")
    st.markdown("Export your generation history and settings, or import backups")
    
    # Tabs for different data management actions
    tab1, tab2, tab3 = st.tabs(["📤 Export Data", "📥 Import Data", "🗑️ Clear Data"])
    
    with tab1:
        st.markdown("### Export Your Data")
        
        # --- CSV Export ---
        st.markdown("#### 📄 Export Generation Log as CSV")
        
        csv_data_string = export_to_csv() # Get CSV data from session state
        
        if csv_data_string:
            st.download_button(
                label="💾 Download CSV",
                data=csv_data_string,
                # Dynamic filename with current date
                file_name=f"ai_image_studio_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download all your generation data including prompts, models, and links as a CSV file."
            )
            
            st.caption(f"Total entries available for CSV export: {len(st.session_state.csv_data)}")
        else:
            st.info("No generation log data available to export yet.")
        
        st.divider() # Separator
        
        # --- JSON Export (Complete Backup) ---
        st.markdown("#### 📋 Export Complete Backup (JSON)")
        st.warning("This exports all your settings, history, projects, and workflows for backup purposes.")
        
        # Combine all relevant session state data into a single dictionary
        full_data_backup = {
            'csv_data': st.session_state.csv_data, # Generation log entries
            'stats': st.session_state.stats, # Analytics statistics
            'tags': st.session_state.tags, # Image tags
            'favorites': st.session_state.favorites, # Favorite image IDs
            'task_history': st.session_state.task_history, # All task history
            'projects': st.session_state.projects, # Saved projects
            'workflows': st.session_state.workflows, # Saved workflows
            'scheduled_tasks': st.session_state.scheduled_tasks, # Scheduled tasks
            'export_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Timestamp of export
        }
        
        # Convert the dictionary to a JSON string with indentation for readability
        json_data_string = json.dumps(full_data_backup, indent=2)
        
        st.download_button(
            label="💾 Download Complete Backup (JSON)",
            data=json_data_string,
            # Dynamic filename with current date and time
            file_name=f"ai_image_studio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download a complete backup of your app's data and settings."
        )
    
    with tab2:
        st.markdown("### Import Data")
        
        # --- CSV Import ---
        st.markdown("#### 📄 Import CSV Generation Log")
        csv_file_upload = st.file_uploader("Upload CSV file", type=['csv'], key="csv_import_uploader")
        
        if csv_file_upload:
            # Button to trigger CSV import
            if st.button("Import CSV Data", key="import_csv_button"):
                try:
                    success, result = load_csv_file(csv_file_upload) # Call function to load CSV
                    if success:
                        st.success(f"✅ Successfully imported {result} entries from CSV!")
                    else:
                        st.error(f"❌ CSV import failed: {result}") # Display error message if import fails
                except Exception as e:
                    st.error(f"An error occurred during CSV import: {str(e)}")
        
        st.divider() # Separator
        
        # --- JSON Import (Backup Restoration) ---
        st.markdown("#### 📋 Import JSON Backup")
        json_file_upload = st.file_uploader("Upload JSON backup file", type=['json'], key="json_import_uploader")
        
        if json_file_upload:
            # Button to trigger JSON import
            if st.button("Import JSON Backup", key="import_json_button"):
                try:
                    # Read and parse the JSON file content
                    backup_data = json.load(json_file_upload)
                    
                    # Restore data - append to existing state to merge data
                    # Only extend if the data exists and is of the correct type
                    if 'csv_data' in backup_data and isinstance(backup_data['csv_data'], list):
                        st.session_state.csv_data.extend(backup_data['csv_data'])
                    
                    if 'stats' in backup_data and isinstance(backup_data['stats'], dict):
                        # Merge stats dictionaries, sum numeric values
                        for key, value in backup_data['stats'].items():
                            if key in st.session_state.stats:
                                if isinstance(value, dict):
                                    # Update existing dictionary stats (e.g., models_used, tags_used)
                                    st.session_state.stats[key].update(value)
                                elif isinstance(st.session_state.stats[key], (int, float)) and isinstance(value, (int, float)):
                                    # Sum numeric stats (e.g., total_tasks)
                                    st.session_state.stats[key] += value
                                else:
                                    # Overwrite if types differ or not dict/number (use cautiously)
                                    st.session_state.stats[key] = value
                    
                    if 'tags' in backup_data and isinstance(backup_data['tags'], dict):
                        st.session_state.tags.update(backup_data['tags']) # Overwrite or add tags
                    
                    if 'favorites' in backup_data and isinstance(backup_data['favorites'], list):
                        st.session_state.favorites.extend(backup_data['favorites'])
                        # Ensure unique favorites after extending
                        st.session_state.favorites = list(set(st.session_state.favorites))

                    if 'task_history' in backup_data and isinstance(backup_data['task_history'], list):
                        st.session_state.task_history.extend(backup_data['task_history'])
                    
                    if 'projects' in backup_data and isinstance(backup_data['projects'], dict):
                        st.session_state.projects.update(backup_data['projects']) # Overwrite or add projects

                    if 'workflows' in backup_data and isinstance(backup_data['workflows'], dict):
                        st.session_state.workflows.update(backup_data['workflows']) # Overwrite or add workflows

                    if 'scheduled_tasks' in backup_data and isinstance(backup_data['scheduled_tasks'], list):
                        st.session_state.scheduled_tasks.extend(backup_data['scheduled_tasks'])
                    
                    st.success("✅ Backup restored successfully! Some data might have been merged or overwritten.")
                    st.rerun() # Rerun to reflect changes in the UI
                    
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file. Please ensure it's a valid backup file generated by this app.")
                except Exception as e:
                    st.error(f"An error occurred during JSON import: {str(e)}")
    
    with tab3:
        st.markdown("### Clear Data")
        st.warning("⚠️ These actions cannot be undone. Use with caution!")
        
        # Columns for clear data buttons
        clear_cols = st.columns(2)
        
        with clear_cols[0]:
            # Button to clear CSV log data
            if st.button("🗑️ Clear CSV Data Entries", type="secondary"):
                # Add a confirmation prompt (using Streamlit's built-in confirmation if available, or a secondary button)
                if st.button("Confirm Clear CSV", key="confirm_clear_csv_button"):
                    st.session_state.csv_data = [] # Reset CSV data list
                    st.success("CSV data cleared.")
                    st.rerun() # Rerun to update UI
        
        with clear_cols[1]:
            # Button to clear statistics and task history
            if st.button("🗑️ Clear Statistics & History", type="secondary"):
                 # Add a confirmation prompt
                 if st.button("Confirm Clear Stats", key="confirm_clear_stats_button"):
                    # Reset key statistics fields to their defaults
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
                    # Clear task-related lists as well for accurate stats
                    st.session_state.task_history = [] 
                    st.session_state.completed_tasks = []
                    st.session_state.failed_tasks = []
                    st.session_state.active_tasks = []
                    st.success("Statistics and task history cleared.")
                    st.rerun() # Rerun to update UI
        
        st.divider() # Separator
        
        # Button for a full app data reset (clears all session state)
        if st.button("⚠️ Clear ALL App Data (Reset to Defaults)", type="secondary", help="This will reset all application data, including settings, history, projects, and workflows, to their initial state."):
            # Add a confirmation prompt for full reset
            if st.button("Confirm Full Reset", key="confirm_full_reset_button"):
                # Clear all keys from the session state dictionary
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Re-initialize session state with default values
                init_session_state() 
                st.success("All app data cleared. Application reset to default settings.")
                st.rerun() # Rerun to apply default settings

# ============================================================================
# PAGE: SETTINGS
# ============================================================================

def display_settings_page():
    """Display settings and configuration options"""
    st.title("⚙️ Settings & Configuration")
    st.markdown("Manage your Google Drive integration, app preferences, and view system information")
    
    # --- Section 1: Google Services Authentication ---
    st.markdown("### 🔐 Google Services Authentication")
    
    if st.session_state.get('authenticated'): # Check if already authenticated
        st.success("✅ Successfully authenticated with Google services!")
        
        # Display connection status for Drive and Sheets, and App Folder ID
        auth_status_cols = st.columns(3)
        
        with auth_status_cols[0]:
            st.metric("Drive Status", "Connected" if st.session_state.get('drive_service') else "Not Connected")
        
        with auth_status_cols[1]:
            st.metric("Sheets Status", "Connected" if st.session_state.get('sheets_service') else "Not Connected")
        
        with auth_status_cols[2]:
            folder_id = st.session_state.get('app_folder_id', 'N/A')
            # Truncate folder ID if it's too long for display
            display_folder_id = (folder_id[:20] + "...") if isinstance(folder_id, str) and len(folder_id) > 20 else folder_id
            st.metric("App Folder ID", display_folder_id)
        
        # Button to re-authenticate (disconnects current session)
        if st.button("🔄 Re-authenticate / Disconnect", type="secondary"):
            # Clear authentication-related session state variables
            st.session_state.authenticated = False
            st.session_state.drive_service = None
            st.session_state.sheets_service = None
            st.session_state.app_folder_id = None
            st.session_state.spreadsheet_id = None
            st.session_state.service = None # Clear credentials as well
            st.rerun() # Rerun to update UI and prompt for authentication
    
    else: # If not authenticated, display authentication form
        st.info("👇 Enter your Google Service Account JSON credentials or upload the file to connect with Google Drive and Sheets.")
        
        # Text area for pasting JSON credentials
        service_account_json_input = st.text_area(
            "Service Account JSON Credentials",
            height=200,
            help="Paste your Google Cloud service account JSON key content here.",
            placeholder='{\n  "type": "service_account",\n  "project_id": "your-project-id",\n  ...\n}',
            key="settings_json_input"
        )
        
        # File uploader for JSON credentials
        uploaded_file = st.file_uploader(
            "Or Upload Service Account JSON File",
            type=['json'],
            help="Alternatively, upload your Google Cloud service account JSON key file.",
            key="settings_auth_upload"
        )
        
        # Button to initiate authentication
        if st.button("🔐 Authenticate with Google", type="primary"):
            json_to_use = None # Variable to hold the JSON content to be used
            # Prioritize JSON pasted directly, then uploaded file
            if service_account_json_input and service_account_json_input.strip():
                json_to_use = service_account_json_input
            elif uploaded_file:
                try:
                    # Read and decode the uploaded file content
                    json_to_use = uploaded_file.read().decode('utf-8')
                except Exception as e:
                    st.error(f"Error reading uploaded file: {str(e)}")
                    json_to_use = None # Ensure json_to_use remains None if file reading fails
            
            if json_to_use: # Proceed if JSON content is available
                with st.spinner("Authenticating with Google services..."):
                    # Call the authentication function
                    success, message = authenticate_with_service_account(json_to_use)
                    
                    if success:
                        st.success(message) # Display success message
                        
                        # Attempt to create/find the app folder and spreadsheet in Drive/Sheets
                        with st.spinner("Setting up Google Drive folder and tracking spreadsheet..."):
                            folder_id = create_app_folder()
                            if folder_id:
                                st.success(f"✅ App folder '{st.session_state.app_folder_id}' is ready in Google Drive.")
                            else:
                                st.warning("Could not create or find the app folder. Please check permissions and try again.")
                            
                            spreadsheet_id = create_or_get_spreadsheet()
                            if spreadsheet_id:
                                st.success(f"✅ Tracking spreadsheet is ready.")
                            else:
                                st.warning("Could not create or find the tracking spreadsheet. Please check permissions.")
                        
                        time.sleep(1) # Short delay to allow spinners to be visible
                        st.rerun() # Rerun the app to reflect the authentication status and setup
                    else:
                        st.error(message) # Display authentication error message
            else:
                st.error("Please provide your service account JSON credentials either by pasting them or uploading the file.")
        
        # Expander with instructions on how to obtain service account credentials
        with st.expander("ℹ️ How to get Google Service Account Credentials", expanded=False):
            st.markdown("""
            1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
            2. Create a new project or select an existing one.
            3. Enable the **Google Drive API** and **Google Sheets API** for your project:
               - Navigate to `APIs & Services` > `Library`.
               - Search for each API and click `Enable`.
            4. Navigate to `IAM & Admin` > `Service Accounts`.
            5. Click `+ CREATE SERVICE ACCOUNT`. Provide a name and description.
            6. Grant the service account the necessary roles:
               - **`Drive Editor`** (to create/manage files in Drive)
               - **`Sheets Editor`** (to write data to the tracking spreadsheet)
            7. Click `Done`. Then, click on the created service account, go to the `KEYS` tab.
            8. Click `ADD KEY` > `Create new key`. Choose `JSON` and click `Create`.
            9. The JSON key file will download. Copy its entire content and paste it into the text area above, or upload the file directly.
            10. **Important:** Ensure the service account email address (found in the JSON or on the Service Accounts page) is also granted `Editor` access directly to the Google Drive folder where the app stores its files if it's not the root Drive.
            """)
    
    st.divider() # Separator
    
    # --- Section 2: App Preferences ---
    st.markdown("### 🎨 App Preferences")
    
    # Layout for preference settings
    pref_cols = st.columns(2)
    
    with pref_cols[0]:
        # Toggle for auto-uploading to Google Drive
        auto_upload_pref = st.checkbox(
            "Auto-upload generated images to Drive",
            value=st.session_state.get('auto_upload_enabled', True),
            help="If checked and authenticated with Google Drive, all generated images will be automatically uploaded."
        )
        st.session_state.auto_upload_enabled = auto_upload_pref # Update session state immediately
    
    with pref_cols[1]:
        # Slider for library items per page, linked to session state
        items_per_page_pref = st.slider(
            "Library items per page",
            12, 96, st.session_state.get('items_per_page', 12), 12, # Min, Max, Default, Step
            help="Number of items to display per page in the Image Library view."
        )
        st.session_state.items_per_page = items_per_page_pref # Update session state
    
    # Theme selection radio buttons
    theme_options = ["Light", "Dark", "System"]
    current_theme_index = theme_options.index(st.session_state.get('theme', 'dark').capitalize()) # Find index of current theme
    
    theme_pref = st.radio(
        "Select Theme",
        theme_options,
        index=current_theme_index,
        horizontal=True,
        key="theme_selector"
    )
    st.session_state.theme = theme_pref.lower() # Store selected theme in session state (lowercase)

    st.divider() # Separator
    
    # --- Section 3: System Information ---
    st.markdown("### 📊 System Information")
    
    # Display key system and usage metrics
    sys_info_cols = st.columns(3)
    
    with sys_info_cols[0]:
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
    
    with sys_info_cols[1]:
        st.metric("Images in Library (Cached)", len(st.session_state.gdrive_images)) # Display cached count
    
    with sys_info_cols[2]:
        st.metric("CSV Log Entries", len(st.session_state.csv_data))
    
    st.divider() # Separator
    
    # --- Section 4: About ---
    st.markdown("### ℹ️ About")
    st.markdown("""
    **AI Image Studio Pro - Ultimate Edition**
    
    A comprehensive AI image generation and management platform designed for professionals and enthusiasts.
    
    **Features:**
    - Multiple AI models (FLUX, Stable Diffusion, Seedream, GPT-4o, etc.) for text-to-image and editing.
    - Seamless integration with Google Drive and Google Sheets for storage and logging.
    - Robust task management and history tracking.
    - Advanced analytics dashboard with model usage, tag insights, and cost estimations.
    - Workflow automation and task scheduling capabilities.
    - Project organization to group related AI-generated assets.
    - Complete data export and import functionality.
    
    Powered by the [KIE.ai API](https://kie.ai).
    """)

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main function to run the Streamlit application"""
    
    # Initialize session state variables if they don't exist
    init_session_state()

    # Apply selected theme (Light, Dark, or System default)
    if st.session_state.theme == 'dark':
        # Apply dark theme styles
        st.markdown("<style>body {background-color: #1e1e1e; color: white;}</style>", unsafe_allow_html=True)
    elif st.session_state.theme == 'light':
        # Apply light theme styles
        st.markdown("<style>body {background-color: white; color: black;}</style>", unsafe_allow_html=True)
    # 'System' theme relies on Streamlit's default or browser settings

    # --- Sidebar Navigation and Controls ---
    with st.sidebar:
        # App logo or title placeholder
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=AI+Image+Studio+Pro", use_container_width=True)
        
        st.markdown("---") # Separator
        
        st.markdown("### 🔐 Google Auth Status")
        
        # Display authentication status and controls in sidebar
        if not st.session_state.get('authenticated'):
            # If not authenticated, show option to upload service account file
            with st.expander("📤 Upload Service File", expanded=False):
                uploaded_file = st.file_uploader(
                    "Service Account JSON",
                    type=['json'],
                    help="Upload your Google Cloud service account JSON key file.",
                    key="sidebar_auth_upload"
                )
                
                if uploaded_file:
                    try:
                        service_json_content = uploaded_file.read().decode('utf-8')
                        
                        # Button to trigger authentication using the uploaded file
                        if st.button("🔓 Authenticate Now", type="primary"):
                            with st.spinner("Authenticating..."):
                                # Call authentication function
                                success, message = authenticate_with_service_account(service_json_content)
                                
                                if success:
                                    # If authentication is successful, attempt to set up Drive folder and spreadsheet
                                    with st.spinner("Setting up Drive folder and spreadsheet..."):
                                        create_app_folder() # Ensure app folder exists
                                        create_or_get_spreadsheet() # Ensure tracking spreadsheet exists
                                    
                                    st.success("✅ Connected to Google Services!")
                                    time.sleep(1) # Short delay for spinner visibility
                                    st.rerun() # Rerun to update sidebar status
                                else:
                                    st.error(message) # Display authentication error
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
                
                st.caption("Or paste JSON in the 'Settings' page")
        else:
            # If authenticated, show connected status and disconnect button
            st.success("✅ Drive Connected")
            if st.button("🔄 Disconnect", type="secondary"):
                # Reset authentication state
                st.session_state.authenticated = False
                st.session_state.drive_service = None
                st.session_state.sheets_service = None
                st.session_state.app_folder_id = None
                st.session_state.spreadsheet_id = None
                st.session_state.service = None
                st.rerun() # Rerun to update sidebar
        
        st.markdown("---") # Separator
        
        # Sidebar Navigation Radio Buttons
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
            label_visibility="collapsed" # Hide labels, only show the buttons
        )
        
        st.markdown("---") # Separator
        
        # Quick Stats displayed in sidebar
        st.markdown("### 📈 Quick Stats")
        st.metric("Total Tasks", st.session_state.stats['total_tasks'])
        st.metric("Images Generated", st.session_state.stats['total_images'])
        # Calculate success rate for display
        total_tasks_stat = st.session_state.stats['total_tasks']
        success_rate_stat = 0
        if total_tasks_stat > 0:
            success_rate_stat = (st.session_state.stats['successful_tasks'] / total_tasks_stat * 100)
        st.metric("Success Rate", f"{success_rate_stat:.1f}%")
        
        # Display warning if there are active tasks
        if st.session_state.active_tasks:
            st.markdown("---")
            st.warning(f"⚡ {len(st.session_state.active_tasks)} Active Task(s)")
        
        st.markdown("---") # Separator
        
        # Final status indicators in sidebar
        if st.session_state.get('authenticated'):
            st.success("✅ Drive Connected")
            if st.session_state.app_folder_id:
                # Display truncated app folder ID for reference
                folder_id_short = st.session_state.app_folder_id[:20] + "..." if st.session_state.app_folder_id and len(st.session_state.app_folder_id) > 20 else st.session_state.app_folder_id
                st.caption(f"App Folder: {folder_id_short}")
        else:
            st.warning("⚠️ Drive Not Connected")
        
        st.markdown("---") # Separator
        
        # App version and footer info
        st.caption("v4.0 Ultimate Pro Edition")
        st.caption("Powered by KIE.ai")
    
    # --- Main Content Area - Render page based on selected navigation ---
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
    
    # --- Footer Section (displayed at the bottom of the main content area) ---
    st.markdown("---") # Separator
    
    # Footer metrics arranged in columns
    footer_cols = st.columns(4)
    
    with footer_cols[0]:
        st.caption(f"📊 {st.session_state.stats['total_tasks']} Total Tasks")
    
    with footer_cols[1]:
        st.caption(f"🖼️ {st.session_state.stats['total_images']} Images Generated")
    
    with footer_cols[2]:
        st.caption(f"✅ {st.session_state.stats['successful_tasks']} Successful")
    
    with footer_cols[3]:
        st.caption(f"⚡ {len(st.session_state.active_tasks)} Active Now")

# Entry point for the Streamlit application
if __name__ == "__main__":
    main()

