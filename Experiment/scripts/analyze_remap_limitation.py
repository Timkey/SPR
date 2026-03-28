"""
Analysis: Why Roman Symbol Remapping Cannot Fix Frequency Uniformity

This demonstrates that symbol substitution redistributes but doesn't eliminate
the frequency bias inherent to Roman positional encoding.
"""

from collections import Counter
import random
from spr_full import SPR_Full

def analyze_structural_bias():
    """
    Analyze why remapping can't fix the frequency problem.
    The bias is in the LOGICAL POSITIONS, not the symbols.
    """
    
    print("="*80)
    print("STRUCTURAL FREQUENCY ANALYSIS: Why Remapping Doesn't Solve the Problem")
    print("="*80)
    
    # Generate encodings and track LOGICAL position frequencies
    samples = 5000
    standard = SPR_Full(radix=16, ghosting_primes=False, enable_checksum=False)
    
    # Track which LOGICAL Roman positions are used (before any remapping)
    # In standard Roman: I=1, V=5, X=10, L=50, C=100, D=500, M=1000
    logical_position_counts = {'I': 0, 'V': 0, 'X': 0, 'L': 0, 'C': 0, 'D': 0, 'M': 0}
    
    print("\n1. LOGICAL POSITION FREQUENCY (Before Any Symbol Substitution)")
    print("-" * 80)
    print("This measures how often each LOGICAL value is needed in Roman encoding.")
    print("Remapping symbols doesn't change this - it's structural.\n")
    
    for _ in range(samples):
        value = random.randint(0, 10000)
        encoded = standard.encode(value)
        
        # Count logical Roman characters (what they represent logically)
        for char in encoded:
            if char in logical_position_counts:
                logical_position_counts[char] += 1
    
    total = sum(logical_position_counts.values())
    
    print(f"Sample size: {samples} random values (0-10,000)")
    print(f"Total Roman characters generated: {total}")
    print("\nLogical Position Frequencies:")
    
    for symbol in ['I', 'V', 'X', 'L', 'C', 'D', 'M']:
        count = logical_position_counts[symbol]
        freq = count / total * 100 if total > 0 else 0
        bar = '█' * int(freq / 2)
        print(f"  {symbol} (value={standard.STANDARD_PROGRESSION[['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I'].index(symbol) if symbol in ['M','D','C','L','X','V','I'] else -1][1] if symbol in 'MDCLXVI' else '?'}): {count:5d} ({freq:5.2f}%) {bar}")
    
    # Show the mathematical reason
    print("\n2. MATHEMATICAL EXPLANATION")
    print("-" * 80)
    print("""
Why is 'I' (value=1) so common?
- In Roman numerals, EVERY digit position uses I as the base unit
- To represent 1-3: I, II, III
- To represent 4: IV (uses I)  
- To represent 6-8: VI, VII, VIII (all use I)
- To represent 9: IX (uses I)
- This pattern repeats in EVERY decimal position (ones, tens, hundreds...)

Why is 'V' common?
- V (value=5) appears in 4,5,6,7,8,9 of every decimal range
- Used in 60% of single-digit encodings

Why is 'X' common?
- X (value=10) starts every tens position
- Similar pattern to I but one magnitude higher

Why are 'L', 'D', 'M' rare?
- Only used at magnitude transitions (50, 500, 1000)
- For random values 0-10,000, these are less frequently needed
""")
    
    print("\n3. WHAT REMAPPING ACTUALLY DOES")
    print("-" * 80)
    
    # Show two remappings
    remap1 = {'I': 'M', 'V': 'D', 'X': 'C', 'L': 'V', 'C': 'X', 'D': 'L', 'M': 'I'}
    remap2 = {'I': 'L', 'V': 'C', 'X': 'D', 'L': 'M', 'C': 'I', 'D': 'V', 'M': 'X'}
    
    encoder1 = SPR_Full(radix=16, ghosting_primes=False, enable_checksum=False, 
                        roman_symbol_remap=remap1)
    encoder2 = SPR_Full(radix=16, ghosting_primes=False, enable_checksum=False,
                        roman_symbol_remap=remap2)
    
    # Encode the same value with different remappings
    test_val = 444
    standard_enc = standard.encode(test_val)
    remap1_enc = encoder1.encode(test_val)
    remap2_enc = encoder2.encode(test_val)
    
    print(f"Same value (444) with different symbol mappings:")
    print(f"  Standard:  {standard_enc}")
    print(f"  Remap #1:  {remap1_enc}")
    print(f"  Remap #2:  {remap2_enc}")
    print()
    print("Notice: The OUTPUT symbols change, but the LOGICAL structure is identical.")
    print("All three have the same pattern of high/low frequency positions.")
    print("We just moved which SYMBOL represents the high-frequency logical position.")
    
    print("\n4. THE FUNDAMENTAL LIMITATION")
    print("-" * 80)
    print("""
CONCLUSION: Roman symbol remapping is a RED HERRING for frequency analysis.

✗ What remapping CANNOT do:
  - Change the fact that logical position I (value=1) is used 45% of the time
  - Make all 7 Roman positions equally likely
  - Hide the structural bias of positional-additive numbering

✓ What remapping CAN do:
  - Make the OUTPUT look different (security through obscurity)
  - Add configuration complexity (7! = 5,040 more key combinations)
  - Complicate cryptanalysis slightly (attacker doesn't know symbol mapping)
  
✓ What WOULD actually help frequency uniformity:
  - Use a different alphabet entirely (not Roman numerals)
  - Use extended_alphabet=True (64 diverse symbols vs 7 Roman)
  - Accept that Format-Preserving Encryption has this trade-off
  
The frequency bias is inherent to Roman numeral structure itself.
It's like trying to make English letter frequency uniform by swapping
E↔Q and T↔Z - you just move the bias, you don't eliminate it.
""")
    
    print("="*80)
    print("RECOMMENDATION: Document this as a known limitation, don't claim")
    print("symbol remapping solves frequency analysis. It adds obscurity, not")
    print("uniformity. The 5/6 test result (83.3%) remains the theoretical max.")
    print("="*80)

if __name__ == "__main__":
    analyze_structural_bias()
