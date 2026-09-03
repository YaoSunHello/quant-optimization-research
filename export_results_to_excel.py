"""
Export frontier simulation results from JSON to CSV and XLSX
"""
import json
import pandas as pd

print("Exporting frontier simulation results to CSV and XLSX...\n")

# Load JSON results
json_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/efficient_frontier_data.json'
with open(json_file, 'r') as f:
    data = json.load(f)

portfolios = data['portfolios']
return_target = data['return_target']

print(f"Processing {len(portfolios)} portfolios...\n")

# Convert to DataFrame
portfolios_with_id = []
for idx, p in enumerate(portfolios, 1):
    row = {
        'Portfolio_ID': idx,
        'US_Equity': p['weights'].get('US Eq', 0),
        'International': p['weights'].get('Intl', 0),
        'Emerging_Markets': p['weights'].get('EM', 0),
        'Bonds': p['weights'].get('Bonds', 0),
        'Real_Estate': p['weights'].get('RE', 0),
        'Expected_Return_Annual': p['expected_return'] / 100,
        'Volatility_Annual': p['volatility'] / 100,
        'VaR_95_5Year': p['var_95_5yr'],
        'VaR_95_Annual': p['var_95_annual'],
        'Prob_Exceed_Target': p['prob_exceed_target'],
    }
    portfolios_with_id.append(row)

df = pd.DataFrame(portfolios_with_id)

# Save to CSV
csv_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/frontier_simulation_results.csv'
df.to_csv(csv_file, index=False)

# Save to Excel
xlsx_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/frontier_simulation_results.xlsx'
df.to_excel(xlsx_file, index=False, sheet_name='Portfolios')

print(f"✅ Saved {len(portfolios_with_id)} portfolios")
print(f"   CSV:  frontier_simulation_results.csv")
print(f"   XLSX: frontier_simulation_results.xlsx")
print(f"\nReturn Target: {return_target*100:.0f}%")
print(f"\nSummary Statistics:")
print(f"  VaR 95% Annual - Min: {df['VaR_95_Annual'].min()*100:.2f}%, Max: {df['VaR_95_Annual'].max()*100:.2f}%")
print(f"  Prob(Return > {return_target*100:.0f}%) - Min: {df['Prob_Exceed_Target'].min()*100:.1f}%, Max: {df['Prob_Exceed_Target'].max()*100:.1f}%")
print(f"  Expected Annual Return - Min: {df['Expected_Return_Annual'].min()*100:.2f}%, Max: {df['Expected_Return_Annual'].max()*100:.2f}%")

# Print PDF statistics
if 'statistics' in data:
    stats = data['statistics']
    print(f"\nProbability Distribution Statistics:")
    print(f"  Mean: {stats['mean']*100:.1f}%")
    print(f"  Median: {stats['median']*100:.1f}%")
    print(f"  Std Dev: {stats['std_dev']*100:.1f}%")
