import streamlit as st
import os
import shutil
from pathlib import Path
import time
import pandas as pd
from datetime import datetime
import plotly.express as px
import humanize
from PIL import Image
import mimetypes
import magic as magic_lib  # Rename to avoid conflict
import hashlib
from collections import defaultdict
import platform
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog

# Function to normalize path for current OS
def normalize_path(path):
    """Convert path to the correct format for the current OS."""
    return str(Path(path))

# Function to get the correct magic library based on OS
def get_magic():
    """Get the appropriate magic library based on the OS."""
    if platform.system() == "Windows":
        try:
            import magic
            return magic
        except ImportError:
            st.error("""
                python-magic-bin needs to be installed on Windows.
                Please run: pip install python-magic-bin
                """)
            return None
    else:
        return magic_lib  # Use renamed import

# Function to get the correct magic library based on OS
def get_magic():
    """Get the appropriate magic library based on the OS."""
    if platform.system() == "Windows":
        try:
            import magic
            return magic
        except ImportError:
            st.error("""
                python-magic-bin needs to be installed on Windows.
                Please run: pip install python-magic-bin
                """)
            return None
    else:
        return magic_lib  # Use renamed import

def get_file_hash(file_path, block_size=65536):
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def get_file_stats(directory):
    """Get statistics about files in the directory."""
    total_files = 0
    total_size = 0
    extensions = set()
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_files += 1
                total_size += os.path.getsize(file_path)
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    extensions.add(ext)
            except Exception:
                continue
                
    return {
        'total_files': total_files,
        'total_size': total_size,
        'extensions': extensions
    }

def display_directory_stats(directory):
    """Display statistics about the selected directory."""
    stats = get_file_stats(directory)
    
    st.markdown(f"""
    <div class="stat-box">
        <h4>📊 Directory Overview</h4>
        <p>📁 Total Files: {stats['total_files']}</p>
        <p>💾 Total Size: {humanize.naturalsize(stats['total_size'])}</p>
        <p>🔤 Unique Extensions: {len(stats['extensions'])}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if stats['extensions']:
        ext_df = pd.DataFrame(
            [(ext, sum(1 for f in Path(directory).rglob(f"*{ext}")))
             for ext in stats['extensions']],
            columns=['Extension', 'Count']
        ).sort_values('Count', ascending=False)
        
        fig = px.bar(ext_df, x='Extension', y='Count',
                    title='File Extensions Distribution',
                    labels={'Extension': 'File Extension', 'Count': 'Number of Files'},
                    color='Count',
                    color_continuous_scale='Viridis')
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#1a1a1a'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def organize_files(directory):
    """
    Organize files in the given directory based on the selected profile and settings.
    Returns: (success, files_moved, skipped_files, total_size, duration)
    """
    try:
        start_time = time.time()
        files_moved = defaultdict(int)
        skipped_files = []
        total_size = 0
        
        # Create organization structure
        profile = ORGANIZATION_PROFILES.get(st.session_state.get('selected_profile', 'Standard'))
        if not profile:
            st.error("Invalid organization profile selected!")
            return False, {}, [], 0, 0
            
        # Create base directories
        for category in profile['categories'].keys():
            category_path = os.path.join(directory, category)
            os.makedirs(category_path, exist_ok=True)
            
        # Get magic instance based on OS
        magic_instance = get_magic()
        if not magic_instance:
            st.error("Unable to initialize magic library for file type detection")
            return False, {}, [], 0, 0
            
        # Process each file
        for root, _, files in os.walk(directory):
            for filename in files:
                try:
                    file_path = os.path.join(root, filename)
                    
                    # Skip files in category folders
                    if any(category in root for category in profile['categories'].keys()):
                        continue
                        
                    # Get file details
                    file_size = os.path.getsize(file_path)
                    try:
                        file_type = magic_instance.from_file(file_path, mime=True)
                    except Exception:
                        # Fallback to mimetypes if magic fails
                        file_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                    
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    # Determine category
                    category = None
                    for cat, rules in profile['categories'].items():
                        if (file_type in rules.get('mime_types', []) or
                            file_ext in rules.get('extensions', []) or
                            any(pattern in filename.lower() for pattern in rules.get('patterns', []))):
                            category = cat
                            break
                            
                    if not category:
                        category = 'Others'
                        
                    # Create date-based subfolder if enabled
                    if st.session_state.get('use_date_folders', False):
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        date_folder = mod_time.strftime('%Y-%m')
                        category = os.path.join(category, date_folder)
                        os.makedirs(os.path.join(directory, category), exist_ok=True)
                        
                    # Move file
                    dest_path = os.path.join(directory, category, filename)
                    if os.path.exists(dest_path):
                        # Handle duplicates
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_path):
                            new_name = f"{base}_{counter}{ext}"
                            dest_path = os.path.join(directory, category, new_name)
                            counter += 1
                            
                    shutil.move(file_path, dest_path)
                    files_moved[category] += 1
                    total_size += file_size
                    
                except Exception as e:
                    skipped_files.append((filename, str(e)))
                    continue
                    
        # Remove empty folders if enabled
        if st.session_state.get('remove_empty_folders', False):
            for root, dirs, files in os.walk(directory, topdown=False):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        if not os.listdir(dir_path):  # Check if directory is empty
                            os.rmdir(dir_path)
                    except Exception:
                        continue
                        
        duration = time.time() - start_time
        return True, files_moved, skipped_files, total_size, duration
        
    except Exception as e:
        st.error(f"Error organizing files: {str(e)}")
        return False, {}, [], 0, 0

def open_file_dialog():
    """Open a directory picker dialog appropriate for the current OS."""
    try:
        if platform.system() == "Darwin":  # macOS
            script = '''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "Select a folder to organize"
                return POSIX path of folderPath
            end tell
            '''
            proc = subprocess.Popen(['osascript', '-e', script],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            result = proc.communicate()
            
            if proc.returncode == 0 and result[0]:
                return result[0].decode('utf-8').strip()
        else:  # Windows and other systems
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            selected_path = filedialog.askdirectory()
            
            if selected_path:
                return normalize_path(selected_path)
    except Exception as e:
        st.error(f"Error opening file picker: {str(e)}")
    return None

# Initialize session state
if 'organization_history' not in st.session_state:
    st.session_state.organization_history = []
if 'total_files_organized' not in st.session_state:
    st.session_state.total_files_organized = 0
if 'preview_files' not in st.session_state:
    st.session_state.preview_files = []
if 'duplicate_files' not in st.session_state:
    st.session_state.duplicate_files = defaultdict(list)
if 'file_search_results' not in st.session_state:
    st.session_state.file_search_results = []
if 'custom_extensions' not in st.session_state:
    st.session_state.custom_extensions = {}
if 'dir_input' not in st.session_state:
    st.session_state.dir_input = ""
if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = 0
if 'selected_profile' not in st.session_state:
    st.session_state.selected_profile = "Standard"

def refresh_stats():
    st.session_state.refresh_key += 1

def handle_browse_click():
    selected_path = open_file_dialog()
    if selected_path:
        st.session_state.dir_input = selected_path

# Define organization profiles
ORGANIZATION_PROFILES = {
    "Standard": {
        "categories": {
            "Documents": {
                "mime_types": ["application/pdf", "text/plain", "application/msword"],
                "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
                "patterns": []
            },
            "Images": {
                "mime_types": ["image/"],
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                "patterns": []
            },
            "Videos": {
                "mime_types": ["video/"],
                "extensions": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"],
                "patterns": []
            },
            "Audio": {
                "mime_types": ["audio/"],
                "extensions": [".mp3", ".wav", ".aac", ".flac", ".m4a"],
                "patterns": []
            },
            "Archives": {
                "mime_types": ["application/zip", "application/x-rar"],
                "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "patterns": []
            },
            "Others": {
                "mime_types": [],
                "extensions": [],
                "patterns": []
            }
        }
    }
}

# Page configuration
st.set_page_config(
    page_title="Smart File Organizer Pro",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content area
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.title("🗂️ Smart File Organizer Pro")
    st.markdown("Organize your files intelligently with advanced categorization")
    
    # Directory input
    st.subheader("📂 Select Directory")
    dir_input = st.text_input("Directory Path", value=st.session_state.dir_input, key=f"dir_input_{st.session_state.refresh_key}")
    
    browse_col1, browse_col2 = st.columns([1, 3])
    with browse_col1:
        st.button("📁 Browse", on_click=handle_browse_click, use_container_width=True)

    # Display current directory stats if valid
    if dir_input and os.path.isdir(dir_input):
        st.session_state.dir_input = dir_input  # Update session state
        display_directory_stats(dir_input)
    
        # Organization controls
        st.subheader("🎯 Organization Controls")
        control_cols = st.columns(2)
        
        with control_cols[0]:
            if st.button("🚀 Start Organization", use_container_width=True):
                success, files_moved, skipped, size_processed, duration = organize_files(dir_input)
                if success:
                    st.success(f"""
                        ✅ Organization Complete!
                        - Files Moved: {sum(files_moved.values())}
                        - Size Processed: {humanize.naturalsize(size_processed)}
                        - Duration: {duration:.2f} seconds
                    """)
                    refresh_stats()
        
        with control_cols[1]:
            if st.button("🔄 Refresh Statistics", use_container_width=True, on_click=refresh_stats):
                pass

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings & Options")
    
    # Organization Profiles
    st.subheader("📋 Organization Profiles")
    selected_profile = st.selectbox(
        "Select Profile",
        list(ORGANIZATION_PROFILES.keys()),
        key="selected_profile"
    )
    
    # Organization Options
    st.subheader("🔧 Organization Options")
    
    # Date-based folders
    use_date_folders = st.checkbox(
        "Create Date-Based Folders",
        value=st.session_state.get('use_date_folders', False),
        help="Organize files into year-month folders"
    )
    st.session_state.use_date_folders = use_date_folders
    
    # Empty folder removal
    remove_empty_folders = st.checkbox(
        "Remove Empty Folders",
        value=st.session_state.get('remove_empty_folders', False),
        help="Delete empty folders after organization"
    )
    st.session_state.remove_empty_folders = remove_empty_folders
