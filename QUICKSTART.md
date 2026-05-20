# Quick Start Guide - Redes Sociais Project

## 1️⃣ First Time Setup

### Clone & Navigate
```bash
cd "/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS-"
```

### Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment
1. Copy `.env` template (already created)
2. Fill in your credentials:
   ```bash
   # Social Media APIs
   INSTAGRAM_TOKEN=your_token_here
   TWITTER_API_KEY=xxx

   # VPS Access
   VPS_HOST=your-vps-server.com
   VPS_USER=username
   VPS_SSH_KEY=/path/to/ssh/key

   # Database
   POSTGRES_HOST=localhost
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_pass
   ```

3. Verify config:
   ```bash
   python -c "from execution import utils; utils.logger.info('Config loaded')"
   ```

## 2️⃣ Project Structure

```
REDES SOCIAIS-/
├── CLAUDE.md              ← Architecture & conventions (read first!)
├── directives/            ← How to do things (SOPs)
│   ├── README.md
│   └── EXAMPLE_*.md
├── execution/             ← Deterministic Python scripts
│   ├── __init__.py
│   ├── utils.py           ← Shared utilities
│   ├── TEMPLATE.py        ← Copy this to create new scripts
│   └── [your scripts]
├── .tmp/                  ← Temporary files (auto-generated)
│   ├── scraped_data/
│   ├── exports/
│   └── processing/
├── .env                   ← Secrets (never commit!)
├── requirements.txt
└── .gitignore
```

## 3️⃣ Understanding the 3 Layers

### 🛠️ Layer 1: Directives (What to do)
- **Location**: `directives/`
- **Format**: Markdown SOPs
- **Example**: `directives/EXAMPLE_fetch_instagram_data.md`
- **For you**: Read to understand workflow

### 🧠 Layer 2: Orchestration (Decision making)
- **Who**: Claude (the agent)
- **What**: Reads directives → calls execution scripts → handles errors
- **For you**: I handle this

### ⚙️ Layer 3: Execution (Doing the work)
- **Location**: `execution/`
- **Language**: Python (camelCase)
- **Template**: `execution/TEMPLATE.py`
- **For you**: Create scripts following the template

## 4️⃣ Creating Your First Script

### Step 1: Create Directive
Copy `directives/EXAMPLE_fetch_instagram_data.md` and customize:
```bash
cp directives/EXAMPLE_fetch_instagram_data.md directives/fetch_instagram_data.md
# Edit with your specific requirements
```

### Step 2: Create Execution Script
Copy `execution/TEMPLATE.py`:
```bash
cp execution/TEMPLATE.py execution/fetchInstagramData.py
```

Replace the `fetchData()` function with your actual logic.

### Step 3: Test Locally
```bash
python execution/fetchInstagramData.py
```

Output should be JSON:
```json
{
  "status": "success",
  "timestamp": "2026-04-06T12:34:56Z",
  "data": [...],
  "rowsProcessed": 123
}
```

### Step 4: Update Directive
Document any edge cases or learnings in your directive.

## 5️⃣ Common Tasks

### 🔄 Running a Data Pipeline
1. **Request**: "Fetch Instagram data and save to Sheets"
2. **I read**: `directives/fetch_instagram_data.md`
3. **I call**: `execution/fetchInstagramData.py`
4. **I monitor**: Errors, retry logic, save results
5. **Update**: Directive if we learn something new

### 🐛 Debugging Issues
```bash
# Check logs
tail -f .tmp/processing/debug.log

# Test a script directly
python execution/fetchInstagramData.py --debug

# Check database
python -c "
from execution import utils
results = utils.executeDbQuery('SELECT * FROM posts LIMIT 5')
print(results)
"
```

### 📊 Adding PostgreSQL Table
1. Write SQL migration in `directives/` (document the schema)
2. Execute via utility function in `execution/utils.py`
3. Update `.env` if new credentials needed
4. Test with SELECT query before INSERT

## 6️⃣ SSH Integration to VPS

### Setup (One-time)
```bash
# Add these to .env
VPS_HOST=your-vps.com
VPS_USER=deploy
VPS_SSH_KEY=/Users/moacirpereira/.ssh/id_rsa
VPS_PORT=22
```

### Execute Remote Commands
```python
from execution import utils
from fabric import Connection

def runRemoteCommand(cmd: str) -> str:
    """Execute command on VPS."""
    c = Connection(
        host=utils.getEnv("VPS_HOST"),
        user=utils.getEnv("VPS_USER"),
        connect_kwargs={"key_filename": utils.getEnv("VPS_SSH_KEY")}
    )
    result = c.run(cmd, hide=True)
    return result.stdout
```

### PostgreSQL via SSH Tunnel
```python
import sshtunnel

tunnel = sshtunnel.SSHTunnelForwarder(
    (utils.getEnv("VPS_HOST"), int(utils.getEnv("VPS_PORT", 22))),
    ssh_username=utils.getEnv("VPS_USER"),
    ssh_pkey=utils.getEnv("VPS_SSH_KEY"),
    remote_bind_address=(
        utils.getEnv("POSTGRES_HOST"),
        int(utils.getEnv("POSTGRES_PORT"))
    )
)
tunnel.start()
# Now connect to localhost:tunnel.local_bind_port
```

## 7️⃣ Git Workflow

### Commit Changes
```bash
git add CLAUDE.md directives/ execution/
git commit -m "feat: add Instagram data fetching directive and script"
```

### What NOT to commit
- `.env` (add to .gitignore ✓)
- `.tmp/` (auto-generated)
- `venv/` (Python virtual env)
- `*.log` files
- API credentials

## 8️⃣ Next Steps

1. ✅ Fill in `.env` with real credentials
2. ✅ Test PostgreSQL connection: `python -c "from execution import utils; conn = utils.getDbConnection(); print('OK')"`
3. ✅ Read `CLAUDE.md` for conventions
4. ✅ Create your first directive
5. ✅ Create your first execution script
6. ✅ Test end-to-end

## 🆘 Getting Help

- **Architecture questions**: Read `CLAUDE.md`
- **Directive examples**: Check `directives/EXAMPLE_*.md`
- **Script template**: Copy `execution/TEMPLATE.py`
- **Common errors**: Check directive edge cases section
- **New patterns**: Update `CLAUDE.md` when you discover them

---

**Status**: ✅ Ready to start building
**Architecture**: 3-Layer (Directives → Orchestration → Execution)
**Convention**: camelCase for Python functions
**Last Updated**: 2026-04-06
