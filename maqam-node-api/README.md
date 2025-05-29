# MAQAM Node.js API (`maqam-node-api`)

This project provides the backend API for communication with Lyrion Media Server and Squeezelite, as well as managing user preferences for the MAQAM audio system.

## Prerequisites

*   Node.js (v16 or newer recommended)
*   npm

## Setup

1.  Clone the repository (or ensure this API is part of the main MAQAM OS repository).
2.  Navigate to the `maqam-node-api` directory.
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Create a `.env` file by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
5.  Edit the `.env` file and set your `NODE_API_KEY`. Other environment variables for Lyrion/Squeezelite URLs might be added later.

## Available Scripts

*   `npm run build`: Compiles TypeScript to JavaScript (output to `dist/`).
*   `npm start`: Starts the production server (requires prior build).
*   `npm run dev`: Starts the development server with auto-reloading using `ts-node-dev`.
*   `npm run lint`: Lints the TypeScript code using ESLint.
*   `npm test`: Runs unit and integration tests using Jest.

## API Endpoints (Initial Overview)

All API endpoints are prefixed with `/api`. Protected endpoints require an `X-API-Key` header.

*   **System**
    *   `GET /system/info`: Get basic API information (public).
    *   `GET /system/preferences`: Get user preferences (protected).
    *   `POST /system/preferences`: Set user preferences (protected).
*   **Lyrion (Mocked)**
    *   `GET /lyrion/status`: Get Lyrion status (protected).
    *   `POST /lyrion/command`: Send a command to Lyrion (protected).
*   **Squeezelite (Mocked)**
    *   `GET /squeezelite/status`: Get Squeezelite status (protected).
    *   `POST /squeezelite/command`: Send a command to Squeezelite (protected).

## Project Structure

*   `src/`: TypeScript source code
    *   `app.ts`: Main Express application setup.
    *   `server.ts`: Server entry point.
    *   `config/`: Configuration loading.
    *   `api/`: Routes, controllers, middleware.
    *   `services/`: Business logic (communication with Lyrion, Squeezelite, preferences).
    *   `utils/`: Utility functions.
*   `dist/`: Compiled JavaScript code (output of build).
*   `tests/`: Test files (unit and integration).

## Further Development

This API will be expanded to include real communication with Lyrion and Squeezelite, and potentially other system management features as per the MAQAM project SDD.
