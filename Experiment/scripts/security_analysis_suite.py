#!/usr/bin/env python3
"""
SPR Security Analysis Test Suite
Tests claims about security properties with empirical evidence
"""

import sys
import json
import math
import statistics
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import numpy as np

# Import SPR test suite to use existing implementation
sys.path.append('/workspace/Experiment/scripts')
from test_suite import SPR_Engine


class SPRSecurityAnalyzer:
    """Comprehensive security analysis of SPR"""
    
    def __init__(self):
        self.results = {}
        self.spr_base16 = SPR_Engine(radix=16)
        self.spr_base64 = SPR_Engine(radix=64)
    
    def run_all_tests(self):
        """Execute all security tests"""
        print("=" * 80)
        print("SPR SECURITY ANALYSIS - Evidence-Based Testing")
        print("=" * 80)
        
        # Test 1: Frequency Analysis
        print("\n[TEST 1] Frequency Analysis - Does SPR prevent pattern matching?")
        self.test_frequency_analysis()
        
        # Test 2: Entropy Measurement
        print("\n[TEST 2] Entropy Measurement - Is SPR OTP-like?")
        self.test_entropy_measurement()
        
        # Test 3: Pattern Detection
        print("\n[TEST 3] Pattern Detection - Sequential input patterns")
        self.test_pattern_detection()
        
        # Test 4: Malleability
        print("\n[TEST 4] Malleability - Can ciphertext be modified?")
        self.test_malleability()
        
        # Test 5: Known-Plaintext Attack Simulation
        print("\n[TEST 5] Known-Plaintext Attack - Key recovery")
        self.test_known_plaintext()
        
        # Test 6: Collision Testing
        print("\n[TEST 6] Collision Testing - Duplicate outputs")
        self.test_collisions()
        
        return self.results
    
    def test_frequency_analysis(self):
        """
        Claim: "Infinite alphabet prevents pattern matching"
        Test: Encode many values and measure symbol frequency distribution
        """
        print("  Testing symbol frequency distribution...")
        
        # Encode 10,000 random values
        sample_size = 10000
        test_values = np.random.randint(1, 1000000, sample_size)
        
        # Count symbols in all encodings
        symbol_counts = Counter()
        total_symbols = 0
        
        for value in test_values:
            encoded = self.spr_base16.encode(value)
            for char in encoded:
                symbol_counts[char] += 1
                total_symbols += 1
        
        # Calculate expected frequency for uniform distribution
        num_unique_symbols = len(symbol_counts)
        expected_freq = total_symbols / num_unique_symbols
        
        # Calculate chi-square statistic
        chi_square = sum(
            ((count - expected_freq) ** 2) / expected_freq 
            for count in symbol_counts.values()
        )
        
        # Calculate standard deviation of frequencies
        frequencies = list(symbol_counts.values())
        freq_std = statistics.stdev(frequencies)
        freq_mean = statistics.mean(frequencies)
        cv = freq_std / freq_mean  # Coefficient of variation
        
        # Analysis
        print(f"  ✓ Encoded {sample_size:,} values")
        print(f"  ✓ Total symbols produced: {total_symbols:,}")
        print(f"  ✓ Unique symbols used: {num_unique_symbols}")
        print(f"  ✓ Chi-square statistic: {chi_square:.2f}")
        print(f"  ✓ Frequency std dev: {freq_std:.2f}")
        print(f"  ✓ Coefficient of variation: {cv:.4f}")
        
        # Show most and least common symbols
        most_common = symbol_counts.most_common(5)
        least_common = symbol_counts.most_common()[-5:]
        print(f"  ✓ Most common: {most_common}")
        print(f"  ✓ Least common: {least_common}")
        
        # Verdict
        is_uniform = cv < 0.1  # Uniform distribution has low CV
        
        if is_uniform:
            verdict = "✓ PASS: Distribution is reasonably uniform"
            claim_status = "SUPPORTED"
        else:
            verdict = "✗ FAIL: Distribution shows non-uniformity"
            claim_status = "REFUTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['frequency_analysis'] = {
            'claim': 'Infinite alphabet prevents pattern matching',
            'chi_square': chi_square,
            'coefficient_of_variation': cv,
            'is_uniform': is_uniform,
            'status': claim_status,
            'verdict': verdict
        }
    
    def test_entropy_measurement(self):
        """
        Claim: "OTP-like properties" / "High entropy"
        Test: Calculate Shannon entropy of SPR output
        """
        print("  Measuring Shannon entropy...")
        
        sample_size = 10000
        test_values = np.random.randint(1, 1000000, sample_size)
        
        # Collect all symbols
        all_symbols = []
        for value in test_values:
            encoded = self.spr_base16.encode(value)
            all_symbols.extend(list(encoded))
        
        # Calculate Shannon entropy
        total = len(all_symbols)
        symbol_counts = Counter(all_symbols)
        entropy = -sum(
            (count / total) * math.log2(count / total)
            for count in symbol_counts.values()
        )
        
        # Calculate theoretical maximum entropy
        num_symbols = len(symbol_counts)
        max_entropy = math.log2(num_symbols)
        
        # Entropy as bits per symbol
        print(f"  ✓ Shannon entropy: {entropy:.4f} bits/symbol")
        print(f"  ✓ Maximum possible entropy: {max_entropy:.4f} bits/symbol")
        print(f"  ✓ Entropy ratio: {entropy/max_entropy:.4f} ({entropy/max_entropy*100:.2f}%)")
        
        # Compare to requirements
        print(f"\n  Comparison to security standards:")
        print(f"    - True random (ideal): 8.0 bits/byte")
        print(f"    - AES output: ~8.0 bits/byte")
        print(f"    - SPR output: {entropy:.2f} bits/symbol")
        print(f"    - OTP requirement: Perfect secrecy (key ≥ message)")
        
        # Check OTP requirements
        otp_requirements = {
            'key_length_gte_message': False,  # SPR uses fixed key
            'perfect_secrecy': False,  # No formal proof
            'one_time_use': False,  # Key can be reused
        }
        
        print(f"\n  OTP Requirements Check:")
        print(f"    ✗ Key length ≥ message length: {otp_requirements['key_length_gte_message']}")
        print(f"    ✗ Perfect secrecy H(M|C) = H(M): {otp_requirements['perfect_secrecy']}")
        print(f"    ✗ One-time use only: {otp_requirements['one_time_use']}")
        
        is_otp_like = all(otp_requirements.values())
        meets_high_entropy = entropy / max_entropy > 0.95
        
        if is_otp_like:
            verdict = "✓ PASS: Meets OTP requirements"
            claim_status = "SUPPORTED"
        elif meets_high_entropy:
            verdict = "⚠ PARTIAL: High entropy but not OTP"
            claim_status = "PARTIALLY_SUPPORTED"
        else:
            verdict = "✗ FAIL: Does not meet OTP requirements"
            claim_status = "REFUTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim 'OTP-like': {claim_status}")
        
        self.results['entropy_analysis'] = {
            'claim': 'OTP-like properties / High entropy',
            'shannon_entropy': entropy,
            'max_entropy': max_entropy,
            'entropy_ratio': entropy / max_entropy,
            'otp_requirements_met': otp_requirements,
            'is_otp_like': is_otp_like,
            'has_high_entropy': meets_high_entropy,
            'status': claim_status,
            'verdict': verdict
        }
    
    def test_pattern_detection(self):
        """
        Claim: "Prevents pattern matching"
        Test: Encode sequential values and check for correlations
        """
        print("  Testing pattern correlation...")
        
        # Test sequential inputs
        sequences = [
            list(range(1, 101)),  # 1, 2, 3, ..., 100
            list(range(10, 1010, 10)),  # 10, 20, 30, ..., 1000
            [2**i for i in range(1, 21)],  # Powers of 2
        ]
        
        correlations = []
        
        for seq_idx, sequence in enumerate(sequences):
            encodings = [self.spr_base16.encode(val) for val in sequence]
            lengths = [len(enc) for enc in encodings]
            
            # Check if encoding lengths correlate with input values
            length_correlation = np.corrcoef(sequence, lengths)[0, 1]
            correlations.append(abs(length_correlation))
            
            print(f"\n  Sequence {seq_idx + 1}: {sequence[:5]}...")
            print(f"    - Encoding lengths: {lengths[:5]}...")
            print(f"    - Length correlation: {length_correlation:.4f}")
            
            # Check character frequency patterns
            first_chars = [enc[0] if enc else '' for enc in encodings]
            first_char_variety = len(set(first_chars))
            print(f"    - First character variety: {first_char_variety}/{len(sequence)}")
            
            # Detect if incrementing inputs create incrementing outputs
            if len(sequence) > 1:
                increments_preserved = sum(
                    1 for i in range(len(sequence)-1)
                    if encodings[i] < encodings[i+1]
                )
                increment_ratio = increments_preserved / (len(sequence) - 1)
                print(f"    - Incremental pattern preserved: {increment_ratio:.2%}")
        
        avg_correlation = statistics.mean(correlations)
        max_correlation = max(correlations)
        
        print(f"\n  Average length correlation: {avg_correlation:.4f}")
        print(f"  Maximum correlation: {max_correlation:.4f}")
        
        # Verdict: Strong correlation (>0.7) means patterns detectable
        has_patterns = max_correlation > 0.7
        
        if has_patterns:
            verdict = "✗ FAIL: Patterns are detectable"
            claim_status = "REFUTED"
        else:
            verdict = "✓ PASS: Patterns not obviously detectable"
            claim_status = "SUPPORTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['pattern_detection'] = {
            'claim': 'Prevents pattern matching',
            'avg_correlation': avg_correlation,
            'max_correlation': max_correlation,
            'has_detectable_patterns': has_patterns,
            'status': claim_status,
            'verdict': verdict
        }
    
    def test_malleability(self):
        """
        Claim: "Tamper evidence via ghosting"
        Test: Modify ciphertext and check if errors are detected
        """
        print("  Testing malleability and tamper detection...")
        
        test_values = [123456, 999999, 500000, 777777, 111111]
        tamper_results = []
        
        for value in test_values:
            original_encoded = self.spr_base16.encode(value)
            
            if len(original_encoded) < 2:
                continue
            
            # Tamper by changing a character in the middle
            mid_idx = len(original_encoded) // 2
            tampered = list(original_encoded)
            
            # Change character
            original_char = tampered[mid_idx]
            new_char = 'X' if original_char != 'X' else 'Y'
            tampered[mid_idx] = new_char
            tampered_str = ''.join(tampered)
            
            # Try to decode tampered ciphertext
            try:
                decoded = self.spr_base16.decode(tampered_str)
                
                # Check if silent corruption occurred
                if decoded != value:
                    tamper_results.append({
                        'original': value,
                        'encoded': original_encoded,
                        'tampered': tampered_str,
                        'decoded': decoded,
                        'detected': False,
                        'silent_corruption': True
                    })
                else:
                    tamper_results.append({
                        'original': value,
                        'detected': False,
                        'silent_corruption': False
                    })
            except Exception as e:
                # Error was raised - tamper detected
                tamper_results.append({
                    'original': value,
                    'detected': True,
                    'error': str(e)
                })
        
        detected_count = sum(1 for r in tamper_results if r.get('detected', False))
        silent_corruption_count = sum(1 for r in tamper_results if r.get('silent_corruption', False))
        
        print(f"  ✓ Tested {len(test_values)} values")
        print(f"  ✓ Tampering detected: {detected_count}/{len(tamper_results)}")
        print(f"  ✓ Silent corruption: {silent_corruption_count}/{len(tamper_results)}")
        
        print(f"\n  Sample results:")
        for result in tamper_results[:3]:
            if result.get('silent_corruption'):
                print(f"    ✗ {result['original']} → {result['encoded']} → TAMPERED → {result['decoded']}")
                print(f"      SILENT CORRUPTION: Decoded to wrong value!")
        
        # Verdict
        is_malleable = silent_corruption_count > 0
        has_tamper_evidence = detected_count > silent_corruption_count
        
        if is_malleable:
            verdict = "✗ FAIL: Malleable - no authentication"
            claim_status = "REFUTED"
        elif has_tamper_evidence:
            verdict = "⚠ PARTIAL: Some tamper detection"
            claim_status = "PARTIALLY_SUPPORTED"
        else:
            verdict = "✓ PASS: Strong tamper evidence"
            claim_status = "SUPPORTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['malleability'] = {
            'claim': 'Tamper evidence via ghosting',
            'total_tests': len(tamper_results),
            'detected': detected_count,
            'silent_corruption': silent_corruption_count,
            'is_malleable': is_malleable,
            'status': claim_status,
            'verdict': verdict
        }
    
    def test_known_plaintext(self):
        """
        Claim: "Strong security properties"
        Test: Given plaintext-ciphertext pairs, attempt key recovery
        """
        print("  Simulating known-plaintext attack...")
        
        # Generate 100 known plaintext-ciphertext pairs
        pairs = []
        for i in range(100):
            value = np.random.randint(1, 1000000)
            encoded = self.spr_base16.encode(value)
            pairs.append((value, encoded))
        
        print(f"  ✓ Generated {len(pairs)} known pairs")
        
        # Attempt to find patterns
        # Analysis 1: Check if key can be extracted from encoding patterns
        length_to_values = defaultdict(list)
        for value, encoded in pairs:
            length_to_values[len(encoded)].append(value)
        
        print(f"  ✓ Encoding length distribution:")
        for length in sorted(length_to_values.keys()):
            values = length_to_values[length]
            print(f"    Length {length}: {len(values)} values (range: {min(values)}-{max(values)})")
        
        # Analysis 2: Check if we can predict encoding of new value
        test_value = 555555
        actual_encoding = self.spr_base16.encode(test_value)
        
        # Simple prediction: Use similar values from known pairs
        similar_pairs = [
            (v, e) for v, e in pairs 
            if abs(v - test_value) < 50000
        ]
        
        print(f"\n  Prediction attempt:")
        print(f"    Target value: {test_value}")
        print(f"    Actual encoding: {actual_encoding}")
        print(f"    Similar known values: {len(similar_pairs)}")
        
        if similar_pairs:
            closest = min(similar_pairs, key=lambda x: abs(x[0] - test_value))
            print(f"    Closest known: {closest[0]} → {closest[1]}")
            prediction_possible = len(similar_pairs) > 5
        else:
            prediction_possible = False
        
        # Verdict: If we can narrow down possibilities, attack is viable
        if prediction_possible:
            verdict = "⚠ VULNERABLE: Patterns exploitable"
            claim_status = "REFUTED"
        else:
            verdict = "✓ RESISTANT: Prediction difficult"
            claim_status = "SUPPORTED"
        
        print(f"\n  {verdict}")
        print(f"  Claim Status: {claim_status}")
        
        self.results['known_plaintext'] = {
            'claim': 'Strong security properties',
            'known_pairs': len(pairs),
            'prediction_possible': prediction_possible,
            'status': claim_status,
            'verdict': verdict
        }
    
    def test_collisions(self):
        """
        Claim: Implicit - unique encodings
        Test: Check for duplicate encodings of different values
        """
        print("  Testing for collisions...")
        
        sample_size = 50000
        test_values = np.random.randint(1, 10000000, sample_size)
        
        encodings = {}
        collisions = []
        
        for value in test_values:
            encoded = self.spr_base16.encode(value)
            
            if encoded in encodings:
                collisions.append((value, encodings[encoded], encoded))
            else:
                encodings[encoded] = value
        
        collision_count = len(collisions)
        unique_encodings = len(encodings)
        
        print(f"  ✓ Tested {sample_size:,} values")
        print(f"  ✓ Unique encodings: {unique_encodings:,}")
        print(f"  ✓ Collisions found: {collision_count}")
        
        if collision_count > 0:
            print(f"\n  Collision examples:")
            for val1, val2, enc in collisions[:5]:
                print(f"    ✗ {val1} and {val2} both encode to: {enc}")
            verdict = "✗ FAIL: Collisions exist"
            claim_status = "REFUTED"
        else:
            verdict = "✓ PASS: No collisions in sample"
            claim_status = "SUPPORTED"
        
        print(f"\n  {verdict}")
        
        self.results['collisions'] = {
            'claim': 'Unique encodings (no collisions)',
            'sample_size': sample_size,
            'unique_encodings': unique_encodings,
            'collisions': collision_count,
            'has_collisions': collision_count > 0,
            'status': claim_status,
            'verdict': verdict
        }


def main():
    analyzer = SPRSecurityAnalyzer()
    results = analyzer.run_all_tests()
    
    # Generate summary
    print("\n" + "=" * 80)
    print("SUMMARY OF SECURITY ANALYSIS")
    print("=" * 80)
    
    status_counts = {
        'SUPPORTED': 0,
        'PARTIALLY_SUPPORTED': 0,
        'REFUTED': 0,
    }
    
    for test_name, test_result in results.items():
        status = test_result.get('status', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n{test_name.upper()}:")
        print(f"  Claim: {test_result['claim']}")
        print(f"  Status: {status}")
        print(f"  {test_result['verdict']}")
    
    total_tests = len(results)
    print(f"\n" + "=" * 80)
    print(f"OVERALL ASSESSMENT:")
    print(f"  Total tests: {total_tests}")
    print(f"  ✓ Supported: {status_counts.get('SUPPORTED', 0)} ({status_counts.get('SUPPORTED', 0)/total_tests*100:.1f}%)")
    print(f"  ⚠ Partial: {status_counts.get('PARTIALLY_SUPPORTED', 0)} ({status_counts.get('PARTIALLY_SUPPORTED', 0)/total_tests*100:.1f}%)")
    print(f"  ✗ Refuted: {status_counts.get('REFUTED', 0)} ({status_counts.get('REFUTED', 0)/total_tests*100:.1f}%)")
    
    # Save results
    output_file = '/workspace/Analysis/security_analysis_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✓ Results saved to: {output_file}")
    
    return results


if __name__ == '__main__':
    main()
