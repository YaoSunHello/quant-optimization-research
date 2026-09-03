"""
Efficient Frontier: VaR vs P(5-year cumulative return > 80%)
Optimized version with reduced portfolio/simulation counts for faster execution
"""
import numpy as np
import json

print("\n" + "="*70)
print("EFFICIENT FRONTIER: VaR vs P(5-Year Return > 80%)")
print("="*70)

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

# Simulation parameters - optimized for speed
N_PORTFOLIOS = 1000
N_SIMS = 3000
N_YEARS = 5
N_DAYS = N_YEARS * 252
RETURN_TARGET = 0.80  # 80% 5-year cumulative return

print(f"\nSimulation Parameters:")
print(f"  Portfolios: {N_PORTFOLIOS}")
print(f"  Simulations per portfolio: {N_SIMS}")
print(f"  Horizon: {N_YEARS} years")
print(f"  Return Target: {RETURN_TARGET*100:.0f}% cumulative return")

daily_returns = returns / 252
daily_vols = vols / np.sqrt(252)
cov_matrix = np.diag(daily_vols) @ corr @ np.diag(daily_vols)
L = np.linalg.cholesky(cov_matrix)

portfolios = []
colors = []

print(f"\nGenerating {N_PORTFOLIOS} portfolios...\n")

for p_idx in range(N_PORTFOLIOS):
    w = np.random.dirichlet(np.ones(len(assets)))

    port_return = np.sum(w * returns)
    port_cov = w @ (np.diag(vols) @ corr @ np.diag(vols)) @ w
    port_vol = np.sqrt(port_cov)

    # Simulate 5-year returns - vectorized approach
    cumulative_returns = np.ones(N_SIMS)
    for day in range(N_DAYS):
        Z = np.random.standard_normal((N_SIMS, len(assets)))
        corr_returns = Z @ L.T
        daily_asset_returns = daily_returns[:, None] + daily_vols[:, None] * corr_returns.T
        daily_port_return = np.sum(w[:, None] * daily_asset_returns, axis=0)
        cumulative_returns *= (1 + daily_port_return)

    final_returns = cumulative_returns - 1  # Convert to return percentage

    # VaR at 95% (5th percentile of returns)
    var_95_5yr = np.percentile(final_returns, 5)
    var_95_annual = var_95_5yr / np.sqrt(N_YEARS)

    # Probability of beating return target (80%)
    prob_exceed_target = np.mean(final_returns > RETURN_TARGET)

    # Color by probability
    if prob_exceed_target < 0.30:
        color = '#d32f2f'  # Red
    elif prob_exceed_target < 0.40:
        color = '#f57c00'  # Orange
    elif prob_exceed_target < 0.50:
        color = '#fbc02d'  # Yellow
    elif prob_exceed_target < 0.60:
        color = '#7cb342'  # Light green
    else:
        color = '#388e3c'  # Dark green

    portfolios.append({
        'var_95_annual': var_95_annual,
        'var_95_5yr': var_95_5yr,
        'prob_exceed_target': prob_exceed_target,
        'expected_return': port_return * 100,
        'volatility': port_vol * 100,
        'weights': {a: float(wt) for a, wt in zip(assets, w)},
    })
    colors.append(color)

    if (p_idx + 1) % 200 == 0:
        print(f"  {p_idx + 1}/{N_PORTFOLIOS}")

# Add standard portfolios
print(f"\nCalculating standard portfolios...")

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
    var_95_annual = var_95_5yr / np.sqrt(N_YEARS)
    prob_exceed_target = np.mean(final_returns > RETURN_TARGET)

    port_return = np.sum(w * returns)
    port_cov = w @ (np.diag(vols) @ corr @ np.diag(vols)) @ w
    port_vol = np.sqrt(port_cov)

    portfolios.append({
        'var_95_annual': var_95_annual,
        'var_95_5yr': var_95_5yr,
        'prob_exceed_target': prob_exceed_target,
        'expected_return': port_return * 100,
        'volatility': port_vol * 100,
        'weights': {a: w_dict.get(a, 0) for a in assets},
        'is_standard': True,
        'marker_type': name.lower(),
    })

    marker_colors = {'conservative': '#388e3c', 'balanced': '#f57c00', 'aggressive': '#d32f2f'}
    colors.append(marker_colors[name.lower()])

    print(f"  {name}: VaR={var_95_annual*100:6.2f}%, P(return > 80%) = {prob_exceed_target*100:5.1f}%")

# Filter portfolios: keep only those with 50% < probability < 99%
filtered_portfolios = []
filtered_colors = []
for p, c in zip(portfolios, colors):
    if 0.50 < p['prob_exceed_target'] < 0.99:
        filtered_portfolios.append(p)
        filtered_colors.append(c)

# Save
data = {'portfolios': filtered_portfolios, 'colors': filtered_colors, 'return_target': RETURN_TARGET}

with open('/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/efficient_frontier_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Saved {len(filtered_portfolios)} portfolios (filtered to 50% < P < 99%)")

if len(filtered_portfolios) > 0:
    vars_95 = np.array([p['var_95_annual'] for p in filtered_portfolios])
    probs = np.array([p['prob_exceed_target'] for p in filtered_portfolios])

    print(f"\nFiltered Frontier Statistics:")
    print(f"  VaR (annualized) range: {vars_95.min()*100:.2f}% to {vars_95.max()*100:.2f}%")
    print(f"  P(return > 80%) range: {probs.min()*100:.1f}% to {probs.max()*100:.1f}%")
    print(f"\n  Insight: Portfolios with higher VaR (less negative)")
    print(f"           tend to have higher probability of beating 80% target")
else:
    print(f"\n⚠️  No portfolios found in the 50%-99% probability range")
