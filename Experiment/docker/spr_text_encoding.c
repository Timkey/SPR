/*
 * SPR Text Encoding in C
 * Encodes arbitrary text via base64 intermediate format
 * Much faster than Python implementation
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

// Base64 encoding table
static const char base64_chars[] = 
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// Base64 decoding table
static int base64_decode_table[256];

// Roman numeral symbols
static const char BASE_SYMBOLS[] = "IVXLCDM";
static const int SYMBOL_COUNT = 7;

// Standard Roman numeral mappings
static const char* STANDARD_ROMAN[] = {
    "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX",
    "", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"
};

typedef struct {
    int radix;
    int rotation_key[7];
    int rotation_key_len;
} SPRConfig;

// Initialize base64 decode table
void init_base64_decode() {
    for (int i = 0; i < 256; i++) {
        base64_decode_table[i] = -1;
    }
    for (int i = 0; i < 64; i++) {
        base64_decode_table[(int)base64_chars[i]] = i;
    }
}

// Base64 encode
int base64_encode(const char* input, int input_len, char* output) {
    int i = 0, j = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];
    int out_len = 0;

    while (input_len--) {
        char_array_3[i++] = *(input++);
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (i = 0; i < 4; i++)
                output[out_len++] = base64_chars[char_array_4[i]];
            i = 0;
        }
    }

    if (i) {
        for (j = i; j < 3; j++)
            char_array_3[j] = '\0';

        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);

        for (j = 0; j < i + 1; j++)
            output[out_len++] = base64_chars[char_array_4[j]];

        while (i++ < 3)
            output[out_len++] = '=';
    }

    output[out_len] = '\0';
    return out_len;
}

// Base64 decode
int base64_decode(const char* input, char* output) {
    int i = 0, j = 0, in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    int out_len = 0;
    int in_len = strlen(input);

    while (in_len-- && input[in_] != '=') {
        if (base64_decode_table[(int)input[in_]] == -1) {
            in_++;
            continue;
        }
        char_array_4[i++] = input[in_++];
        if (i == 4) {
            for (i = 0; i < 4; i++)
                char_array_4[i] = base64_decode_table[(int)char_array_4[i]];

            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

            for (i = 0; i < 3; i++)
                output[out_len++] = char_array_3[i];
            i = 0;
        }
    }

    if (i) {
        for (j = 0; j < i; j++)
            char_array_4[j] = base64_decode_table[(int)char_array_4[j]];

        char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);

        for (j = 0; j < i - 1; j++)
            output[out_len++] = char_array_3[j];
    }

    output[out_len] = '\0';
    return out_len;
}

// Apply rotation to symbol
char spr_apply_rotation(char symbol, int rotation) {
    for (int i = 0; i < SYMBOL_COUNT; i++) {
        if (BASE_SYMBOLS[i] == symbol) {
            int new_idx = (i + rotation) % SYMBOL_COUNT;
            return BASE_SYMBOLS[new_idx];
        }
    }
    return symbol;
}

// Simple Roman encoding for ASCII values (0-127)
void ascii_to_roman(int value, char* output) {
    if (value == 0) {
        strcpy(output, "N");
        return;
    }
    
    int out_idx = 0;
    
    // Hundreds
    int hundreds = value / 100;
    for (int i = 0; i < hundreds; i++) {
        output[out_idx++] = 'C';
    }
    value %= 100;
    
    // Fifties
    if (value >= 50) {
        output[out_idx++] = 'L';
        value -= 50;
    }
    
    // Tens with subtractive notation
    int tens = value / 10;
    if (tens == 4) {
        output[out_idx++] = 'X';
        output[out_idx++] = 'L';
        value -= 40;
    } else if (tens == 9) {
        output[out_idx++] = 'X';
        output[out_idx++] = 'C';
        value -= 90;
    } else {
        for (int i = 0; i < tens; i++) {
            output[out_idx++] = 'X';
        }
        value %= 10;
    }
    
    // Ones with subtractive notation
    if (value == 4) {
        output[out_idx++] = 'I';
        output[out_idx++] = 'V';
    } else if (value == 9) {
        output[out_idx++] = 'I';
        output[out_idx++] = 'X';
    } else {
        if (value >= 5) {
            output[out_idx++] = 'V';
            value -= 5;
        }
        for (int i = 0; i < value; i++) {
            output[out_idx++] = 'I';
        }
    }
    
    output[out_idx] = '\0';
}

// Convert integer to Roman with rotation
void int_to_roman_rotated(int value, int position, SPRConfig* config, char* output) {
    char temp[64];
    ascii_to_roman(value, temp);
    
    // Apply rotation
    int rotation = config->rotation_key[position % config->rotation_key_len];
    int len = strlen(temp);
    for (int i = 0; i < len; i++) {
        output[i] = spr_apply_rotation(temp[i], rotation);
    }
    output[len] = '\0';
}

// Reverse rotation
char spr_reverse_rotation(char symbol, int rotation) {
    for (int i = 0; i < SYMBOL_COUNT; i++) {
        if (BASE_SYMBOLS[i] == symbol) {
            int new_idx = (i - rotation + SYMBOL_COUNT) % SYMBOL_COUNT;
            return BASE_SYMBOLS[new_idx];
        }
    }
    return symbol;
}

// Roman to integer with proper subtractive notation
int roman_to_int_simple(const char* roman, int rotation) {
    if (strcmp(roman, "N") == 0) return 0;
    
    // Reverse rotation first
    char unrotated[64];
    int len = strlen(roman);
    for (int i = 0; i < len; i++) {
        unrotated[i] = spr_reverse_rotation(roman[i], rotation);
    }
    unrotated[len] = '\0';
    
    // Get symbol values
    int values[64];
    for (int i = 0; i < len; i++) {
        char c = unrotated[i];
        if (c == 'I') values[i] = 1;
        else if (c == 'V') values[i] = 5;
        else if (c == 'X') values[i] = 10;
        else if (c == 'L') values[i] = 50;
        else if (c == 'C') values[i] = 100;
        else if (c == 'D') values[i] = 500;
        else if (c == 'M') values[i] = 1000;
        else values[i] = 0;
    }
    
    // Apply subtractive notation rules
    int value = 0;
    for (int i = 0; i < len; i++) {
        if (i + 1 < len && values[i] < values[i + 1]) {
            value -= values[i];
        } else {
            value += values[i];
        }
    }
    
    return value;
}

// SPR encode text
int spr_encode_text(const char* text, SPRConfig* config, char* output) {
    // Step 1: Base64 encode
    char b64[4096];
    int b64_len = base64_encode(text, strlen(text), b64);
    
    // Step 2: SPR encode each base64 character
    int out_pos = 0;
    for (int i = 0; i < b64_len; i++) {
        int ascii_val = (int)b64[i];
        
        // Encode this ASCII value
        char spr_chunk[128];
        int_to_roman_rotated(ascii_val, i, config, spr_chunk);
        
        // Add separator if not first
        if (i > 0) {
            output[out_pos++] = '|';
            output[out_pos++] = '|';
        }
        
        // Copy SPR chunk
        strcpy(output + out_pos, spr_chunk);
        out_pos += strlen(spr_chunk);
    }
    
    output[out_pos] = '\0';
    return out_pos;
}

// SPR decode text
int spr_decode_text(const char* encoded, SPRConfig* config, char* output) {
    // Parse SPR chunks
    char b64[4096];
    int b64_pos = 0;
    
    char chunk[128];
    int chunk_pos = 0;
    int position = 0;
    
    for (int i = 0; i <= strlen(encoded); i++) {
        if (encoded[i] == '|' && encoded[i+1] == '|') {
            // Process chunk
            chunk[chunk_pos] = '\0';
            int rotation = config->rotation_key[position % config->rotation_key_len];
            int ascii_val = roman_to_int_simple(chunk, rotation);
            b64[b64_pos++] = (char)ascii_val;
            
            chunk_pos = 0;
            position++;
            i++; // Skip second |
        } else if (encoded[i] == '\0') {
            // Last chunk
            chunk[chunk_pos] = '\0';
            int rotation = config->rotation_key[position % config->rotation_key_len];
            int ascii_val = roman_to_int_simple(chunk, rotation);
            b64[b64_pos++] = (char)ascii_val;
        } else {
            chunk[chunk_pos++] = encoded[i];
        }
    }
    
    b64[b64_pos] = '\0';
    
    // Base64 decode
    return base64_decode(b64, output);
}

// Benchmark function
void benchmark_text_encoding(int iterations) {
    SPRConfig config = {
        .radix = 16,
        .rotation_key = {0, 2, 4, 1, 5, 3, 6},
        .rotation_key_len = 7
    };
    
    const char* test_strings[] = {
        "Hello, World!",
        "user@example.com",
        "SecurePassword123!",
        "The quick brown fox jumps over the lazy dog"
    };
    int num_tests = 4;
    
    printf("SPR Text Encoding Benchmark (C)\n");
    printf("================================\n\n");
    
    for (int t = 0; t < num_tests; t++) {
        const char* text = test_strings[t];
        char encoded[8192];
        char decoded[4096];
        
        // Encoding benchmark
        clock_t start = clock();
        for (int i = 0; i < iterations; i++) {
            spr_encode_text(text, &config, encoded);
        }
        clock_t end = clock();
        double encode_time = (double)(end - start) / CLOCKS_PER_SEC;
        double encode_ops = iterations / encode_time;
        
        // Decoding benchmark
        spr_encode_text(text, &config, encoded);
        start = clock();
        for (int i = 0; i < iterations; i++) {
            spr_decode_text(encoded, &config, decoded);
        }
        end = clock();
        double decode_time = (double)(end - start) / CLOCKS_PER_SEC;
        double decode_ops = iterations / decode_time;
        
        // Verify correctness
        spr_decode_text(encoded, &config, decoded);
        int correct = strcmp(text, decoded) == 0;
        
        printf("Text: \"%s\"\n", text);
        printf("  Encoding: %10.0f ops/sec\n", encode_ops);
        printf("  Decoding: %10.0f ops/sec\n", decode_ops);
        printf("  Correct:  %s\n\n", correct ? "✓" : "✗");
    }
}

int main(int argc, char* argv[]) {
    init_base64_decode();
    
    int iterations = 10000;
    if (argc > 1) {
        iterations = atoi(argv[1]);
    }
    
    benchmark_text_encoding(iterations);
    
    return 0;
}
