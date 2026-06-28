# AI Project Suite - Comprehensive Documentation

## Overview

The AI Project Suite is a comprehensive ecosystem of tools designed to help you organize, process, and automate various AI-related tasks. This suite includes:

- File organization and duplicate detection
- ChatGPT content extraction and categorization
- Searchable prompt database
- RAG (Retrieval Augmented Generation) document ingestion system
- Full-text and semantic search
- Voice-enabled AI assistant
- AI influencer content pipeline
- Social media automation tools
- Project management dashboard
- Browser extension for chat history saving

## System Requirements

- Python 3.8 or higher
- Node.js (for dashboard development)
- At least 4GB of RAM (8GB recommended)
- 10GB of free disk space

## Installation

### 1. Clone or Download the Repository

All components are in the project directory you've created.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Additional Tools (if needed)

Some components may require additional tools:

- Chrome browser (for Selenium automation)
- FFmpeg (for audio processing, if using speech features)

## Component Documentation

### 1. File Organization System

#### File Sorter (`file_sorter.py`)
The file sorter organizes files by type and content, creating a structured directory system.

**Usage:**
```bash
python file_sorter.py
```

**Features:**
- Categorizes files by type (code, documents, images, etc.)
- Uses content analysis to determine file categories
- Handles naming conflicts automatically

#### Duplicate Detector (`duplicate_detector.py`)
Detects and removes duplicate files based on content hashes.

**Usage:**
```bash
python duplicate_detector.py
```

**Features:**
- Content-based duplicate detection using SHA256 hashes
- Multiple removal strategies (keep original, newest, oldest, largest, smallest)
- Move duplicates to a separate folder option

### 2. Content Processing System

#### ChatGPT Extractor (`chatgpt_extractor.py`)
Extracts code snippets and prompts from ChatGPT conversation exports.

**Usage:**
```bash
python chatgpt_extractor.py
```

**Features:**
- Supports JSON, Markdown, and text formats
- Extracts code blocks with language detection
- Handles multiple export formats

#### Prompt Categorizer (`prompt_categorizer.py`)
Categorizes prompts by functionality and project type.

**Usage:**
```bash
python prompt_categorizer.py
```

**Features:**
- Natural language processing for categorization
- Functional categories (coding, research, content creation, etc.)
- Project categories (web development, AI/ML, mobile, etc.)

#### Searchable Prompt Database (`searchable_prompt_db.py`)
Creates a searchable database of prompts and solutions.

**Usage:**
```bash
python searchable_prompt_db.py
```

**Features:**
- SQLite database with full-text search
- Categorization support
- Statistics and reporting

### 3. RAG System

#### Document Ingestor (`rag_document_ingestor.py`)
Ingests documents for the RAG system.

**Usage:**
```bash
python rag_document_ingestor.py
```

**Features:**
- Supports PDF, DOCX, TXT, JSON, HTML, CSV
- Text chunking with overlap
- Multiple file format support

#### Full-Text and Semantic Search (`fulltext_semantic_search.py`)
Provides both full-text and semantic search capabilities.

**Usage:**
```bash
python fulltext_semantic_search.py
```

**Features:**
- TF-IDF based full-text search
- Semantic search using sentence embeddings
- Hybrid search combining both approaches

### 4. AI Assistant

#### Voice AI Assistant (`voice_ai_assistant.py`)
A voice-enabled AI assistant with various automation capabilities.

**Usage:**
```bash
python voice_ai_assistant.py
```

**Configuration:**
- Set up your OpenAI API key in the config file
- Configure wake word and other settings

**Features:**
- Speech recognition and synthesis
- Web search capabilities
- Application control
- Note taking
- System commands

#### Enhanced Voice AI Assistant (`enhanced_voice_ai_assistant.py`)
An enhanced version with additional computer automation features.

**Usage:**
```bash
python enhanced_voice_ai_assistant.py
```

**Additional Features:**
- Screenshot capture
- Screen locking
- System information
- File and folder operations
- Email sending
- Reminder setting
- Mouse and keyboard automation

### 5. Content Creation Pipeline

#### AI Influencer Pipeline (`ai_influencer_pipeline.py`)
Generates content for AI influencers and social media.

**Usage:**
```bash
python ai_influencer_pipeline.py
```

**Configuration:**
- Set up your OpenAI API key in the config file
- Configure content style and target audience

**Features:**
- Generates posts, captions, blog posts, video scripts
- Creates visual content
- Generates hashtags
- Content calendar generation

### 6. Social Media Automation

#### Social Media Automation (`social_media_automation.py`)
Automates social media posting and engagement.

**Usage:**
```bash
python social_media_automation.py
```

**Configuration:**
- Set up API keys for each platform (Twitter, Instagram, Facebook)
- Configure posting schedules
- Set engagement parameters

**Features:**
- Scheduled posting
- Auto-engagement (likes, comments, follows)
- Cross-platform posting
- Engagement metrics tracking

### 7. Project Management Dashboard

#### Dashboard Backend (`project-dashboard/api.py`)
Flask-based API for the project management dashboard.

**Usage:**
```bash
cd project-dashboard
python api.py
```

**Features:**
- RESTful API endpoints
- SQLite database
- Project and task management
- Activity logging
- Integration management

#### Dashboard Frontend (`project-dashboard/index.html`)
Web-based dashboard interface.

**Usage:**
Open `project-dashboard/index.html` in your browser, or serve it through the Flask API.

### 8. Browser Extension

#### Chat History Saver Extension (`browser-extension/`)
A browser extension to save chat histories from various platforms.

**Installation:**
1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `browser-extension` folder

**Features:**
- Saves chats from ChatGPT, Claude, Bard, and other platforms
- Export functionality
- Local storage of chat histories

## Configuration

### API Keys
Most AI-powered components require API keys:

1. **OpenAI API Key**: Required for AI assistant, content generation, and search
2. **Twitter API Keys**: Required for Twitter automation
3. **Instagram Credentials**: Required for Instagram automation
4. **Facebook API Key**: Required for Facebook automation

Create configuration files for each component with your API keys.

### Configuration Files

Each component has its own configuration file:
- `voice_assistant_config.json` - Voice assistant settings
- `ai_influencer_config.json` - Content creation settings
- `social_media_config.json` - Social media automation settings
- `enhanced_voice_assistant_config.json` - Enhanced assistant settings

## Running the System

### 1. Initial Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set up API keys in configuration files
3. Run the file organization tools to sort your existing files

### 2. Daily Operations
1. Use the voice assistant for daily tasks
2. Generate content using the AI influencer pipeline
3. Schedule social media posts
4. Monitor your projects through the dashboard

### 3. Maintenance
1. Regularly run duplicate detection
2. Update content in the RAG system
3. Monitor automation tasks
4. Backup configuration files

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are properly configured
2. **Dependency Issues**: Run `pip install -r requirements.txt` to install missing dependencies
3. **File Permission Errors**: Ensure the application has read/write permissions to the working directories
4. **Speech Recognition Errors**: Check microphone permissions and internet connection

### Performance Tips

1. **Large File Processing**: Process large files during off-peak hours
2. **AI Service Limits**: Be aware of rate limits for AI services
3. **Database Performance**: Regularly clean up old entries from the database
4. **Memory Usage**: Close unused applications when running memory-intensive tasks

## Security Considerations

1. **API Key Security**: Never commit API keys to version control
2. **Data Privacy**: Be mindful of the data being processed and stored
3. **Access Control**: Limit access to sensitive components
4. **Regular Updates**: Keep dependencies updated to address security vulnerabilities

## Extending the System

The system is designed to be extensible:

1. **New File Types**: Add support for additional file types in the document ingestor
2. **New Platforms**: Extend the browser extension to support more chat platforms
3. **New Features**: Add functionality to the AI assistant
4. **New Integrations**: Connect additional services to the dashboard

## Support and Community

For support:
- Check the individual README files in each component directory
- Review the source code comments for implementation details
- Join the community forums (if available)

## License

This project is licensed under the MIT License - see the LICENSE file for details.