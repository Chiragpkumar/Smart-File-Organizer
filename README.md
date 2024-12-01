# 🚀 Smart File Organizer Pro (v2.0)

A powerful, intelligent file organization tool with advanced categorization, analytics, and a user-friendly interface built with Streamlit.

## ✨ Features

### 📋 Organization Profiles
- **Standard Profile**: General-purpose file organization


### 🎯 Core Capabilities
- 🔍 Content-based file type detection
- 📁 Intelligent file categorization
- 🔄 Duplicate file detection
- 📊 File analytics and statistics
- 📅 Date-based organization
- 🗑️ Empty folder cleanup
- 🎨 Modern, user-friendly interface

### 🛠️ Advanced Features
- Customizable file extensions per category
- MIME type recognition
- Flexible category toggling
- Comprehensive error handling
- Cross-platform compatibility (Windows & macOS)
- File movement history tracking
- Performance metrics

## 🔧 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone [your-repository-url]
cd smart-file-organizer-pro
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Windows-Specific Installation
On Windows, you'll need to install an additional package:
```bash
pip install python-magic-bin
```

## 🚀 Usage

### Starting the Application
```bash
streamlit run app.py
```

### Using the Application

1. **Select Organization Profile**
   - Choose from Standard, Developer, Media Professional, or Custom profiles
   - Each profile comes with pre-configured categories and extensions

2. **Configure Categories**
   - Enable/disable categories as needed
   - Customize file extensions in Custom profile
   - View supported file types per category

3. **Advanced Options**
   - Toggle content-type detection
   - Enable/disable duplicate detection
   - Set date-based organization
   - Configure empty folder cleanup

4. **Select Directory**
   - Choose the directory to organize
   - Review detected files and categories
   - Start organization process

5. **Review Results**
   - View organization statistics
   - Check duplicate files (if enabled)
   - Review file movement history
   - Analyze performance metrics

## 📊 Features in Detail

### Organization Profiles

#### Standard Profile
- Documents (pdf, doc, docx, txt, etc.)
- Images (jpg, png, gif, etc.)
- Audio (mp3, wav, flac, etc.)
- Video (mp4, avi, mkv, etc.)
- Archives (zip, rar, 7z, etc.)


### Analytics Features
- File count per category
- Storage usage analysis
- Duplicate file reports
- Organization history
- Performance metrics

## 🔒 Security Features
- Safe file handling
- No sensitive data storage
- Minimal file system permissions
- Content verification
- Error recovery

## ⚙️ Technical Details

### Dependencies
```
streamlit==1.24.0
pandas==2.0.2
plotly==5.15.0
python-magic==0.4.27
Pillow==9.5.0
humanize==4.6.0
```

### System Requirements
- OS: Windows 10+ / macOS 10.14+
- RAM: 4GB minimum
- Storage: 100MB + space for organized files
- Python: 3.11 or higher

## 🔍 Troubleshooting

### Common Issues

1. **File Type Detection Issues**
   - Ensure python-magic-bin is installed on Windows
   - Check file permissions
   - Verify file isn't corrupted

2. **Performance Issues**
   - Reduce directory size
   - Disable content-type detection
   - Close unnecessary applications

3. **Permission Errors**
   - Run as administrator (if needed)
   - Check folder permissions
   - Verify file access rights

### Error Messages

- "Content type detection not available": Install python-magic-bin (Windows)
- "Permission denied": Check folder access rights
- "File in use": Close applications using the file

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Python community for excellent libraries
- Contributors and users for feedback and support

## 📞 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with:
   - OS version
   - Python version
   - Error message
   - Steps to reproduce
