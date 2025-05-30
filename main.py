from PySide6.QtWidgets import (QSpinBox, QMainWindow, QApplication,
                               QMessageBox, QFileDialog, QComboBox,
                               QDoubleSpinBox, QVBoxLayout, QWidget,
                               QSplashScreen, QLabel)
from PySide6.QtGui import QValidator, QDesktopServices, QScreen, QPixmap, QIcon
from PySide6.QtCore import QTimer, Slot, QCoreApplication, QUrl, QStandardPaths, QDir, Qt

import sys
import os

# Importa le tue classi locali
# Assicurati che questi import siano corretti rispetto alla struttura delle tue directory
# Assicurati che ui_interface.py esista e contenga Ui_MainWindow
from src.ui_interface import *
from src.Functions import GuiFunctions  # Assicurati che Functions.py esista
# Assicurati che custom_spinbox.py esista
from src.custom_spinbox import CustomStepSpinBox
# Assicurati che MenuFunctions.py esista
from src.MenuFunctions import MenuFunctions

# Assicurati che queste classi custom siano disponibili
# Potresti dover aggiustare gli import a seconda di dove si trovano
try:
    from Custom_Widgets import *
    from Custom_Widgets.QAppSettings import QAppSettings
    # Aggiungi qui gli import specifici se Custom_Widgets.py contiene classi come loadJsonStyle
    # from Custom_Widgets.JsonStyle import loadJsonStyle # Esempio
    # from Custom_Widgets.QAppSettings import QAppSettings # Esempio
except ImportError:
    print("Warning: Custom_Widgets not found. Styling and settings might not work.")
    # Definisci dummy functions/classes se necessario per evitare NameError

    class QAppSettings:
        @staticmethod
        def updateAppSettings(window): pass

    def loadJsonStyle(window, ui, jsonFiles): pass


class MainWindow(QMainWindow):
    REC_DUR = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create and show splash screen with logo
        splash_pixmap = QPixmap("icons\logo.jpg")
        self.splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
        self.splash.show()

        # Set window title and icon
        self.setWindowTitle("SignaLab")
        self.setWindowIcon(QIcon("logo.jpg"))

        # Assicurati che loadJsonStyle sia definita o importata correttamente
        loadJsonStyle(self, self.ui, jsonFiles={"json-styles/style.json"})

        # Setup logo and title from JSON configuration
        self.setup_logo()

        # Crea l'istanza di GuiFunctions
        self.gui_functions = GuiFunctions(self)

        # Configura i controlli personalizzati (questo sostituisce gli spinbox)
        self.setup_custom_controls()

        # ***** MODIFICA QUI *****
        # EFFETTUA LE CONNESSIONI DOPO CHE GLI SPINBOX PERSONALIZZATI SONO STATI CREATI
        # Chiama il metodo pubblico da GuiFunctions
        self.gui_functions.connect_scale_controls()
        # ************************

        # Crea l'istanza di MenuFunctions, passando il riferimento aggiornato a gui_functions
        # Assicurati che MenuFunctions possa gestire l'inizializzazione successiva se necessario
        self.menu_functions = MenuFunctions(
            # Passa il riferimento a self.gui_functions
            self, gui_functions_ref=self.gui_functions)

        # Popola ComboBox FFT
        fft_options = ["Time D.", "FFT"]
        if hasattr(self.ui, 'FFTcomb'):
            self.ui.FFTcomb.addItems(fft_options)
        if hasattr(self.ui, 'FFTcomb_2'):
            self.ui.FFTcomb_2.addItems(fft_options)

        self.is_recording = False
        self.recorded_data = []
        self.recording_timer = QTimer(self)
        self.recording_timer.setSingleShot(True)
        if hasattr(self.menu_functions, 'stop_recording_and_save'):
            self.recording_timer.timeout.connect(
                self.menu_functions.stop_recording_and_save)

        # Connetti la sorgente dati alla funzione di raccolta dati (già corretta)
        if hasattr(self.gui_functions, 'signal_source') and self.gui_functions.signal_source:
            self.gui_functions.signal_source.data_updated.connect(
                self.collect_data_if_recording)

        # Close splash screen after 2 seconds and show main window
        QTimer.singleShot(2000, self.splash.close)
        QTimer.singleShot(2000, self.show)

        # Assicurati che QAppSettings sia definita o importata
        QAppSettings.updateAppSettings(self)

        # Force initial scale update
        self.gui_functions.on_voltage_setting_changed()
        self.gui_functions.on_time_setting_changed()

    def setup_logo(self):
        try:
            with open("json-styles/style.json", 'r') as f:
                import json
                config = json.load(f)
                logo_config = config["QMainWindow"][0].get("logo", {})
                
                if logo_config:
                    # Set window icon (this will appear in the title bar)
                    self.setWindowIcon(QIcon(logo_config["path"]))
                    
                    # Set window title
                    text_config = logo_config.get("text", {})
                    if text_config:
                        self.setWindowTitle(text_config["content"])
        except Exception as e:
            print(f"Error setting up logo: {e}")

    def setup_custom_controls(self):
        print("Configuring custom controls and setting defaults...")
        voltage_sequence = [1, 2, 5, 7.5]
        time_sequence = [0.5, 1, 2, 5]
        volt_units = ["V", "mV", "uV"]
        time_units = ["s", "ms", "us"]

        def replace_and_setup(spinbox_ui_name, combobox_ui_name, parent_frame_ui_name,
                              sequence_data, unit_list, default_value, default_unit_text):
            if not hasattr(self.ui, parent_frame_ui_name):
                print(
                    f"CRITICAL: Parent frame attribute '{parent_frame_ui_name}' not found in UI. Controls cannot be set up.")
                return
            parent_widget = getattr(self.ui, parent_frame_ui_name)
            if not parent_widget:
                print(
                    f"CRITICAL: Parent widget from attribute '{parent_frame_ui_name}' is None. Controls cannot be set up.")
                return

            layout = parent_widget.layout()
            if not layout:
                print(
                    f"Info: No layout for '{parent_frame_ui_name}', creating default QVBoxLayout.")
                layout = QVBoxLayout(parent_widget)
                parent_widget.setLayout(layout)

            # Replace SpinBox
            if hasattr(self.ui, spinbox_ui_name):
                old_spinbox = getattr(self.ui, spinbox_ui_name)
                # Ensure it's the type we expect from Designer
                if isinstance(old_spinbox, QDoubleSpinBox):
                    # Find the item in the layout for precise replacement
                    item_to_replace = None
                    index_to_replace_at = -1
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        if item and item.widget() == old_spinbox:
                            item_to_replace = item
                            index_to_replace_at = i
                            break

                    new_spinbox = CustomStepSpinBox(
                        sequence=sequence_data, parent=parent_widget)
                    new_spinbox.setValue(default_value)
                    # CRITICAL: Update self.ui reference
                    setattr(self.ui, spinbox_ui_name, new_spinbox)

                    if item_to_replace:
                        # Remove old item from layout
                        layout.takeAt(index_to_replace_at)
                        old_spinbox.deleteLater()  # Elimina il vecchio oggetto
                        layout.insertWidget(index_to_replace_at, new_spinbox)
                    # Fallback if not found in layout (shouldn't happen if UI is consistent)
                    else:
                        layout.addWidget(new_spinbox)
                        old_spinbox.deleteLater()  # Still delete the old one
                    print(
                        f"Replaced {spinbox_ui_name} with CustomStepSpinBox, set to {default_value}.")
                else:
                    print(
                        f"Error: {spinbox_ui_name} in UI is not QDoubleSpinBox (type: {type(old_spinbox)}). Cannot replace.")
            else:
                print(
                    f"Warning: {spinbox_ui_name} not found in UI. Check name.")

            # Populate ComboBox (Assumiamo che la ComboBox non venga sostituita, solo popolata)
            if hasattr(self.ui, combobox_ui_name):
                combobox = getattr(self.ui, combobox_ui_name)
                if isinstance(combobox, QComboBox):
                    combobox.clear()
                    combobox.addItems(unit_list)
                    idx = combobox.findText(
                        default_unit_text, Qt.MatchFlag.MatchFixedString)
                    combobox.setCurrentIndex(idx if idx != -1 else 0)
                    print(
                        f"Populated {combobox_ui_name}, set to {default_unit_text}.")
                else:
                    print(
                        f"Warning: {combobox_ui_name} in UI is not QComboBox.")
            else:
                print(
                    f"Warning: {combobox_ui_name} not found in UI. Check name.")

        # Esegue la sostituzione e il setup per i controlli Volt/Div e Time/Div
        replace_and_setup('voltdiv_spbx', 'voltdiv_cb', 'selframe1', voltage_sequence,
                          volt_units, GuiFunctions.DEFAULT_VOLT_DIV_VALUE, "V")
        replace_and_setup('timediv_spbx', 'timediv_cb', 'selframe2', time_sequence,
                          time_units, GuiFunctions.DEFAULT_TIME_DIV_VALUE, "s")

    @Slot(float, float)
    def collect_data_if_recording(self, value1, value2):
        if self.is_recording:
            self.recorded_data.append((value1, value2))

    def closeEvent(self, event): super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
