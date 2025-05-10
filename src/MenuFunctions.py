# --- START OF FILE MenuFunctions.py ---
from PySide6.QtWidgets import QMessageBox, QFileDialog, QComboBox, QApplication, QWidget
# Assicurati che QAction sia importato
from PySide6.QtGui import QDesktopServices, QAction
from PySide6.QtCore import Slot, QUrl, QStandardPaths, QDir, QObject, Qt,QTimer

import os
import datetime


class MenuFunctions(QObject):
    def __init__(self, mainwindow, signal_source_ref=None, gui_functions_ref=None, parent=None):
        super().__init__(parent)
        self.main = mainwindow
        self.ui = mainwindow.ui
        self.signal_source = signal_source_ref
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

        # --- CORREZIONE QUI ---
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
        # --- FINE CORREZIONE ---

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
            base_path = os.path.dirname(os.path.abspath(
                self.main.__class__.__module__.__file__))
            if not os.path.exists(os.path.join(base_path, file_name)):
                base_path = os.path.dirname(base_path)
        except:
            base_path = os.getcwd()
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(file_path)):
                QMessageBox.warning(self.main, "Error",
                                    f"Cannot open: {file_path}")
        else:
            QMessageBox.information(
                self.main, "Not Found", f"File not found: {file_path}")

    @Slot()
    def save_current_tab_screenshot(self):
        if not hasattr(self.ui, 'tabWidget'):
            return
        current_tab = self.ui.tabWidget.currentWidget()
        if not current_tab:
            return

        def do_grab(path):
            try:
                QApplication.processEvents()
                pixmap = current_tab.grab()
            except Exception as e:
                QMessageBox.critical(self.main, "Error",
                                     f"Screenshot failed: {e}")
                return
            if not pixmap.save(path):
                QMessageBox.warning(self.main, "Error",
                                    f"Cannot save to: {path}")
            else:
                QMessageBox.information(
                    self.main, "Saved", f"Screenshot saved to:\n{path}")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"scope_tab_{ts}.png"
        dpath = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation) or QDir.homePath()
        fpath, _ = QFileDialog.getSaveFileName(self.main, "Save Screenshot", os.path.join(
            dpath, fname), "PNG (*.png);;JPEG (*.jpg)")
        if fpath:
            tab4_widget = self.ui.tabWidget.findChild(QWidget, "tab_4")
            is_tab4 = tab4_widget and current_tab == tab4_widget
            delay = 250 if is_tab4 else 50
            QTimer.singleShot(delay, lambda p=fpath: do_grab(p))

    @Slot()
    def toggle_recording(self):
        if not self.main.is_recording:
            self.main.is_recording = True
            self.main.recorded_data.clear()
            self.main.recording_timer.start(self.main.REC_DUR)
            if hasattr(self.ui, 'actionStart_Recording'):
                self.ui.actionStart_Recording.setText("Stop Recording")
            if hasattr(self.ui, 'statusbar'):
                self.ui.statusbar.showMessage(
                    f"Recording... ({self.main.REC_DUR} ms)", self.main.REC_DUR + 500)
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
            QMessageBox.information(self.main, "Info", "No data recorded.")
            return
        fname = "recorded_data.txt"
        dpath = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation) or QDir.homePath()
        fpath, _ = QFileDialog.getSaveFileName(
            self.main, "Save Data", os.path.join(dpath, fname), "Text (*.txt)")
        if fpath:
            try:
                with open(fpath, 'w') as f:
                    f.write("Channel1,Channel2\n")
                    for v1, v2 in self.main.recorded_data:
                        f.write(f"{v1:.6f},{v2:.6f}\n")
                QMessageBox.information(
                    self.main, "Saved", f"Data saved to:\n{fpath}")
            except Exception as e:
                QMessageBox.critical(self.main, "Error", f"Cannot save: {e}")

    @Slot()
    def set_domain_frequency(self):
        self._set_fft_combo_by_text(self.ui.FFTcomb, "FFT")
        self._set_fft_combo_by_text(self.ui.FFTcomb_2, "FFT")

    @Slot()
    def set_domain_time(self):
        self._set_fft_combo_by_text(self.ui.FFTcomb, "Time D.")
        self._set_fft_combo_by_text(self.ui.FFTcomb_2, "Time D.")

    def _set_fft_combo_by_text(self, combo, text):
        if combo and isinstance(combo, QComboBox):
            idx = combo.findText(text, Qt.MatchFlag.MatchFixedString)
            if idx != -1:
                combo.setCurrentIndex(idx)

    @Slot()
    def set_default_view_voltage(self):
        if hasattr(self.ui, 'voldiv_spbx') and hasattr(self.ui, 'voldiv_cb') and self.gui_functions:
            idx = self.ui.voldiv_cb.findText(
                "V", Qt.MatchFlag.MatchFixedString)
            self.ui.voldiv_cb.setCurrentIndex(
                idx if idx != -1 else self.gui_functions.DEFAULT_VOLT_DIV_UNIT_INDEX)
            self.ui.voldiv_spbx.setValue(
                self.gui_functions.DEFAULT_VOLT_DIV_VALUE)

    @Slot()
    def set_default_view_time(self):
        if hasattr(self.ui, 'timediv_spbx') and hasattr(self.ui, 'timediv_cb') and self.gui_functions:
            idx = self.ui.timediv_cb.findText(
                "s", Qt.MatchFlag.MatchFixedString)
            self.ui.timediv_cb.setCurrentIndex(
                idx if idx != -1 else self.gui_functions.DEFAULT_TIME_DIV_UNIT_INDEX)
            self.ui.timediv_spbx.setValue(
                self.gui_functions.DEFAULT_TIME_DIV_VALUE)
# --- FINE DEL FILE MenuFunctions.py ---
