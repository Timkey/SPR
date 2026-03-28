#!/usr/bin/env python3
"""
SPR Performance Benchmark Suite
Tests performance claims with actual measurements
"""

import sys
import time
import json
import statistics
from typing import List, Tuple
import numpy as np

sys.path.append('/workspace/Experiment/scripts')
from test_suite import SPR_Engine

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("Warning: cryptography library not available, using simulated benchmarks")


class SPRPerformanceBenchmark:
    """Benchmark SPR against actual cryptographic alternatives"""
    
    def __init__(self):
        self.results = {}
        self.spr_base16 = SPR_Engine(radix=16)
        self.spr_base64 = SPR_Engine(radix=64)
        
        if HAS_CRYPTO:
            # Initialize AES-GCM for comparison
            self.aes_key = AESGCM.generate_key(bit_length=256)
            self.aes = AESGCM(self.aes_key)
    
    def run_all_benchmarks(self):
        """Execute all performance benchmarks"""
        print("=" * 80)
        print("SPR PERFORMANCE BENCHMARKS - Evidence-Based Testing")
        print("=" * 80)
        
        # Benchmark 1: SPR encode/decode speed
        print("\n[BENCHMARK 1] SPR Encoding/Decoding Speed")
        self.benchmark_spr_speed()
        
        # Benchmark 2: SPR vs AES-GCM
        print("\n[BENCHMARK 2] SPR vs AES-GCM (Symmetric Encryption)")
        self.benchmark_vs_aes()
        
        # Benchmark 3: SPR vs PBKDF2
        print("\n[BENCHMARK 3] SPR vs PBKDF2 (Key Derivation)")
        self.benchmark_vs_pbkdf2()
        
        # Benchmark 4: Space complexity verification
        print("\n[BENCHMARK 4] Space Complexity - O(log N) Verification")
        self.benchmark_space_complexity()
        
        # Benchmark 5: Scalability testing
        print("\n[BENCHMARK 5] Scalability Testing")
        self.benchmark_scalability()
        
        return self.results
    
    def benchmark_spr_speed(self):
        """Measure actual SPR performance"""
        print("  Measuring SPR encode/decode operations...")
        
        test_sizes = [1000, 10000, 100000]
        
        for size in test_sizes:
            values = np.random.randint(1, 1000000, size)
            
            # Benchmark encoding
            start = time.perf_counter()
            encoded = [self.spr_base16.encode(v) for v in values]
            encode_time = time.perf_counter() - start
            
            # Benchmark decoding
            start = time.perf_counter()
            decoded = [self.spr_base16.decode(e) for e in encoded]
            decode_time = time.perf_counter() - start
            
            encode_ops_per_sec = size / encode_time
            decode_ops_per_sec = size / decode_time
            
            print(f"\n  Sample size: {size:,}")
            print(f"    Encoding: {encode_time:.4f}s ({encode_ops_per_sec:,.0f} ops/sec)")
            print(f"    Decoding: {decode_time:.4f}s ({decode_ops_per_sec:,.0f} ops/sec)")
            print(f"    Avg per operation: {(encode_time + decode_time) / (2 * size) * 1000:.4f}ms")
        
        # Store final results
        self.results['spr_speed'] = {
            'claim': 'Fast encoding/decoding operations',
            'encode_ops_per_sec': encode_ops_per_sec,
            'decode_ops_per_sec': decode_ops_per_sec,
            'status': 'MEASURED'
        }
    
    def benchmark_vs_aes(self):
        """
        Claim: "Faster than AES for key obfuscation"
        Compare SPR to AES-GCM
        """
        print("  Comparing SPR vs AES-GCM...")
        
        if not HAS_CRYPTO:
            print("  ⚠ Cryptography library not available - simulation only")
            self.results['vs_aes'] = {
                'claim': 'Faster than AES',
                'status': 'SKIPPED',
                'verdict': 'Cannot verify without cryptography library'
            }
            return
        
        sample_size = 10000
        test_data = [str(i).zfill(16).encode() for i in range(sample_size)]
        
        # Benchmark AES-GCM encryption
        start = time.perf_counter()
        for data in test_data:
            nonce = b'0' * 12  # Fixed for benchmark (should be random in production)
            self.aes.encrypt(nonce, data, None)
        aes_time = time.perf_counter() - start
        aes_ops_per_sec = sample_size / aes_time
        
        # Benchmark SPR encoding
        spr_values = list(range(1, sample_size + 1))
        start = time.perf_counter()
        for value in spr_values:
            self.spr_base16.encode(value)
        spr_time = time.perf_counter() - start
        spr_ops_per_sec = sample_size / spr_time
        
        print(f"\n  Sample size: {sample_size:,} operations")
        print(f"  AES-GCM: {aes_time:.4f}s ({aes_ops_per_sec:,.0f} ops/sec)")
        print(f"  SPR: {spr_time:.4f}s ({spr_ops_per_sec:,.0f} ops/sec)")
        
        speedup = spr_ops_per_sec / aes_ops_per_sec
        print(f"\n  SPR vs AES speedup: {speedup:.2f}x")
        
        # Verdict based on claimed 20x-50x speedup
        claimed_speedup_min = 20
        claimed_speedup_max = 50
        
        if speedup >= claimed_speedup_min:
            verdict = f"✓ PASS: {speedup:.1f}x faster (claim: 20-50x)"
            claim_status = "SUPPORTED"
        elif speedup > 1:
            verdict = f"⚠ PARTIAL: {speedup:.1f}x faster but below claimed 20-50x"
            claim_status = "PARTIALLY_SUPPORTED"
        else:
            verdict = f"✗ FAIL: {speedup:.1f}x - AES is faster"
            claim_status = "REFUTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        print(f"\n  NOTE: This comparison is problematic because:")
        print(f"    - AES-GCM provides authenticated encryption (SPR doesn't)")
        print(f"    - AES has hardware acceleration (AES-NI) in modern CPUs")
        print(f"    - SPR is obfuscation, not encryption")
        print(f"    - Different security properties make direct comparison invalid")
        
        self.results['vs_aes'] = {
            'claim': 'Faster than AES (20x-50x)',
            'aes_ops_per_sec': aes_ops_per_sec,
            'spr_ops_per_sec': spr_ops_per_sec,
            'speedup': speedup,
            'claimed_min': claimed_speedup_min,
            'claimed_max': claimed_speedup_max,
            'status': claim_status,
            'verdict': verdict,
            'note': 'Comparison is conceptually flawed - different security properties'
        }
    
    def benchmark_vs_pbkdf2(self):
        """
        Claim: "More efficient for key derivation"
        Compare SPR to PBKDF2 (actual key derivation function)
        """
        print("  Comparing SPR vs PBKDF2...")
        
        if not HAS_CRYPTO:
            print("  ⚠ Cryptography library not available - simulation only")
            self.results['vs_pbkdf2'] = {
                'claim': 'More efficient than PBKDF2',
                'status': 'SKIPPED',
                'verdict': 'Cannot verify without cryptography library'
            }
            return
        
        sample_size = 100  # PBKDF2 is intentionally slow
        
        # Benchmark PBKDF2 (proper key derivation)
        iterations = 100000  # Standard iteration count
        start = time.perf_counter()
        for i in range(sample_size):
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'salt' + str(i).encode(),
                iterations=iterations,
                backend=default_backend()
            )
            kdf.derive(b'password' + str(i).encode())
        pbkdf2_time = time.perf_counter() - start
        pbkdf2_ops_per_sec = sample_size / pbkdf2_time
        
        # Benchmark SPR
        start = time.perf_counter()
        for i in range(sample_size):
            self.spr_base16.encode(i + 1000)
        spr_time = time.perf_counter() - start
        spr_ops_per_sec = sample_size / spr_time
        
        print(f"\n  Sample size: {sample_size} operations")
        print(f"  PBKDF2 ({iterations:,} iterations): {pbkdf2_time:.4f}s ({pbkdf2_ops_per_sec:.2f} ops/sec)")
        print(f"  SPR: {spr_time:.4f}s ({spr_ops_per_sec:,.0f} ops/sec)")
        
        speedup = spr_ops_per_sec / pbkdf2_ops_per_sec
        print(f"\n  SPR vs PBKDF2 speedup: {speedup:,.0f}x")
        
        print(f"\n  CRITICAL ISSUE: This comparison is INVALID")
        print(f"    ✗ PBKDF2 is INTENTIONALLY slow (prevents brute force)")
        print(f"    ✗ Slowness is a SECURITY FEATURE, not a bug")
        print(f"    ✗ SPR being faster means it's LESS secure for key derivation")
        print(f"    ✗ Comparing apples to oranges - different purposes")
        
        verdict = "✗ INVALID: Comparison conceptually flawed"
        claim_status = "INVALID_COMPARISON"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['vs_pbkdf2'] = {
            'claim': 'More efficient than PBKDF2',
            'pbkdf2_ops_per_sec': pbkdf2_ops_per_sec,
            'spr_ops_per_sec': spr_ops_per_sec,
            'speedup': speedup,
            'status': claim_status,
            'verdict': verdict,
            'note': 'PBKDF2 is intentionally slow for security - being faster is NOT better'
        }
    
    def benchmark_space_complexity(self):
        """
        Claim: "O(log_b N) space complexity"
        Verify with empirical measurements
        """
        print("  Verifying O(log N) space complexity...")
        
        # Test exponentially growing values
        test_values = [10**i for i in range(1, 13)]  # 10 to 10^12
        
        results = []
        for value in test_values:
            encoded = self.spr_base16.encode(value)
            length = len(encoded)
            
            # Theoretical O(log_16 N)
            theoretical = math.log(value, 16) if value > 0 else 0
            
            results.append({
                'value': value,
                'length': length,
                'theoretical': theoretical,
                'ratio': length / theoretical if theoretical > 0 else 0
            })
            
            print(f"  {value:>15,}: length={length:2d}, theoretical={theoretical:5.2f}, ratio={length/theoretical:.2f}")
        
        # Check if growth is logarithmic
        values_log = [math.log10(r['value']) for r in results]
        lengths = [r['length'] for r in results]
        
        # Linear regression to verify O(log N)
        coeffs = np.polyfit(values_log, lengths, 1)
        r_squared = np.corrcoef(values_log, lengths)[0, 1] ** 2
        
        print(f"\n  Linear regression (log scale):")
        print(f"    Slope: {coeffs[0]:.4f}")
        print(f"    R²: {r_squared:.6f}")
        
        # Verdict: R² > 0.99 means strong logarithmic relationship
        is_logarithmic = r_squared > 0.99
        
        if is_logarithmic:
            verdict = "✓ PASS: Space complexity is O(log N)"
            claim_status = "SUPPORTED"
        else:
            verdict = "✗ FAIL: Space complexity not logarithmic"
            claim_status = "REFUTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['space_complexity'] = {
            'claim': 'O(log_b N) space complexity',
            'r_squared': r_squared,
            'is_logarithmic': is_logarithmic,
            'status': claim_status,
            'verdict': verdict,
            'measurements': results
        }
    
    def benchmark_scalability(self):
        """Test how SPR scales with value size"""
        print("  Testing scalability...")
        
        value_ranges = [
            (1, 1000, "Small (1-1K)"),
            (1000, 1000000, "Medium (1K-1M)"),
            (1000000, 1000000000, "Large (1M-1B)"),
        ]
        
        for min_val, max_val, label in value_ranges:
            sample = np.random.randint(min_val, max_val, 1000)
            
            start = time.perf_counter()
            encoded = [self.spr_base16.encode(v) for v in sample]
            elapsed = time.perf_counter() - start
            
            ops_per_sec = len(sample) / elapsed
            avg_length = statistics.mean(len(e) for e in encoded)
            
            print(f"\n  {label}:")
            print(f"    Operations/sec: {ops_per_sec:,.0f}")
            print(f"    Avg encoding length: {avg_length:.2f}")
            print(f"    Time per operation: {elapsed/len(sample)*1000:.4f}ms")
        
        self.results['scalability'] = {
            'status': 'MEASURED',
            'note': 'Performance relatively consistent across value ranges'
        }


import math


def main():
    benchmark = SPRPerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    
    # Generate summary
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 80)
    
    for test_name, test_result in results.items():
        print(f"\n{test_name.upper()}:")
        if 'claim' in test_result:
            print(f"  Claim: {test_result['claim']}")
        print(f"  Status: {test_result.get('status', 'N/A')}")
        if 'verdict' in test_result:
            print(f"  {test_result['verdict']}")
        if 'note' in test_result:
            print(f"  Note: {test_result['note']}")
    
    # Save results
    output_file = '/workspace/Analysis/performance_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✓ Results saved to: {output_file}")
    
    return results


if __name__ == '__main__':
    main()
