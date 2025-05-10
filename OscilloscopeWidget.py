# OscilloscopeWidget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Slot, Signal
import pyqtgraph as pg
import numpy as np

class Oscilloscope(QWidget):
    def __init__(self, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self); self.setLayout(self.layout)
        self.plot_widget = pg.PlotWidget(); self.plot_widget.setBackground('black')
        try: pg.setConfigOptions(useOpenGL=True)
        except Exception: pg.setConfigOptions(useOpenGL=False)
        self.layout.addWidget(self.plot_widget)
        self.plot = self.plot_widget.plot(pen=pg.mkPen('y', width=2))
        self.buffer_size = buffer_size; self.sampling_rate_hz = sampling_rate_hz
        self.gui_funcs = gui_functions_ref
        self.y_data = np.zeros(self.buffer_size, dtype=np.float64)
        # self.time_values rappresenta i tempi relativi all'inizio del buffer (da 0 a T_buffer)
        self.time_values = np.arange(self.buffer_size) * (1.0 / self.sampling_rate_hz)
        self.ptr = 0
        self.display_timer = QTimer(self); self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(33) # ~30 FPS display update
        self.display_mode = "Time D."
        self._initial_scale_set = False
        QTimer.singleShot(0, self.initialize_scales) # Chiamata post-init

    def initialize_scales(self):
        self.update_voltage_scale()
        self.update_time_scale()
        self._initial_scale_set = True
        self.update_display() # Forza un primo disegno

    @Slot()
    def update_voltage_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'voldiv_spbx') and hasattr(self.gui_funcs.ui, 'voldiv_cb')): return
        value = self.gui_funcs.ui.voldiv_spbx.value()
        unit_text = self.gui_funcs.ui.voldiv_cb.currentText()
        multiplier = 1.0
        if unit_text == "mV": multiplier = 1e-3
        elif unit_text == "uV": multiplier = 1e-6
        
        if self.display_mode == "Time D.":
            volt_range_total = 10 * value * multiplier # 10 divisioni verticali
            self.plot_widget.setYRange(-volt_range_total / 2, volt_range_total / 2, padding=0.05)
            self.plot_widget.getAxis('left').setLabel('Voltage', units=unit_text)

    @Slot()
    def update_time_scale(self):
        if not (hasattr(self.gui_funcs.ui, 'timediv_spbx') and hasattr(self.gui_funcs.ui, 'timediv_cb')): return
        time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
        unit_text = self.gui_funcs.ui.timediv_cb.currentText()
        unit_multiplier = 1.0
        if unit_text == "ms": unit_multiplier = 1e-3
        elif unit_text == "us": unit_multiplier = 1e-6
        
        if self.display_mode == "Time D.":
            # Durata totale della finestra da visualizzare (es. 10 divisioni)
            total_display_window_time = time_per_div_val * unit_multiplier * 10
            
            # Il nostro buffer `self.y_data` contiene `self.buffer_size` campioni.
            # Lo plottiamo contro `self.x_data` (indici da 0 a N-1).
            # Dobbiamo dire a pyqtgraph che questi N-1 indici rappresentano `total_display_window_time`.
            # L'asse X andrà da 0 (inizio della finestra visibile) a `total_display_window_time`.
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.01)
            self.plot_widget.getAxis('bottom').setLabel('Time', units=unit_text)
            # NOTA: setData userà un x_axis scalato per mappare il buffer sulla finestra temporale
            # Questo sarà gestito in update_display delle sottoclassi.

    def add_new_data_point(self, new_data):
        self.y_data[self.ptr] = new_data
        self.ptr = (self.ptr + 1) % self.buffer_size
    def update_display(self): pass


class Signal1Oscilloscope(Oscilloscope):
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(buffer_size, sampling_rate_hz, gui_functions_ref, parent)
        self.plot_widget.setTitle("Signal 1"); self.plot.setPen(pg.mkPen('g', width=2))
        self.signal_source = signal_source
        self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([]); self.last_fft_magnitude = np.zeros(self.fft_len, dtype=np.float64)
        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)

    @Slot(float, float)
    def on_new_data(self, value1, value2): self.add_new_data_point(value1)
    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag1.size == self.fft_len: self.last_fft_magnitude = fft_mag1
        if x_freq_hz.size == self.fft_len: self.last_x_freq_hz = x_freq_hz

    def update_display(self):
        if self.display_mode == "Time D.":
            if not self._initial_scale_set: self.update_time_scale(); self.update_voltage_scale(); self._initial_scale_set = True
            # else: self.update_time_scale(); self.update_voltage_scale() # Aggiorna sempre scale se visibile

            # Calcola l'asse temporale per la finestra corrente
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms": multiplier_time = 1e-3
            elif unit_text_time == "us": multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10
            
            # Crea un asse x per il plotting che va da 0 a total_display_window_time
            # mappando i buffer_size punti su questo intervallo.
            plot_x_time = np.linspace(0, total_display_window_time, self.buffer_size)

            self.plot_widget.setLimits(xMin=0, xMax=total_display_window_time) # Limiti per pan/zoom
            self.plot.setData(plot_x_time, self.y_data) # Plotta y_data contro l'asse X scalato
        elif self.display_mode == "FFT":
            self._initial_scale_set = False
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz'); self.plot_widget.setLabel('left', 'Magnitude')
            self.plot_widget.setLogMode(x=False, y=True); self.plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis)
            if self.last_x_freq_hz.size > 0:
                 self.plot_widget.setXRange(self.last_x_freq_hz[0], self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0]+1e-9, padding=0.02)
                 self.plot_widget.setLimits(xMin=self.last_x_freq_hz[0], xMax=self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0] * 1.1 + 1e-9)
            if self.last_x_freq_hz.size > 0 and self.last_fft_magnitude.size > 0: self.plot.setData(self.last_x_freq_hz, self.last_fft_magnitude)
            else: self.plot.setData([], [])

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode: self.display_mode = mode
            self._initial_scale_set = False # Forza riapplicazione scale al prossimo update_display
            if mode == "FFT": self.plot_widget.enableAutoRange('xy', True)
            # Non serve else per TimeD, update_display e i metodi di scala gestiranno il range
            self.update_display()
        else: print(f"Unknown mode for Signal1: {mode}")


class Signal2Oscilloscope(Oscilloscope): # Simile a Signal1Oscilloscope
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(buffer_size, sampling_rate_hz, gui_functions_ref, parent)
        self.plot_widget.setTitle("Signal 2"); self.plot.setPen(pg.mkPen('b', width=2))
        self.signal_source = signal_source; self.display_mode = "Time D."
        self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([]); self.last_fft_magnitude = np.zeros(self.fft_len, dtype=np.float64)
        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)
        if not self._initial_scale_set: QTimer.singleShot(0, self.update_voltage_scale); QTimer.singleShot(0, self.update_time_scale); self._initial_scale_set = True

    @Slot(float, float)
    def on_new_data(self, value1, value2): self.add_new_data_point(value2)
    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag2.size == self.fft_len: self.last_fft_magnitude = fft_mag2
        if x_freq_hz.size == self.fft_len: self.last_x_freq_hz = x_freq_hz

    def update_display(self): # Simile a Signal1Oscilloscope
        if self.display_mode == "Time D.":
            if not self._initial_scale_set: self.update_time_scale(); self.update_voltage_scale(); self._initial_scale_set = True
            else: self.update_time_scale(); self.update_voltage_scale()
            time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
            unit_text_time = self.gui_funcs.ui.timediv_cb.currentText()
            multiplier_time = 1.0
            if unit_text_time == "ms": multiplier_time = 1e-3
            elif unit_text_time == "us": multiplier_time = 1e-6
            total_display_window_time = time_per_div_val * multiplier_time * 10
            plot_x_time = np.linspace(0, total_display_window_time, self.buffer_size)
            self.plot_widget.setLimits(xMin=0, xMax=total_display_window_time)
            self.plot.setData(plot_x_time, self.y_data)
        elif self.display_mode == "FFT":
            self._initial_scale_set = False
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz'); self.plot_widget.setLabel('left', 'Magnitude')
            self.plot_widget.setLogMode(x=False, y=True); self.plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis)
            if self.last_x_freq_hz.size > 0:
                self.plot_widget.setXRange(self.last_x_freq_hz[0], self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0]+1e-9, padding=0.02)
                self.plot_widget.setLimits(xMin=self.last_x_freq_hz[0], xMax=self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0] * 1.1 + 1e-9)
            if self.last_x_freq_hz.size > 0 and self.last_fft_magnitude.size > 0: self.plot.setData(self.last_x_freq_hz, self.last_fft_magnitude)
            else: self.plot.setData([], [])

    @Slot(str)
    def set_display_mode(self, mode): # Simile a Signal1Oscilloscope
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode: self.display_mode = mode
            self._initial_scale_set = False
            if mode == "FFT": self.plot_widget.enableAutoRange('xy', True)
            self.update_display()
        else: print(f"Unknown mode for Signal2: {mode}")


class CombinedOscilloscope(QWidget):
    def __init__(self, signal_source, buffer_size, sampling_rate_hz, gui_functions_ref, parent=None):
        super().__init__(parent=parent)
        self.signal_source = signal_source; self.buffer_size = buffer_size
        self.sampling_rate_hz = sampling_rate_hz; self.gui_funcs = gui_functions_ref
        self.layout = QVBoxLayout(self); self.setLayout(self.layout)
        self.plot_widget = pg.PlotWidget(); self.plot_widget.setBackground('black')
        try: pg.setConfigOptions(useOpenGL=True)
        except Exception: pg.setConfigOptions(useOpenGL=False)
        self.layout.addWidget(self.plot_widget)
        self.curve1 = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Signal 1')
        self.curve2 = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Signal 2')
        self.plot_widget.setTitle("Combined Signal 1 & 2")
        self.time_values_for_plot = np.zeros(self.buffer_size) # Asse X per il plot, scalato
        self.y1 = np.zeros(self.buffer_size, dtype=np.float64); self.y2 = np.zeros(self.buffer_size, dtype=np.float64)
        self.ptr = 0; self.display_mode = "Time D."; self.fft_len = self.buffer_size // 2
        self.last_x_freq_hz = np.array([])
        self.last_fft_mag1 = np.zeros(self.fft_len, dtype=np.float64); self.last_fft_mag2 = np.zeros(self.fft_len, dtype=np.float64)
        self.display_timer = QTimer(self); self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(50)
        self.signal_source.data_updated.connect(self.on_new_data)
        self.signal_source.fft_data_updated.connect(self.on_new_fft_data)
        if self.gui_funcs:
            self.gui_funcs.voltage_scale_changed.connect(self.update_voltage_scale)
            self.gui_funcs.time_scale_changed.connect(self.update_time_scale)
        self._initial_scale_set = False
        QTimer.singleShot(0, self.initialize_scales_combined)

    def initialize_scales_combined(self):
        self.update_voltage_scale()
        self.update_time_scale()
        self._initial_scale_set = True
        self.update_display()

    @Slot()
    def update_voltage_scale(self): # Copiato e adattato da Oscilloscope
        if not (hasattr(self.gui_funcs.ui, 'voldiv_spbx') and hasattr(self.gui_funcs.ui, 'voldiv_cb')): return
        value = self.gui_funcs.ui.voldiv_spbx.value(); unit_text = self.gui_funcs.ui.voldiv_cb.currentText()
        multiplier = 1.0
        if unit_text == "mV": multiplier = 1e-3
        elif unit_text == "uV": multiplier = 1e-6
        if self.display_mode == "Time D.":
            volt_range_total = 10 * value * multiplier
            self.plot_widget.setYRange(-volt_range_total / 2, volt_range_total / 2, padding=0.05)
            self.plot_widget.setLabel('left', 'Voltage', units=unit_text)

    @Slot()
    def update_time_scale(self): # Copiato e adattato da Oscilloscope
        if not (hasattr(self.gui_funcs.ui, 'timediv_spbx') and hasattr(self.gui_funcs.ui, 'timediv_cb')): return
        time_per_div_val = self.gui_funcs.ui.timediv_spbx.value()
        unit_text = self.gui_funcs.ui.timediv_cb.currentText()
        unit_multiplier = 1.0
        if unit_text == "ms": unit_multiplier = 1e-3
        elif unit_text == "us": unit_multiplier = 1e-6
        if self.display_mode == "Time D.":
            total_display_window_time = time_per_div_val * unit_multiplier * 10
            self.time_values_for_plot = np.linspace(0, total_display_window_time, self.buffer_size)
            self.plot_widget.setXRange(0, total_display_window_time, padding=0.01)
            self.plot_widget.setLabel('bottom', 'Time', units=unit_text)

    @Slot(float, float)
    def on_new_data(self, value1, value2):
        self.y1[self.ptr] = value1; self.y2[self.ptr] = value2
        self.ptr = (self.ptr + 1) % self.buffer_size

    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def on_new_fft_data(self, x_freq_hz, fft_mag1, fft_mag2):
        if fft_mag1.size == self.fft_len: self.last_fft_mag1 = fft_mag1
        if fft_mag2.size == self.fft_len: self.last_fft_mag2 = fft_mag2
        if x_freq_hz.size == self.fft_len: self.last_x_freq_hz = x_freq_hz

    def update_display(self):
        if self.display_mode == "Time D.":
            if not self._initial_scale_set: self.update_time_scale(); self.update_voltage_scale(); self._initial_scale_set = True
            else: self.update_time_scale(); self.update_voltage_scale()
            self.plot_widget.setLimits(xMin=self.time_values_for_plot[0], xMax=self.time_values_for_plot[-1] if self.time_values_for_plot.size > 0 else 0)
            self.curve1.setData(self.time_values_for_plot, self.y1); self.curve2.setData(self.time_values_for_plot, self.y2)
        elif self.display_mode == "FFT":
            self._initial_scale_set = False
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz'); self.plot_widget.setLabel('left', 'Magnitude')
            self.plot_widget.setLogMode(x=False, y=True); self.plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis)
            if self.last_x_freq_hz.size > 0:
                self.plot_widget.setXRange(self.last_x_freq_hz[0], self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0]+1e-9, padding=0.02)
                self.plot_widget.setLimits(xMin=self.last_x_freq_hz[0], xMax=self.last_x_freq_hz[-1] if self.last_x_freq_hz.size > 1 else self.last_x_freq_hz[0] * 1.1 + 1e-9)
                if self.last_fft_mag1.size > 0: self.curve1.setData(self.last_x_freq_hz, self.last_fft_mag1)
                else: self.curve1.setData([],[])
                if self.last_fft_mag2.size > 0: self.curve2.setData(self.last_x_freq_hz, self.last_fft_mag2)
                else: self.curve2.setData([],[])
            else: self.curve1.setData([], []); self.curve2.setData([], [])

    @Slot(str)
    def set_display_mode(self, mode):
        if mode in ["Time D.", "FFT"]:
            if self.display_mode != mode: self.display_mode = mode
            self._initial_scale_set = False
            if mode == "FFT": self.plot_widget.enableAutoRange('xy', True)
            self.update_display()
        else: print(f"Unknown mode for Combined: {mode}")