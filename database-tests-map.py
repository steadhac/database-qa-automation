import matplotlib.pyplot as plt

# Test suites and their test cases
test_suites = {
    "SQL CRUD": [
        "SQL-001: Create & Read",
        "SQL-002: Update",
        "SQL-003: Delete"
    ],
    "SQL Vault": [
        "SQL-004: AES-256-GCM",
        "SQL-005: Metadata",
        "SQL-006: Key Isolation",
        "SQL-007: Tampering",
        "SQL-008: Checksum"
    ],
    "Data Integrity": [
        "INT-001: Unique",
        "INT-002: Foreign Keys",
        "INT-003: Concurrent"
    ],
    "Performance": [
        "PERF-001: Bulk Insert",
        "PERF-002: Query (< 100ms)",
        "PERF-003: EXPLAIN (< 50ms)"
    ],
    "Schema": [
        "SCH-001: Structure",
        "SCH-002: Index",
        "SCH-003: Migration"
    ],
    "API": [
        "API-001: Create",
        "API-002: Retrieve",
        "API-003: Error"
    ],
    "CLI": [
        "CLI-001: Export",
        "CLI-002: Delete",
        "CLI-003: Stats",
        "CLI-004: Query"
    ]
}

total_tests = sum(len(tests) for tests in test_suites.values())

colors = {
    "SQL CRUD": "#FF6B6B",
    "SQL Vault": "#FF8C42",
    "Data Integrity": "#4ECDC4",
    "Performance": "#45B7D1",
    "Schema": "#96CEB4",
    "API": "#FFEAA7",
    "CLI": "#DDA15E"
}

positions = {
    "SQL CRUD": (-10, 6),
    "SQL Vault": (-2, 6),
    "Data Integrity": (6, 6),
    "Performance": (14, 6),
    "Schema": (-6, -6),
    "API": (2, -6),
    "CLI": (10, -6)
}

fig, ax = plt.subplots(figsize=(22, 12))

for suite, (x, y) in positions.items():
    tests = test_suites[suite]
    bubble_radius = 2.8 + (len(tests) * 0.25)
    
    # Draw bubble
    circle = plt.Circle((x, y), radius=bubble_radius, 
                       color=colors[suite], 
                       alpha=0.75, ec='black', lw=2.5)
    ax.add_patch(circle)
    
    # Suite title (INSIDE bubble, smaller font)
    ax.text(x, y + bubble_radius - 1.2, suite, 
           ha='center', va='center', fontsize=10, 
           fontweight='bold', color='black')
    
    # Test count
    ax.text(x, y + bubble_radius - 2, f"({len(tests)})", 
           ha='center', va='center', fontsize=8, 
           style='italic', color='darkslategray')
    
    # Test cases (tighter spacing to fit inside)
    y_start = y + (len(tests) * 0.25)
    for i, test in enumerate(tests):
        test_y = y_start - (i * 0.55)
        ax.text(x, test_y, test, 
               ha='center', va='center', fontsize=7.5, 
               color='darkblue', weight='normal')

# Main title
ax.text(0, 14.5, "Database QA Automation Test Map", 
       ha='center', va='center', fontsize=18, fontweight='bold')

# Legend on middle left side
legend_x = -19
legend_y = 2
ax.text(legend_x + 1.5, legend_y + 2.5, "Test Categories", fontsize=10, fontweight='bold')

for i, (suite, color) in enumerate(colors.items()):
    test_count = len(test_suites[suite])
    y_pos = legend_y + 1.5 - (i * 0.75)
    
    rect = plt.Rectangle((legend_x + 0.2, y_pos - 0.2), 0.4, 0.4, 
                         facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    
    ax.text(legend_x + 1.2, y_pos, f"{suite}: {test_count}", 
           ha='left', va='center', fontsize=8, fontweight='bold')

# Summary
summary_y = legend_y - 5.5
rect = plt.Rectangle((legend_x + 0.2, summary_y - 0.3), 3.5, 0.7, 
                     facecolor='lightgreen', edgecolor='darkgreen', 
                     linewidth=2, alpha=0.6)
ax.add_patch(rect)
ax.text(legend_x + 2, summary_y, f"Total: {total_tests}", 
       ha='center', va='center', fontsize=9, fontweight='bold', color='darkgreen')

# Axis setup
ax.set_xlim(-21, 20)
ax.set_ylim(-13, 16)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig('test_map.png', dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Test map generated: test_map.png ({total_tests} tests)")
plt.show()