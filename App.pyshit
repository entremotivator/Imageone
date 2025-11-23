import streamlit as st
import requests
import json
import time
import io
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import base64

# -----------------------------
# PIL (Safe Import)
# -----------------------------
try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None
    st.error("Pillow is missing. Add 'Pillow' to requirements.txt")

# -----------------------------
# Google Drive (Safe Import)
# -----------------------------
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
except Exception:
    service_account = None
    build = None
    MediaIoBaseUpload = None
    MediaIoBaseDownload = None
    st.error("Google API packages missing. Add these to requirements.txt: "
             "google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client")


# ============================================================================
# Streamlit Cloud Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Image Editor Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 10px 0;
    }
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
        padding-bottom: 100%;
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
        object-fit: contain;
        transition: transform 0.3s ease;
    }
    .image-container:hover img {
        transform: scale(1.05);
    }
    .image-placeholder {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #999;
        font-size: 14px;
    }
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
    .status-waiting {
        background-color: #ffc107;
        color: black;
    }
    .status-fail {
        background-color: #dc3545;
        color: white;
    }
    .filter-panel {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
    }
    .view-toggle {
        display: flex;
        gap: 10px;
        margin: 10px 0;
    }
    .metadata-badge {
        display: inline-block;
        background: #e9ecef;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        margin: 2px;
        color: #495057;
    }
    .image-info {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "https://api.kie.ai/api/v1/jobs"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ============================================================================
# Session State Initialization
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'api_key': "",
        'task_history': [],
        'current_task': None,
        'authenticated': False,
        'service': None,
        'credentials': None,
        'generated_images': [],
        'library_images': [],
        'gdrive_folder_id': None,
        'auto_upload': True,
        'polling_active': False,
        'service_account_info': None,
        'upload_queue': [],
        'stats': {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'total_images': 0,
            'uploaded_images': 0
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
        'image_cache': {}  # Cache for image bytes
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# Image Display Functions with Both URL and Bytes Support
# ============================================================================

def get_gdrive_image_bytes(file_id):
    """Download image bytes from Google Drive with caching."""
    if not st.session_state.service:
        return None
    
    # Check cache first
    if file_id in st.session_state.image_cache:
        return st.session_state.image_cache[file_id]
    
    try:
        request = st.session_state.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        image_bytes = fh.read()
        
        # Cache the bytes
        st.session_state.image_cache[file_id] = image_bytes
        return image_bytes
    except Exception as e:
        st.error(f"Error downloading image {file_id}: {str(e)}")
        return None

def display_gdrive_image(file_info, caption="", use_column_width=True, width=None):
    """
    Displays an image from Google Drive with fallback options.
    Priority: Direct bytes download > Original generation URL > Drive URLs
    """
    if not file_info:
        st.warning("⚠️ No file information provided")
        return
    
    file_id = file_info.get('id') or file_info.get('file_id')
    file_name = file_info.get('name') or file_info.get('file_name', 'Unknown')
    
    # Try method 1: Download bytes directly from Google Drive (BEST - No CORS issues)
    if st.session_state.service and file_id:
        image_bytes = get_gdrive_image_bytes(file_id)
        if image_bytes:
            try:
                st.image(image_bytes, caption=caption, use_column_width=use_column_width, width=width)
                return
            except Exception as e:
                st.warning(f"Failed to display from bytes: {str(e)}")
    
    # Try method 2: Use original generation URL (HIGH QUALITY - Direct from API)
    original_url = file_info.get('original_generation_url') or file_info.get('original_url')
    if original_url and original_url.startswith('http'):
        try:
            st.image(original_url, caption=caption, use_column_width=use_column_width, width=width)
            st.caption(f"📡 Loaded from: Original Generation URL")
            return
        except Exception as e:
            st.warning(f"Failed to display from original URL: {str(e)}")
    
    # Try method 3: Google Drive public URLs (Multiple fallbacks)
    drive_urls = [
        file_info.get('drive_public_url'),
        file_info.get('public_image_url'),
        file_info.get('drive_direct_link'),
        file_info.get('direct_link'),
        f"https://drive.google.com/uc?export=view&id={file_id}" if file_id else None,
        f"https://lh3.googleusercontent.com/d/{file_id}" if file_id else None
    ]
    
    for url in drive_urls:
        if url:
            try:
                st.image(url, caption=caption, use_column_width=use_column_width, width=width)
                st.caption(f"📡 Loaded from: Google Drive URL")
                return
            except Exception as e:
                continue
    
    # If all methods fail
    st.error(f"❌ Unable to display image: {file_name}")
    st.info(f"🔗 File ID: {file_id}")
    if file_id and st.session_state.service:
        st.info("💡 Try refreshing the library or re-uploading the image")
    
    # Show download link as last resort
    if file_info.get('webViewLink'):
        st.markdown(f"[🔗 Open in Google Drive]({file_info['webViewLink']})")

def display_image_with_urls(image_url, caption="", use_column_width=True, width=None):
    """Display image from a direct URL (for generated images before upload)."""
    try:
        st.image(image_url, caption=caption, use_column_width=use_column_width, width=width)
    except Exception as e:
        st.error(f"❌ Failed to display image: {str(e)}")
        st.info(f"🔗 URL: {image_url}")

# ============================================================================
# Google Drive Functions with Service Account
# ============================================================================

def authenticate_with_service_account(service_account_json):
    """Authenticate with Google Drive using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_json,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        st.session_state.credentials = credentials
        st.session_state.service = service
        st.session_state.authenticated = True
        return True, "Successfully authenticated with Google Drive"
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
            'parents': [folder_id],
            'description': f'Task ID: {task_id or "N/A"} | Original URL: {image_url}'
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(image_data),
            mimetype=mime_type,
            resumable=True
        )
        
        file = st.session_state.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, webContentLink, mimeType, size, createdTime'
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
        
        uploaded_info = {
            'file_id': file_id,
            'file_name': file.get('name'),
            'drive_web_link': file.get('webViewLink'),
            'drive_content_link': file.get('webContentLink'),
            'drive_public_url': f"https://drive.google.com/uc?export=view&id={file_id}",
            'drive_thumbnail_url': f"https://drive.google.com/thumbnail?id={file_id}&sz=w800",
            'drive_direct_link': f"https://lh3.googleusercontent.com/d/{file_id}",
            'original_generation_url': image_url,
            'mime_type': file.get('mimeType'),
            'file_size': file.get('size'),
            'uploaded_at': datetime.now().isoformat(),
            'created_time': file.get('createdTime'),
            'task_id': task_id,
            'id': file_id,
            'name': file.get('name'),
            'public_image_url': f"https://drive.google.com/uc?export=view&id={file_id}",
            'thumbnail_url': f"https://drive.google.com/thumbnail?id={file_id}&sz=w800",
            'original_url': image_url,
            'webViewLink': file.get('webViewLink'),
            'mimeType': file.get('mimeType'),
            'createdTime': file.get('createdTime'),
            'size': file.get('size')
        }
        
        st.session_state.stats['uploaded_images'] += 1
        return uploaded_info
        
    except Exception as e:
        st.error(f"Error uploading to Google Drive: {str(e)}")
        return None

def list_gdrive_images(folder_id: Optional[str] = None):
    """List all images in Google Drive folder with enhanced URL data."""
    if not st.session_state.service:
        return []
    
    try:
        if not folder_id:
            folder_id = st.session_state.gdrive_folder_id or create_app_folder()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                results = st.session_state.service.files().list(
                    q=f"'{folder_id}' in parents and trashed=false and (mimeType contains 'image')",
                    spaces='drive',
                    fields='files(id, name, webContentLink, webViewLink, createdTime, size, mimeType, thumbnailLink, description)',
                    pageSize=500,
                    orderBy='createdTime desc'
                ).execute()
                
                files = results.get('files', [])
                
                processed_files = []
                for file in files:
                    file_id = file['id']
                    
                    original_url = None
                    description = file.get('description', '')
                    if 'Original URL:' in description:
                        try:
                            original_url = description.split('Original URL:')[1].strip().split(' |')[0]
                        except Exception:
                            pass
                    
                    file['drive_web_link'] = file.get('webViewLink')
                    file['drive_content_link'] = file.get('webContentLink')
                    file['drive_public_url'] = f"https://drive.google.com/uc?export=view&id={file_id}"
                    file['drive_thumbnail_url'] = f"https://drive.google.com/thumbnail?id={file_id}&sz=w800"
                    file['drive_direct_link'] = f"https://lh3.googleusercontent.com/d/{file_id}"
                    file['original_generation_url'] = original_url
                    file['public_image_url'] = file['drive_public_url']
                    file['thumbnail_url'] = file['drive_thumbnail_url']
                    file['original_url'] = original_url
                    file['direct_link'] = file['drive_direct_link']
                    file['createdTime'] = file.get('createdTime', datetime.now().isoformat())
                    file['size'] = file.get('size', 0)
                    
                    processed_files.append(file)
                
                return processed_files
                
            except Exception as retry_error:
                error_msg = str(retry_error).lower()
                if any(err_str in error_msg for err_str in ['ssl', 'decryption', 'bad record mac', 'connection timed out']):
                    if attempt < max_retries - 1:
                        st.warning(f"Attempt {attempt + 1}/{max_retries}: Retrying connection...")
                        time.sleep(2)
                        continue
                    else:
                        st.error(f"❌ Connection failed after {max_retries} attempts.")
                        return []
                else:
                    st.error(f"❌ Failed to list images: {str(retry_error)}")
                    return []
        
        return []
        
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []

def delete_gdrive_file(file_id: str):
    """Delete a file from Google Drive."""
    if not st.session_state.service:
        return False
    
    try:
        st.session_state.service.files().delete(fileId=file_id).execute()
        # Clear from cache
        if file_id in st.session_state.image_cache:
            del st.session_state.image_cache[file_id]
        return True
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False

# ============================================================================
# API Functions
# ============================================================================

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
                return {"success": False, "error": data.get('msg', 'Unknown API error')}
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
                return {"success": False, "error": data.get('msg', 'Unknown API error')}
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
            
            progress_val = min((attempt + 1) / max_attempts, 0.95)
            progress_bar.progress(progress_val)
            status_text.text(f"Status: {state.upper()} | Attempt {attempt + 1}/{max_attempts}")
            
            if state == "success":
                progress_bar.progress(1.0)
                status_text.text("✅ Task completed successfully!")
                st.session_state.stats['successful_tasks'] += 1
                return {"success": True, "data": task_data}
            elif state == "fail":
                progress_bar.empty()
                status_text.text("❌ Task failed")
                st.session_state.stats['failed_tasks'] += 1
                return {"success": False, "error": task_data.get('failMsg', 'Unknown failure'), "data": task_data}
            
            time.sleep(delay)
        else:
            status_text.text(f"⚠️ Error: {result.get('error')}")
            time.sleep(delay)
    
    progress_bar.empty()
    status_text.text("⏱️ Task timed out")
    return {"success": False, "error": "Task timed out after maximum attempts"}

# ============================================================================
# UI Components
# ============================================================================

def render_sidebar():
    """Render the sidebar with configuration and stats."""
    with st.sidebar:
        st.title("🎨 AI Image Editor Pro")
        st.markdown("---")
        
        # Google Drive Authentication
        st.subheader("🔐 Google Drive Setup")
        
        if not st.session_state.authenticated:
            st.info("📋 Upload your Service Account JSON file")
            uploaded_file = st.file_uploader(
                "Service Account JSON",
                type=['json'],
                help="Get this from Google Cloud Console"
            )
            
            if uploaded_file:
                try:
                    service_account_json = json.load(uploaded_file)
                    st.session_state.service_account_info = service_account_json
                    success, message = authenticate_with_service_account(service_account_json)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Invalid JSON file: {str(e)}")
        else:
            st.success("✅ Connected to Google Drive")
            if st.button("🔄 Disconnect", type="secondary"):
                st.session_state.authenticated = False
                st.session_state.service = None
                st.session_state.credentials = None
                st.session_state.image_cache = {}
                st.rerun()
        
        st.markdown("---")
        
        # API Key Configuration
        st.subheader("🔑 API Configuration")
        api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            help="Enter your KIE.AI API key"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📊 Statistics")
        stats = st.session_state.stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tasks", stats['total_tasks'])
            st.metric("Successful", stats['successful_tasks'])
        with col2:
            st.metric("Failed", stats['failed_tasks'])
            st.metric("Uploaded", stats['uploaded_images'])
        
        # Success rate
        if stats['total_tasks'] > 0:
            success_rate = (stats['successful_tasks'] / stats['total_tasks']) * 100
            st.progress(success_rate / 100)
            st.caption(f"Success Rate: {success_rate:.1f}%")

def render_generate_tab():
    """Render the image generation tab."""
    st.header("🎨 Generate Images")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt",
            height=100,
            placeholder="Describe the image you want to generate..."
        )
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            model = st.selectbox(
                "Model",
                ["flux-1.1-pro", "flux-1-pro", "flux-1-dev", "flux-1-schnell"],
                index=0
            )
        
        with col_b:
            width = st.number_input("Width", min_value=256, max_value=1440, value=1024, step=64)
        
        with col_c:
            height = st.number_input("Height", min_value=256, max_value=1440, value=1024, step=64)
        
        col_d, col_e = st.columns(2)
        
        with col_d:
            num_images = st.slider("Number of Images", min_value=1, max_value=4, value=1)
        
        with col_e:
            auto_upload = st.checkbox("Auto-upload to Drive", value=st.session_state.auto_upload)
            st.session_state.auto_upload = auto_upload
        
        if st.button("🚀 Generate", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("❌ Please enter your API key in the sidebar")
                return
            
            if not prompt:
                st.error("❌ Please enter a prompt")
                return
            
            with st.spinner("Creating generation task..."):
                input_params = {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": num_images
                }
                
                result = create_task(st.session_state.api_key, model, input_params)
                
                if result["success"]:
                    task_id = result["task_id"]
                    st.success(f"✅ Task created: {task_id}")
                    
                    poll_result = poll_task_until_complete(st.session_state.api_key, task_id)
                    
                    if poll_result["success"]:
                        task_data = poll_result["data"]
                        output_urls = task_data.get("outputUrls", [])
                        
                        if output_urls:
                            st.success(f"🎉 Generated {len(output_urls)} image(s)!")
                            
                            for idx, url in enumerate(output_urls):
                                st.session_state.stats['total_images'] += 1
                                
                                image_data = {
                                    'url': url,
                                    'prompt': prompt,
                                    'model': model,
                                    'task_id': task_id,
                                    'timestamp': datetime.now().isoformat(),
                                    'index': idx
                                }
                                
                                st.session_state.generated_images.append(image_data)
                                
                                if auto_upload and st.session_state.authenticated:
                                    file_name = f"generated_{task_id}_{idx}.png"
                                    with st.spinner(f"Uploading image {idx + 1}..."):
                                        upload_result = upload_to_gdrive(url, file_name, task_id)
                                        if upload_result:
                                            st.success(f"✅ Uploaded: {file_name}")
                            
                            st.rerun()
                        else:
                            st.error("❌ No images generated")
                    else:
                        st.error(f"❌ Generation failed: {poll_result.get('error')}")
                else:
                    st.error(f"❌ Failed to create task: {result.get('error')}")
    
    with col2:
        st.subheader("📝 Tips")
        st.info("""
        **Prompt Tips:**
        - Be specific and descriptive
        - Include style, mood, lighting
        - Mention composition details
        - Use quality modifiers
        
        **Examples:**
        - "A serene Japanese garden at sunset"
        - "Cyberpunk city street, neon lights"
        - "Portrait of a cat, oil painting style"
        """)
    
    # Display recently generated images
    if st.session_state.generated_images:
        st.markdown("---")
        st.subheader("🖼️ Recently Generated")
        
        cols = st.columns(4)
        for idx, img_data in enumerate(reversed(st.session_state.generated_images[-8:])):
            with cols[idx % 4]:
                display_image_with_urls(
                    img_data['url'],
                    caption=f"{img_data.get('prompt', '')[:30]}...",
                    use_column_width=True
                )
                st.caption(f"🕒 {img_data.get('timestamp', '')[:19]}")

def render_library_tab():
    """Render the image library tab with enhanced viewing."""
    st.header("📚 Image Library")
    
    if not st.session_state.authenticated:
        st.warning("⚠️ Please connect to Google Drive in the sidebar to view your library")
        return
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search", placeholder="Search by name...")
        st.session_state.library_search_query = search_query
    
    with col2:
        view_mode = st.selectbox("View", ["Grid", "List"], index=0 if st.session_state.library_view_mode == 'grid' else 1)
        st.session_state.library_view_mode = view_mode.lower()
    
    with col3:
        sort_by = st.selectbox("Sort", ["Newest", "Oldest", "Name A-Z", "Name Z-A"])
        sort_map = {
            "Newest": "date_desc",
            "Oldest": "date_asc",
            "Name A-Z": "name_asc",
            "Name Z-A": "name_desc"
        }
        st.session_state.library_sort_by = sort_map[sort_by]
    
    with col4:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.image_cache = {}  # Clear cache on refresh
            st.rerun()
    
    # Load images
    with st.spinner("Loading images from Google Drive..."):
        images = list_gdrive_images()
        st.session_state.library_images = images
    
    if not images:
        st.info("📭 No images found in your library. Generate some images first!")
        return
    
    # Filter
    if search_query:
        images = [img for img in images if search_query.lower() in img.get('name', '').lower()]
    
    # Sort
    if st.session_state.library_sort_by == "date_desc":
        images = sorted(images, key=lambda x: x.get('createdTime', ''), reverse=True)
    elif st.session_state.library_sort_by == "date_asc":
        images = sorted(images, key=lambda x: x.get('createdTime', ''))
    elif st.session_state.library_sort_by == "name_asc":
        images = sorted(images, key=lambda x: x.get('name', ''))
    elif st.session_state.library_sort_by == "name_desc":
        images = sorted(images, key=lambda x: x.get('name', ''), reverse=True)
    
    st.markdown(f"**{len(images)}** images found")
    st.markdown("---")
    
    # Display
    if st.session_state.library_view_mode == 'grid':
        cols = st.columns(4)
        for idx, img in enumerate(images):
            with cols[idx % 4]:
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                
                # Display image with fallback methods
                display_gdrive_image(img, caption="", use_column_width=True)
                
                # Image info
                st.markdown(f"**{img.get('name', 'Unknown')[:20]}...**")
                
                # File size
                size_bytes = int(img.get('size', 0))
                if size_bytes > 0:
                    size_mb = size_bytes / (1024 * 1024)
                    st.caption(f"📦 {size_mb:.2f} MB")
                
                # Creation time
                created_time = img.get('createdTime', '')
                if created_time:
                    try:
                        dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        st.caption(f"🕒 {dt.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        pass
                
                # Actions
                col_a, col_b = st.columns(2)
                with col_a:
                    if img.get('webViewLink'):
                        st.link_button("🔗 Drive", img['webViewLink'], use_container_width=True)
                
                with col_b:
                    if st.button("🗑️", key=f"del_{img['id']}", use_container_width=True):
                        if delete_gdrive_file(img['id']):
                            st.success("Deleted!")
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # List view
        for img in images:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    display_gdrive_image(img, caption="", width=150)
                
                with col2:
                    st.markdown(f"### {img.get('name', 'Unknown')}")
                    
                    size_bytes = int(img.get('size', 0))
                    if size_bytes > 0:
                        size_mb = size_bytes / (1024 * 1024)
                        st.write(f"📦 Size: {size_mb:.2f} MB")
                    
                    st.write(f"🆔 ID: `{img.get('id', 'N/A')}`")
                    
                    created_time = img.get('createdTime', '')
                    if created_time:
                        try:
                            dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            st.write(f"🕒 Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        except:
                            pass
                    
                    # Show URLs
                    with st.expander("🔗 View URLs"):
                        if img.get('original_generation_url'):
                            st.code(img['original_generation_url'], language=None)
                            st.caption("⚡ Original Generation URL (Best Quality)")
                        
                        if img.get('drive_public_url'):
                            st.code(img['drive_public_url'], language=None)
                            st.caption("☁️ Google Drive Public URL")
                        
                        if img.get('drive_direct_link'):
                            st.code(img['drive_direct_link'], language=None)
                            st.caption("🔗 Direct Link")
                
                with col3:
                    if img.get('webViewLink'):
                        st.link_button("🔗 Open in Drive", img['webViewLink'], use_container_width=True)
                    
                    if st.button("🗑️ Delete", key=f"del_list_{img['id']}", use_container_width=True):
                        if delete_gdrive_file(img['id']):
                            st.success("Deleted!")
                            st.rerun()
                
                st.markdown("---")

# ============================================================================
# Main App
# ============================================================================

def main():
    """Main application entry point."""
    render_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["🎨 Generate", "📚 Library"])
    
    with tab1:
        render_generate_tab()
    
    with tab2:
        render_library_tab()

if __name__ == "__main__":
    main()
