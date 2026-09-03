"""
Generate PDF data for probability of exceeding target and add to JSON
"""
import json
import numpy as np

print("Generating PDF data and adding to JSON...\n")

# Load simulation results
json_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/efficient_frontier_data.json'
with open(json_file, 'r') as f:
    data = json.load(f)

portfolios = data['portfolios']
return_target = data['return_target']

# Extract probabilities
probs = np.array([p['prob_exceed_target'] for p in portfolios])

print(f"Total portfolios: {len(probs)}")
print(f"Probability range: {probs.min():.1%} to {probs.max():.1%}")
print(f"Mean probability: {probs.mean():.1%}")
print(f"Median probability: {np.median(probs):.1%}")
print(f"Std Dev: {probs.std():.1%}\n")

# Create PDF (histogram bins)
n_bins = 40
hist, bin_edges = np.histogram(probs, bins=n_bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
pdf_values = hist / (len(probs) * (bin_edges[1] - bin_edges[0]))

# Create CDF
sorted_probs = np.sort(probs)
cdf_values = np.arange(1, len(sorted_probs) + 1) / len(sorted_probs)

# Add to data
data['pdf'] = {
    'labels': [f"{x:.1%}" for x in bin_centers],
    'values': pdf_values.tolist(),
    'bin_edges': bin_edges.tolist(),
    'histogram_counts': hist.tolist(),
}

data['cdf'] = {
    'probabilities': sorted_probs.tolist(),
    'cumulative_percent': cdf_values.tolist(),
}

data['statistics'] = {
    'mean': float(probs.mean()),
    'median': float(np.median(probs)),
    'std_dev': float(probs.std()),
    'min': float(probs.min()),
    'max': float(probs.max()),
    'total_portfolios': len(probs),
}

# Save updated JSON
with open(json_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Added PDF, CDF, and statistics to JSON")
print(f"\nData added:")
print(f"  - PDF: {len(data['pdf']['labels'])} bins")
print(f"  - CDF: {len(data['cdf']['probabilities'])} points")
print(f"  - Statistics: Mean, Median, Std Dev, Min, Max")
