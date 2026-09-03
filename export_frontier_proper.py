"""
Export frontier simulation results to CSV and proper XLSX
"""
import numpy as np
import json
import pandas as pd
import csv

print("Running frontier simulation and exporting to CSV/XLSX...\n")

# Asset parameters
assets = ['US Eq', 'Intl', 'EM', 'Bonds', 'RE']
returns = np.array([0.10, 0.09, 0.115, 0.045, 0.09])
vols = np.array([0.18, 0.20, 0.28, 0.05, 0.16])

corr = np.array([
    [1.00,  0.78, 0.72, -0.15, 0.65],
    [0.78,  1.00, 0.82, -0.10, 0.60],
    [0.72,  0.82, 1.00,  0.05, 0.55],
    [-0.15, -0.10, 0.05, 1.00, 0.15],
    [0.65,  0.60, 0.55, 0.15, 1.00],
])

# Simulation parameters
N_PORTFOLIOS = 500
N_SIMS = 1000
N_YEARS = 5
N_DAYS = N_YEARS * 252
RETURN_TARGET = 0.60

daily_returns = returns / 252
daily_vols = vols / np.sqrt(252)
cov_matrix = np.diag(daily_vols) @ corr @ np.diag(daily_vols)
L = np.linalg.cholesky(cov_matrix)

portfolios_data = []

print(f"Generating {N_PORTFOLIOS} portfolios...\n")

for p_idx in range(N_PORTFOLIOS):
    w = np.random.dirichlet(np.ones(len(assets)))

    port_return = np.sum(w * returns)
    port_cov = w @ (np.diag(vols) @ corr @ np.diag(vols)) @ w
    port_vol = np.sqrt(port_cov)

    # Simulate 5-year returns
    cumulative_returns = np.ones(N_SIMS)
    for day in range(N_DAYS):
        Z = np.random.standard_normal((N_SIMS, len(assets)))
        corr_returns = Z @ L.T
        daily_asset_returns = daily_returns[:, None] + daily_vols[:, None] * corr_returns.T
        daily_port_return = np.sum(w[:, None] * daily_asset_returns, axis=0)
        cumulative_returns *= (1 + daily_port_return)

    final_returns = cumulative_returns - 1

    # VaR at 95% (5th percentile of returns)
    var_95_5yr = np.percentile(final_returns, 5)
    var_95_annual = (1 + var_95_5yr) ** (1 / N_YEARS) - 1

    # Probability of beating return target
    prob_exceed_target = np.mean(final_returns > RETURN_TARGET)

    # Percentile statistics
    percentiles = np.percentile(final_returns, [1, 5, 10, 25, 50, 75, 90, 95, 99])

    portfolios_data.append({
        'Portfolio_ID': p_idx + 1,
        'US_Equity': w[0],
        'International': w[1],
        'Emerging_Markets': w[2],
        'Bonds': w[3],
        'Real_Estate': w[4],
        'Expected_Return_Annual': port_return,
        'Volatility_Annual': port_vol,
        'VaR_95_5Year': var_95_5yr,
        'VaR_95_Annual': var_95_annual,
        'Prob_Exceed_60pct': prob_exceed_target,
        'Mean_Return': np.mean(final_returns),
        'Std_Dev_Return': np.std(final_returns),
        'Min_Return': np.min(final_returns),
        'Max_Return': np.max(final_returns),
        'P1': percentiles[0],
        'P5': percentiles[1],
        'P10': percentiles[2],
        'P25': percentiles[3],
        'P50': percentiles[4],
        'P75': percentiles[5],
        'P90': percentiles[6],
        'P95': percentiles[7],
        'P99': percentiles[8],
    })

    if (p_idx + 1) % 100 == 0:
        print(f"  {p_idx + 1}/{N_PORTFOLIOS}")

# Add standard portfolios
standard_configs = {
    'Conservative': {'US Eq': 0.12, 'Intl': 0.08, 'EM': 0.05, 'Bonds': 0.55, 'RE': 0.20},
    'Balanced': {'US Eq': 0.25, 'Intl': 0.15, 'EM': 0.10, 'Bonds': 0.30, 'RE': 0.20},
    'Aggressive': {'US Eq': 0.40, 'Intl': 0.20, 'EM': 0.20, 'Bonds': 0.10, 'RE': 0.10},
}

for name, w_dict in standard_configs.items():
    w = np.array([w_dict[a] for a in assets])

    cumulative_returns = np.ones(N_SIMS)
    for day in range(N_DAYS):
        Z = np.random.standard_normal((N_SIMS, len(assets)))
        corr_returns = Z @ L.T
        daily_asset_returns = daily_returns[:, None] + daily_vols[:, None] * corr_returns.T
        daily_port_return = np.sum(w[:, None] * daily_asset_returns, axis=0)
        cumulative_returns *= (1 + daily_port_return)

    final_returns = cumulative_returns - 1

    var_95_5yr = np.percentile(final_returns, 5)
    var_95_annual = (1 + var_95_5yr) ** (1 / N_YEARS) - 1
    prob_exceed_target = np.mean(final_returns > RETURN_TARGET)

    port_return = np.sum(w * returns)
    port_cov = w @ (np.diag(vols) @ corr @ np.diag(vols)) @ w
    port_vol = np.sqrt(port_cov)

    percentiles = np.percentile(final_returns, [1, 5, 10, 25, 50, 75, 90, 95, 99])

    portfolios_data.append({
        'Portfolio_ID': name,
        'US_Equity': w[0],
        'International': w[1],
        'Emerging_Markets': w[2],
        'Bonds': w[3],
        'Real_Estate': w[4],
        'Expected_Return_Annual': port_return,
        'Volatility_Annual': port_vol,
        'VaR_95_5Year': var_95_5yr,
        'VaR_95_Annual': var_95_annual,
        'Prob_Exceed_60pct': prob_exceed_target,
        'Mean_Return': np.mean(final_returns),
        'Std_Dev_Return': np.std(final_returns),
        'Min_Return': np.min(final_returns),
        'Max_Return': np.max(final_returns),
        'P1': percentiles[0],
        'P5': percentiles[1],
        'P10': percentiles[2],
        'P25': percentiles[3],
        'P50': percentiles[4],
        'P75': percentiles[5],
        'P90': percentiles[6],
        'P95': percentiles[7],
        'P99': percentiles[8],
    })

    print(f"  {name}")

# Convert to DataFrame
df = pd.DataFrame(portfolios_data)

# Save to CSV
csv_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/frontier_simulation_results.csv'
df.to_csv(csv_file, index=False)
print(f"\n✅ Saved to CSV: frontier_simulation_results.csv")

# Save to proper XLSX using openpyxl
try:
    xlsx_file = '/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/frontier_simulation_results.xlsx'
    df.to_excel(xlsx_file, index=False, engine='openpyxl')
    print(f"✅ Saved to XLSX: frontier_simulation_results.xlsx")
except Exception as e:
    print(f"⚠️  XLSX save failed ({e}), using CSV alternative")

print(f"\n✅ Total portfolios: {len(portfolios_data)}")
print(f"\nSummary Statistics:")
print(f"  VaR 95% Annual - Min: {df['VaR_95_Annual'].min()*100:.2f}%, Max: {df['VaR_95_Annual'].max()*100:.2f}%")
print(f"  Prob(Return > 60%) - Min: {df['Prob_Exceed_60pct'].min()*100:.1f}%, Max: {df['Prob_Exceed_60pct'].max()*100:.1f}%")
print(f"  Expected Annual Return - Min: {df['Expected_Return_Annual'].min()*100:.2f}%, Max: {df['Expected_Return_Annual'].max()*100:.2f}%")
