import math

class SPR_Engine:
    """
    Implementation of the Sealed Positional Roman (SPR) Architecture.
    Features: High-Radix Positional Slots, Subtractive Logic, and Index-Dependent Ghosting.
    """
    
    # Standard Roman Symbol Mapping
    ROMAN_MAP = [
        ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400),
        ('C', 100), ('XC', 90), ('L', 50), ('XL', 40),
        ('X', 10), ('IX', 9), ('V', 5), ('IV', 4), ('I', 1)
    ]

    def __init__(self, radix=16, ghosting_key=[1, 1], delimiter="|"):
        self.radix = radix
        self.ghosting_key = ghosting_key
        self.delimiter = delimiter

    def _int_to_roman_digit(self, n):
        """Standard Roman additive-subtractive encoding for a single digit."""
        if n == 0: return "N" # 'Nulla' for zero
        result = ""
        for symbol, value in self.ROMAN_MAP:
            while n >= value:
                result += symbol
                n -= value
        return result

    def _roman_digit_to_int(self, s):
        """Standard Roman decoding for a single digit."""
        if s == "N": return 0
        res = 0
        i = 0
        # Convert map to dict for lookahead
        val_map = dict(self.ROMAN_MAP)
        
        while i < len(s):
            s1 = val_map.get(s[i], 0)
            if i + 1 < len(s):
                s2 = val_map.get(s[i+1], 0)
                if s1 >= s2:
                    res += s1
                    i += 1
                else:
                    res += (s2 - s1)
                    i += 2
            else:
                res += s1
                i += 1
        return res

    def encode(self, value):
        """Encodes a decimal integer into an SPR string."""
        if value == 0:
            return "N"
        
        slots = []
        temp_val = value
        
        # 1. Successive Division for Positional Radix
        while temp_val > 0:
            slots.append(temp_val % self.radix)
            temp_val //= self.radix
        
        # 2. Apply Ghosting & Romanization
        encoded_slots = []
        for i, digit_val in enumerate(slots):
            ghost_factor = self.ghosting_key[i % len(self.ghosting_key)]
            ghosted_val = digit_val * ghost_factor
            encoded_slots.append(self._int_to_roman_digit(ghosted_val))
            
        return self.delimiter.join(encoded_slots)

    def decode(self, spr_string):
        """Decodes an SPR string back into a decimal integer."""
        if spr_string == "N": return 0
        
        slots = spr_string.split(self.delimiter)
        total_value = 0
        
        for i, s_digit in enumerate(slots):
            ghosted_val = self._roman_digit_to_int(s_digit)
            ghost_factor = self.ghosting_key[i % len(self.ghosting_key)]
            digit_val = ghosted_val // ghost_factor
            total_value += digit_val * (self.radix ** i)
            
        return total_value

def run_test_suite(limit=1000, sample_size=5):
    """
    Tests multiple configurations of SPR against an incrementing input.
    Visualizes the first few samples of each configuration.
    """
    configs = [
        {"name": "Standard Hex-Roman", "radix": 16, "key": [1, 1]},
        {"name": "High-Radix Obfuscated", "radix": 64, "key": [3, 7, 2]},
        {"name": "Prime Base Shift", "radix": 31, "key": [1, 13, 1, 17]},
        {"name": "Binary Roman (Stress)", "radix": 2, "key": [1, 5]}
    ]
    
    for config in configs:
        print(f"\n{'='*80}")
        print(f"TESTING CONFIG: {config['name']}")
        print(f"Radix: {config['radix']} | Ghosting Key: {config['key']}")
        print(f"{'='*80}")
        print(f"{'Input':<8} | {'Encoded (SPR)':<40} | {'Decoded':<8} | {'Status'}")
        print(f"{'-'*80}")
        
        engine = SPR_Engine(radix=config["radix"], ghosting_key=config["key"])
        success = True
        
        for i in range(limit):
            encoded = engine.encode(i)
            decoded = engine.decode(encoded)
            is_match = (i == decoded)
            
            # Show visual samples for the first 'sample_size' inputs
            if i < sample_size:
                status_str = "✓" if is_match else "✗"
                # Truncate encoded string if too long for display
                disp_encoded = (encoded[:37] + '...') if len(encoded) > 40 else encoded
                print(f"{i:<8} | {disp_encoded:<40} | {decoded:<8} | {status_str}")
            
            if not is_match:
                print(f"\nFAILURE at input {i}!")
                print(f"  Expected: {i}")
                print(f"  Encoded:  {encoded}")
                print(f"  Decoded:  {decoded}")
                success = False
                break
        
        if success:
            print(f"...")
            print(f"RESULT: All {limit} inputs passed consistency check.")

if __name__ == "__main__":
    # Run test suite with visualization enabled for the first 10 samples
    run_test_suite(limit=1000, sample_size=10)
    
    # Final check on high-value data
    print(f"\n{'='*80}")
    print(f"HIGH-VALUE DATA CONSISTENCY CHECK")
    print(f"{'='*80}")
    demo_vals = [400000, 500000, 10000000] # Representative of land costs/leasings
    engine = SPR_Engine(radix=256, ghosting_key=[13, 42, 7])
    
    for val in demo_vals:
        enc = engine.encode(val)
        dec = engine.decode(enc)
        print(f"Input: {val:<10} | SPR: {enc:<30} | Match: {val == dec}")