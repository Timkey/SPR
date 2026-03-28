"""
Focused frequency analysis test: Position-dependent rotation vs static vs none.
Only measures Roman characters I,V,X,L,C,D,M (excludes checksums, delimiters, digits).
"""

import random
from collections import Counter
from scipy import stats
from spr_full import SPR_Full

def frequency_test(encoder, samples=10000, label="Test"):
    """Measure frequency distribution of Roman characters only."""
    
    all_chars = []
    for _ in range(samples):
        value = random.randint(0, 1000000)
        encoded = encoder.encode(value)
        
        # Extract ONLY Roman numeral characters
        for char in encoded:
            if char in 'IVXLCDM':
                all_chars.append(char)
    
    counter = Counter(all_chars)
    total = len(all_chars)
    
    # Calculate statistics
    roman_chars = ['I', 'V', 'X', 'L', 'C', 'D', 'M']
    observed = [counter.get(c, 0) for c in roman_chars]
    expected = [total / 7] * 7
    
    chi_square = sum((obs - exp)**2 / exp for obs, exp in zip(observed, expected))
    p_value = 1 - stats.chi2.cdf(chi_square, df=6)
    
    # Variance from uniform
    variance = sum((count - expected[0])**2 for count in observed) / 7
    
    # Frequency range
    freqs = [counter.get(c, 0) / total * 100 for c in roman_chars]
    max_freq = max(freqs)
    min_freq = min(freqs)
    span = max_freq - min_freq
    
    print(f"\n{label}")
    print("=" * 80)
    print(f"Total Roman characters: {total:,}")
    print("\nFrequency Distribution:")
    
    for char in roman_chars:
        count = counter.get(char, 0)
        freq = count / total * 100
        bar = '█' * int(freq / 2)
        print(f"  {char}: {count:6,} ({freq:5.2f}%) {bar}")
    
    print(f"\nStatistics:")
    print(f"  Chi-square: {chi_square:,.2f}")
    print(f"  P-value: {p_value:.6f}")
    print(f"  Variance: {variance:,.0f}")
    print(f"  Range: {min_freq:.2f}% - {max_freq:.2f}% (span: {span:.2f}%)")
    
    # Pass/fail (p < 0.05 means significantly non-uniform)
    if p_value >= 0.05:
        print(f"  ✓ PASS: Distribution is uniform (p = {p_value:.4f} ≥ 0.05)")
    else:
        print(f"  ✗ FAIL: Distribution is non-uniform (p = {p_value:.6f} < 0.05)")
    
    return {
        'chi_square': chi_square,
        'p_value': p_value,
        'variance': variance,
        'span': span,
        'max_freq': max_freq,
        'min_freq': min_freq
    }

def main():
    print("="*80)
    print("FREQUENCY ANALYSIS: Position-Dependent Rotation Impact")
    print("="*80)
    print("\nTesting 10,000 random values (0-1,000,000)")
    print("Measuring ONLY Roman characters: I, V, X, L, C, D, M")
    print("Hypothesis: Rotation should drastically improve uniformity\n")
    
    samples = 10000
    
    # Test 1: No remapping (baseline)
    print("\n" + "─" * 80)
    print("TEST 1: BASELINE (No Remapping)")
    print("─" * 80)
    
    baseline = SPR_Full(
        radix=16,
        ghosting_primes=True,
        enable_checksum=False  # Exclude checksums from frequency count
    )
    
    baseline_stats = frequency_test(baseline, samples, "No remapping (baseline)")
    
    # Test 2: Static remapping
    print("\n" + "─" * 80)
    print("TEST 2: STATIC REMAPPING")
    print("─" * 80)
    
    static_remap = {'I': 'M', 'V': 'D', 'X': 'C', 'L': 'V', 'C': 'L', 'D': 'X', 'M': 'I'}
    static = SPR_Full(
        radix=16,
        ghosting_primes=True,
        enable_checksum=False,
        roman_symbol_remap=static_remap
    )
    
    static_stats = frequency_test(static, samples, "Static remapping")
    
    # Test 3: Position-dependent rotation
    print("\n" + "─" * 80)
    print("TEST 3: POSITION-DEPENDENT ROTATION")
    print("─" * 80)
    
    rotation = SPR_Full(
        radix=16,
        ghosting_primes=True,
        enable_checksum=False,
        rotation_key=[0, 2, 4, 1, 5, 3, 6]
    )
    
    rotation_stats = frequency_test(rotation, samples, "Position-dependent rotation")
    
    # Summary comparison
    print("\n" + "="*80)
    print("COMPARATIVE SUMMARY")
    print("="*80)
    
    print(f"\n{'Metric':<25} {'Baseline':<15} {'Static':<15} {'Rotation':<15}")
    print("─" * 80)
    print(f"{'Chi-square':<25} {baseline_stats['chi_square']:>14,.0f} {static_stats['chi_square']:>14,.0f} {rotation_stats['chi_square']:>14,.0f}")
    print(f"{'Variance':<25} {baseline_stats['variance']:>14,.0f} {static_stats['variance']:>14,.0f} {rotation_stats['variance']:>14,.0f}")
    print(f"{'Frequency span':<25} {baseline_stats['span']:>14.2f}% {static_stats['span']:>14.2f}% {rotation_stats['span']:>14.2f}%")
    print(f"{'P-value':<25} {baseline_stats['p_value']:>14.6f} {static_stats['p_value']:>14.6f} {rotation_stats['p_value']:>14.6f}")
    
    # Improvement calculations
    print("\n" + "─" * 80)
    print("IMPROVEMENTS vs BASELINE")
    print("─" * 80)
    
    static_variance_improvement = ((baseline_stats['variance'] - static_stats['variance']) / baseline_stats['variance']) * 100
    rotation_variance_improvement = ((baseline_stats['variance'] - rotation_stats['variance']) / baseline_stats['variance']) * 100
    
    static_span_improvement = ((baseline_stats['span'] - static_stats['span']) / baseline_stats['span']) * 100
    rotation_span_improvement = ((baseline_stats['span'] - rotation_stats['span']) / baseline_stats['span']) * 100
    
    print(f"\nStatic Remapping:")
    print(f"  Variance reduction: {static_variance_improvement:+.2f}%")
    print(f"  Span reduction: {static_span_improvement:+.2f}%")
    
    print(f"\nPosition-Dependent Rotation:")
    print(f"  Variance reduction: {rotation_variance_improvement:+.2f}%")
    print(f"  Span reduction: {rotation_span_improvement:+.2f}%")
    
    # Winner
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if rotation_stats['p_value'] >= 0.05:
        print("\n🎉 SUCCESS: Position-dependent rotation achieves uniform distribution!")
        print(f"   P-value {rotation_stats['p_value']:.4f} ≥ 0.05 (statistically uniform)")
        print(f"   This SOLVES the frequency analysis limitation!")
    elif rotation_stats['variance'] < baseline_stats['variance'] * 0.5:
        print("\n✓ MAJOR IMPROVEMENT: Position-dependent rotation is much better!")
        print(f"   Variance reduced by {rotation_variance_improvement:.1f}%")
        print(f"   Still not perfectly uniform (p={rotation_stats['p_value']:.6f}), but dramatically improved")
    else:
        print("\n⚠️ MINOR IMPROVEMENT: Rotation helps but doesn't solve the problem")
        print(f"   Variance reduced by {rotation_variance_improvement:.1f}%")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
