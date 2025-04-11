# Age Detection Desktop App

A desktop application for analyzing faces in real-time using a webcam or batch processing image folders. The app uses the deepface library to detect age, gender, emotion, and race.

![Application Screenshot](assets/screenshot.jpg)

## Features

- **Live Camera Analysis**: Capture and analyze faces in real-time
- **Batch Processing**: Process entire folders of images at once
- **Face Analysis**: Detects age, gender, emotion, and race
- **Progress Indication**: Shows model download and loading progress
- **Multiple Face Detectors**: Choose between opencv, retinaface, mtcnn, and ssd
- **Multiple Recognition Models**: Support for Facenet512, VGG-Face, ArcFace, and more
- **Export Options**: Export results in CSV or JSON format
- **Beautiful UI**: Modern interface using the Sun Valley ttk theme
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.8+
- Webcam (for live capture feature)
- ~2GB of disk space (for model files)

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install age-detection-app
age-detection-app
```

### Option 2: Clone and install from source

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/age-detection-desktop-app.git
   cd age-detection-desktop-app
   ```

2. Install the app:
   ```bash
   pip install -e .
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Quick Start

1. Launch the application
2. Click "Preload Models" to download and load all required models
3. For camera analysis:
   - Click "Start Camera" to activate your webcam
   - Click "Capture & Analyze" to analyze the face
4. For batch processing:
   - Go to the "Batch Processing" tab
   - Select a folder of images
   - Click "Start Processing"
   - Export the results when complete

See [USAGE.md](USAGE.md) for more detailed instructions.

## Packaging

To create a standalone executable:

### Windows
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

### macOS
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets:assets" main.py
```

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets:assets" main.py
```

## Configuration

The app saves configurations and downloaded models to your user home directory:
- Models: `~/.deepface/weights/`
- Export files: `~/Documents/AgeDetectionExports/` (can be changed in the app)

## Troubleshooting

- **First Run**: The initial run will download model files (~2GB total), which may take some time
- **Camera Access**: Ensure your webcam is connected and not in use by another application
- **No Face Detected**: Try adjusting lighting or positioning, or select a different face detector
- **Model Loading Errors**: Use the "Preload Models" button to initialize all models before using them

## License

This project is licensed under the terms of the license included in the repository.

## Acknowledgements

- [DeepFace](https://github.com/serengil/deepface) - The face analysis library
- [Sun Valley ttk theme](https://github.com/rdbende/Sun-Valley-ttk-theme) - The modern UI theme
