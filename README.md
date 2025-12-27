***


# ScTracker

This software functions as an automated monitoring solution for SoundCloud user profiles. Designed for stability and operational efficiency, it employs a hybrid technical approach to detect new content immediately upon release and archive it locally.

While this script represents a foundational implementation, it effectively solves the problem of automated archiving by combining two specific technologies:
1.  **Detection:** Utilizes `yt-dlp` to parse profile metadata via low-latency network requests, ensuring minimal resource usage during the monitoring phase.
2.  **Retrieval:** Deploys **Selenium** (via headless Chrome) to execute a browser automation sequence for file retrieval through third-party processing services.

## Technical Architecture

The system operates on a continuous polling loop defined by the following logic:

1.  **Poll:** The script queries the target SoundCloud profile at a user-defined interval (default: 100 seconds) to identify the most recent upload.
2.  **Validation:** The URL of the latest track is cross-referenced against a local database (`archive.txt`).
3.  **Execution:** If the URL is not found in the local database:
    *   The system initializes a headless Chrome instance.
    *   It navigates to the external download provider.
    *   It manages DOM interactions to trigger conversion and download.
    *   It verifies file integrity and sanitizes the filename by removing vendor suffixes.
4.  **Commit:** Upon successful download, the URL is written to `archive.txt` to prevent redundant operations.

## Prerequisites

*   **Python 3.8** or higher.
*   **Google Chrome** installed on the host machine.
*   **Selenium WebDriver** (managed automatically or via PATH).
*   **yt-dlp** library.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Struder659/sc-tracker.git
    cd soundcloud-tracker
    ```

2.  **Install required Python packages:**
    ```bash
    pip install yt-dlp selenium
    ```

## Configuration

Before deployment, modify the `config.py` file to set the target parameters:

```
# Target Configuration
TARGET_PROFILE_URL = "[https://soundcloud.com/youruser/tracks]"

# Polling frequency in seconds
CHECK_INTERVAL = 100
```

## Usage

Execute the script via the command line:

```
python tracker.py
```

The process runs in the foreground. To stop execution, send a standard interrupt signal (Ctrl+C).

## Logging and Debugging

The system maintains two operational files in the root directory:

*   **archive.txt:** A persistent ledger of processed URLs. Deleting lines from this file will cause the script to re-download those specific tracks.
*   **tracker_debug.log:** A comprehensive technical log containing timestamped events, state changes, and stack traces for error analysis.

## Disclaimer

This tool is intended solely for educational purposes and personal archiving. The user assumes full responsibility for compliance with SoundCloud's Terms of Service and applicable copyright laws. The author accepts no liability for misuse of this software.
