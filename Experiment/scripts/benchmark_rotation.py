"""
Performance benchmark: Position-dependent rotation overhead
"""

import time
from spr_full import SPR_Full

def benchmark(encoder, iterations=10000, label="Test"):
    """Measure encoding/decoding speed."""
    
    test_values = list(range(1, iterations + 1))
    
    # Encoding benchmark
    start = time.time()
    encoded = [encoder.encode(val) for val in test_values]
    encode_time = time.time() - start
    encode_ops_per_sec = iterations / encode_time
    
    # Decoding benchmark
    start = time.time()
    decoded = [encoder.decode(enc) for enc in encoded]
    decode_time = time.time() - start
    decode_ops_per_sec = iterations / decode_time
    
    # Verify correctness
    errors = sum(1 for i, val in enumerate(test_values) if decoded[i] != val)
    
    print(f"\n{label}")
    print("─" * 80)
    print(f"Iterations: {iterations:,}")
    print(f"Encoding time: {encode_time:.3f}s ({encode_ops_per_sec:,.0f} ops/sec)")
    print(f"Decoding time: {decode_time:.3f}s ({decode_ops_per_sec:,.0f} ops/sec)")
    print(f"Total time: {encode_time + decode_time:.3f}s")
    print(f"Correctness: {iterations - errors}/{iterations} ({(1 - errors/iterations)*100:.2f}%)")
    
    return {
        'encode_ops_per_sec': encode_ops_per_sec,
        'decode_ops_per_sec': decode_ops_per_sec,
        'total_time': encode_time + decode_time,
        'errors': errors
    }

def main():
    print("="*80)
    print("PERFORMANCE BENCHMARK: Position-Dependent Rotation Overhead")
    print("="*80)
    
    iterations = 10000
    print(f"\nTesting {iterations:,} encode/decode operations\n")
    
    # Test 1: Minimal configuration (baseline)
    print("TEST 1: MINIMAL (Baseline - fastest)")
    minimal = SPR_Full(radix=16, ghosting_primes=False, enable_checksum=False)
    minimal_stats = benchmark(minimal, iterations, "Minimal configuration")
    
    # Test 2: Full features WITHOUT rotation
    print("\nTEST 2: FULL FEATURES (No rotation)")
    full_no_rotation = SPR_Full(
        radix=31,
        geometric_progression=[3, 7, 2],
        modulus=2**20-1,
        ghosting_primes=True,
        starting_offset=7,
        enable_checksum=True
    )
    full_no_rotation_stats = benchmark(full_no_rotation, iterations, "Full features (no rotation)")
    
    # Test 3: Full features WITH static remapping
    print("\nTEST 3: FULL + STATIC REMAPPING")
    remap = {'I': 'M', 'V': 'D', 'X': 'C', 'L': 'V', 'C': 'L', 'D': 'X', 'M': 'I'}
    full_static = SPR_Full(
        radix=31,
        geometric_progression=[3, 7, 2],
        modulus=2**20-1,
        ghosting_primes=True,
        starting_offset=7,
        enable_checksum=False,  # Disable for fair comparison
        roman_symbol_remap=remap
    )
    full_static_stats = benchmark(full_static, iterations, "Full features + static remap")
    
    # Test 4: Full features WITH position-dependent rotation
    print("\nTEST 4: FULL + POSITION-DEPENDENT ROTATION")
    full_rotation = SPR_Full(
        radix=31,
        geometric_progression=[3, 7, 2],
        modulus=2**20-1,
        ghosting_primes=True,
        starting_offset=7,
        enable_checksum=False,  # Disable for fair comparison
        rotation_key=[0, 2, 4, 1, 5, 3, 6]
    )
    full_rotation_stats = benchmark(full_rotation, iterations, "Full features + rotation")
    
    # Summary
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    
    print(f"\n{'Configuration':<35} {'Encode (ops/s)':<18} {'Decode (ops/s)':<18} {'Overhead'}")
    print("─" * 80)
    
    configs = [
        ("Minimal (baseline)", minimal_stats),
        ("Full (no rotation)", full_no_rotation_stats),
        ("Full + static remap", full_static_stats),
        ("Full + rotation", full_rotation_stats)
    ]
    
    baseline_encode = minimal_stats['encode_ops_per_sec']
    baseline_decode = minimal_stats['decode_ops_per_sec']
    
    for name, stats in configs:
        encode_overhead = (1 - stats['encode_ops_per_sec'] / baseline_encode) * 100
        decode_overhead = (1 - stats['decode_ops_per_sec'] / baseline_decode) * 100
        
        print(f"{name:<35} {stats['encode_ops_per_sec']:>15,.0f}  {stats['decode_ops_per_sec']:>15,.0f}  "
              f"{encode_overhead:>+6.1f}%")
    
    # Specific comparisons
    print("\n" + "─" * 80)
    print("KEY COMPARISONS")
    print("─" * 80)
    
    # Static vs Rotation overhead
    static_encode = full_static_stats['encode_ops_per_sec']
    rotation_encode = full_rotation_stats['encode_ops_per_sec']
    rotation_vs_static = ((rotation_encode - static_encode) / static_encode) * 100
    
    print(f"\nRotation vs Static Remapping:")
    print(f"  Encoding: {rotation_vs_static:+.2f}% speed difference")
    
    static_decode = full_static_stats['decode_ops_per_sec']
    rotation_decode = full_rotation_stats['decode_ops_per_sec']
    rotation_vs_static_decode = ((rotation_decode - static_decode) / static_decode) * 100
    print(f"  Decoding: {rotation_vs_static_decode:+.2f}% speed difference")
    
    # Full features overhead vs minimal
    full_vs_minimal = ((full_rotation_stats['encode_ops_per_sec'] - baseline_encode) / baseline_encode) * 100
    print(f"\nFull (with rotation) vs Minimal:")
    print(f"  Encoding: {full_vs_minimal:+.2f}% overhead")
    print(f"  Still achieves: {full_rotation_stats['encode_ops_per_sec']:,.0f} ops/sec")
    
    # Assessment
    print("\n" + "="*80)
    print("PERFORMANCE ASSESSMENT")
    print("="*80)
    
    if rotation_vs_static > -10:
        print("\n✓ EXCELLENT: Rotation adds <10% overhead vs static remapping")
        print(f"  Actual overhead: {abs(rotation_vs_static):.1f}%")
    elif rotation_vs_static > -20:
        print("\n✓ ACCEPTABLE: Rotation adds 10-20% overhead vs static remapping")
        print(f"  Actual overhead: {abs(rotation_vs_static):.1f}%")
    else:
        print("\n⚠️ SIGNIFICANT: Rotation adds >20% overhead vs static remapping")
        print(f"  Actual overhead: {abs(rotation_vs_static):.1f}%")
    
    # Use case assessment
    print("\nUse Case Viability:")
    
    ops_needed = {
        "Key generation": 1,
        "Authentication token": 100,
        "Session management": 1000,
        "High-frequency API": 100000
    }
    
    for use_case, ops in ops_needed.items():
        time_needed = ops / full_rotation_stats['encode_ops_per_sec']
        if time_needed < 0.001:
            verdict = "✓ EXCELLENT"
        elif time_needed < 0.1:
            verdict = "✓ GOOD"
        elif time_needed < 1.0:
            verdict = "⚠️ MARGINAL"
        else:
            verdict = "✗ POOR"
        
        print(f"  {use_case:<25} {ops:>8,} ops: {time_needed*1000:>8.2f}ms {verdict}")
    
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    if full_rotation_stats['encode_ops_per_sec'] > 20000:
        print("\n✓ Position-dependent rotation is VIABLE for production use")
        print(f"  - Achieves {full_rotation_stats['encode_ops_per_sec']:,.0f} ops/sec")
        print(f"  - 96% frequency variance reduction worth the {abs(full_vs_minimal):.1f}% overhead")
        print(f"  - Suitable for key generation, tokens, authentication")
    elif full_rotation_stats['encode_ops_per_sec'] > 10000:
        print("\n⚠️ Position-dependent rotation is ACCEPTABLE but consider use case")
        print(f"  - Achieves {full_rotation_stats['encode_ops_per_sec']:,.0f} ops/sec")
        print(f"  - Good for low-frequency operations (<1000/sec)")
        print(f"  - May need optimization for high-throughput scenarios")
    else:
        print("\n✗ Position-dependent rotation may be TOO SLOW for most use cases")
        print(f"  - Only achieves {full_rotation_stats['encode_ops_per_sec']:,.0f} ops/sec")
        print(f"  - Consider static remapping or minimal config for performance")
    
    print("="*80)

if __name__ == "__main__":
    main()
