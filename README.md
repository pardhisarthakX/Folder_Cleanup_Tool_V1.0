# Folder_Cleanup_Tool_V1.0

A Python-based desktop folder management and cleanup application built with Streamlit. The tool scans folders, analyzes files, detects duplicates using SHA-256 hashing, organizes files into categories, supports controlled file renaming, and provides a safer dry-run mode before making actual changes.

## Features

* Folder scanning and file analysis
* File categorization
* Duplicate file detection
* SHA-256 based duplicate identification
* Automatic file organization
* File renaming
* Dry-run mode for safe preview
* Review folder for detected duplicates
* Archive support
* Undo support for the latest cleanup operation
* Streamlit-based graphical interface
* Configurable cleanup rules
* Test-folder generator for safe testing

## Technology Stack

* Python
* Streamlit
* Pandas
* SHA-256 hashing
* JSON configuration
* Pytest
* Git/GitHub

## Project Structure

```text
Folder-Management-Tool/
│
├── src/
│   └── folder_cleanup/
│       ├── __init__.py
│       ├── ui.py
│       └── ...
│
├── test_folder_generator/
├── tests/
├── config.json
├── requirements.txt
├── pyproject.toml
├── README.md
├── .gitignore
└── LICENSE
```

## Requirements

* Windows 10/11
* Python 3.9 or newer
* Git
* A supported web browser

Python 3.11 or 3.12 is recommended.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/Folder-Management-Tool.git
cd Folder-Management-Tool
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If using Command Prompt:

```cmd
.venv\Scripts\activate
```

### 4. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 5. Install dependencies

Preferred:

```powershell
python -m pip install -e ".[dev]"
```

If the editable installation is unavailable:

```powershell
python -m pip install -r requirements.txt
```

Then:

```powershell
python -m pip install -e .
```

## Running the Application

From the project root:

```powershell
python -m streamlit run src\folder_cleanup\ui.py
```

Using `python -m streamlit` is recommended because it works even when the `streamlit` command is not directly available in the system PATH.

The application normally opens at:

```text
http://localhost:8501
```

## Safe First Run

The application should first be tested using a disposable test folder rather than an important personal folder.

Generate the test folder:

```powershell
cd test_folder_generator
python make_test_folder.py
```

Return to the project root:

```powershell
cd ..
```

Start the application:

```powershell
python -m streamlit run src\folder_cleanup\ui.py
```

Use the generated test folder in the application.

For the first test:

1. Select the test folder.
2. Scan the folder.
3. Keep Dry Run enabled.
4. Review the proposed operations.
5. Only after verifying the results should real cleanup operations be considered.

## Dry Run

Dry Run is designed to allow the application to analyze and preview changes without immediately modifying the original files.

It is strongly recommended to keep Dry Run enabled during initial testing.

## Duplicate Detection

The application uses SHA-256 hashing to compare file contents.

Files with matching hashes can be identified as duplicates even when their filenames are different.

Example:

```text
document1.pdf
document_copy.pdf
```

If their contents are identical, their SHA-256 hashes will also match.

## Configuration

Application behavior can be controlled through:

```text
config.json
```

The configuration contains rules such as file categories and cleanup behavior.

Do not place passwords, API keys, personal credentials, or other secrets in configuration files committed to GitHub.

## Testing

Run the test suite using:

```powershell
python -m pytest
```

If the project contains additional test configuration, follow the configuration defined in `pyproject.toml`.

## Troubleshooting

### Error: Python is not recognized

Install Python and make sure Python is added to PATH.

Verify:

```powershell
python --version
```

### Error: `pip` is not recognized

Use:

```powershell
python -m pip --version
```

instead of calling `pip` directly.

### Error: `pyproject.toml` not found

Make sure the terminal is opened in the actual project root.

The directory should contain:

```text
pyproject.toml
requirements.txt
src/
```

Then run:

```powershell
python -m pip install -e ".[dev]"
```

### Error: `streamlit` is not recognized

Use:

```powershell
python -m streamlit run src\folder_cleanup\ui.py
```

### Error: `ModuleNotFoundError`

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Then reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Error: Port 8501 is already in use

Run Streamlit on another port:

```powershell
python -m streamlit run src\folder_cleanup\ui.py --server.port 8502
```

Then open:

```text
http://localhost:8502
```

### Error: DLL load failed / Application Control policy blocked a file

This can occur when Windows blocks a native Python extension such as a compiled `.pyd`/DLL.

First identify the dependency causing the error:

```powershell
python -c "import pandas; print(pandas.__version__)"
```

If necessary, recreate the virtual environment:

```powershell
deactivate
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If Windows continues reporting that an Application Control policy blocked a DLL, do not disable Windows security protections just to run the application. Check the specific blocked module and the Windows security/organization policy responsible for the block.

### Error: Permission denied while scanning a folder

Some Windows folders are protected.

Try a normal user-owned test folder first.

Avoid testing the application initially against:

```text
C:\Windows
C:\Program Files
C:\Program Files (x86)
```

### Error: File is being used by another process

Close applications that currently have the file open and retry the scan.

### Error: Files are not being detected

Check:

1. The selected path exists.
2. The application has access to the folder.
3. The folder actually contains supported files.
4. The configured file categories/extensions match the files.

### Error: Cleanup changes the wrong folder

Stop the operation and verify the selected path before running cleanup.

Always use Dry Run first.

## Development Workflow

After making changes:

```powershell
git status
git add .
git commit -m "Update folder management tool"
git push
```

## Security

This application works with files on the local computer.

Before running cleanup operations:

* Verify the selected folder.
* Use Dry Run first.
* Keep backups of important files.
* Do not commit personal files to GitHub.
* Do not commit passwords, API keys, or other secrets.

## License

Add the appropriate license for your project before publishing the repository.

## Author

Sarthak Pardhi

## Project Status

Academic / Educational Project
