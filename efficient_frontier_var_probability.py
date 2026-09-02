"""
================================================================================
EFFICIENT FRONTIER IN VaR-PROBABILITY SPACE
================================================================================

INNOVATION: Instead of the traditional efficient frontier in Risk-Return space,
we explore the frontier in Value-at-Risk vs. Cumulative Probability space.

This reveals: For a given VaR budget (downside risk constraint), what's the
maximum probability of achieving positive returns? And how does this frontier
evolve as we vary the portfolio composition?

METHODOLOGY:
1. Generate 1,000+ random portfolio compositions
2. For each portfolio, calculate:
   - Annualized VaR at 95% confidence
   - Cumulative probability metric (average P(Return > threshold) across thresholds)
   - Expected return and volatility
3. Plot all portfolios to reveal the efficient frontier
4. Highlight the 3 standard portfolios (Aggressive, Balanced, Conservative)
"""

import numpy as np
import pandas as pd
import json
from scipy.linalg import cholesky

# Asset class parameters (same as main analysis)
asset_classes = {
    'US Equities': {'return': 0.10, 'vol': 0.18},
    'Intl Developed': {'return': 0.09, 'vol': 0.20},
    'Emerging Markets': {'return': 0.115, 'vol': 0.28},
    'Investment Bonds': {'return': 0.045, 'vol': 0.05},
    'Real Estate': {'return': 0.09, 'vol': 0.16},
}

# Correlation matrix
correlation_matrix = np.array([
    [1.00,  0.78, 0.72, -0.15, 0.65],
    [0.78,  1.00, 0.82, -0.10, 0.60],
    [0.72,  0.82, 1.00,  0.05, 0.55],
    [-0.15, -0.10, 0.05, 1.00, 0.15],
    [0.65,  0.60, 0.55, 0.15, 1.00],
])

asset_list = list(asset_classes.keys())
n_assets = len(asset_list)

print("\n" + "="*80)
print("EFFICIENT FRONTIER: VaR vs CUMULATIVE PROBABILITY")
print("="*80)

# Simulation parameters
n_simulations = 50000
n_years = 5
n_periods = n_years * 252
n_portfolios = 2000  # Number of random portfolios to generate

print(f"\nGenerating {n_portfolios} random portfolios...")
print(f"Monte Carlo simulations per portfolio: {n_simulations} paths")

# Prepare covariance matrix
daily_vols = np.array([asset_classes[asset]['vol'] / np.sqrt(252) for asset in asset_list])
annual_means = np.array([asset_classes[asset]['return'] for asset in asset_list])
daily_means = annual_means / 252

daily_cov_matrix = np.diag(daily_vols) @ correlation_matrix @ np.diag(daily_vols)
L = np.linalg.cholesky(daily_cov_matrix)

# Return thresholds for cumulative probability calculation
return_thresholds = [0.00, 0.05, 0.10, 0.15, 0.20, 0.30]

# Store results
frontier_data = {
    'portfolios': [],
    'portfolio_names': [],
    'colors': [],
}

# Generate random portfolios
np.random.seed(42)

for p in range(n_portfolios):
    # Random weights (normalized)
    weights = np.random.dirichlet(np.ones(n_assets))

    # Calculate portfolio statistics
    portfolio_mean = np.sum(weights * annual_means)
    portfolio_cov = weights @ (np.diag(np.array([asset_classes[asset]['vol'] for asset in asset_list])) @
                                correlation_matrix @
                                np.diag(np.array([asset_classes[asset]['vol'] for asset in asset_list]))) @ weights
    portfolio_vol = np.sqrt(portfolio_cov)

    # Quick run: sample paths for VaR calculation (reduced sample for speed)
    n_sample = 5000  # Smaller sample for frontier generation
    portfolio_log_returns = np.zeros((n_sample, n_periods))

    for t in range(n_periods):
        Z = np.random.standard_normal((n_sample, n_assets))
        correlated_Z = Z @ L.T
        asset_returns = daily_means + daily_vols * correlated_Z
        portfolio_log_returns[:, t] = asset_returns @ weights

    # Calculate cumulative returns
    cumulative_returns = np.exp(np.cumsum(portfolio_log_returns, axis=1))
    final_returns = cumulative_returns[:, -1] - 1
    cumulative_log_returns = np.sum(portfolio_log_returns, axis=1)

    # VaR at 95%
    var_95_5yr = np.percentile(cumulative_log_returns, 5)
    var_95_annual = var_95_5yr / np.sqrt(n_years)

    # Calculate cumulative probability (average probability across all thresholds)
    probabilities = []
    for threshold in return_thresholds:
        prob = np.mean(final_returns > threshold)
        probabilities.append(prob)

    # Cumulative probability metric (average probability across thresholds)
    # This represents: "How likely is this portfolio to beat various targets?"
    avg_probability = np.mean(probabilities)

    # Assign color based on probability (gradient from red to green)
    if avg_probability < 0.75:
        color = '#d32f2f'  # Red
    elif avg_probability < 0.80:
        color = '#f57c00'  # Orange
    elif avg_probability < 0.85:
        color = '#fbc02d'  # Yellow
    elif avg_probability < 0.90:
        color = '#7cb342'  # Light green
    else:
        color = '#388e3c'  # Dark green

    frontier_data['portfolios'].append({
        'var_95_annual': float(var_95_annual * 100),
        'avg_probability': float(avg_probability * 100),
        'expected_return': float(portfolio_mean * 100),
        'volatility': float(portfolio_vol * 100),
        'weights': {asset: float(w) for asset, w in zip(asset_list, weights)},
        'prob_by_threshold': {str(t): float(p) for t, p in zip(return_thresholds, probabilities)},
    })
    frontier_data['colors'].append(color)

    if (p + 1) % 250 == 0:
        print(f"  Generated {p + 1}/{n_portfolios} portfolios")

print(f"\n✓ Generated {n_portfolios} portfolios")

# Add the 3 standard portfolios with special markers
standard_portfolios = {
    'Aggressive (80% Stocks)': {
        'US Equities': 0.40,
        'Intl Developed': 0.20,
        'Emerging Markets': 0.20,
        'Investment Bonds': 0.10,
        'Real Estate': 0.10,
        'marker': 'aggressive'
    },
    'Balanced (60% Stocks)': {
        'US Equities': 0.25,
        'Intl Developed': 0.15,
        'Emerging Markets': 0.10,
        'Investment Bonds': 0.30,
        'Real Estate': 0.20,
        'marker': 'balanced'
    },
    'Conservative (40% Stocks)': {
        'US Equities': 0.12,
        'Intl Developed': 0.08,
        'Emerging Markets': 0.05,
        'Investment Bonds': 0.50,
        'Real Estate': 0.25,
        'marker': 'conservative'
    }
}

print("\nCalculating standard portfolios statistics...")

for portfolio_name, weights_dict in standard_portfolios.items():
    weights = np.array([weights_dict[asset] for asset in asset_list])

    # Full simulation for standard portfolios
    portfolio_log_returns = np.zeros((n_simulations, n_periods))

    for t in range(n_periods):
        Z = np.random.standard_normal((n_simulations, n_assets))
        correlated_Z = Z @ L.T
        asset_returns = daily_means + daily_vols * correlated_Z
        portfolio_log_returns[:, t] = asset_returns @ weights

    cumulative_returns = np.exp(np.cumsum(portfolio_log_returns, axis=1))
    final_returns = cumulative_returns[:, -1] - 1
    cumulative_log_returns = np.sum(portfolio_log_returns, axis=1)

    var_95_5yr = np.percentile(cumulative_log_returns, 5)
    var_95_annual = var_95_5yr / np.sqrt(n_years)

    portfolio_mean = np.sum(weights * annual_means)
    portfolio_cov = weights @ (np.diag(np.array([asset_classes[asset]['vol'] for asset in asset_list])) @
                                correlation_matrix @
                                np.diag(np.array([asset_classes[asset]['vol'] for asset in asset_list]))) @ weights
    portfolio_vol = np.sqrt(portfolio_cov)

    probabilities = []
    for threshold in return_thresholds:
        prob = np.mean(final_returns > threshold)
        probabilities.append(prob)

    avg_probability = np.mean(probabilities)

    frontier_data['portfolios'].append({
        'var_95_annual': float(var_95_annual * 100),
        'avg_probability': float(avg_probability * 100),
        'expected_return': float(portfolio_mean * 100),
        'volatility': float(portfolio_vol * 100),
        'weights': weights_dict,
        'prob_by_threshold': {str(t): float(p) for t, p in zip(return_thresholds, probabilities)},
        'is_standard': True,
        'marker_type': standard_portfolios[portfolio_name]['marker'],
    })

    if 'aggressive' in standard_portfolios[portfolio_name]['marker']:
        frontier_data['colors'].append('#d32f2f')
    elif 'balanced' in standard_portfolios[portfolio_name]['marker']:
        frontier_data['colors'].append('#f57c00')
    else:
        frontier_data['colors'].append('#388e3c')

    frontier_data['portfolio_names'].append(portfolio_name)

    print(f"  {portfolio_name}: VaR={var_95_annual*100:.2f}%, AvgProb={avg_probability*100:.2f}%")

# Save data
output_path = "/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/efficient_frontier_data.json"
with open(output_path, 'w') as f:
    json.dump(frontier_data, f, indent=2)

print(f"\n✓ Efficient frontier data saved to efficient_frontier_data.json")

# Print frontier statistics
print("\n" + "="*80)
print("EFFICIENT FRONTIER STATISTICS")
print("="*80)

frontiers_arr = np.array([p['var_95_annual'] for p in frontier_data['portfolios']])
probs_arr = np.array([p['avg_probability'] for p in frontier_data['portfolios']])
returns_arr = np.array([p['expected_return'] for p in frontier_data['portfolios']])
vols_arr = np.array([p['volatility'] for p in frontier_data['portfolios']])

print(f"\nAnnualized VaR (95%)")
print(f"  Min (Most Conservative): {frontiers_arr.min():.2f}%")
print(f"  Max (Most Aggressive):   {frontiers_arr.max():.2f}%")
print(f"  Median:                  {np.median(frontiers_arr):.2f}%")

print(f"\nAverage Probability (across thresholds)")
print(f"  Min: {probs_arr.min():.2f}%")
print(f"  Max: {probs_arr.max():.2f}%")
print(f"  Median: {np.median(probs_arr):.2f}%")

print(f"\nExpected Annual Returns")
print(f"  Min: {returns_arr.min():.2f}%")
print(f"  Max: {returns_arr.max():.2f}%")
print(f"  Median: {np.median(returns_arr):.2f}%")

print(f"\nPortfolio Volatility")
print(f"  Min: {vols_arr.min():.2f}%")
print(f"  Max: {vols_arr.max():.2f}%")
print(f"  Median: {np.median(vols_arr):.2f}%")

# Find efficient frontier (Pareto optimal points)
print("\n" + "="*80)
print("EFFICIENT FRONTIER (Pareto Optimal Portfolios)")
print("="*80)

# For each VaR level, find the portfolio with highest probability
var_levels = np.percentile(frontiers_arr, np.linspace(0, 100, 11))
print(f"\nTop performers at each VaR level:")
print(f"{'VaR (95%)':>12} | {'Avg Probability':>18} | {'Annual Return':>15} | {'Volatility':>12}")
print("-" * 65)

for var_level in var_levels:
    mask = np.abs(frontiers_arr - var_level) < 0.3  # Within 0.3% of target
    if np.sum(mask) > 0:
        best_idx = np.argmax(probs_arr[mask])
        best_portfolio = frontier_data['portfolios'][np.where(mask)[0][best_idx]]
        print(f"{best_portfolio['var_95_annual']:>11.2f}% | {best_portfolio['avg_probability']:>17.2f}% | {best_portfolio['expected_return']:>14.2f}% | {best_portfolio['volatility']:>11.2f}%")

print("\n" + "="*80)
print("✅ FRONTIER ANALYSIS COMPLETE")
print("="*80)
print("\nThe efficient frontier shows the Pareto optimal trade-off between:")
print("  • Annualized VaR (95%): Downside risk constraint")
print("  • Cumulative Probability: Average likelihood of beating return thresholds")
print("\nKey insight: Higher VaR (less negative = less downside risk) enables")
print("higher cumulative probabilities, but with potential return sacrifice.")
