import sys

def fix_indentation(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines 542 to 607 (0-indexed: 541 to 606)
    start_idx = 541
    end_idx = 607

    new_lines = []
    for i, line in enumerate(lines):
        if start_idx <= i <= end_idx:
            # Outdent by 4 spaces
            if line.startswith('    '):
                new_lines.append(line[4:])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    fix_indentation(r"c:\Users\ACER\OneDrive\Desktop\Ai_Validator\app.py")
