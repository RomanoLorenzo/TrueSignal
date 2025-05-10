# Functions.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from src.OscilloscopeWidget import Oscilloscope, CombinedOscilloscope, Signal1Oscilloscope, Signal2Oscilloscope
from PySide6.QtCore import Slot, QObject, QTimer, Signal
import numpy as np


class SignalSource(QObject):
    data_updated = Signal(float, float)
    fft_data_updated = Signal(np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, buffer_size, update_interval_ms=1, fft_update_interval_ms=100, parent=None):
        super().__init__(parent)
        if buffer_size <= 0:
            raise ValueError("Buffer size must be positive.")
        self.buffer_size = buffer_size
        self.update_interval_ms = update_interval_ms  # Store for reference if needed
        self.sampling_rate_hz = 1000.0 / \
            self.update_interval_ms if self.update_interval_ms > 0 else 1000.0

        self.phase = 0
        self.amp = 5
        self.cnt = 0
        self.slope = 20
        self.maxv = 5
        self.value1 = 0.0
        self.value2 = 0.0

        self.y1_buffer = np.zeros(self.buffer_size, dtype=np.float64)
        self.y2_buffer = np.zeros(self.buffer_size, dtype=np.float64)
        self.ptr = 0

        self.fft_len = self.buffer_size // 2
        self.x_freq_hz = np.fft.rfftfreq(
            self.buffer_size, d=1.0/self.sampling_rate_hz)[:self.fft_len]
        self.fft_mag1 = np.zeros(self.fft_len, dtype=np.float64)
        self.fft_mag2 = np.zeros(self.fft_len, dtype=np.float64)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_signals_and_emit_data)
        self.data_timer.start(self.update_interval_ms)

        self.fft_timer = QTimer(self)
        self.fft_timer.timeout.connect(self.calculate_fft_and_emit)
        self.fft_timer.start(fft_update_interval_ms)

    def update_signals_and_emit_data(self):
        self.phase += 0.1
        if self.phase > 2 * np.pi:
            self.phase -= 2 * np.pi
        current_val1 = self.amp * np.sin(self.phase)
        self.cnt += 0.1
        current_val2 = self.slope * self.cnt
        if current_val2 > self.maxv:
            self.cnt = 0
            current_val2 = 0
        self.y1_buffer[self.ptr] = current_val1
        self.y2_buffer[self.ptr] = current_val2
        self.ptr = (self.ptr + 1) % self.buffer_size
        self.data_updated.emit(current_val1, current_val2)

    def calculate_fft_and_emit(self):
        if self.buffer_size > 0:
            y1_snapshot = np.copy(self.y1_buffer)
            y2_snapshot = np.copy(self.y2_buffer)
            window = np.hanning(self.buffer_size)
            fft_coeffs1 = np.fft.rfft(y1_snapshot * window)
            fft_coeffs2 = np.fft.rfft(y2_snapshot * window)
            self.fft_mag1 = np.abs(fft_coeffs1[:self.fft_len])
            self.fft_mag2 = np.abs(fft_coeffs2[:self.fft_len])
            self.fft_data_updated.emit(
                self.x_freq_hz, self.fft_mag1, self.fft_mag2)
        else:
            empty_arr = np.array([], dtype=np.float64)
            self.fft_data_updated.emit(empty_arr, empty_arr, empty_arr)


class GuiFunctions(QObject):
    voltage_scale_changed = Signal()
    time_scale_changed = Signal()

    BUFFER_SIZE = 1024
    DEFAULT_VOLT_DIV_VALUE = 1.0
    DEFAULT_VOLT_DIV_UNIT_INDEX = 0
    DEFAULT_TIME_DIV_VALUE = 1.0
    DEFAULT_TIME_DIV_UNIT_INDEX = 0

    def __init__(self, Mainwindow):
        super().__init__()
        self.main = Mainwindow
        self.ui = Mainwindow.ui

        self.signal_source = SignalSource(
            buffer_size=self.BUFFER_SIZE,
            update_interval_ms=1,
            fft_update_interval_ms=100
        )
        self.oscilloscope_widgets = []
        self.combined_osc = None
        self.signal1_osc_tab2 = None
        self.signal2_osc_tab3 = None
        self.signal1_osc_tab4 = None
        self.signal2_osc_tab4 = None

        self.setupOscilloscope()
        self.setupSignal1Oscilloscope()
        self.setupSignal2Oscilloscope()
        self.setupTab4Oscilloscopes()

        if hasattr(self.ui, 'FFTcomb'):
            self.ui.FFTcomb.currentIndexChanged.connect(
                self._update_display_modes)
        if hasattr(self.ui, 'FFTcomb_2'):
            self.ui.FFTcomb_2.currentIndexChanged.connect(
                self._update_display_modes)
        self._update_display_modes()

        if hasattr(self.ui, 'tabWidget') and isinstance(self.ui.tabWidget, QTabWidget):
            self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
            self.on_tab_changed(self.ui.tabWidget.currentIndex())
        else:
            print("Warning: tabWidget not found or not a QTabWidget in UI.")
        self._connect_scale_controls()

    def _connect_scale_controls(self):
        if hasattr(self.ui, 'voltdiv_spbx'):
            self.ui.voltdiv_spbx.valueChanged.connect(
                self.on_voltage_setting_changed)
        if hasattr(self.ui, 'voltdiv_cb'):
            self.ui.voltdiv_cb.currentIndexChanged.connect(
                self.on_voltage_setting_changed)
        if hasattr(self.ui, 'timediv_spbx'):
            self.ui.timediv_spbx.valueChanged.connect(
                self.on_time_setting_changed)
        if hasattr(self.ui, 'timediv_cb'):
            self.ui.timediv_cb.currentIndexChanged.connect(
                self.on_time_setting_changed)

    def _add_osc_widget(self, osc_widget_instance):
        if osc_widget_instance:
            if hasattr(osc_widget_instance, 'display_timer'):
                self.oscilloscope_widgets.append(osc_widget_instance)
            if hasattr(osc_widget_instance, 'update_voltage_scale'):
                self.voltage_scale_changed.connect(
                    osc_widget_instance.update_voltage_scale)
            if hasattr(osc_widget_instance, 'update_time_scale'):
                self.time_scale_changed.connect(
                    osc_widget_instance.update_time_scale)

    def setupOscilloscope(self):
        tab1_widget = self.ui.tabWidget.findChild(QWidget, "tab_1")
        if tab1_widget is None:
            print("Tab 'tab_1' not found!")
            return
        layout = tab1_widget.layout()
        if layout is None:
            layout = QVBoxLayout(tab1_widget)
            tab1_widget.setLayout(layout)
        self.combined_osc = CombinedOscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.combined_osc)
        layout.addWidget(self.combined_osc)

    def setupSignal1Oscilloscope(self):
        tab2_widget = self.ui.tabWidget.findChild(QWidget, "tab_2")
        if tab2_widget is None:
            print("Tab 'tab_2' not found!")
            return
        layout = tab2_widget.layout()
        if layout is None:
            layout = QVBoxLayout(tab2_widget)
            tab2_widget.setLayout(layout)
        self.signal1_osc_tab2 = Signal1Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.signal1_osc_tab2)
        layout.addWidget(self.signal1_osc_tab2)

    def setupSignal2Oscilloscope(self):
        tab3_widget = self.ui.tabWidget.findChild(QWidget, "tab_3")
        if tab3_widget is None:
            print("Tab 'tab_3' not found!")
            return
        layout = tab3_widget.layout()
        if layout is None:
            layout = QVBoxLayout(tab3_widget)
            tab3_widget.setLayout(layout)
        self.signal2_osc_tab3 = Signal2Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.signal2_osc_tab3)
        layout.addWidget(self.signal2_osc_tab3)

    def setupTab4Oscilloscopes(self):
        tab4_widget = self.ui.tabWidget.findChild(QWidget, "tab_4")
        if tab4_widget is None:
            print("Tab 'tab_4' not found!")
            return
        layout = tab4_widget.layout()
        if layout is None:
            layout = QVBoxLayout(tab4_widget)
            tab4_widget.setLayout(layout)
        if not isinstance(layout, QVBoxLayout):
            QWidget().setLayout(layout)
            layout = QVBoxLayout(tab4_widget)
            tab4_widget.setLayout(layout)
        self.signal1_osc_tab4 = Signal1Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self.signal1_osc_tab4.plot_widget.setTitle("Signal 1")
        self._add_osc_widget(self.signal1_osc_tab4)
        layout.addWidget(self.signal1_osc_tab4)
        self.signal2_osc_tab4 = Signal2Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self.signal2_osc_tab4.plot_widget.setTitle("Signal 2")
        self._add_osc_widget(self.signal2_osc_tab4)
        layout.addWidget(self.signal2_osc_tab4)

    @Slot()
    def on_voltage_setting_changed(self): self.voltage_scale_changed.emit()
    @Slot()
    def on_time_setting_changed(self): self.time_scale_changed.emit()

    @Slot()
    def _update_display_modes(self):
        fft1 = self.ui.FFTcomb.currentText() == "FFT"
        fft2 = self.ui.FFTcomb_2.currentText() == "FFT"
        if self.combined_osc:
            self.combined_osc.set_display_mode(
                "FFT" if fft1 and fft2 else "Time D.")
        if self.signal1_osc_tab2:
            self.signal1_osc_tab2.set_display_mode(
                "FFT" if fft1 else "Time D.")
        if self.signal2_osc_tab3:
            self.signal2_osc_tab3.set_display_mode(
                "FFT" if fft2 else "Time D.")
        if self.signal1_osc_tab4:
            self.signal1_osc_tab4.set_display_mode(
                "FFT" if fft1 else "Time D.")
        if self.signal2_osc_tab4:
            self.signal2_osc_tab4.set_display_mode(
                "FFT" if fft2 else "Time D.")

    @Slot(int)
    def on_tab_changed(self, index):
        current_tab = self.ui.tabWidget.widget(index)
        for osc in self.oscilloscope_widgets:
            if hasattr(osc, 'display_timer'):
                osc.display_timer.stop()
        active_oscs_in_current_tab = []
        if current_tab:
            if current_tab is self.ui.tab_1 and self.combined_osc:
                active_oscs_in_current_tab.append(self.combined_osc)
            elif current_tab is self.ui.tab_2 and self.signal1_osc_tab2:
                active_oscs_in_current_tab.append(self.signal1_osc_tab2)
            elif current_tab is self.ui.tab_3 and self.signal2_osc_tab3:
                active_oscs_in_current_tab.append(self.signal2_osc_tab3)
            elif current_tab is self.ui.tab_4:  # Assuming self.ui.tab_4 is the QWidget for tab 4
                if self.signal1_osc_tab4:
                    active_oscs_in_current_tab.append(self.signal1_osc_tab4)
                if self.signal2_osc_tab4:
                    active_oscs_in_current_tab.append(self.signal2_osc_tab4)
        for osc in active_oscs_in_current_tab:
            if hasattr(osc, 'display_timer'):
                osc.display_timer.start()
                if hasattr(osc, 'update_display'):
                    osc.update_display()