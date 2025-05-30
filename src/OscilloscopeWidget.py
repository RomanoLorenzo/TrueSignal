# OscilloscopeWidget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Slot, Signal
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import QDateTime
import pyqtgraph as pg
import numpy as np
from src.trigger_handler import TriggerHandler
import time


class Oscilloscope(QWidget):
    def __init__(self, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('black')
        try:
            pg.setConfigOptions(useOpenGL=True)
        except Exception:
            pg.setConfigOptions(useOpenGL=False)
        self.layout.addWidget(self.plot_widget)
        self.plot = self.plot_widget.plot(pen=pg.mkPen('y', width=2))
        self.buffer_size = buffer_size
        self.sampling_rate_hz = sampling_rate_hz
        self.gui_funcs = gui_functions_ref
        self.y_data = np.zeros(self.buffer_size, dtype=np.float64)
        self.ptr = 0
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(33)  # ~30 FPS display update
        self.display_mode = "Time D."
        self._initial_scale_set = False
        self._last_display_mode = None
        
        self.trigger_handler = TriggerHandler(self.buffer_size)
        
        if hasattr(self.gui_funcs.ui, 'PositiveEdgech'):
            self.gui_funcs.ui.PositiveEdgech.stateChanged.connect(self.on_pos_edge_trigger_changed)
        if hasattr(self.gui_funcs.ui, 'NegativeEdgech'):
            self.gui_funcs.ui.NegativeEdgech.stateChanged.connect(self.on_neg_edge_trigger_changed)
            
        QTimer.singleShot(0, self.initialize_scales)
        
        # Add screen recording attributes
        self.is_recording = False
        self.recording_start_time = None
        self.tab_name = ""  # Will be set by the main window

    def initialize_scales(self):
        if self.display_mode == "Time D.":
            self.plot_widget.setLogMode(x=False, y=False)
            self.plot_widget.setYRange(-1, 1, padding=0.05)
            self.plot_widget.setXRange(0, 0.1, padding=0.05)
            self.update_voltage_scale()
            self.update_time_scale()
            
        elif self.display_mode == "FFT":
            initial_max_freq = self.sampling_rate_hz / 2
            self.plot_widget.setYRange(1e-10, 1, padding=0.05)
            self.plot_widget.setXRange(0, initial_max_freq, padding=0.05)
            
            self.plot_widget.setLogMode(x=False, y=True)
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
            self.plot_widget.setLabel('left', 'Magnitude')
            
            self.plot_widget.setYRange(np.log10(1e-10), 0, padding=0.05)

        self._initial_scale_set = True
        self._last_display_mode = self.display_mode

    @Slot()
    def update_voltage_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'voltdiv_spbx') and hasattr(self.gui_funcs.ui, 'voltdiv_cb')):
            return

        value = self.gui_funcs.ui.voltdiv_spbx.value()
        unit_text = self.gui_funcs.ui.voltdiv_cb.currentText()

        multiplier = 1.0
        if unit_text == "mV":
            multiplier = 1e-3
        elif unit_text == "uV":
            multiplier = 1e-6

        if self.display_mode == "Time D.":
            volt_range_total = 10 * value * multiplier
            self.plot_widget.setYRange(-volt_range_total / 2,
                                       volt_range_total / 2, padding=0.05)
            self.plot_widget.getAxis('left').setLabel(
                'Voltage', units=unit_text)

    @Slot()
    def update_time_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'timediv_spbx') and hasattr(self.gui_funcs.ui, 'timediv_cb')):
            return

        time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
        unit_text = self.gui_funcs.ui.timediv_cb.currentText()

        unit_multiplier = 1.0
        if unit_text == "ms":
            unit_multiplier = 1e-3
        elif unit_text == "us":
            unit_multiplier = 1e-6

        if self.display_mode == "Time D.":
            total_display_window_time = time_per_div_val * unit_multiplier * 10
            self.plot_widget.setXRange(
                0, total_display_window_time, padding=0.01)
            self.plot_widget.getAxis('bottom').setLabel(
                'Time', units=unit_text)

    @Slot(int)
    def on_pos_edge_trigger_changed(self, state):
        self.trigger_handler.set_pos_edge_enabled(state == 2)
        if state == 0:
            self.trigger_handler.unfreeze()

    @Slot(int)
    def on_neg_edge_trigger_changed(self, state):
        self.trigger_handler.set_neg_edge_enabled(state == 2)
        if state == 0:
            self.trigger_handler.unfreeze()

    def add_new_data_point(self, new_data):
        self.y_data[self.ptr] = new_data
        self.ptr = (self.ptr + 1) % self.buffer_size
        
        if self.display_mode == "Time D.":
            trigger_idx = self.trigger_handler.check_trigger(self.y_data)
            if trigger_idx is not None:
                self.center_display_at_trigger(trigger_idx)

    def center_display_at_trigger(self, trigger_idx):
        if not self.trigger_handler.is_frozen:
            return
            
        points_before = self.buffer_size // 2
        points_after = self.buffer_size - points_before
        
        centered_data = np.zeros_like(self.y_data)
        
        for i in range(points_before):
            idx = (trigger_idx - points_before + i) % self.buffer_size
            centered_data[i] = self.y_data[idx]
            
        for i in range(points_after):
            idx = (trigger_idx + i) % self.buffer_size
            centered_data[points_before + i] = self.y_data[idx]
            
        self.y_data = centered_data
        
        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10
            
            trigger_time = total_display_window_time / 2
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.05)
            
            signal_range = np.ptp(self.y_data)
            current_volt_div = self.gui_funcs.ui.voltdiv_spbx.value()
            unit_text_volt = self.gui_funcs.ui.voltdiv_cb.currentText()
            volt_multiplier = 1.0
            if unit_text_volt == "mV":
                volt_multiplier = 1e-3
            elif unit_text_volt == "uV":
                volt_multiplier = 1e-6
                
            current_volt_range = current_volt_div * volt_multiplier * 10
            if signal_range > current_volt_range * 0.8:
                new_volt_div = (signal_range / 8) / volt_multiplier
                self.gui_funcs.ui.voltdiv_spbx.setValue(new_volt_div)
            elif signal_range < current_volt_range * 0.2:
                new_volt_div = (signal_range / 4) / volt_multiplier
                self.gui_funcs.ui.voltdiv_spbx.setValue(new_volt_div)
                
            self.update_voltage_scale()
            self.update_display()

    def update_display(self):
        if not self._initial_scale_set:
            self.initialize_scales()
            return

        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10

            plot_x_time = np.linspace(0, total_display_window_time, self.buffer_size)
            self.plot.setData(plot_x_time, self.y_data)
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.02)

        elif self.display_mode == "FFT":
            if self.last_x_freq_hz.size > 0 and self.last_fft_magnitude.size > 0:
                magnitude = np.maximum(self.last_fft_magnitude, 1e-10)
                self.plot.setData(self.last_x_freq_hz, magnitude)
                
                max_freq = np.max(self.last_x_freq_hz)
                max_mag = np.max(magnitude)
                
                self.plot_widget.setXRange(0, max_freq * 1.1, padding=0.05)
                if max_mag > 1e-10:
                    self.plot_widget.setYRange(np.log10(1e-10), np.log10(max_mag * 2), padding=0.05)
            else:
                self.plot.setData([], [])

    def reset_view(self):
        if self.display_mode == "Time D.":
            self.y_data = np.zeros(self.buffer_size, dtype=np.float64)
            self.ptr = 0
        else:
            self.plot_widget.clear()
            self.plot = self.plot_widget.plot(pen=pg.mkPen('y', width=2))
            
        self._initial_scale_set = False
        self.initialize_scales()

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode:
                self.display_mode = mode
                self.reset_view()
        else:
            print(f"Unknown mode: {mode}")

    def set_tab_name(self, name):
        self.tab_name = name
        
    def start_recording(self):
        self.is_recording = True
        self.recording_start_time = time.time()
        
    def stop_recording(self):
        self.is_recording = False
        self.recording_start_time = None
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_recording:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Set up the font
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 255))  # Blue color
            
            # Get current time
            current_time = QDateTime.currentDateTime()
            time_str = current_time.toString("hh:mm:ss.zzz")
            
            # Get frequency information
            freq_info = ""
            if self.display_mode == "FFT" and hasattr(self, 'last_x_freq_hz') and len(self.last_x_freq_hz) > 0:
                peak_freq = self.last_x_freq_hz[np.argmax(self.last_fft_magnitude)]
                freq_info = f"Peak Freq: {peak_freq:.2f} Hz"
            
            # Combine information
            info_text = f"Time: {time_str}\nTab: {self.tab_name}\n{freq_info}"
            
            # Draw text in upper right corner with 10px margin
            rect = self.rect()
            painter.drawText(rect.adjusted(0, 10, -10, 0), Qt.AlignRight | Qt.AlignTop, info_text)


class Signal1Oscilloscope(Oscilloscope):
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(buffer_size, sampling_rate_hz, gui_functions_ref, parent)
        self.plot_widget.setTitle("Channel 1")
        self.plot.setPen(pg.mkPen('g', width=2))
        self.signal_source = signal_source
        self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([])
        self.last_fft_magnitude = np.zeros(self.fft_len, dtype=np.float64)
        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)

    @Slot(float, float)
    def on_new_data(self, value1, value2):
        if not self.trigger_handler.is_frozen:
            self.add_new_data_point(value1)

    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag1.size == self.fft_len:
            self.last_fft_magnitude = fft_mag1
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {fft_mag1.size}")
            
        if x_freq_hz.size == self.fft_len:
            self.last_x_freq_hz = x_freq_hz
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {x_freq_hz.size}")

    def update_display(self):
        if not self._initial_scale_set:
            self.initialize_scales()
            return

        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10

            plot_x_time = np.linspace(0, total_display_window_time, self.buffer_size)
            self.plot.setData(plot_x_time, self.y_data)
            
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.02)

        elif self.display_mode == "FFT":
            if self.last_x_freq_hz.size > 0 and self.last_fft_magnitude.size > 0:
                magnitude = np.maximum(self.last_fft_magnitude, 1e-10)
                self.plot.setData(self.last_x_freq_hz, magnitude)
                
                max_freq = np.max(self.last_x_freq_hz)
                max_mag = np.max(magnitude)
                
                self.plot_widget.setXRange(0, max_freq * 1.1, padding=0.05)
                if max_mag > 1e-10:
                    self.plot_widget.setYRange(np.log10(1e-10), np.log10(max_mag * 2), padding=0.05)
            else:
                self.plot.setData([], [])

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode:
                self.display_mode = mode
                self.reset_view()
        else:
            print(f"Unknown mode: {mode}")


class Signal2Oscilloscope(Oscilloscope):
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(buffer_size, sampling_rate_hz, gui_functions_ref, parent)
        self.plot_widget.setTitle("Channel 2")
        self.plot.setPen(pg.mkPen('b', width=2))
        self.signal_source = signal_source
        self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([])
        self.last_fft_magnitude = np.zeros(self.fft_len, dtype=np.float64)
        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)

    @Slot(float, float)
    def on_new_data(self, value1, value2):
        if not self.trigger_handler.is_frozen:
            self.add_new_data_point(value2)

    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag2.size == self.fft_len:
            self.last_fft_magnitude = fft_mag2
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {fft_mag2.size}")
            
        if x_freq_hz.size == self.fft_len:
            self.last_x_freq_hz = x_freq_hz
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {x_freq_hz.size}")

    def update_display(self):
        if not self._initial_scale_set:
            self.initialize_scales()
            return

        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10

            plot_x_time = np.linspace(0, total_display_window_time, self.buffer_size)
            self.plot.setData(plot_x_time, self.y_data)
            
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.02)

        elif self.display_mode == "FFT":
            if self.last_x_freq_hz.size > 0 and self.last_fft_magnitude.size > 0:
                magnitude = np.maximum(self.last_fft_magnitude, 1e-10)
                self.plot.setData(self.last_x_freq_hz, magnitude)
                
                max_freq = np.max(self.last_x_freq_hz)
                max_mag = np.max(magnitude)
                
                self.plot_widget.setXRange(0, max_freq * 1.1, padding=0.05)
                if max_mag > 1e-10:
                    self.plot_widget.setYRange(np.log10(1e-10), np.log10(max_mag * 2), padding=0.05)
            else:
                self.plot.setData([], [])

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode:
                self.display_mode = mode
                self.reset_view()
        else:
            print(f"Unknown mode: {mode}")


class CombinedOscilloscope(QWidget):
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(parent=parent)
        self.signal_source = signal_source
        self.buffer_size = buffer_size
        self.sampling_rate_hz = sampling_rate_hz
        self.gui_funcs = gui_functions_ref
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('black')
        try:
            pg.setConfigOptions(useOpenGL=True)
        except Exception:
            pg.setConfigOptions(useOpenGL=False)
        self.layout.addWidget(self.plot_widget)
        self.curve1 = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Channel 1')
        self.curve2 = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Channel 2')
        self.plot_widget.setTitle("Combined Channels 1 & 2")

        # Initialize data arrays
        self.time_values_for_plot = np.zeros(self.buffer_size)
        self.y1_data = np.zeros(self.buffer_size, dtype=np.float64)
        self.y2_data = np.zeros(self.buffer_size, dtype=np.float64)
        self.ptr = 0
        
        # Initialize recording-related attributes
        self.is_recording = False
        self.recording_start_time = None
        self.tab_name = "Combined"
        self.display_mode = "Time D."
        self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([])
        self.last_fft_mag1 = np.zeros(self.fft_len, dtype=np.float64)
        self.last_fft_mag2 = np.zeros(self.fft_len, dtype=np.float64)

        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(33)

        self.trigger_handler1 = TriggerHandler(self.buffer_size)
        self.trigger_handler2 = TriggerHandler(self.buffer_size)
        
        if hasattr(self.gui_funcs.ui, 'PositiveEdgech'):
            self.gui_funcs.ui.PositiveEdgech.stateChanged.connect(self.on_pos_edge_trigger_changed)
        if hasattr(self.gui_funcs.ui, 'NegativeEdgech'):
            self.gui_funcs.ui.NegativeEdgech.stateChanged.connect(self.on_neg_edge_trigger_changed)

        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)

        if self.gui_funcs:
            self.gui_funcs.voltage_scale_changed.connect(
                self.update_voltage_scale)
            self.gui_funcs.time_scale_changed.connect(self.update_time_scale)

        self._initial_scale_set = False
        QTimer.singleShot(0, self.initialize_scales_combined)

    def initialize_scales_combined(self):
        if self.display_mode == "Time D.":
            self.plot_widget.setLogMode(x=False, y=False)
            self.plot_widget.setYRange(-1, 1, padding=0.05)
            self.plot_widget.setXRange(0, 0.1, padding=0.05)
            self.update_voltage_scale()
            self.update_time_scale()
            
        elif self.display_mode == "FFT":
            initial_max_freq = self.sampling_rate_hz / 2
            self.plot_widget.setYRange(1e-10, 1, padding=0.05)
            self.plot_widget.setXRange(0, initial_max_freq, padding=0.05)
            
            self.plot_widget.setLogMode(x=False, y=True)
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
            self.plot_widget.setLabel('left', 'Magnitude')
            
            self.plot_widget.setYRange(np.log10(1e-10), 0, padding=0.05)

        self._initial_scale_set = True

    @Slot()
    def update_voltage_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'voltdiv_spbx') and hasattr(self.gui_funcs.ui, 'voltdiv_cb')):
            return
        value = self.gui_funcs.ui.voltdiv_spbx.value()
        unit_text = self.gui_funcs.ui.voltdiv_cb.currentText()
        multiplier = 1.0
        if unit_text == "mV":
            multiplier = 1e-3
        elif unit_text == "uV":
            multiplier = 1e-6

        if self.display_mode == "Time D.":
            volt_range_total = 10 * value * multiplier
            self.plot_widget.setYRange(-volt_range_total / 2,
                                       volt_range_total / 2, padding=0.05)
            self.plot_widget.setLabel('left', 'Voltage', units=unit_text)

    @Slot()
    def update_time_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'timediv_spbx') and hasattr(self.gui_funcs.ui, 'timediv_cb')):
            return
        time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
        unit_text = self.gui_funcs.ui.timediv_cb.currentText()
        unit_multiplier = 1.0
        if unit_text == "ms":
            unit_multiplier = 1e-3
        elif unit_text == "us":
            unit_multiplier = 1e-6

        if self.display_mode == "Time D.":
            total_display_window_time = time_per_div_val * unit_multiplier * 10
            self.time_values_for_plot = np.linspace(
                0, total_display_window_time, self.buffer_size)
            self.plot_widget.setXRange(
                0, total_display_window_time, padding=0.01)
            self.plot_widget.setLabel('bottom', 'Time', units=unit_text)

    @Slot(int)
    def on_pos_edge_trigger_changed(self, state):
        self.trigger_handler1.set_pos_edge_enabled(state == 2)
        self.trigger_handler2.set_pos_edge_enabled(state == 2)
        if state == 0:
            self.trigger_handler1.unfreeze()
            self.trigger_handler2.unfreeze()

    @Slot(int)
    def on_neg_edge_trigger_changed(self, state):
        self.trigger_handler1.set_neg_edge_enabled(state == 2)
        self.trigger_handler2.set_neg_edge_enabled(state == 2)
        if state == 0:
            self.trigger_handler1.unfreeze()
            self.trigger_handler2.unfreeze()

    def center_display_at_trigger(self, trigger_idx, signal_num):
        if signal_num == 1 and not self.trigger_handler1.is_frozen:
            return
        if signal_num == 2 and not self.trigger_handler2.is_frozen:
            return
            
        points_before = self.buffer_size // 2
        points_after = self.buffer_size - points_before
        
        centered_data1 = np.zeros_like(self.y1_data)
        centered_data2 = np.zeros_like(self.y2_data)
        
        for i in range(points_before):
            idx = (trigger_idx - points_before + i) % self.buffer_size
            centered_data1[i] = self.y1_data[idx]
            centered_data2[i] = self.y2_data[idx]
            
        for i in range(points_after):
            idx = (trigger_idx + i) % self.buffer_size
            centered_data1[points_before + i] = self.y1_data[idx]
            centered_data2[points_before + i] = self.y2_data[idx]
            
        self.y1_data = centered_data1
        self.y2_data = centered_data2
        
        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10
            
            trigger_time = total_display_window_time / 2
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.05)
            
            signal1_range = np.ptp(self.y1_data)
            signal2_range = np.ptp(self.y2_data)
            max_signal_range = max(signal1_range, signal2_range)
            
            current_volt_div = self.gui_funcs.ui.voltdiv_spbx.value()
            unit_text_volt = self.gui_funcs.ui.voltdiv_cb.currentText()
            volt_multiplier = 1.0
            if unit_text_volt == "mV":
                volt_multiplier = 1e-3
            elif unit_text_volt == "uV":
                volt_multiplier = 1e-6
                
            current_volt_range = current_volt_div * volt_multiplier * 10
            if max_signal_range > current_volt_range * 0.8:
                new_volt_div = (max_signal_range / 8) / volt_multiplier
                self.gui_funcs.ui.voltdiv_spbx.setValue(new_volt_div)
            elif max_signal_range < current_volt_range * 0.2:
                new_volt_div = (max_signal_range / 4) / volt_multiplier
                self.gui_funcs.ui.voltdiv_spbx.setValue(new_volt_div)
                
            self.update_voltage_scale()
            self.update_display()

    @Slot(float, float)
    def on_new_data(self, value1, value2):
        if not (self.trigger_handler1.is_frozen or self.trigger_handler2.is_frozen):
            self.y1_data[self.ptr] = value1
            self.y2_data[self.ptr] = value2
            self.ptr = (self.ptr + 1) % self.buffer_size
            
            if self.display_mode == "Time D.":
                trigger_idx1 = self.trigger_handler1.check_trigger(self.y1_data)
                trigger_idx2 = self.trigger_handler2.check_trigger(self.y2_data)
                
                if trigger_idx1 is not None:
                    self.center_display_at_trigger(trigger_idx1, 1)
                elif trigger_idx2 is not None:
                    self.center_display_at_trigger(trigger_idx2, 2)

    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag1.size == self.fft_len:
            self.last_fft_mag1 = fft_mag1
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {fft_mag1.size}")
            
        if fft_mag2.size == self.fft_len:
            self.last_fft_mag2 = fft_mag2
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {fft_mag2.size}")
            
        if x_freq_hz.size == self.fft_len:
            self.last_x_freq_hz = x_freq_hz
        else:
            print(f"Size mismatch - expected {self.fft_len}, got {x_freq_hz.size}")

    def update_display(self):
        if not self._initial_scale_set:
            self.initialize_scales_combined()
            return

        if self.display_mode == "Time D.":
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms":
                multiplier_time = 1e-3
            elif unit_text_time == "us":
                multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10

            self.time_values_for_plot = np.linspace(0, total_display_window_time, self.buffer_size)
            self.curve1.setData(self.time_values_for_plot, self.y1_data)
            self.curve2.setData(self.time_values_for_plot, self.y2_data)
            
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.02)

        elif self.display_mode == "FFT":
            if self.last_x_freq_hz.size > 0:
                magnitude1 = np.maximum(self.last_fft_mag1, 1e-10)
                magnitude2 = np.maximum(self.last_fft_mag2, 1e-10)
                
                self.curve1.setData(self.last_x_freq_hz, magnitude1)
                self.curve2.setData(self.last_x_freq_hz, magnitude2)
                
                max_freq = np.max(self.last_x_freq_hz)
                max_mag = max(np.max(magnitude1), np.max(magnitude2))
                
                self.plot_widget.setXRange(0, max_freq * 1.1, padding=0.05)
                if max_mag > 1e-10:
                    self.plot_widget.setYRange(np.log10(1e-10), np.log10(max_mag * 2), padding=0.05)
            else:
                self.curve1.setData([], [])
                self.curve2.setData([], [])

    def reset_view(self):
        if self.display_mode == "Time D.":
            self.y1_data = np.zeros(self.buffer_size, dtype=np.float64)
            self.y2_data = np.zeros(self.buffer_size, dtype=np.float64)
            self.ptr = 0
        else:
            self.plot_widget.clear()
            self.curve1 = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Channel 1')
            self.curve2 = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Channel 2')
            
        self._initial_scale_set = False
        self.initialize_scales_combined()

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode:
                self.display_mode = mode
                self.reset_view()
        else:
            print(f"Unknown mode: {mode}")

    def set_tab_name(self, name):
        self.tab_name = name
        
    def start_recording(self):
        self.is_recording = True
        self.recording_start_time = time.time()
        
    def stop_recording(self):
        self.is_recording = False
        self.recording_start_time = None
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_recording:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Set up the font
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 255))  # Blue color
            
            # Get current time
            current_time = QDateTime.currentDateTime()
            time_str = current_time.toString("hh:mm:ss.zzz")
            
            # Get frequency information for both signals
            freq_info = ""
            if self.display_mode == "FFT":
                if hasattr(self, 'last_x_freq_hz') and len(self.last_x_freq_hz) > 0:
                    peak_freq1 = self.last_x_freq_hz[np.argmax(self.last_fft_mag1)]
                    peak_freq2 = self.last_x_freq_hz[np.argmax(self.last_fft_mag2)]
                    freq_info = f"Signal 1 Peak: {peak_freq1:.2f} Hz\nSignal 2 Peak: {peak_freq2:.2f} Hz"
            
            # Combine information
            info_text = f"Time: {time_str}\nTab: {self.tab_name}\n{freq_info}"
            
            # Draw text in upper right corner with 10px margin
            rect = self.rect()
            painter.drawText(rect.adjusted(0, 10, -10, 0), Qt.AlignRight | Qt.AlignTop, info_text)
