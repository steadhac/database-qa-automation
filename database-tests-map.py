import matplotlib.pyplot as plt

# -----------------------------
# Test suites and their test cases with IDs
# -----------------------------
test_suites = {
    "Test CRUD Operations": [
        "SQL-001: Create Record and Read",
        "SQL-002: Update Record",
        "SQL-003: Delete Cascade",
    ],
    "Test Vault Operations": [
        "SQL-004: Encrypted Data",
        "SQL-005: Metadata Tracking",
        "SQL-006: Key Management",
        "SQL-007: Tampering Detection"
    ],
    "Test Performance": [
        "PERF-001: Write Performance",
        "PERF-002: Read Performance",
        "PERF-003: End-to-End Execution",
        "PERF-004: Regression Detection",
        "PERF-005: Production Checks"
    ],
    "Test SchemaValidation": [
        "SCH-001: Table Structure",
        "SCH-002: Index Verification",
        "SCH-003: Schema Migration"
    ],
    "Test CLI Commands": [
        "CLI-001: CLI Export",
        "CLI-002: CLI Bulk Delete",
        "CLI-003: CLI Stats",
        "CLI-004: CLI Query"
    ],
    "Test API": [
        "API-001: User Creation via API Workflow",
        "API-002: Retrieval and serialized output",
        "API-003: API Error Handling for Invalid Data"
    ]
}

# -----------------------------
# Compute bubble positions (grid)
# -----------------------------
suites = list(test_suites.keys())
num_suites = len(suites)
cols = 3  # 2 rows, 3 columns
rows = -(-num_suites // cols)  # ceiling division
x_spacing = 8
y_spacing = 6

positions = {}
for i, suite in enumerate(suites):
    col = i % cols
    row = i // cols
    positions[suite] = (col * x_spacing, -row * y_spacing)

# Center horizontally
all_x = [x for x, y in positions.values()]
x_center = (max(all_x) + min(all_x)) / 2
for k in positions:
    positions[k] = (positions[k][0] - x_center, positions[k][1])

# -----------------------------
# Draw bubbles
# -----------------------------
plt.figure(figsize=(18, 10))
ax = plt.gca()

bubble_radius = 3  # slightly smaller for clarity

for suite, (x, y) in positions.items():
    tests = test_suites[suite]
    
    # Draw suite bubble
    circle = plt.Circle((x, y), radius=bubble_radius, color='#87CEFA', alpha=0.6, ec='navy', lw=2)
    ax.add_patch(circle)
    
    # Draw suite name on top of bubble
    plt.text(x, y + bubble_radius*0.5, suite, ha='center', va='center', fontsize=12, fontweight='bold', color='navy')
    
    # Draw test cases inside bubble, stacked
    for i, test in enumerate(tests):
        plt.text(x, y - 0.3*i, test, ha='center', va='center', fontsize=10, color='black')

plt.axis('equal')
plt.axis('off')
plt.title("Database QA Automation: Test Suites with Test Cases", fontsize=18)
plt.tight_layout()
plt.show()
