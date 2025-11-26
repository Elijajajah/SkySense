# Skysense: Ai weather buddy

This project is a simple weather prediction web application using a FastAPI backend and a frontend HTML interface.

---

## Requirements

- Python 3.10+
- Modern web browser (Chrome, Edge, Firefox, etc.)
- VS Code with **Live Server** extension (optional, but recommended)

---

## Setup Instructions

### 1. Install Python

Download and install Python from [python.org](https://www.python.org/downloads/).  
Make sure `python` and `pip` are available in your system PATH.

### 2. Install dependencies

Open a terminal in the `./backend/` folder and run:

```bash
pip install -r requirements.txt
```

This will install all necessary packages for running the FastAPI backend, including `fastapi`, `tensorflow`, `scikit-learn`, and others.

### 3. Run the backend server

From the `./backend/` folder, run:

```bash
uvicorn main:app --reload
```

- This starts the FastAPI server at `http://127.0.0.1:8000`.
- The server will automatically reload if you make changes to the Python files.

### 4. Run the frontend

Open the `index.html` use **Live Server** in VS Code:

- Right-click the `index.html` → **Open with Live Server**
- The frontend will automatically communicate with the backend for predictions.

---

## Usage

1. Fill in the weather data fields or use the **Randomize** button to auto-generate values.
2. Click **Submit** to get a predicted weather type and confidence percentage.
3. The results will display a circle graph with confidence and a short description.

---

## Notes

- Ensure the backend is running before submitting any requests from the frontend.
- The backend is configured with CORS to allow any origin, so it will work locally without additional configuration.
- You can modify `requirements.txt` or the frontend files for customization.

---
