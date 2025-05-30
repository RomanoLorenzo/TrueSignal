# TrueSignal

TrueSignal: An open source desktop-based signal analyzer. Download the SignaLab software, plug the TrueSignal oscilloscope into the USB and be ready to analyze everything.

## Table of Contents

*   [Overview](#overview)
*   [Features](#features)
*   [Hardware Requirements](#hardware-requirements)
*   [Software Prerequisites](#software-prerequisites)
*   [Installation](#installation)
*   [Running the Application](#running-the-application)
*   [Usage](#usage)
*   [Project Structure](#project-structure)
*   [Screenshots](#screenshots)
*   [License](#license)
*   [Acknowledgements](#acknowledgements)

## Overview

SignaLab is the companion software for the **TrueSignal** hardware, an open-source USB oscilloscope. It provides a user-friendly desktop application for capturing, displaying, and analyzing analog signals in real-time. Whether you're a hobbyist, student, or engineer, SignaLab aims to provide essential oscilloscope functionalities with the flexibility of open-source software.

The application allows users to view signals in both the time domain and frequency domain (via FFT), control display parameters, set up triggers, and record or save data and plots.

## Features

*   **Dual-Channel Oscilloscope:** View two independent analog signals (Channel 1 & Channel 2).
*   **Combined Signal View:** Display both channels overlaid on a single plot.
*   **Real-time FFT Analysis:** Switch between Time Domain and Frequency Domain (FFT) views for each channel.
*   **Adjustable Scales:**
    *   **Voltage/Division:** Customize vertical scaling (V, mV, uV).
    *   **Time/Division:** Customize horizontal scaling (s, ms, µs).
*   **Triggering System:**
    *   Positive Edge Trigger
    *   Negative Edge Trigger
    *   Derivative Trigger with adjustable threshold.
*   **Data & Plot Management:**
    *   **Save Plot:** Export current plot views as images (PNG, JPG, SVG).
    *   **Record Data:** Log raw signal data (Channel 1, Channel 2) to a text file.
    *   **Screen Recording Overlay:** Display current time, tab name, and peak frequencies (in FFT mode) directly on the plot area when recording externally.
*   **Customizable UI:** The application supports theming via JSON style sheets (powered by `PySide6-CustomWidgets`).
*   **Tabbed Interface:**
    *   Tab 1: Combined Channel 1 & 2 View
    *   Tab 2: Channel 1 View
    *   Tab 3: Channel 2 View
    *   Tab 4: Separate Channel 1 & Channel 2 Views
*   **Informational Overlay:** During screen recording (using external tools), the application can overlay time, tab name, and frequency information on the plots.

## Hardware Requirements

*   **TrueSignal Oscilloscope:** This software is designed to work with the TrueSignal open-source USB oscilloscope hardware.
    
*   A computer with a free USB port.

## Software Prerequisites

*   **Python:** Version 3.8 or newer is recommended.
*   **pip:** Python package installer (usually comes with Python).
*   **Git:** For cloning the repository (optional, you can also download a zip).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RomanoLorenzo/TrueSignal.git
    https://github.com/RomanoLorenzo/TrueSignal
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once the installation is complete, you can run the SignaLab application from the project's root directory:


Ensure your TrueSignal oscilloscope hardware is connected to a USB port before starting the application.
## Usage
  Connect Hardware: Plug your TrueSignal oscilloscope into a USB port on your computer.
  Launch SignaLab: Run main.py as described above.
  Interface:
  Tabs: Select different views (Combined, Channel 1, Channel 2, Dual View).
  Controls Panel (Left Sidebar):
  View: Toggle between Time Domain and FFT for each channel.
  Trigger: Enable Positive/Negative edge triggers or Derivative trigger. Adjust the derivative threshold.
  Volt/Div & Time/Div: Use the custom spin boxes and combo boxes to adjust the display scales.
  Menu Bar:
  FILE: Save current plot, Quit.
  DEVICE: (Placeholder for future device-specific actions).
  VIEW: Quickly switch all plots to Time/Frequency domain, or reset V/Div, T/Div to default.
  RECORD: Start/Stop timed recording of raw signal data.
  HELP: View information file.
  Main Window Buttons (if implemented based on main_window.py):
  Start/Stop Recording (for on-screen overlay information).
  python main.py


## Project Structure

*   `.`
    *   `icons/`                  # Application icons
    *   `json-styles/`            # UI theme files
    *   `src/`                    # Source code modules
        *   `Functions.py`        # Core GUI logic, signal source, oscilloscope setup
        *   `OscilloscopeWidget.py` # Oscilloscope plot widget classes
        *   `MenuFunctions.py`    # Handles menu bar actions
        *   `trigger_handler.py`  # Logic for signal triggering
        *   `custom_spinbox.py`   # Custom QDoubleSpinBox for stepped values
        *   `ui_interface.py`     # Auto-generated UI from Qt Designer
        *   `ui_main.py`          # User interface class 
    *   `main.py`                 # Main application entry point
    *   `main_window.py`          # MainWindow class, sets up additional UI elements like trigger/recording controls
    *   `requirements.txt`        # Python package dependencies
    *   `README.md`               # This file
## License


## Screenshots
#TO ADD SOME SCREENSHOTS OF THE WORKING ENVIRONMENT.


## Acknowledgements
* Romano Lorenzo
* Massafra Alessandro
