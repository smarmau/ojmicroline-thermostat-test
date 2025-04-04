# Thermostat Test Application

A menu-driven Python script to interact with OJ Microline WiFi thermostats. This application allows you to test various thermostat operations before integrating with another project.

## Features

- Connect to OJ Microline thermostats (WD5 and WG4 series)
- View thermostat information and status
- Set temperature
- Change preset modes (Schedule, Manual, Comfort, etc.)
- Save configuration for easy reconnection

## Requirements

- Python 3.7+
- ojmicroline-thermostat package (v3.3.0)

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python thermostat_test.py
```

### First-time Setup

1. Select option 1 to configure the API connection
2. Choose your thermostat model (WD5 or WG4 series)
3. Enter your credentials (username, password, and any model-specific details)
4. The application will test the connection and fetch your thermostats

### Menu Options

- **Configure API Connection**: Set up connection details for your thermostats
- **Show Thermostats**: Display all connected thermostats and their basic information
- **View Thermostat Details**: Show detailed information about a specific thermostat
- **Set Temperature**: Change the target temperature of a thermostat
- **Set Preset Mode**: Change the operating mode (Schedule, Manual, Comfort, etc.)
- **Refresh Thermostat Data**: Update thermostat data from the API
- **Exit**: Close the application

## Configuration

The application saves your configuration in a `config.txt` file in the same directory. This file contains your credentials and connection details for easy reconnection.

## Supported Models

- WD5 series (OWD5, MWD5)
- WG4 series (UWG4, AWG4)

## Notes

- This is a test application and should not be used in production environments.
- Your credentials are stored in plain text in the config.txt file. Ensure this file is secured appropriately.
