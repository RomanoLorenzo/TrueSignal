from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QCheckBox, QDoubleSpinBox, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from src.ui_main import Ui_MainWindow
from src.OscilloscopeWidget import Signal1Oscilloscope, Signal2Oscilloscope, CombinedOscilloscope

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize oscilloscopes
        self.signal1_osc = None
        self.signal2_osc = None
        self.combined_osc = None
        
        self.setup_trigger_controls()
        self.setup_recording_controls()
        
    def setup_trigger_controls(self):
        # Add derivative trigger checkbox
        self.ui.DerivativeTriggerch = QCheckBox("Derivative Trigger")
        self.ui.DerivativeTriggerch.setChecked(False)
        self.ui.gridLayout.addWidget(self.ui.DerivativeTriggerch, 4, 0)
        
        # Add derivative threshold spinbox
        self.ui.derivativeThresholdSpinBox = QDoubleSpinBox()
        self.ui.derivativeThresholdSpinBox.setRange(0.01, 10.0)
        self.ui.derivativeThresholdSpinBox.setValue(0.1)
        self.ui.derivativeThresholdSpinBox.setSingleStep(0.01)
        self.ui.gridLayout.addWidget(QLabel("Derivative Threshold:"), 4, 1)
        self.ui.gridLayout.addWidget(self.ui.derivativeThresholdSpinBox, 4, 2)
        
        # Connect trigger signals
        self.ui.DerivativeTriggerch.stateChanged.connect(self.on_derivative_trigger_changed)
        self.ui.derivativeThresholdSpinBox.valueChanged.connect(self.on_derivative_threshold_changed)
        
    def setup_recording_controls(self):
        # Add screen recording controls
        record_layout = QHBoxLayout()
        self.ui.StartRecordingButton = QPushButton("Start Recording")
        self.ui.StopRecordingButton = QPushButton("Stop Recording")
        self.ui.StopRecordingButton.setEnabled(False)
        record_layout.addWidget(self.ui.StartRecordingButton)
        record_layout.addWidget(self.ui.StopRecordingButton)
        self.ui.gridLayout.addLayout(record_layout, 5, 0, 1, 3)
        
        # Connect recording signals
        self.ui.StartRecordingButton.clicked.connect(self.start_recording)
        self.ui.StopRecordingButton.clicked.connect(self.stop_recording)
        
    def on_derivative_trigger_changed(self, state):
        threshold = self.ui.derivativeThresholdSpinBox.value()
        for osc in [self.signal1_osc, self.signal2_osc, self.combined_osc]:
            if osc is not None and hasattr(osc, 'trigger_handler'):
                osc.trigger_handler.set_derivative_enabled(state == 2, threshold)  # Qt.Checked = 2
        
    def on_derivative_threshold_changed(self, value):
        if self.ui.DerivativeTriggerch.isChecked():
            for osc in [self.signal1_osc, self.signal2_osc, self.combined_osc]:
                if osc is not None and hasattr(osc, 'trigger_handler'):
                    osc.trigger_handler.set_derivative_threshold(value)
                    
    def start_recording(self):
        current_widget = self.ui.tabWidget.currentWidget()
        if current_widget:
            current_widget.set_tab_name(self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()))
            current_widget.start_recording()
            self.ui.StartRecordingButton.setEnabled(False)
            self.ui.StopRecordingButton.setEnabled(True)
            
    def stop_recording(self):
        current_widget = self.ui.tabWidget.currentWidget()
        if current_widget:
            current_widget.stop_recording()
            self.ui.StartRecordingButton.setEnabled(True)
            self.ui.StopRecordingButton.setEnabled(False) 