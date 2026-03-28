# Dockerfile for SPR C Implementation
FROM gcc:latest

WORKDIR /app

# Copy C source
COPY spr.c .

# Compile with optimizations
RUN gcc -O3 -march=native -o spr spr.c -lm

# Default command
CMD ["./spr", "100000"]
