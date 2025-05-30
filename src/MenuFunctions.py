# --- START OF FILE MenuFunctions.py ---
from PySide6.QtWidgets import QMessageBox, QFileDialog, QComboBox, QApplication, QWidget
from PySide6.QtGui import QDesktopServices, QAction
# QTimer potrebbe servire per fallback
from PySide6.QtCore import Slot, QUrl, QStandardPaths, QDir, QObject, Qt, QTimer

import os
import datetime
import pyqtgraph as pg  # Importa pyqtgraph
try:
    # ImageExporter è solitamente qui
    from pyqtgraph.exporters import ImageExporter
except ImportError:
    ImageExporter = None  # Fallback nel caso non sia trovato o per versioni più vecchie


class MenuFunctions(QObject):
    def __init__(self, mainwindow, signal_source_ref=None, gui_functions_ref=None, parent=None):
        super().__init__(parent)
        self.main = mainwindow
        self.ui = mainwindow.ui
        self.signal_source = signal_source_ref
        # Fondamentale per accedere ai widget oscilloscopio
        self.gui_functions = gui_functions_ref
        self._connect_actions()

    def _connect_actions(self):
        print("Connecting Menu actions...")
        # FILE Menu
        action_to_connect = None
        if hasattr(self.ui, 'actionQuit'):
            action_to_connect = getattr(self.ui, 'actionQuit')
        elif hasattr(self.ui, 'actionClose'):
            action_to_connect = getattr(self.ui, 'actionClose')

        if action_to_connect and isinstance(action_to_connect, QAction):
            action_to_connect.triggered.connect(self.main.close)
            print(
                f"Connected '{action_to_connect.objectName()}' to main window close.")
        else:
            print(
                "Warning: Quit action ('actionQuit' or 'actionClose') not found or not a QAction.")

        if hasattr(self.ui, 'actionSave') and isinstance(self.ui.actionSave, QAction):
            self.ui.actionSave.triggered.connect(
                self.save_current_tab_screenshot)
        else:
            print("Warning: actionSave not found or not a QAction.")

        # VIEW Menu
        if hasattr(self.ui, 'actionFrequency_Domain') and isinstance(self.ui.actionFrequency_Domain, QAction):
            self.ui.actionFrequency_Domain.triggered.connect(
                self.set_domain_frequency)
        else:
            print("Warning: actionFrequency_Domain not found or not a QAction.")

        if hasattr(self.ui, 'actionTime_Domain') and isinstance(self.ui.actionTime_Domain, QAction):
            self.ui.actionTime_Domain.triggered.connect(self.set_domain_time)
        else:
            print("Warning: actionTime_Domain not found or not a QAction.")

        if hasattr(self.ui, 'actionMain_View') and isinstance(getattr(self.ui, 'actionMain_View'), QAction):
            self.ui.actionMain_View.triggered.connect(
                self.set_default_view_voltage)
        else:
            print("Warning: actionMain_View (Voltage) not found or not a QAction.")

        if hasattr(self.ui, 'actionMain_View_2') and isinstance(getattr(self.ui, 'actionMain_View_2'), QAction):
            self.ui.actionMain_View_2.triggered.connect(
                self.set_default_view_time)
        else:
            print("Warning: actionMain_View_2 (Time) not found or not a QAction.")

        # RECORD Menu
        if hasattr(self.ui, 'actionStart_Recording') and isinstance(self.ui.actionStart_Recording, QAction):
            self.ui.actionStart_Recording.triggered.connect(
                self.toggle_recording)
        else:
            print("Warning: actionStart_Recording not found or not a QAction.")

        # HELP Menu
        if hasattr(self.ui, 'actionInformation') and isinstance(self.ui.actionInformation, QAction):
            self.ui.actionInformation.triggered.connect(
                self.show_information_file)
        else:
            print("Warning: actionInformation not found or not a QAction.")

    @Slot()
    def show_information_file(self):
        file_name = "information.txt"
        base_path = ""
        try:
            if hasattr(self.main.__class__.__module__, '__file__'):
                base_path = os.path.dirname(os.path.abspath(
                    self.main.__class__.__module__.__file__))
                if not os.path.exists(os.path.join(base_path, file_name)):
                    parent_dir_path = os.path.dirname(base_path)
                    if os.path.exists(os.path.join(parent_dir_path, file_name)):
                        base_path = parent_dir_path
            else:
                base_path = os.getcwd()
        except Exception:
            base_path = os.getcwd()

        file_path = os.path.join(base_path, file_name)

        if os.path.exists(file_path):
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(file_path)):
                QMessageBox.warning(self.main, "Error",
                                    f"Cannot open file: {file_path}\nEnsure you have a default application for .txt files.")
        else:
            QMessageBox.information(
                self.main, "Not Found", f"Information file not found at: {file_path}")

    @Slot()
    def save_current_tab_screenshot(self):
        if ImageExporter is None:
            QMessageBox.critical(
                self.main, "Error", "pyqtgraph.exporters.ImageExporter is not available. Cannot save plot screenshot.")
            return

        if not hasattr(self.ui, 'tabWidget') or not self.gui_functions:
            QMessageBox.warning(
                self.main, "Error", "Required components (TabWidget or GuiFunctions) not available.")
            return

        tab_widget = self.ui.tabWidget
        current_tab_index = tab_widget.currentIndex()

        # Lista di dizionari {"plot_item": item, "suggested_name_part": "part"}
        plots_to_export_info = []

        # Identificare i PlotItem in base al tab corrente
        # Accediamo ai widget oscilloscopio tramite self.gui_functions
        osc_widget = None
        if current_tab_index == 0:  # Tab 1 -> combined_osc
            osc_widget = self.gui_functions.combined_osc
            if osc_widget and hasattr(osc_widget, 'plot_widget'):
                plots_to_export_info.append({
                    "plot_item": osc_widget.plot_widget.getPlotItem(),
                    "suggested_name_part": f"tab{current_tab_index+1}_combined"
                })
        elif current_tab_index == 1:  # Tab 2 -> signal1_osc_tab2
            osc_widget = self.gui_functions.signal1_osc_tab2
            if osc_widget and hasattr(osc_widget, 'plot_widget'):
                plots_to_export_info.append({
                    "plot_item": osc_widget.plot_widget.getPlotItem(),
                    "suggested_name_part": f"tab{current_tab_index+1}_signal1"
                })
        elif current_tab_index == 2:  # Tab 3 -> signal2_osc_tab3
            osc_widget = self.gui_functions.signal2_osc_tab3
            if osc_widget and hasattr(osc_widget, 'plot_widget'):
                plots_to_export_info.append({
                    "plot_item": osc_widget.plot_widget.getPlotItem(),
                    "suggested_name_part": f"tab{current_tab_index+1}_signal2"
                })
        elif current_tab_index == 3:  # Tab 4 -> signal1_osc_tab4 AND signal2_osc_tab4
            osc_widget1 = self.gui_functions.signal1_osc_tab4
            osc_widget2 = self.gui_functions.signal2_osc_tab4
            if osc_widget1 and hasattr(osc_widget1, 'plot_widget'):
                plots_to_export_info.append({
                    "plot_item": osc_widget1.plot_widget.getPlotItem(),
                    "suggested_name_part": f"tab{current_tab_index+1}_signal1"
                })
            if osc_widget2 and hasattr(osc_widget2, 'plot_widget'):
                plots_to_export_info.append({
                    "plot_item": osc_widget2.plot_widget.getPlotItem(),
                    "suggested_name_part": f"tab{current_tab_index+1}_signal2"
                })
        else:
            # Fallback per tab non specificamente gestiti (es. se si aggiungono altri tab)
            # Oppure se il tab corrente non contiene un PlotWidget noto.
            # In questo caso, potremmo usare il vecchio metodo di grab() o non fare nulla.
            # Per ora, mostriamo un messaggio se nessun plot è identificato.
            pass

        if not plots_to_export_info:
            # Se nessun plot specifico è stato trovato, prova a fare un grab dell'intero widget del tab
            # Questo è un fallback utile se un tab non ha un plot pyqtgraph o per tab non ancora mappati
            current_tab_page_widget = tab_widget.widget(current_tab_index)
            if current_tab_page_widget:
                self._grab_entire_tab_fallback(
                    current_tab_page_widget, f"tab{current_tab_index+1}_full")
            else:
                QMessageBox.information(
                    self.main, "Info", "No content found in the current tab to save.")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_save_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation) or \
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation) or \
            QDir.homePath()

        for export_info in plots_to_export_info:
            plot_item_to_export = export_info["plot_item"]
            name_part = export_info["suggested_name_part"]

            suggested_file_name = f"scope_{name_part}_{timestamp}.png"

            # Chiedi all'utente dove salvare ciascun plot (se ce n'è più di uno, come in Tab 4)
            file_path_to_save, _ = QFileDialog.getSaveFileName(
                self.main,
                f"Save Plot ({name_part})",  # Titolo del dialogo aggiornato
                os.path.join(default_save_path, suggested_file_name),
                # Aggiunto SVG per qualità vettoriale
                "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;SVG Images (*.svg);;All Files (*)"
            )

            if file_path_to_save:
                try:
                    # Crea l'exporter per il PlotItem specifico
                    exporter = ImageExporter(plot_item_to_export)

                    # Opzionale: imposta parametri di esportazione, come dimensioni
                    # exporter.parameters()['width'] = 1024 # Esempio
                    # exporter.parameters()['height'] = 768 # Esempio

                    # Processa eventi una volta per assicurare che il grafico sia aggiornato
                    # prima che l'exporter faccia il suo lavoro.
                    QApplication.processEvents()

                    exporter.export(file_path_to_save)
                    QMessageBox.information(
                        self.main, "Plot Saved", f"Plot ({name_part}) saved to:\n{file_path_to_save}")
                except Exception as e:
                    QMessageBox.critical(self.main, "Export Error",
                                         f"Could not export plot ({name_part}): {str(e)}")

    def _grab_entire_tab_fallback(self, tab_page_widget, base_name_suggestion):
        """Metodo di fallback per catturare l'intero widget del tab."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_save_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation) or \
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation) or \
            QDir.homePath()
        suggested_file_name = f"scope_{base_name_suggestion}_{timestamp}.png"

        file_path_to_save, _ = QFileDialog.getSaveFileName(
            self.main,
            "Save Full Tab Screenshot",
            os.path.join(default_save_path, suggested_file_name),
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )

        if file_path_to_save:
            # Per il grab generico, un piccolo delay e repaint possono ancora essere utili
            delay_ms = 300  # Delay ridotto rispetto a prima, ma ancora presente

            # Definiamo una piccola lambda o funzione interna per il grab
            def _do_generic_grab(path, widget):
                try:
                    QApplication.processEvents()  # Processa eventi pendenti
                    widget.repaint()             # Forza repaint
                    QApplication.processEvents()  # Processa l'evento di repaint

                    pixmap = widget.grab()
                    if pixmap.isNull():
                        QMessageBox.warning(
                            self.main, "Error", "Failed to grab screenshot (pixmap is null).")
                        return
                    if not pixmap.save(path):
                        QMessageBox.warning(
                            self.main, "Save Error", f"Cannot save screenshot to: {path}")
                    else:
                        QMessageBox.information(
                            self.main, "Saved", f"Screenshot saved to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(
                        self.main, "Screenshot Error", f"Error grabbing widget: {e}")

            QTimer.singleShot(delay_ms, lambda p=file_path_to_save,
                              t=tab_page_widget: _do_generic_grab(p, t))

    @Slot()
    def toggle_recording(self):
        if not self.main.is_recording:
            self.main.is_recording = True
            self.main.recorded_data.clear()
            record_duration = getattr(self.main, 'REC_DUR', 1000)
            self.main.recording_timer.start(record_duration)
            if hasattr(self.ui, 'actionStart_Recording'):
                self.ui.actionStart_Recording.setText("Stop Recording")
            if hasattr(self.ui, 'statusbar'):
                self.ui.statusbar.showMessage(
                    f"Recording... ({record_duration} ms)", record_duration + 500)
        else:
            self.stop_recording_and_save()

    @Slot()
    def stop_recording_and_save(self):
        self.main.is_recording = False
        if self.main.recording_timer.isActive():
            self.main.recording_timer.stop()
        if hasattr(self.ui, 'actionStart_Recording'):
            self.ui.actionStart_Recording.setText("Start Recording")
        if hasattr(self.ui, 'statusbar'):
            self.ui.statusbar.clearMessage()

        if not self.main.recorded_data:
            QMessageBox.information(self.main, "Info", "No data was recorded.")
            return

        default_file_name = f"recorded_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        default_save_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation)
        if not default_save_path:
            default_save_path = QDir.homePath()

        file_path_to_save, _ = QFileDialog.getSaveFileName(
            self.main,
            "Save Recorded Data",
            os.path.join(default_save_path, default_file_name),
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path_to_save:
            try:
                with open(file_path_to_save, 'w') as f:
                    f.write("Channel1,Channel2\n")
                    for v1, v2 in self.main.recorded_data:
                        f.write(f"{v1:.6f},{v2:.6f}\n")
                QMessageBox.information(
                    self.main, "Data Saved", f"Recorded data successfully saved to:\n{file_path_to_save}")
            except Exception as e:
                QMessageBox.critical(
                    self.main, "Save Error", f"Could not save data: {e}")

    @Slot()
    def set_domain_frequency(self):
        if hasattr(self.ui, 'FFTcomb'):
            self._set_fft_combo_by_text(self.ui.FFTcomb, "FFT")
        if hasattr(self.ui, 'FFTcomb_2'):
            self._set_fft_combo_by_text(self.ui.FFTcomb_2, "FFT")

    @Slot()
    def set_domain_time(self):
        if hasattr(self.ui, 'FFTcomb'):
            self._set_fft_combo_by_text(self.ui.FFTcomb, "Time D.")
        if hasattr(self.ui, 'FFTcomb_2'):
            self._set_fft_combo_by_text(self.ui.FFTcomb_2, "Time D.")

    def _set_fft_combo_by_text(self, combo, text):
        if combo and isinstance(combo, QComboBox):
            idx = combo.findText(text, Qt.MatchFlag.MatchFixedString)
            if idx != -1:
                combo.setCurrentIndex(idx)
            else:
                print(
                    f"Warning: Text '{text}' not found in ComboBox '{combo.objectName()}'.")

    @Slot()
    def set_default_view_voltage(self):
        if not self.gui_functions:
            print("Warning: gui_functions not available in MenuFunctions.")
            return
        if not hasattr(self.ui, 'voltdiv_spbx'):
            print("Warning: voltdiv_spbx not found in UI.")
            return
        if not hasattr(self.ui, 'voltdiv_cb'):
            print("Warning: voltdiv_cb not found in UI.")
            return

        default_value = self.gui_functions.DEFAULT_VOLT_DIV_VALUE
        idx = self.ui.voltdiv_cb.findText("V", Qt.MatchFlag.MatchFixedString)
        if idx == -1:
            idx = self.gui_functions.DEFAULT_VOLT_DIV_UNIT_INDEX

        self.ui.voltdiv_cb.setCurrentIndex(idx)
        self.ui.voltdiv_spbx.setValue(default_value)
        # if self.gui_functions:
        #     self.gui_functions.on_voltage_setting_changed()

    @Slot()
    def set_default_view_time(self):
        if not self.gui_functions:
            print("Warning: gui_functions not available in MenuFunctions.")
            return
        if not hasattr(self.ui, 'timediv_spbx'):
            print("Warning: timediv_spbx not found in UI.")
            return
        if not hasattr(self.ui, 'timediv_cb'):
            print("Warning: timediv_cb not found in UI.")
            return

        default_value = self.gui_functions.DEFAULT_TIME_DIV_VALUE
        idx = self.ui.timediv_cb.findText("s", Qt.MatchFlag.MatchFixedString)
        if idx == -1:
            idx = self.gui_functions.DEFAULT_TIME_DIV_UNIT_INDEX

        self.ui.timediv_cb.setCurrentIndex(idx)
        self.ui.timediv_spbx.setValue(default_value)
        # if self.gui_functions:
        #     self.gui_functions.on_time_setting_changed()

# --- END OF FILE MenuFunctions.py ---
