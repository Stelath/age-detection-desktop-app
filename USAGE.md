# Age Detection Desktop App

This desktop application allows you to analyze faces from either a webcam or batch process folders of images. It uses the deepface library to perform facial analysis, including age detection, gender, emotion, and race recognition.

## Features

- **Live Camera Analysis**: Capture images from your webcam and analyze them in real-time
- **Batch Processing**: Process entire folders of images and export the results
- **Model Selection**: Choose between different face detectors and recognition models
- **Progress Indication**: Shows download and loading progress for models
- **Export Options**: Export results in CSV or JSON format
- **Beautiful UI**: Uses the Sun Valley ttk theme for a modern look

## How to Use

### Starting the Application

Run the application with:

```bash
python main.py
```

### Using the Camera Mode

1. **Preload Models**: Click the "Preload Models" button to download and load all required models. This shows a progress dialog.
2. **Select Face Detector**: Choose a face detector from the dropdown menu (opencv, retinaface, mtcnn, ssd).
3. **Start Camera**: Click "Start Camera" to activate your webcam.
4. **Capture & Analyze**: Click "Capture & Analyze" to take a picture and analyze the face.
5. **View Results**: The analysis results will appear on the right side of the screen.
6. **View All Data**: Click "Show All Data" to see the complete analysis results.
7. **Save Image**: Click "Save Image" to save the captured image and its analysis results.

### Using Batch Processing

1. **Select Folder**: Click "Browse..." to select a folder containing images to process.
2. **Configure Options**: Choose whether to process subfolders recursively and select analysis options.
3. **Start Processing**: Click "Start Processing" to begin batch processing images.
4. **View Results**: When processing is complete, click "View Results" to see the analysis results.
5. **Export Results**: Choose an export format (CSV or JSON) and click "Export Results" to save the results.

## Troubleshooting

- If no face is detected, the app will show a "No face detected" message.
- For batch processing, files that failed analysis will be listed in the "Failed Files" tab.
- If you encounter model loading errors, use the "Preload Models" button to ensure all models are properly downloaded.
- The first run may take some time as it downloads the required models.

## Configuration Options

### Face Detectors

- **opencv**: Fast but less accurate, good for general use
- **retinaface**: More accurate but slower, good for difficult face detection scenarios
- **mtcnn**: Good balance between speed and accuracy
- **ssd**: Fast for multiple faces in an image

### Recognition Models

- **Facenet512**: High accuracy, recommended default
- **VGG-Face**: Good all-around performance
- **Facenet**: Faster than Facenet512 but slightly less accurate
- **OpenFace**: Fast but less accurate
- **DeepFace**: Specialized for certain face recognition tasks
- **ArcFace**: High accuracy but requires more processing power
