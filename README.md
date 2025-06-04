# Orchids SWE Intern Challenge Template

This project consists of a backend built with FastAPI and a frontend built with Next.js and TypeScript.

## Setup

To get this project running, follow these steps:

### 1. Clone the repository

```bash
git clone <repository_url>
cd orchids-challenge
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

The backend uses `uv` for package management. Install the dependencies:

```bash
uv sync
```

### 3. Environment Variables

Create a `.env` file in the `backend` directory with the following content:

```dotenv
BROWSERBASE_API_KEY=your_browserbase_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace `your_browserbase_api_key_here` and `your_gemini_api_key_here` with your actual API keys. You can obtain a Browserbase API key from [Browserbase](https://browserbase.com/) and a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

Add the `.env` file to your `.gitignore` to prevent committing your API keys:

```bash
echo ".env" >> .gitignore
```

### 4. Running the Backend

Make sure you are in the project root directory (`orchids-challenge`). Run the backend development server using `uv`:

```bash
cd .. # Go back to project root if you are in backend directory
python3 -m uvicorn backend.app.main:app --reload
```

Keep this terminal window open.

### 5. Frontend Setup

Open a new terminal window and navigate to the frontend directory:

```bash
cd frontend
```

Install the frontend dependencies using npm:

```bash
npm install
```

### 6. Running the Frontend

Start the frontend development server:

```bash
npm run dev
```

Keep this terminal window open. The frontend should be accessible at `http://localhost:3000`.

## Usage

Open your browser to `http://localhost:3000`. Enter a website URL in the input field and click "Clone Website" to generate an HTML clone.
