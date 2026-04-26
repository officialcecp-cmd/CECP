# CECP Club — Official Website & Portal

Welcome to the official codebase for the **Centre for Electronics & Coding Projects (CECP)** website. This project is built using Django and uses a live Supabase PostgreSQL database for data management.

## 🚀 Getting Started

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository
Open your terminal (Command Prompt, PowerShell, or Git Bash) and run:
```bash
git clone https://github.com/officialcecp-cmd/CECP.git
cd CECP
```

### 2. Set Up the Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.
```bash
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Once the virtual environment is activated, install all required packages:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
You need to set up your `.env` file to connect to the live Supabase database and configure Google OAuth.

1. Create a file named `.env` in the root folder of the project (the same folder as `manage.py`).
2. Open the `.env` file and paste the following exactly as written:

```ini
# Supabase Database Connection
DATABASE_URL=postgresql://postgres.ugozvelpulcwapawtcoz:YOUR_SUPABASE_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# Google OAuth Credentials
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
```
*(Ask Aditya or the Club Head for the exact passwords and keys to fill in here!)*
*(Note: Do not commit your `.env` file to GitHub. It is already ignored in `.gitignore`.)*

### 5. Run the Server
Because we are connected to a live cloud database, **you do not need to run migrations**. You can just start the server immediately!

```bash
python manage.py runserver
```

Go to `http://127.0.0.1:8000/` in your browser.

---

## 🛠️ Development Workflow

* **Pulling latest changes:** Before you start working, always run `git pull origin main` to get the latest code.
* **Database Updates:** Because everyone is connected to the same live Supabase database, if someone adds a project or a team member via the Admin Portal, it will instantly show up on your local machine too! You don't need to create dummy data.
* **Admin Portal:** You can access the Master Dashboard at `http://127.0.0.1:8000/admin/`. If you need master admin access, ask the Club Head for the credentials.
