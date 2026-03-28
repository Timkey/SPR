"""
Test if Roman symbol remapping improves frequency analysis results.
"""

import sys
import random
from collections import Counter
from spr_full import SPR_Full

def analyze_frequency(samples: int = 10000):
    """Analyze character frequency distribution with and without remapping."""
    
    # Test 1: Standard encoding (no remapping)
    print("="*80)
    print("FREQUENCY ANALYSIS: Standard vs Remapped Encoding")
    print("="*80)
    
    print("\n1. STANDARD ENCODING (No Remapping)")
    print("-" * 80)
    standard = SPR_Full(radix=16, ghosting_primes=True, enable_checksum=True)
    
    all_chars_std = []
    for _ in range(samples):
        value = random.randint(0, 1000000)
        encoded = standard.encode(value)
        # Extract just the Roman numerals (remove length prefixes and checksum)
        for char in encoded:
            if char in 'IVXLCDM':
                all_chars_std.append(char)
    
    counter_std = Counter(all_chars_std)
    total_std = len(all_chars_std)
    
    print(f"Total Roman characters: {total_std}")
    print("\nCharacter Frequencies:")
    for char in sorted(counter_std.keys()):
        freq = counter_std[char] / total_std * 100
        print(f"  {char}: {counter_std[char]:6d} ({freq:5.2f}%)")
    
    # Calculate variance (measure of non-uniformity)
    expected_freq = total_std / 7  # Uniform distribution across I,V,X,L,C,D,M
    variance_std = sum((count - expected_freq)**2 for count in counter_std.values()) / 7
    print(f"\nVariance from uniform: {variance_std:.2f}")
    print(f"Standard deviation: {variance_std**0.5:.2f}")
    
    # Test 2: Remapped encoding
    print("\n2. REMAPPED ENCODING (Symbol Substitution)")
    print("-" * 80)
    
    # Create a permutation that redistributes frequently-used symbols
    # Map I (most common) to L, V to C, X to D (less common positions)
    remap = {
        'I': 'L',  # I is most common, remap to mid-frequency position
        'V': 'C',
        'X': 'D',
        'L': 'M',
        'C': 'I',  # C is less common, remap to high-frequency position
        'D': 'V',
        'M': 'X'
    }
    
    remapped = SPR_Full(radix=16, ghosting_primes=True, enable_checksum=True, 
                        roman_symbol_remap=remap)
    
    all_chars_remap = []
    for _ in range(samples):
        value = random.randint(0, 1000000)
        encoded = remapped.encode(value)
        # Extract just the Roman numerals
        for char in encoded:
            if char in 'IVXLCDM':
                all_chars_remap.append(char)
    
    counter_remap = Counter(all_chars_remap)
    total_remap = len(all_chars_remap)
    
    print(f"Total Roman characters: {total_remap}")
    print(f"Remapping: {remap}")
    print("\nCharacter Frequencies:")
    for char in sorted(counter_remap.keys()):
        freq = counter_remap[char] / total_remap * 100
        print(f"  {char}: {counter_remap[char]:6d} ({freq:5.2f}%)")
    
    # Calculate variance
    expected_freq_remap = total_remap / 7
    variance_remap = sum((count - expected_freq_remap)**2 for count in counter_remap.values()) / 7
    print(f"\nVariance from uniform: {variance_remap:.2f}")
    print(f"Standard deviation: {variance_remap**0.5:.2f}")
    
    # Comparison
    print("\n3. COMPARISON")
    print("="*80)
    variance_reduction = ((variance_std - variance_remap) / variance_std) * 100
    
    # Check if distribution is more uniform
    max_freq_std = max(counter_std[char] / total_std * 100 for char in counter_std)
    min_freq_std = min(counter_std[char] / total_std * 100 for char in counter_std)
    range_std = max_freq_std - min_freq_std
    
    max_freq_remap = max(counter_remap[char] / total_remap * 100 for char in counter_remap)
    min_freq_remap = min(counter_remap[char] / total_remap * 100 for char in counter_remap)
    range_remap = max_freq_remap - min_freq_remap
    
    print(f"Standard Encoding:")
    print(f"  Frequency range: {min_freq_std:.2f}% - {max_freq_std:.2f}% (span: {range_std:.2f}%)")
    print(f"  Variance: {variance_std:.2f}")
    
    print(f"\nRemapped Encoding:")
    print(f"  Frequency range: {min_freq_remap:.2f}% - {max_freq_remap:.2f}% (span: {range_remap:.2f}%)")
    print(f"  Variance: {variance_remap:.2f}")
    
    print(f"\nImprovement:")
    print(f"  Variance reduction: {variance_reduction:+.2f}%")
    print(f"  Range reduction: {((range_std - range_remap) / range_std * 100):+.2f}%")
    
    if variance_remap < variance_std:
        print(f"\n✓ RESULT: Remapping IMPROVES frequency uniformity!")
    else:
        print(f"\n✗ RESULT: Remapping does not improve uniformity (might need better mapping)")
    
    print("\n" + "="*80)
    print("NOTE: Perfect uniformity (14.29% per character) is mathematically")
    print("impossible for Roman positional encoding, but remapping can redistribute")
    print("the bias across different symbols, making frequency analysis harder.")
    print("="*80)

if __name__ == "__main__":
    samples = 10000
    if len(sys.argv) > 1:
        samples = int(sys.argv[1])
    
    analyze_frequency(samples)
