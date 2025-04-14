from setuptools import setup, find_packages

setup(
    name="age-detection-app",
    version="0.1.0",
    description="A desktop application for detecting age from facial images",
    author="age-detection-team",
    packages=find_packages(),
    py_modules=["main"],
    include_package_data=True,
    install_requires=[
        "deepface>=0.0.79",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "sv-ttk>=2.0.0",
        "tf-keras",
    ],
    entry_points={
        "console_scripts": [
            "age-detection-app=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
)