from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtGui import QValidator
import math

# --- Custom SpinBox Class ---
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
                # This condition is a bit specific and might not be necessary with standard float string conversions.
                # If float(".5") -> 0.5 and str(0.5) -> "0.5", then s_val.startswith('0.') will be true.
                # Leaving it as is for now, assuming it handles an edge case you encountered.
                if val < 1 and val > 0 and not s_val.startswith('0.'):
                    decimals += 1
                max_decimals = max(max_decimals, decimals)
        self.setDecimals(max_decimals if max_decimals > 0 else 1)

        # self.setSingleStep(0.1) # This is less relevant due to custom stepBy override.
                                # It's used by base QDoubleSpinBox.stepBy if not overridden.

    def stepBy(self, steps):
        """Overrides the default stepBy to move through the sequence."""
        if not self._sequence:
            super().stepBy(steps) # Fallback if sequence is somehow empty
            return

        current_value = self.value()
        
        # Find the index of the item in the sequence that is current_value or closest to current_value.
        # This effectively determines our starting point in the sequence.
        current_sequence_index = -1
        # Prioritize finding an exact (or very close) match in the sequence
        for i, seq_val in enumerate(self._sequence):
            if math.isclose(current_value, seq_val, rel_tol=1e-9, abs_tol=1e-9): # Added abs_tol for small values
                current_sequence_index = i
                break
        
        if current_sequence_index == -1: # Not found via isclose, so find robustly closest
            current_sequence_index = self._find_closest_index(current_value)
            # If current_value was not in sequence, and we want to snap to closest before stepping:
            # if not math.isclose(current_value, self._sequence[current_sequence_index], rel_tol=1e-9, abs_tol=1e-9):
            #    self.setValue(self._sequence[current_sequence_index]) # This would be a pre-step snap
            #    # For now, we step from the determined current_sequence_index directly.

        new_index = current_sequence_index + steps
        new_index = max(0, min(new_index, len(self._sequence) - 1)) # Clamp index

        target_value = self._sequence[new_index]
        
        # Only set value if it's actually changing to avoid redundant signals
        # and to handle floating point comparisons carefully.
        if not math.isclose(self.value(), target_value, rel_tol=1e-9, abs_tol=1e-9):
            self.setValue(target_value)
        # No call to super().stepBy() as we are fully overriding.

    def _find_closest_index(self, value):
        """Helper to find the index of the value closest to 'value' in the sequence."""
        if not self._sequence: return 0
        # Find the value in the sequence that has the minimum absolute difference to the input value
        closest_val = min(self._sequence, key=lambda x: abs(x - value))
        try:
            # Return the index of this closest value
            return self._sequence.index(closest_val)
        except ValueError:
            # Should not happen if min() correctly returns an element from _sequence
            return 0
        
    def fixup(self, input_str):
        """Corrects invalid input entered directly."""
        try:
            value = float(input_str)
            # Check if the value is already in the sequence (within tolerance)
            is_in_sequence = False
            closest_value_in_sequence = self._sequence[0] # Default to first if nothing else matches
            for seq_val in self._sequence:
                if math.isclose(value, seq_val, rel_tol=1e-9, abs_tol=1e-9):
                    closest_value_in_sequence = seq_val
                    is_in_sequence = True
                    break
            
            if not is_in_sequence:
                # If not in sequence, find the absolutely closest value from the sequence
                closest_index = self._find_closest_index(value)
                closest_value_in_sequence = self._sequence[closest_index]

            return "{:.{}f}".format(closest_value_in_sequence, self.decimals())

        except ValueError:
            # If input cannot be converted to float, revert to current value's closest sequence member
            # (or just current value if it's already valid by some chance, though fixup implies it wasn't)
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
            
            # Check if value is one of the sequence values (Acceptable)
            for seq_val in self._sequence:
                if math.isclose(value, seq_val, rel_tol=1e-9, abs_tol=1e-9):
                    # Check if it's within min/max bounds (already handled by sequence construction, but good practice)
                    if self.minimum() <= value <= self.maximum():
                        return (QValidator.State.Acceptable, input_str, pos)
                    else: # Should not happen if sequence defines min/max
                        return (QValidator.State.Invalid, input_str, pos)

            # Check if input is a prefix of any sequence value (Intermediate)
            # This allows typing "1.2" if "1.23" is in sequence, or "1" if "1.0" is in sequence.
            is_prefix = False
            # Normalize input_str for prefix checking (e.g. remove trailing '.')
            normalized_input_str = input_str.rstrip('.')

            for seq_val in self._sequence:
                # Format seq_val consistently for string comparison
                seq_val_str = "{:.{}f}".format(seq_val, self.decimals()) 
                if seq_val_str.startswith(normalized_input_str):
                    is_prefix = True
                    break
            
            if is_prefix:
                # Further check if the partially typed value is within overall min/max
                # This helps catch "9" if max is "7.5" but "0.9" is in sequence.
                # However, this can be tricky. If a value is a prefix of a sequence number,
                # it's usually considered Intermediate. The final fixup will correct it.
                # For now, if it's a prefix, let's be lenient.
                if self.minimum() <= value <= self.maximum(): # Check the numeric value of the prefix
                     return (QValidator.State.Intermediate, input_str, pos)
                # If numeric value of prefix is already out of bounds, but it *is* a prefix (e.g. typing "10" for seq "100")
                # This part of logic can be complex. The default QDoubleSpinBox validation is also quite involved.
                # For simplicity, if it's a prefix, let it be Intermediate. Fixup will handle final.
                return (QValidator.State.Intermediate, input_str, pos)


            # If not Acceptable and not Intermediate (as a prefix), it's Invalid
            return (QValidator.State.Invalid, input_str, pos)

        except ValueError: # Not a valid float
            return (QValidator.State.Invalid, input_str, pos)