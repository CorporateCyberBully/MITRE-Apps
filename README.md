# AI MITRE ATT&CK Technique Mapping GUI
![GUI Screenshot](https://github.com/actualcyberbully/MITRE-Apps/assets/93664530/ab9a572f-b175-4fe7-908d-cacf75228c83)

This repository contains a Python-based graphical user interface (GUI) application designed to map input sentences describing cybersecurity attacks to corresponding MITRE ATT&CK techniques. Utilizing the `sentence-transformers` library for semantic similarity and the official MITRE ATT&CK dataset, the application provides an intuitive way to find related techniques within the MITRE framework.

## Contents

1. **`aimitremapping_gui.py`**: The main Python script for the application. It features a GUI for users to input descriptions of cybersecurity attacks and view the top 3 matching MITRE ATT&CK techniques based on semantic similarity.

2. **`setup_dependencies.py`**: A setup script to ensure all necessary Python packages are installed before running the main application. It checks for and installs `requests`, `sentence-transformers`, and `numpy`.

## Prerequisites

- Python 3.6 or later.
- Internet connection for downloading the MITRE ATT&CK dataset and Python packages.
- Administrator privileges might be required for installing Python packages.

## Installation and Setup

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
## Running the Application

After setting up the environment, you can run the main application using the following command:

```sh
python setup_dependencies.py
python aimitremapping_gui.py
```
## Upon launching, the application will:

Automatically check for the latest MITRE ATT&CK dataset. If the dataset is older than 30 days or not present, it will download the latest version.
Display a GUI where you can input a description of a cybersecurity attack and submit it for processing.
Show a "Please Wait..." message while processing the input.
Display the top 3 matching MITRE ATT&CK techniques based on the input description.

## Features
Data Update Check: Automatically checks and updates the MITRE ATT&CK dataset if necessary.
Dark Theme: A user-friendly interface with a dark theme for ease of use in various lighting conditions.
Semantic Mapping: Utilizes advanced NLP models to semantically map input sentences to MITRE ATT&CK techniques.

## Troubleshooting
If you encounter any issues with package installation, ensure that your Python environment has the correct permissions and that your Python version is up to date. For more help, please check the official documentation of the packages or submit an issue on this repository.

## Contributions
Contributions to this project are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
