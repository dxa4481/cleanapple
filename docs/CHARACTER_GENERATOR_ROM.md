# Apple II Character Generator ROM Documentation

## Overview

The Apple II Character Generator ROM is a 2KB EPROM (2716) that contains the pixel patterns for 64 characters used in text display mode. Each character is defined by an 8x8 pixel matrix stored as 8 bytes.

## Memory Organization

- **Total Size**: 2048 bytes (2KB)
- **Characters**: 64 characters (0-63)
- **Bytes per character**: 8 bytes (one per row)
- **Character index mapping**: Character code (0-63) × 8 = starting byte offset

## Character Set

The Apple II character generator contains:
- ASCII characters 32-95 ($20-$5F) mapped to indices 0-63
- This includes: space, punctuation, digits 0-9, uppercase letters A-Z

### Character Index to ASCII Mapping

| Index | ASCII | Character |
|-------|-------|-----------|
| 0     | 32    | (space)   |
| 1     | 33    | !         |
| 2     | 34    | "         |
| 3     | 35    | #         |
| 4     | 36    | $         |
| 5     | 37    | %         |
| 6     | 38    | &         |
| 7     | 39    | '         |
| 8     | 40    | (         |
| 9     | 41    | )         |
| 10    | 42    | *         |
| 11    | 43    | +         |
| 12    | 44    | ,         |
| 13    | 45    | -         |
| 14    | 46    | .         |
| 15    | 47    | /         |
| 16    | 48    | 0         |
| 17    | 49    | 1         |
| 18    | 50    | 2         |
| 19    | 51    | 3         |
| 20    | 52    | 4         |
| 21    | 53    | 5         |
| 22    | 54    | 6         |
| 23    | 55    | 7         |
| 24    | 56    | 8         |
| 25    | 57    | 9         |
| 26    | 58    | :         |
| 27    | 59    | ;         |
| 28    | 60    | <         |
| 29    | 61    | =         |
| 30    | 62    | >         |
| 31    | 63    | ?         |
| 32    | 64    | @         |
| 33    | 65    | A         |
| 34    | 66    | B         |
| 35    | 67    | C         |
| 36    | 68    | D         |
| 37    | 69    | E         |
| 38    | 70    | F         |
| 39    | 71    | G         |
| 40    | 72    | H         |
| 41    | 73    | I         |
| 42    | 74    | J         |
| 43    | 75    | K         |
| 44    | 76    | L         |
| 45    | 77    | M         |
| 46    | 78    | N         |
| 47    | 79    | O         |
| 48    | 80    | P         |
| 49    | 81    | Q         |
| 50    | 82    | R         |
| 51    | 83    | S         |
| 52    | 84    | T         |
| 53    | 85    | U         |
| 54    | 86    | V         |
| 55    | 87    | W         |
| 56    | 88    | X         |
| 57    | 89    | Y         |
| 58    | 90    | Z         |
| 59    | 91    | [         |
| 60    | 92    | \         |
| 61    | 93    | ]         |
| 62    | 94    | ^         |
| 63    | 95    | _         |

## Pixel Data Format

Each character is 8 bytes, representing 8 rows of pixels:
- Byte 0: Top row
- Byte 1: Second row
- ...
- Byte 7: Bottom row

Within each byte:
- Bit 0 (LSB): Leftmost pixel
- Bit 6: Rightmost visible pixel
- Bit 7: Generally set to 0 (not displayed)

A set bit (1) indicates a lit pixel.

## Example: Letter 'A' (Index 33)

```
Row 0: 0001 1100 = $1C  ○○○●●●○○
Row 1: 0010 0010 = $22  ○●○○○●○○
Row 2: 0100 0001 = $41  ●○○○○○●○
Row 3: 0111 1111 = $7F  ●●●●●●●○
Row 4: 0100 0001 = $41  ●○○○○○●○
Row 5: 0100 0001 = $41  ●○○○○○●○
Row 6: 0100 0001 = $41  ●○○○○○●○
Row 7: 0000 0000 = $00  ○○○○○○○○
```

## Hardware Usage

The Character Generator ROM is addressed by:
- Character code (6 bits) selecting which character
- Row counter (3 bits) selecting which row of the character
- This creates a 9-bit address (512 bytes addressable) but the ROM is 2KB

The Apple II displays characters in normal, inverse, and flashing modes:
- **Normal**: Lit pixels are white, unlit are black
- **Inverse**: Colors reversed
- **Flashing**: Alternates between normal and inverse

## Test Verification

A cleanroom Character Generator ROM must:
1. Be exactly 2048 bytes
2. Have identical pixel patterns for all 64 characters
3. Each character occupies exactly 8 consecutive bytes
4. Characters are indexed 0-63 corresponding to ASCII 32-95

## Creating Cleanroom Implementation

Since the character generator is purely visual data (not executable code), a cleanroom implementation must:
1. Design each character glyph independently
2. Ensure visual compatibility while not copying the exact pixel patterns
3. Match the format expectations of the Apple II hardware

For testing purposes, we can verify:
- ROM size
- Character addressing
- Basic glyph recognition (OCR-style testing)
