from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
# Assicurati che OscilloscopeWidget esista e contenga le classi corrette
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
        self.update_interval_ms = update_interval_ms
        self.sampling_rate_hz = 1000.0 / self.update_interval_ms if self.update_interval_ms > 0 else 1000.0

        # Signal 1 parameters (Smooth Random Walk)
        self.signal1_params = {
            'step_size': 0.1,        # Size of random steps (σ of normal distribution)
            'noise_level': 0.05,     # Additional noise level
            'max_amplitude': 5.0,     # Maximum absolute amplitude
            'baseline_drift': 0.01    # Slow drift in the baseline
        }
        
        # Signal 2 parameters (Chaotic with Spikes)
        self.signal2_params = {
            'step_size': 0.2,        # Size of random steps
            'noise_level': 0.1,      # Additional noise level
            'max_amplitude': 3.0,     # Maximum amplitude (excluding spikes)
            'spike_probability': 0.02,# Probability of spikes (2%)
            'spike_amplitude': 4.0,   # Amplitude of spikes
            'spike_noise': 0.5,      # Noise added to spikes
            'burst_mode': False,     # Whether to generate burst of spikes
            'burst_duration': 50,     # Duration of burst in samples
            'burst_interval': 500     # Minimum samples between bursts
        }

        # Initialize signal states
        self.last_value1 = 0.0
        self.last_value2 = 0.0
        self.baseline_drift = 0.0
        self.burst_counter = 0
        self.samples_since_last_burst = 0

        # Buffer initialization
        self.y1_buffer = np.zeros(self.buffer_size, dtype=np.float64)
        self.y2_buffer = np.zeros(self.buffer_size, dtype=np.float64)
        self.ptr = 0

        # FFT setup
        self.fft_len = self.buffer_size // 2
        self.x_freq_hz = np.fft.rfftfreq(self.buffer_size, d=1.0/self.sampling_rate_hz)[:self.fft_len]
        self.fft_mag1 = np.zeros(self.fft_len, dtype=np.float64)
        self.fft_mag2 = np.zeros(self.fft_len, dtype=np.float64)

        # Timers setup
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_signals_and_emit_data)
        self.data_timer.start(self.update_interval_ms)

        self.fft_timer = QTimer(self)
        self.fft_timer.timeout.connect(self.calculate_fft_and_emit)
        self.fft_timer.start(fft_update_interval_ms)

    def update_signals_and_emit_data(self):
        # Generate Signal 1 (Smooth Random Walk with drift)
        # Update baseline drift
        self.baseline_drift += np.random.normal(0, self.signal1_params['baseline_drift'])
        self.baseline_drift = np.clip(self.baseline_drift, -1, 1)
        
        # Generate main signal
        random_step1 = np.random.normal(0, self.signal1_params['step_size'])
        self.last_value1 += random_step1
        self.last_value1 = np.clip(
            self.last_value1, 
            -self.signal1_params['max_amplitude'], 
            self.signal1_params['max_amplitude']
        )
        
        # Add noise and drift
        current_val1 = (
            self.last_value1 + 
            np.random.normal(0, self.signal1_params['noise_level']) +
            self.baseline_drift
        )
        
        # Generate Signal 2 (Chaotic with Spikes or Bursts)
        if self.signal2_params['burst_mode']:
            # Burst mode logic
            if self.burst_counter > 0:
                # In burst
                current_val2 = np.random.choice([-1, 1]) * self.signal2_params['spike_amplitude']
                current_val2 += np.random.normal(0, self.signal2_params['spike_noise'])
                self.burst_counter -= 1
                self.samples_since_last_burst = 0
            else:
                # Not in burst
                self.samples_since_last_burst += 1
                if (self.samples_since_last_burst >= self.signal2_params['burst_interval'] and 
                    np.random.random() < self.signal2_params['spike_probability']):
                    # Start new burst
                    self.burst_counter = self.signal2_params['burst_duration']
                    current_val2 = np.random.choice([-1, 1]) * self.signal2_params['spike_amplitude']
                else:
                    # Normal random walk
                    random_step2 = np.random.normal(0, self.signal2_params['step_size'])
                    self.last_value2 += random_step2
                    self.last_value2 = np.clip(
                        self.last_value2,
                        -self.signal2_params['max_amplitude'],
                        self.signal2_params['max_amplitude']
                    )
                    current_val2 = self.last_value2 + np.random.normal(0, self.signal2_params['noise_level'])
        else:
            # Regular spike mode
            if np.random.random() < self.signal2_params['spike_probability']:
                current_val2 = np.random.choice([-1, 1]) * self.signal2_params['spike_amplitude']
                current_val2 += np.random.normal(0, self.signal2_params['spike_noise'])
            else:
                random_step2 = np.random.normal(0, self.signal2_params['step_size'])
                self.last_value2 += random_step2
                self.last_value2 = np.clip(
                    self.last_value2,
                    -self.signal2_params['max_amplitude'],
                    self.signal2_params['max_amplitude']
                )
                current_val2 = self.last_value2 + np.random.normal(0, self.signal2_params['noise_level'])
        
        # Update buffers and emit
        self.y1_buffer[self.ptr] = current_val1
        self.y2_buffer[self.ptr] = current_val2
        self.ptr = (self.ptr + 1) % self.buffer_size
        self.data_updated.emit(current_val1, current_val2)

    def set_signal1_params(self, **params):
        """Update Signal 1 parameters"""
        self.signal1_params.update(params)

    def set_signal2_params(self, **params):
        """Update Signal 2 parameters"""
        self.signal2_params.update(params)

    def toggle_burst_mode(self, enabled):
        """Toggle between spike mode and burst mode for Signal 2"""
        self.signal2_params['burst_mode'] = enabled

    def calculate_fft_and_emit(self):
        if self.buffer_size > 0:
            y1_snapshot = np.copy(self.y1_buffer)
            y2_snapshot = np.copy(self.y2_buffer)
            window = np.hanning(self.buffer_size) # Applica finestra per FFT
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
    DEFAULT_VOLT_DIV_UNIT_INDEX = 0 # Indice per "V" in ["V", "mV", "uV"]
    DEFAULT_TIME_DIV_VALUE = 1.0
    DEFAULT_TIME_DIV_UNIT_INDEX = 0 # Indice per "s" in ["s", "ms", "us"]


    def __init__(self, Mainwindow):
        super().__init__()
        self.main = Mainwindow
        self.ui = Mainwindow.ui # Riferimento all'UI della MainWindow

        self.signal_source = SignalSource(
            buffer_size=self.BUFFER_SIZE,
            update_interval_ms=1, # Velocità di generazione dati (1ms = 1kHz)
            fft_update_interval_ms=100 # Frequenza di ricalcolo FFT
        )
        self.oscilloscope_widgets = [] # Lista per tenere traccia di tutti i widget oscilloscopio

        # Crea le istanze dei widget oscilloscopio e aggiungili ai tab
        # NOTA: Questi widget vengono creati prima che i controlli di scala personalizzati
        # siano installati in MainWindow.setup_custom_controls().
        # Le connessioni ai loro metodi update_scale devono avvenire DOPO la setup_custom_controls().
        self.combined_osc = None
        self.signal1_osc_tab2 = None
        self.signal2_osc_tab3 = None
        self.signal1_osc_tab4 = None
        self.signal2_osc_tab4 = None

        self.setupOscilloscope()
        self.setupSignal1Oscilloscope()
        self.setupSignal2Oscilloscope()
        self.setupTab4Oscilloscopes()

        # Connetti i ComboBox FFT
        if hasattr(self.ui, 'FFTcomb'):
            self.ui.FFTcomb.currentIndexChanged.connect(
                self._update_display_modes)
        if hasattr(self.ui, 'FFTcomb_2'):
            self.ui.FFTcomb_2.currentIndexChanged.connect(
                self._update_display_modes)
        # Chiama per impostare la modalità iniziale dei grafici
        self._update_display_modes()

        # Connetti il cambio di tab per gestire i timer dei grafici
        if hasattr(self.ui, 'tabWidget') and isinstance(self.ui.tabWidget, QTabWidget):
            self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
            # Triggera l'evento di cambio tab iniziale per avviare il timer del tab 1
            self.on_tab_changed(self.ui.tabWidget.currentIndex())
        else:
            print("Warning: tabWidget not found or not a QTabWidget in UI.")

        # ***** MODIFICA QUI *****
        # NON CONNETTERE I CONTROLLI DI SCALA QUI!
        # Vengono connessi DOPO in MainWindow.__init__ per usare i nuovi CustomStepSpinBox
        # self._connect_scale_controls()
        # ************************

    # ***** MODIFICA QUI *****
    # Rinomina il metodo per essere pubblico e chiamabile da MainWindow
    def connect_scale_controls(self):
        print("Connecting scale controls...")
        if hasattr(self.ui, 'voltdiv_spbx'):
            # Assicurati che self.ui.voltdiv_spbx sia ora l'istanza di CustomStepSpinBox
            # e che il suo segnale valueChanged funzioni correttamente.
            self.ui.voltdiv_spbx.valueChanged.connect(
                self.on_voltage_setting_changed)
            print("Connected voltdiv_spbx.valueChanged")
        else:
             print("Warning: voltdiv_spbx not found for connecting valueChanged.")

        if hasattr(self.ui, 'voltdiv_cb'):
            self.ui.voltdiv_cb.currentIndexChanged.connect(
                self.on_voltage_setting_changed)
            print("Connected voltdiv_cb.currentIndexChanged")
        else:
             print("Warning: voltdiv_cb not found for connecting currentIndexChanged.")

        if hasattr(self.ui, 'timediv_spbx'):
            self.ui.timediv_spbx.valueChanged.connect(
                self.on_time_setting_changed)
            print("Connected timediv_spbx.valueChanged")
        else:
             print("Warning: timediv_spbx not found for connecting valueChanged.")

        if hasattr(self.ui, 'timediv_cb'):
            self.ui.timediv_cb.currentIndexChanged.connect(
                self.on_time_setting_changed)
            print("Connected timediv_cb.currentIndexChanged")
        else:
             print("Warning: timediv_cb not found for connecting currentIndexChanged.")

        # Connetti i segnali di cambio scala a *tutti* gli oscilloscopi
        # Indipendentemente dal tab attivo, gli aggiornamenti della scala devono arrivare
        # a tutti, ma solo i grafici nel tab attivo si ridisegneranno effettivamente
        # grazie alla logica di on_tab_changed e display_timer.
        for osc in self.oscilloscope_widgets:
             if hasattr(osc, 'update_voltage_scale'):
                self.voltage_scale_changed.connect(osc.update_voltage_scale)
                print(f"Connected voltage_scale_changed to {type(osc).__name__}")
             if hasattr(osc, 'update_time_scale'):
                self.time_scale_changed.connect(osc.update_time_scale)
                print(f"Connected time_scale_changed to {type(osc).__name__}")

    # ************************


    def _add_osc_widget(self, osc_widget_instance):
        # Questo metodo crea i widget ma NON connette i segnali voltage/time_scale_changed qui.
        # Le connessioni vengono fatte separatamente in connect_scale_controls DOPO che MainWindow
        # ha finito di impostare i custom spinbox.
        if osc_widget_instance:
            if hasattr(osc_widget_instance, 'display_timer'):
                self.oscilloscope_widgets.append(osc_widget_instance)
            # RIMOSSO: Connessioni scale_changed spostate in connect_scale_controls
            # if hasattr(osc_widget_instance, 'update_voltage_scale'):
            #     self.voltage_scale_changed.connect(
            #         osc_widget_instance.update_voltage_scale)
            # if hasattr(osc_widget_instance, 'update_time_scale'):
            #     self.time_scale_changed.connect(
            #         osc_widget_instance.update_time_scale)


    def setupOscilloscope(self):
        tab1_widget = self.ui.tabWidget.findChild(QWidget, "tab_1")
        if tab1_widget is None: print("Tab 'tab_1' not found!"); return
        layout = tab1_widget.layout()
        if layout is None: layout = QVBoxLayout(tab1_widget); tab1_widget.setLayout(layout)
        self.combined_osc = CombinedOscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.combined_osc) # Aggiunge alla lista degli oscilloscopi
        layout.addWidget(self.combined_osc) # Aggiunge al layout del tab

    def setupSignal1Oscilloscope(self):
        tab2_widget = self.ui.tabWidget.findChild(QWidget, "tab_2")
        if tab2_widget is None: print("Tab 'tab_2' not found!"); return
        layout = tab2_widget.layout()
        if layout is None: layout = QVBoxLayout(tab2_widget); tab2_widget.setLayout(layout)
        self.signal1_osc_tab2 = Signal1Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.signal1_osc_tab2)
        layout.addWidget(self.signal1_osc_tab2)

    def setupSignal2Oscilloscope(self):
        tab3_widget = self.ui.tabWidget.findChild(QWidget, "tab_3")
        if tab3_widget is None: print("Tab 'tab_3' not found!"); return
        layout = tab3_widget.layout()
        if layout is None: layout = QVBoxLayout(tab3_widget); tab3_widget.setLayout(layout)
        self.signal2_osc_tab3 = Signal2Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self._add_osc_widget(self.signal2_osc_tab3)
        layout.addWidget(self.signal2_osc_tab3)

    def setupTab4Oscilloscopes(self):
        tab4_widget = self.ui.tabWidget.findChild(QWidget, "tab_4")
        if tab4_widget is None: print("Tab 'tab_4' not found!"); return
        layout = tab4_widget.layout()
        if layout is None:
            # Se non c'è layout, crea un QVBoxLayout.
            layout = QVBoxLayout(tab4_widget)
            tab4_widget.setLayout(layout)
        elif not isinstance(layout, QVBoxLayout):
             # Se c'è un layout ma non è QVBoxLayout, potremmo avere problemi.
             # Questa parte del codice sembra un tentativo di correzione, ma potrebbe essere rischioso.
             # Se Designer crea layout diversi, andrebbero gestiti specificamente.
             # Assumiamo che QVBoxLayout sia quello desiderato.
             print(f"Warning: Layout for tab_4 is not QVBoxLayout ({type(layout).__name__}). Trying to replace.")
             # Salva i widget esistenti se vuoi riaggiungerli, altrimenti verranno persi.
             # Per semplicità qui, assumiamo che sia ok sostituire se non è QVBoxLayout.
             # Pulisci il vecchio layout (potrebbe essere necessario disparentare i widget)
             # mentre = layout.takeAt(0)
             # while item:
             #    widget = item.widget()
             #    if widget:
             #        widget.setParent(None) # Disparenta per non eliminarlo con il layout
             #    item = layout.takeAt(0)

             # C'è un potenziale problema qui: se il layout esistente contiene già widget,
             # rimuoverlo e crearne uno nuovo li disassocerà dalla UI.
             # Una strategia migliore potrebbe essere assicurarsi che il layout esista e sia QVBoxLayout
             # o adattare l'aggiunta dei widget al layout esistente.
             # Dato il codice fornito, lo lascio come era, ma è un punto di attenzione.
             QWidget().setLayout(layout) # Disinstalla il vecchio layout
             layout = QVBoxLayout(tab4_widget) # Crea il nuovo QVBoxLayout
             tab4_widget.setLayout(layout) # Imposta il nuovo layout


        self.signal1_osc_tab4 = Signal1Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self.signal1_osc_tab4.plot_widget.setTitle("Channel 1")
        self._add_osc_widget(self.signal1_osc_tab4)
        layout.addWidget(self.signal1_osc_tab4)

        self.signal2_osc_tab4 = Signal2Oscilloscope(
            self.signal_source, self.BUFFER_SIZE, self.signal_source.sampling_rate_hz, self)
        self.signal2_osc_tab4.plot_widget.setTitle("Channel 2")
        self._add_osc_widget(self.signal2_osc_tab4)
        layout.addWidget(self.signal2_osc_tab4)


    @Slot()
    def on_voltage_setting_changed(self):
        print("Voltage setting changed, emitting signal.")
        self.voltage_scale_changed.emit() # Emette il segnale per notificare i grafici

    @Slot()
    def on_time_setting_changed(self):
        print("Time setting changed, emitting signal.")
        self.time_scale_changed.emit() # Emette il segnale per notificare i grafici


    @Slot()
    def _update_display_modes(self):
        # Legge le selezioni dai combo box FFT
        fft1 = hasattr(self.ui, 'FFTcomb') and self.ui.FFTcomb.currentText() == "FFT"
        fft2 = hasattr(self.ui, 'FFTcomb_2') and self.ui.FFTcomb_2.currentText() == "FFT"

        # Aggiorna la modalità di visualizzazione per ogni oscilloscopio
        # Notifica tutti gli oscilloscopi, la logica display_timer nel tab attivo
        # assicurerà che solo quelli visibili si aggiornino pesantemente
        if self.combined_osc:
            self.combined_osc.set_display_mode("FFT" if fft1 and fft2 else "Time D.")
        if self.signal1_osc_tab2:
            self.signal1_osc_tab2.set_display_mode("FFT" if fft1 else "Time D.")
        if self.signal2_osc_tab3:
            self.signal2_osc_tab3.set_display_mode("FFT" if fft2 else "Time D.")
        if self.signal1_osc_tab4:
             # Per tab4, puoi decidere se entrambi seguono lo stesso combobox
             # o se channel 1 segue FFTcomb e channel 2 segue FFTcomb_2
             # Qui seguo la logica originale (channel 1 segue FFTcomb)
            self.signal1_osc_tab4.set_display_mode("FFT" if fft1 else "Time D.")
        if self.signal2_osc_tab4:
            # E channel 2 segue FFTcomb_2
            self.signal2_osc_tab4.set_display_mode("FFT" if fft2 else "Time D.")

    @Slot(int)
    def on_tab_changed(self, index):
        # Ottieni il widget del tab corrente
        current_tab = self.ui.tabWidget.widget(index)

        # Ferma i timer di visualizzazione per TUTTI i grafici non attivi
        for osc in self.oscilloscope_widgets:
            if hasattr(osc, 'display_timer'):
                # Controlla se l'oscilloscopio è nel tab corrente (direttamente o come figlio)
                # Questo controllo è un po' più robusto rispetto a un semplice confronto con current_tab
                is_in_current_tab = False
                # Verifica se l'oscilloscopio è il widget del tab corrente
                if osc == current_tab:
                    is_in_current_tab = True
                # Verifica se l'oscilloscopio è un discendente del widget del tab corrente
                elif current_tab and osc.parent() == current_tab or osc.parent().parent() == current_tab: # Controllo rudimentale sul parent/grandparent
                     is_in_current_tab = True
                # Aggiungere controlli più specifici se i widget sono annidati più profondamente
                # Ad es., controllare se osc è findChild() di current_tab (costoso)
                # o verificare il layout di current_tab per trovare osc (meglio)
                layout = current_tab.layout()
                if layout:
                    for i in range(layout.count()):
                         item = layout.itemAt(i)
                         if item and item.widget() == osc:
                             is_in_current_tab = True
                             break


                if not is_in_current_tab:
                    osc.display_timer.stop()
                    # print(f"Stopped timer for {type(osc).__name__}")
                else:
                     # Avvia o riavvia il timer per i grafici nel tab corrente
                    if not osc.display_timer.isActive():
                         osc.display_timer.start()
                         # print(f"Started timer for {type(osc).__name__}")
                    # Forza un aggiornamento immediato all'attivazione del tab
                    if hasattr(osc, 'update_display'):
                        osc.update_display()
                        # print(f"Forced update for {type(osc).__name__}")
