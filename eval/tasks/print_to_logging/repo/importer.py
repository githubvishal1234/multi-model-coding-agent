def parse_rows(lines):
    """Parse "sku,qty" lines into (sku, qty) tuples, skipping malformed lines."""
    rows = []
    print(f"importing {len(lines)} lines")
    for number, line in enumerate(lines, 1):
        parts = line.strip().split(",")
        if len(parts) != 2 or not parts[1].strip().isdigit():
            print(f"skipping line {number}: {line.strip()!r}")
            continue
        rows.append((parts[0].strip(), int(parts[1])))
    print(f"imported {len(rows)} rows")
    return rows
