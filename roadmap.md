# Project Roadmap (Retrospective)

This document outlines the detailed roadmap and the steps taken by each team member to complete the file vault project.

## Dominik - Backend Development
**Responsibility:** Python Server (`backend/main.py`)
- **Step 1: Set up FastAPI application**
  - Initialize the main API structure.
  - Implement CORS middleware to allow communication with the frontend.
- **Step 2: Database and State Management**
  - Define application lifespan events to handle database initialization using `aiosqlite`.
  - Create the `users` and `files` SQLite tables for data persistence.
- **Step 3: Authentication Implementation**
  - Implement password hashing and verification using `bcrypt`.
  - Create JWT token generation (`create_access_token`) and validation logic.
  - Set up `OAuth2PasswordBearer` and `get_current_user` dependency for secure endpoints.
- **Step 4: API Endpoints**
  - Create the `/login` endpoint to authenticate users and return JWTs.
  - Build the `/me` endpoint to verify tokens.
  - Implement the `/files` `GET` endpoint to list available files.
  - Implement the `/files` `POST` endpoint to handle file uploads securely.
  - Build the `/file/{id}` `GET` endpoint for secure file downloading.
  - Create the `/file/{id}` `DELETE` endpoint to allow users to remove their uploaded files.

## Patrik - Operations and Utility Scripts
**Responsibility:** Frontend Containerfile, User Creation Script, Bash Scripts
- **Step 1: Frontend Containerization**
  - Write the `frontend/Containerfile` to package the SvelteKit application and serve it via Nginx.
- **Step 2: User Management Script**
  - Develop `backend/create_user.py` to allow administrators to securely add new users from the CLI.
  - Add password matching validation, security checks, and bcrypt hashing to the script.
- **Step 3: Bash Automation (Part 1)**
  - Write the `scripts/create-user` bash wrapper to easily run the user creation Python script.
  - Contribute to the environment setup scripts (`dev-server`, `deploy`, `stop`).

## Lukas - Operations and Maintenance
**Responsibility:** Backend Containerfile, Archiving Script, Bash Scripts
- **Step 1: Backend Containerization**
  - Write the `backend/Containerfile` to run the FastAPI application efficiently in an isolated environment.
- **Step 2: File Archivation System**
  - Create `backend/archive_files.py` to handle the zipping of old files.
  - Connect to the SQLite database to find files older than 30 days.
  - Implement logic to pack these old files into a `.tar.gz` archive and manage storage space.
- **Step 3: Bash Automation (Part 2)**
  - Write the `scripts/archive-files` bash wrapper to easily run the archiving Python script.
  - Contribute to the main deployment and operational scripts (`dev-server`, `deploy`, `stop`) alongside Patrik.

## Vojta - Infrastructure and API Design
**Responsibility:** Nginx Configuration, API Design
- **Step 1: API Design**
  - Collaborate on defining the structure of the REST API (routes: `/login`, `/me`, `/files`, `/file/{id}`).
  - Determine the JSON payload structures and authentication methods (JWT).
- **Step 2: Nginx Web Server Configuration**
  - Write `frontend/nginx.conf` to configure the web server.
  - Set up routing and fallback to `index.html` for the Single Page Application (SPA) routing to work correctly in production.

## Samuel - Frontend Development
**Responsibility:** Web Interface (`frontend/`)
- **Step 1: Project Setup**
  - Initialize the SvelteKit project with Vite, TypeScript, and Tailwind CSS.
  - Configure code formatting and linting tools (`Prettier`, `Svelte-check`).
- **Step 2: Component Architecture**
  - Create reusable UI components (Buttons, Cards, Inputs, Labels, Tables, Alert Dialogs) using `bits-ui` and Tailwind variants.
  - Implement layout structures (`+layout.svelte`, `+layout.ts`, `layout.css`).
- **Step 3: State and API Management**
  - Build reactive stores/classes for managing the user's authentication state (`login.svelte.ts`).
  - Implement a vault state manager (`vault.svelte.ts`) to handle fetching, uploading, and deleting files.
- **Step 4: User Interface Integration**
  - Build the main application pages and routing interfacing with the backend REST API.
  - Handle client-side routing, JWT storage, file upload progress, and file lists display.
