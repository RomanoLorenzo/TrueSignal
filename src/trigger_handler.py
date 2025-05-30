import numpy as np
from PySide6.QtCore import QObject, Signal, Slot

class TriggerHandler(QObject):
    trigger_detected = Signal(int)  # Emits buffer index where trigger occurred

    def __init__(self, buffer_size):
        super().__init__()
        self.buffer_size = buffer_size
        self.pos_edge_enabled = False
        self.neg_edge_enabled = False
        self.derivative_enabled = False
        self.derivative_threshold = 0.1  # Default threshold for derivative trigger
        self.is_frozen = False
        self.frozen_data = None
        self.frozen_index = None
        self.last_value = None
        
    def set_pos_edge_enabled(self, enabled):
        self.pos_edge_enabled = enabled
        if enabled:
            self.neg_edge_enabled = False
            self.derivative_enabled = False
        if not enabled and not self.neg_edge_enabled:
            self.is_frozen = False
            
    def set_neg_edge_enabled(self, enabled):
        self.neg_edge_enabled = enabled
        if enabled:
            self.pos_edge_enabled = False
            self.derivative_enabled = False
        if not enabled and not self.pos_edge_enabled:
            self.is_frozen = False

    def set_derivative_enabled(self, enabled, threshold=0.1):
        self.derivative_enabled = enabled
        self.derivative_threshold = threshold
        if enabled:
            self.pos_edge_enabled = False
            self.neg_edge_enabled = False

    def check_trigger(self, buffer):
        if self.is_frozen:
            return None

        if not (self.pos_edge_enabled or self.neg_edge_enabled or self.derivative_enabled):
            return None

        # Start checking from the most recent data point
        current_idx = (self.buffer_size - 1)
        
        # We need at least 2 points for any trigger detection
        if current_idx < 1:
            return None

        # Get current and previous values
        current_val = buffer[current_idx]
        prev_val = buffer[current_idx - 1]

        # Check derivative trigger
        if self.derivative_enabled:
            derivative = abs(current_val - prev_val)
            if derivative > self.derivative_threshold:
                self.is_frozen = True
                self.frozen_index = current_idx
                return current_idx

        # Check positive edge trigger
        if self.pos_edge_enabled and prev_val < 0 and current_val >= 0:
            self.is_frozen = True
            self.frozen_index = current_idx
            return current_idx

        # Check negative edge trigger
        if self.neg_edge_enabled and prev_val > 0 and current_val <= 0:
            self.is_frozen = True
            self.frozen_index = current_idx
            return current_idx

        return None

    def unfreeze(self):
        self.is_frozen = False
        self.frozen_data = None
        self.frozen_index = None 