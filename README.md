# DefexAI 🚀
AI-powered DevOps + Security defect detection before production.

## Structure
## Prerequisites

- Python 3.9 or higher
- RabbitMQ (for async processing)
- OpenAI API key
- (Optional) GitHub Personal Access Token

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DefexAI
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the project root (or export them in your shell):

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Required (for posting comments to GitHub PRs)
GITHUB_BOT_TOKEN=your_github_personal_access_token_here

# Optional (defaults to localhost if not set)
RABBITMQ_URL=amqp://guest:guest@localhost/

# Optional (defaults to gpt-4o-mini if not set)
MODEL=gpt-4o-mini
```

**Note:** The application uses `python-dotenv` to load environment variables from a `.env` file automatically.

#### Setting up GitHub Bot Token

To post comments on GitHub PRs, you need to create a GitHub Personal Access Token (PAT) for your bot user:

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name (e.g., "DefexAI Bot Token")
   - Select the following scopes:
     - `repo` (Full control of private repositories) - for private repos
     - OR `public_repo` (Access public repositories) - for public repos only
   - Click "Generate token"
   - **Copy the token immediately** (you won't be able to see it again)

2. **Set the token as an environment variable:**
   - Add it to your `.env` file as `GITHUB_BOT_TOKEN=your_token_here`
   - Or export it: `export GITHUB_BOT_TOKEN=your_token_here`

3. **Optional: Store as GitHub Secret (for reference):**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DEFEXAI_BOT_TOKEN`
   - Value: Paste your bot token
   - Click "Add secret"
   
   **Note:** The workflow doesn't currently use this secret, but storing it here is useful for reference and future use.

### 5. Start RabbitMQ (if using async processing)

**Using Docker:**
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

**Or install locally:**
- macOS: `brew install rabbitmq && brew services start rabbitmq`
- Ubuntu: `sudo apt-get install rabbitmq-server && sudo systemctl start rabbitmq-server`

### 6. Run the Application

**Start the FastAPI server:**
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

**Run background workers (for async processing):**
```bash
# From the project root
python -m app.workers.review_worker
```

### 7. Expose API with ngrok (for GitHub webhooks/CI integration)

To allow GitHub Actions or webhooks to access your local API, use ngrok to create a public tunnel:

**Install ngrok:**
- macOS: `brew install ngrok/ngrok/ngrok`
- Or download from: https://ngrok.com/download

**Start ngrok tunnel:**
```bash
ngrok http 8000
```

This will provide a public URL (e.g., `https://xxxx-xxxx-xxxx.ngrok-free.app`) that forwards to your local `http://localhost:8000`.

**Note:** 
- The ngrok URL changes each time you restart ngrok (unless you have a paid plan with a static domain)
- Update your GitHub Actions workflow or webhook configuration with the new ngrok URL
- For production, use a proper domain and HTTPS instead of ngrok

## API Endpoints

### Health Check
```bash
GET /health
```

### Code Review
```bash
POST /code/review
Content-Type: application/json

# Option 1: Provide diff directly
{
  "diff": "--- a/file.txt\n+++ b/file.txt\n@@ ...",
  "max_bytes": 500
}

# Option 2: Provide repo and branches
{
  "repo": "owner/repo",
  "base": "main",
  "head": "feature-branch",
  "max_bytes": 1000
}

# Option 3: Provide PR number
{
  "repo": "owner/repo",
  "pr_number": 123
}
```

## Development

Run with auto-reload for development:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
