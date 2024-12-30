# VirtualCharacterChat (VCC)

VirtualCharacterChat (VCC) is an interactive platform that allows users to communicate with virtual characters through both voice and image-based conversations. The project relies on Node.js, Python, and Unity, and is dependent on ChatGPT API for its conversational capabilities. This repository contains the core components required for developers to customize and extend the platform.

## Prerequisites

### Required Software
- **Node.js** (v16.0 or higher)
- **Python** (v3.8 or higher)
- **Unity** (2021.3 LTS recommended)

### Required Dependencies
- **Node.js packages**:
  - `ws`
- **Python libraries** (Install via `requirements.txt`)
- **Additional**:
  - `style-bert-vits2` (Ensure `Server.bat` is available and functional)

## Setup Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repository/vcc.git
cd vcc
```

### Step 2: Install Node.js Dependencies
```bash
cd nodejs
npm install
```

### Step 3: Install Python Dependencies
```bash
cd ../python
pip install -r requirements.txt
```

### Step 4: Unity Configuration
- Open the `Unity/Game_UI` project in Unity.
- Ensure all assets are correctly loaded.

### Step 5: Prepare Style-BERT-VITS2
- Download and set up the `style-bert-vits2` directory.
- Ensure `Server.bat` is available for execution.

## Execution Instructions

### 1. Start the Node.js Server
Navigate to the Node.js directory and execute the following:
```bash
node index.js
```

### 2. Start the Python Server
Navigate to the Python `main` folder and run:
```bash
python server.py
```

### 3. Launch Style-BERT-VITS2
Execute `Server.bat` in the prepared `style-bert-vits2` directory.

### 4. Open the Unity Project
- Launch the `Game_UI` scene within Unity.
- Enter play mode to initiate the application.

## Features
- **Voice Interaction**: Real-time voice communication with virtual characters.
- **Image Interaction**: Users can interact with characters using image-based inputs.
- **Customizable Models**: Includes a free Live2D model for character representation (ensure compliance with licensing for commercial use).

## Notes and Limitations
1. **Development State**: This project is incomplete and requires further development for production use.
2. **Licensing**: The included Live2D model is for non-commercial use only. Replace or verify the license before any commercial deployment.
3. **ChatGPT API Dependency**: A valid API key for ChatGPT is required.

## Contribution
We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes with clear messages.
4. Submit a pull request.

## Contact
For any issues or queries, please reach out to [godbyeonghunhan@gmail.com].
