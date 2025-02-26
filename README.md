# Luna Social

A Full stack social media website made in FastAPI, SQLite, Html, Css and Javascript
inspired from simular social meadia's like Twitter(X) and Bluesky 

## How to Run the Project

### Step 1: Set Up the Backend Environment

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Create a virtual environment:
   
    ```bash
    python -m venv backenv
    ```
    
    If you encounter an error with `python` not found, use `python3` instead:

    ```bash
    python3 -m venv backenv
    ```

4. Activate the virtual environment:

    - On **Linux/macOS**:

        ```bash
        source backenv/bin/activate
        ```

    - On **Windows**:

        ```bash
        .\backenv\Scripts\activate
        ```

5. Install the required dependencies:

    ```bash
    pip install -r Requirements.txt
    ```

### Step 2: Run the Backend

1. Start the FastAPI server with Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```
2. If you encounter an error like `Directory 'src/image/post_image' does not exist`, create the necessary directory:

    ```bash
    mkdir -p src/image/post_image
    ```

   This will start the backend server at `http://127.0.0.1:8000`.

### Step 3: Run the Frontend with Live Server

1. To view the frontend, open `index.html` in your code editor and use the "Live Server" extension to run the app locally.
