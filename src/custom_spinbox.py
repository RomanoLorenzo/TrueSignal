from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtGui import QValidator
import math

class CustomStepSpinBox(QDoubleSpinBox):

    def __init__(self, sequence, parent=None):
        super().__init__(parent)

        if not sequence:
            raise ValueError("CustomStepSpinBox sequence cannot be empty!")
        self._sequence = sorted([float(v) for v in sequence])
        self.setMinimum(self._sequence[0])
        self.setMaximum(self._sequence[-1])
        self.setValue(self._sequence[0])

        max_decimals = 0
        for val in self._sequence:
            s_val = str(val)
            if '.' in s_val:
                decimals = len(s_val.split('.')[-1])
                if val < 1 and val > 0 and not s_val.startswith('0.'):
                    decimals += 1
                max_decimals = max(max_decimals, decimals)
        self.setDecimals(max_decimals if max_decimals > 0 else 1)

    def stepBy(self, steps):
        """Overrides the default stepBy to move through the sequence."""
        if not self._sequence:
            super().stepBy(steps) # Fallback if sequence is somehow empty
            return

        current_value = self.value()
        current_sequence_index = -1
        for i, seq_val in enumerate(self._sequence):
            if math.isclose(current_value, seq_val, rel_tol=1e-9, abs_tol=1e-9): # Added abs_tol for small values
                current_sequence_index = i
                break
        
        if current_sequence_index == -1:
            current_sequence_index = self._find_closest_index(current_value)

        new_index = current_sequence_index + steps
        new_index = max(0, min(new_index, len(self._sequence) - 1))

        target_value = self._sequence[new_index]

        if not math.isclose(self.value(), target_value, rel_tol=1e-9, abs_tol=1e-9):
            self.setValue(target_value)
            self._last_valid_value = target_value

    def _find_closest_index(self, value):
        """Helper to find the index of the value closest to 'value' in the sequence."""
        if not self._sequence: return 0
        
        closest_val = min(self._sequence, key=lambda x: abs(x - value))
        try:
            return self._sequence.index(closest_val)
        except ValueError:
            return 0
        
    def fixup(self, input_str):
        """Corrects invalid input entered directly."""
        try:
            value = float(input_str)
            is_in_sequence = False
            closest_value_in_sequence = self._sequence[0]
            for seq_val in self._sequence:
                if math.isclose(value, seq_val, rel_tol=1e-9, abs_tol=1e-9):
                    closest_value_in_sequence = seq_val
                    is_in_sequence = True
                    break
            
            if not is_in_sequence:
                closest_index = self._find_closest_index(value)
                closest_value_in_sequence = self._sequence[closest_index]
            self._last_valid_value = closest_value_in_sequence
            return "{:.{}f}".format(closest_value_in_sequence, self.decimals())

        except ValueError:
            current_index = self._find_closest_index(self.value())
            closest_value = self._sequence[current_index]
            return "{:.{}f}".format(closest_value, self.decimals())

    def validate(self, input_str, pos):
        """Validates input as it is typed."""
        if not self._sequence: # Should not happen due to __init__ check
             return (QValidator.State.Invalid, input_str, pos)

        if not input_str: # Empty string
            return (QValidator.State.Intermediate, input_str, pos) # Allow empty for typing
        
        if input_str == '-' and self.minimum() < 0: # Allow typing negative sign if min is negative
            return (QValidator.State.Intermediate, input_str, pos)
        if input_str == '.': # Allow typing decimal point
            return (QValidator.State.Intermediate, input_str, pos)
        if input_str.endswith('.') and input_str.count('.') == 1: # Allow typing numbers like "1."
             try:
                val_check = float(input_str[:-1]) # check if "1" is valid start
                if self.minimum() <= val_check <= self.maximum(): # Crude check
                     return (QValidator.State.Intermediate, input_str, pos)
             except ValueError:
                pass # Invalid prefix

        try:
            value = float(input_str)
            for seq_val in self._sequence:
                if math.isclose(value, seq_val, rel_tol=1e-9, abs_tol=1e-9):
                    # Check if it's within min/max bounds (already handled by sequence construction, but good practice)
                    if self.minimum() <= value <= self.maximum():
                        return (QValidator.State.Acceptable, input_str, pos)
                    else: # Should not happen if sequence defines min/max
                        return (QValidator.State.Invalid, input_str, pos)

            is_prefix = False
            normalized_input_str = input_str.rstrip('.')

            for seq_val in self._sequence:
                seq_val_str = "{:.{}f}".format(seq_val, self.decimals()) 
                if seq_val_str.startswith(normalized_input_str):
                    is_prefix = True
                    break
            if is_prefix:
                return (QValidator.State.Intermediate, input_str, pos)

            return (QValidator.State.Intermediate, input_str, pos)

        except ValueError: # Not a valid float
            return (QValidator.State.Invalid, input_str, pos)
        
    def focusOutEvent(self, event):
        """
        Override focus out to prevent resetting to default value when focusing out.
        
        Args:
            event: The focus out event
        """
        # Get the current value before focus out
        current_value = self.value()

        # Let the base class handle the event
        super().focusOutEvent(event)

        # If the value got reset to 0.1 or minimum value, restore the previous valid value
        if abs(self.value() - self._sequence[0]) < 0.001 and not math.isclose(current_value, self._sequence[0], rel_tol=1e-9):
            # Block signals temporarily to avoid recursive signal activation
            self.blockSignals(True)
            self.setValue(self._last_valid_value)
            self.blockSignals(False)

    def setValue(self, value):
        """
        Override setValue to track the last valid value.
        
        Args:
            value: The value to set
        """
        # Call the parent class implementation first
        super().setValue(value)

        # Then store this as the last valid value (if it's not the minimum/reset value)
        if not math.isclose(value, self._sequence[0], rel_tol=1e-9) or value == self._sequence[0]:
            self._last_valid_value = value
