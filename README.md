# 🎙️ Podcast Relationship Mapper

**Run this AI-powered podcast analysis tool in GitHub Codespaces with just a few clicks!**

This web application analyzes podcast audio using Google's Gemini AI to extract people, organizations, events, and relationships, then creates an interactive knowledge graph to visualize connections.

## 🚀 Quick Start with GitHub Codespaces

### Step 1: Open in Codespaces
1. **Click the green "Code" button** on this repository
2. **Select "Codespaces" tab**
3. **Click "Create codespace on main"**
4. **Wait 2-3 minutes** for the environment to set up automatically

### Step 2: Get Your Google AI API Key
1. **Visit [Google AI Studio](https://aistudio.google.com/app/apikey)**
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the generated key** (it looks like: `AIzaSyC...`)

### Step 3: Set Up Your API Key
In the Codespaces terminal (bottom panel), run:
```bash
export GEMINI_API_KEY="paste_your_api_key_here"
```
*Replace `paste_your_api_key_here` with your actual API key*

### Step 4: Start the Application
```bash
python run_server.py
```

### Step 5: Open the Web Interface
1. **Look for a popup** saying "Your application running on port 8000 is available"
2. **Click "Open in Browser"**
3. **If no popup appears**: Click the "Ports" tab → Click the globe icon next to port 8000

### Step 6: Access the Frontend
1. **Open a new terminal tab** (click the + next to the terminal)
2. **Run the frontend server**:
```bash
cd frontend
python -m http.server 3000
```
3. **Click the globe icon** next to port 3000 in the Ports tab

## 🎯 How to Use

### Upload Your First Podcast
1. **Click "Upload New Episode"** in the web interface
2. **Enter episode title** (e.g., "Episode 1: Introduction")
3. **Select your audio file** (MP3, WAV, etc.)
4. **Click "Upload and Process"**
5. **Wait for processing** (this may take several minutes depending on file size)

### Explore the Knowledge Graph
1. **Select your processed episode** from the dropdown
2. **Click "Load Graph"**
3. **Interact with the visualization**:
   - **Click nodes** to see detailed information
   - **Drag nodes** to rearrange the layout
   - **Zoom and pan** to explore different areas

## ✨ What This Tool Does

### 🧠 AI Analysis
- **Splits audio** into 5-minute chunks for detailed analysis
- **Extracts entities**: People, organizations, events, concepts, source materials
- **Identifies relationships** between entities
- **Links everything** to specific timestamps in the audio

### 📊 Interactive Visualization
- **Network graph** showing all connections
- **Color-coded nodes** by entity type
- **Detailed panels** with timestamp references
- **Searchable and filterable** content

### 🗄️ Data Storage
- **SQLite database** stores all extracted information
- **Persistent storage** across sessions
- **Timestamp references** for fact-checking
- **Ready for PostgreSQL** migration in production

## 🛠️ Troubleshooting

### "GEMINI_API_KEY not set" Error
```bash
# Make sure you've set your API key:
export GEMINI_API_KEY="your_actual_api_key_here"

# Verify it's set:
echo $GEMINI_API_KEY
```

### Port Already in Use
```bash
# Kill any existing processes:
pkill -f "python.*main.py"
pkill -f "python.*http.server"

# Then restart:
python run_server.py
```

### Frontend Not Loading
1. **Check the Ports tab** in Codespaces
2. **Make sure both ports 8000 and 3000 are running**
3. **Try refreshing the browser tab**

### Audio Processing Fails
- **Check file format**: MP3, WAV, AAC, OGG, FLAC are supported
- **File size limit**: Large files (>100MB) may timeout
- **Try shorter clips** for testing (5-10 minutes)

## 🔧 Advanced Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Database Management
```bash
# Reset database (WARNING: deletes all data):
rm podcast_mapper.db
python -c "from database import create_tables; create_tables()"

# Test your setup:
python test_setup.py
```

## 📁 Project Structure
```
├── main.py              # FastAPI backend server
├── run_server.py        # Easy startup script
├── database.py          # Database models and setup
├── audio_processor.py   # AI analysis engine
├── data_service.py      # Data management
├── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html      # Web interface
│   ├── styles.css      # Styling
│   └── app.js          # Frontend logic
└── README.md           # This file
```

## 🎓 For Developers

### API Endpoints
- `POST /api/episodes` - Create new episode
- `POST /api/episodes/{id}/process` - Upload and process audio
- `GET /api/episodes/{id}/graph` - Get graph data
- `GET /api/entities/{id}/details` - Get entity details

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run setup tests
python test_setup.py

# Check API health
curl http://localhost:8000/test
```

## 💡 Tips for Best Results

### Audio File Recommendations
- **File size**: Keep files under 100MB for faster processing
- **Length**: 10-30 minute segments work best for testing
- **Quality**: Clear audio with minimal background noise
- **Format**: MP3 or WAV files are most reliable

### Getting Better AI Analysis
- **Content-rich podcasts** work best (interviews, discussions, documentaries)
- **Clear speech** with minimal overlapping voices
- **Structured content** with distinct topics and names

## 🔍 Understanding the Results

### Entity Types Explained
- **👤 People**: Individuals mentioned (hosts, guests, historical figures)
- **🏢 Organizations**: Companies, institutions, government agencies
- **📅 Events**: Specific occurrences, meetings, historical events
- **💡 Concepts**: Ideas, theories, methodologies, topics
- **📚 Source Material**: Books, documents, studies, websites referenced

### Relationship Types
- **Founded/Created**: Who started what organization or concept
- **Worked at/With**: Employment or collaboration relationships
- **Researched/Studied**: Academic or investigative connections
- **Influenced/Inspired**: Intellectual or creative relationships
- **Participated in**: Event attendance or involvement

## 🗃️ Data Management

### Viewing Your Data
```bash
# See all episodes
curl http://localhost:8000/api/episodes

# Check processing status
curl http://localhost:8000/api/episodes/1

# Export graph data
curl http://localhost:8000/api/episodes/1/graph > episode_1_graph.json
```

### Database Backup
```bash
# Backup your database
cp podcast_mapper.db backup_$(date +%Y%m%d).db

# Restore from backup
cp backup_20241213.db podcast_mapper.db
```

## 🚀 Performance Tips

### For Large Files
1. **Split long podcasts** into 30-60 minute segments
2. **Process during off-peak hours** (Gemini API limits)
3. **Monitor processing** in the browser console for progress

### Memory Management
```bash
# If you run out of memory:
pkill -f python
python run_server.py
```

## 🔐 Privacy & Security

### API Key Security
- **Never commit** your API key to version control
- **Use environment variables** only
- **Regenerate keys** if accidentally exposed

### Data Privacy
- **Audio files** are processed but not permanently stored
- **Extracted text** is saved in the local database
- **No data** is sent to third parties except Google's Gemini API

## 🌟 Example Use Cases

### Research & Journalism
- **Track sources** mentioned across multiple episodes
- **Map relationships** between interview subjects
- **Verify claims** with timestamp references

### Education
- **Study complex topics** with visual relationship maps
- **Create study guides** from lecture recordings
- **Track recurring themes** across course materials

### Content Creation
- **Analyze competitor content** for topic coverage
- **Find connection patterns** for story development
- **Research background** for interview preparation

## 🤝 Getting Help

### If Something Goes Wrong
1. **Check the terminal** for error messages
2. **Look at browser console** (F12 → Console tab)
3. **Restart both servers** if things get stuck
4. **Try a smaller test file** first

### Common Success Patterns
- ✅ Start with a 5-10 minute test file
- ✅ Use clear, interview-style content
- ✅ Wait for "complete" status before loading graph
- ✅ Check both port 8000 and 3000 are accessible

## 📈 Future Roadmap

### Coming Soon
- **Audio playback** with clickable timestamps
- **Search and filter** capabilities
- **Export options** (PDF, CSV, JSON)
- **Batch processing** for multiple files

### Advanced Features
- **User authentication** for multi-user setups
- **PostgreSQL support** for production use
- **API integrations** with podcast platforms
- **Mobile-responsive** interface

---

**🎉 You're all set!** Start by uploading a short podcast clip and explore the knowledge graph it creates. The AI will surprise you with the connections it discovers!