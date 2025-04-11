# Age Detection Desktop App

A desktop application for detecting age, emotion, gender, and race from facial images using the deepface library.

## Features

- Live camera capture and analysis
- Batch processing of image folders
- Analysis of age, emotion, gender, and race
- Export results in CSV or JSON format
- Cross-platform support (Windows and macOS)
- User-friendly interface with Sun Valley theme

## Requirements

- Python 3.7+
- Webcam (for live capture feature)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/age-detection-desktop-app.git
   cd age-detection-desktop-app
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Packaging

To create a standalone executable:

### Windows
```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### macOS
```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## License

This project is licensed under the terms of the license included in the repository.
