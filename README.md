# 🎓 Master Thesis AI Corrector (Privacy-Focused)

An intelligent tool that uses **Google Vertex AI** to review and provide feedback on master thesis PDFs. Unlike generic AI APIs, this tool uses the enterprise-grade Vertex AI, ensuring your data is **never used to train Google's models**.

## 💰 Free Trial & Privacy Note

### 🆓 Get Started for Free!

**Google Cloud offers $300 in free credits for 90 days** for new accounts! This is more than enough to review multiple theses.

### 🔒 Privacy Guarantee

This tool uses **Google Vertex AI (Enterprise API)**, which means:
- ✅ Your thesis content is **NOT used to train Google's models**
- ✅ Your data remains private and secure
- ✅ Enterprise-grade data handling and compliance
- ❌ Unlike free generic APIs (like the consumer Gemini API), which may use your data for training

**Why this matters:** When you use free consumer APIs, your thesis content could potentially be used to improve the AI model. With Vertex AI, your academic work stays private.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Google Cloud account (new accounts get $300 free credit!)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Google Cloud Credentials

Follow these steps to get your credentials:

#### 🔹 Step 2.1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter a project name (e.g., "thesis-corrector")
5. Click **"Create"**

#### 🔹 Step 2.2: Enable Vertex AI API

1. In the Google Cloud Console, use the search bar at the top
2. Search for **"Vertex AI API"**
3. Click on it and press **"Enable"**
4. Wait for the API to be enabled (this may take a minute)

#### 🔹 Step 2.3: Create a Service Account

1. In the left sidebar, go to **"IAM & Admin"** → **"Service Accounts"**
2. Click **"Create Service Account"**
3. Enter a name (e.g., "thesis-corrector-service")
4. Click **"Create and Continue"**

#### 🔹 Step 2.4: Grant Permissions

1. In the **"Grant this service account access to project"** section:
   - Search for and select **"Vertex AI User"** (or "Vertex AI-Nutzer" in German)
   - Click **"Continue"**
2. Click **"Done"** (you can skip the optional steps)

#### 🔹 Step 2.5: Create and Download JSON Key

1. Find your newly created service account in the list
2. Click on the service account email
3. Go to the **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"** - the JSON file will download automatically

#### 🔹 Step 2.6: Place the Key File

1. Rename the downloaded file to `auth_key.json`
2. Move it to the root of this project directory:
   ```
   Master_thesis_corrector/
   ├── auth_key.json          ← Place it here
   ├── requirements.txt
   ├── README.md
   └── ...
   ```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Create the .env file
touch .env
```

Then add the following content (replace with your actual project ID):

```ini
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_APPLICATION_CREDENTIALS="auth_key.json"
```

**How to find your Project ID:**
- In Google Cloud Console, look at the project dropdown at the top
- The Project ID is shown there (it's usually different from the project name)

### Step 4: Run the Application

#### Option A: Web Interface (Recommended) 🌐

```bash
streamlit run master_thesis_corrector/ui/app.py
```

Then open your browser to `http://localhost:8501` and upload your PDF!

#### Option B: Command Line 💻

```bash
python -m master_thesis_corrector.main <path_to_your_thesis.pdf> [output_path]
```

Example:
```bash
python -m master_thesis_corrector.main thesis.pdf Review_Report.pdf
```

---

## 📋 What It Does

The Master Thesis Corrector analyzes your thesis PDF and provides:

- **📊 Quantitative Scores**: Clarity, Logic, and Rigor (0-10 scale)
- **📝 Executive Summary**: High-level overview of each section
- **⚠️ Critical Issues**: Structural and logical flaws
- **✏️ Line-by-Line Edits**: Specific corrections with reasoning
- **📄 Professional PDF Report**: Downloadable feedback report

### How It Works

1. **Smart PDF Parsing**: Automatically detects sections based on headers
2. **Concurrent Analysis**: Reviews all sections simultaneously (fast!)
3. **AI-Powered Review**: Uses Gemini 2.5 Pro for comprehensive feedback
4. **Structured Output**: Generates a professional PDF report

---

## 🛠️ Technical Details

### Architecture

- **PDF Parsing**: PyMuPDF (fitz) for intelligent section detection
- **AI Backend**: Google Vertex AI (Gemini 2.5 Pro)
- **Report Generation**: ReportLab for professional PDFs
- **Web Interface**: Streamlit for easy drag-and-drop usage

### Dependencies

- `google-cloud-aiplatform` - Vertex AI SDK
- `pymupdf` - Smart PDF parsing
- `reportlab` - PDF report generation
- `streamlit` - Web interface
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

---

## 🧪 Testing & Debugging

### Test PDF Parsing

To see what sections are detected from your PDF:

```bash
python test_pdf_parsing.py <path_to_pdf>
```

This will show:
- All detected sections
- The full text content of each section
- What gets sent to the model

### Test Model Input

To see exactly what prompt is sent to the model:

```bash
python test_model_input.py <path_to_pdf> [section_name]
```

This helps debug if the model is receiving the correct text or if there are parsing issues.

## ❓ Troubleshooting

### "GOOGLE_CLOUD_PROJECT environment variable is missing"

- Make sure you created the `.env` file in the project root
- Check that the file contains `GOOGLE_CLOUD_PROJECT="your-project-id"`
- Verify your project ID is correct (not the project name!)

### "Service account file not found"

- Ensure `auth_key.json` is in the project root directory
- Check that the filename matches exactly (case-sensitive)
- Verify the path in `.env` is correct: `GOOGLE_APPLICATION_CREDENTIALS="auth_key.json"`

### "google-cloud-aiplatform package not installed"

```bash
pip install google-cloud-aiplatform
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### "Vertex AI API not enabled"

- Go to Google Cloud Console
- Search for "Vertex AI API"
- Click "Enable"

---

## 📚 Project Structure

```
Master_thesis_corrector/
├── api/
│   ├── base.py          # Vertex AI base client
│   └── section.py       # Section review API
├── schema/
│   └── section.py       # Pydantic data models
├── prompts/
│   └── section.py       # AI prompt templates
├── utils/
│   ├── pdf_parser.py    # Smart PDF section detection
│   └── reporter.py      # PDF report generation
├── ui/
│   └── app.py           # Streamlit web interface
├── auth_key.json        # Your service account key (not in git!)
├── .env                 # Environment variables (not in git!)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## 🔐 Security Notes

- ⚠️ **Never commit `auth_key.json` to version control!**
- ⚠️ **Never commit `.env` to version control!**
- ✅ Both files are already in `.gitignore`
- ✅ Keep your service account key secure and private

---

## 📝 License

This project is provided as-is for academic use.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## 📧 Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Verify your Google Cloud setup is correct
3. Ensure all dependencies are installed
4. Check that your service account has the "Vertex AI User" role

---

**Happy thesis reviewing! 🎓✨**
