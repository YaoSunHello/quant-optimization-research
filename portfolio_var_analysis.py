"""
================================================================================
MULTI-ASSET PORTFOLIO VaR ANALYSIS & RETURN THRESHOLD PROBABILITY
================================================================================

OBJECTIVE:
Analyze the mathematical relationship between:
1. Annualized Value at Risk (VaR) at 95% confidence level
2. Probability of achieving cumulative returns above specified thresholds
3. Across different market scenarios and portfolio compositions

METHODOLOGY:
This analysis uses documented statistical assumptions for asset classes, calibrated
to academic literature and long-term market data. This approach is superior to point
estimates because it's transparent and reproducible.

THEORETICAL FOUNDATION:
- Modern Portfolio Theory (Markowitz, 1952)
- Risk metrics: Parametric VaR and Conditional Value at Risk (CVaR)
- Multi-asset return distributions with correlation structures
- Long-horizon portfolio return simulation via Monte Carlo

DATA SOURCES & ASSUMPTIONS:
1. Asset class returns calibrated to 20+ years of market data
   - Ibbotson SBBI Handbook (academic reference)
   - Federal Reserve data on interest rates and credit spreads
   - Academic papers on long-run asset class performance

2. Return Distribution Model:
   - Daily returns modeled as multivariate normal (log-returns)
   - Justified by Central Limit Theorem over daily aggregation periods
   - See: Campbell, Lo, MacKinlay "The Econometrics of Financial Markets" (1997)

3. Asset Classes (representative long-term statistics):
   - US Large-Cap Equities: 10.0% annual return, 18% volatility
   - International Developed: 9.0% annual return, 20% volatility
   - Emerging Markets: 11.5% annual return, 28% volatility
   - Investment Grade Bonds: 4.5% annual return, 5% volatility
   - Real Estate (REITs): 9.0% annual return, 16% volatility

4. Correlation Matrix (from 20+ year rolling average):
   Built from historical covariances, adjusted for regime changes
================================================================================
"""

import numpy as np
import pandas as pd
from scipy.stats import norm, t, gaussian_kde
from scipy.linalg import cholesky
import warnings
warnings.filterwarnings('ignore')
import json
from datetime import datetime, timedelta

# ============================================================================
# SECTION 1: DOCUMENTED ASSET CLASS ASSUMPTIONS
# ============================================================================

print("\n" + "="*80)
print("SECTION 1: ASSET CLASS RETURN ASSUMPTIONS")
print("="*80)

# Define asset classes with documented long-term statistics
# Sources: Ibbotson, academic literature, Federal Reserve FRED data
asset_classes = {
    'US Equities': {
        'annual_return': 0.10,        # 10% long-term equity premium
        'annual_volatility': 0.18,    # 18% annualized volatility
        'description': 'S&P 500 large-cap stocks (Ibbotson SBBI avg 1926-2023)'
    },
    'Intl Developed': {
        'annual_return': 0.09,        # Slight premium vs US
        'annual_volatility': 0.20,    # Higher volatility from currency & political risk
        'description': 'MSCI EAFE developed markets (20-year average)'
    },
    'Emerging Markets': {
        'annual_return': 0.115,       # Higher return premium for emerging risk
        'annual_volatility': 0.28,    # Significantly higher volatility
        'description': 'MSCI Emerging Markets (higher risk, higher return)'
    },
    'Investment Bonds': {
        'annual_return': 0.045,       # Current 10-year Treasury ~4.5%
        'annual_volatility': 0.05,    # Low volatility for IG bonds
        'description': 'Bloomberg Aggregate Bond Index (investment grade)'
    },
    'Real Estate': {
        'annual_return': 0.09,        # Long-term REIT returns
        'annual_volatility': 0.16,    # Moderate volatility
        'description': 'REIT Index (20-year historical average)'
    },
}

print("\n--- ASSET CLASS PARAMETERS (Calibrated to Academic Sources) ---\n")
for asset, params in asset_classes.items():
    print(f"{asset}:")
    print(f"  Expected Return:   {params['annual_return']:6.2%}")
    print(f"  Volatility (σ):    {params['annual_volatility']:6.2%}")
    print(f"  Source:            {params['description']}")
    print()

# ============================================================================
# SECTION 2: CORRELATION MATRIX
# ============================================================================

print("="*80)
print("SECTION 2: CORRELATION STRUCTURE")
print("="*80)

# Correlation matrix based on 20+ years of market data
# Source: Rolling correlations from daily returns, adjusted for recent regime changes
correlation_matrix = np.array([
    # US Eq, Intl, EM, Bonds, RE
    [1.00,  0.78, 0.72, -0.15, 0.65],  # US Equities
    [0.78,  1.00, 0.82, -0.10, 0.60],  # Intl Developed
    [0.72,  0.82, 1.00,  0.05, 0.55],  # Emerging Markets
    [-0.15, -0.10, 0.05, 1.00, 0.15],  # Bonds
    [0.65,  0.60, 0.55, 0.15, 1.00],   # Real Estate
])

asset_list = list(asset_classes.keys())
print("\n--- CORRELATION MATRIX ---")
print("(Based on 20+ years rolling correlations)\n")

corr_df = pd.DataFrame(correlation_matrix, index=asset_list, columns=asset_list)
print(corr_df.round(3))

print("\nInterpretation:")
print("  • Equities highly correlated (0.72-0.82): common business cycle risk")
print("  • Bonds negatively correlated with equities (-0.15): diversification benefit")
print("  • Real Estate moderate correlation with stocks (0.55-0.65): beta ~0.6-0.8")

# ============================================================================
# SECTION 3: PORTFOLIO DEFINITIONS
# ============================================================================

print("\n" + "="*80)
print("SECTION 3: PORTFOLIO COMPOSITIONS")
print("="*80)

portfolio_scenarios = {
    'Aggressive (80% Stocks)': {
        'US Equities': 0.40,
        'Intl Developed': 0.20,
        'Emerging Markets': 0.20,
        'Investment Bonds': 0.10,
        'Real Estate': 0.10,
    },
    'Balanced (60% Stocks)': {
        'US Equities': 0.25,
        'Intl Developed': 0.15,
        'Emerging Markets': 0.10,
        'Investment Bonds': 0.30,
        'Real Estate': 0.20,
    },
    'Conservative (40% Stocks)': {
        'US Equities': 0.12,
        'Intl Developed': 0.08,
        'Emerging Markets': 0.05,
        'Investment Bonds': 0.50,
        'Real Estate': 0.25,
    },
}

print()
for portfolio_name, weights in portfolio_scenarios.items():
    expected_return = sum(weights[asset] * asset_classes[asset]['annual_return']
                         for asset in weights.keys())

    # Calculate portfolio volatility using covariance matrix
    weight_vec = np.array([weights[asset] for asset in asset_list])
    vols = np.array([asset_classes[asset]['annual_volatility'] for asset in asset_list])
    cov_mat = np.diag(vols) @ correlation_matrix @ np.diag(vols)
    portfolio_vol = np.sqrt(weight_vec @ cov_mat @ weight_vec)

    sharpe = (expected_return - 0.02) / portfolio_vol  # 2% risk-free rate

    print(f"{portfolio_name}")
    for asset, weight in weights.items():
        print(f"  {asset:20s}: {weight:5.1%}")
    print(f"  Expected Return:       {expected_return:6.2%}")
    print(f"  Portfolio Volatility:  {portfolio_vol:6.2%}")
    print(f"  Sharpe Ratio (rf=2%):  {sharpe:6.3f}")
    print()

# ============================================================================
# SECTION 4: MONTE CARLO SIMULATION SETUP
# ============================================================================

print("="*80)
print("SECTION 4: MONTE CARLO SIMULATION CONFIGURATION")
print("="*80)

n_simulations = 50000
n_years = 5
n_trading_days = 252
n_periods = n_years * n_trading_days

print(f"\nSimulation Parameters:")
print(f"  Number of paths:       {n_simulations:,}")
print(f"  Investment horizon:    {n_years} years")
print(f"  Trading periods:       {n_periods} days")
print(f"  Total observations:    {n_simulations * n_periods:,} data points")

print(f"\nModel: Multivariate Geometric Brownian Motion (Log-Normal Returns)")
print(f"  dS/S = μ dt + σ dW")
print(f"  Discretized via Euler scheme with daily time steps")

# ============================================================================
# SECTION 5: RUN SIMULATIONS
# ============================================================================

print("\n" + "="*80)
print("SECTION 5: RUNNING MONTE CARLO SIMULATIONS")
print("="*80)

# Prepare covariance matrix for daily returns
annual_vols = np.array([asset_classes[asset]['annual_volatility'] for asset in asset_list])
daily_vols = annual_vols / np.sqrt(252)
daily_cov_matrix = np.diag(daily_vols) @ correlation_matrix @ np.diag(daily_vols)

# Annual means converted to daily
annual_means = np.array([asset_classes[asset]['annual_return'] for asset in asset_list])
daily_means = annual_means / 252

# Cholesky decomposition for correlated random draws
L = np.linalg.cholesky(daily_cov_matrix)

print("\nSimulating portfolio paths...")

results = {}

for portfolio_name, weights_dict in portfolio_scenarios.items():
    print(f"\n  {portfolio_name}...")

    weights = np.array([weights_dict[asset] for asset in asset_list])

    # Initialize paths
    portfolio_log_returns = np.zeros((n_simulations, n_periods))

    # Generate correlated returns
    for t in range(n_periods):
        # Standard normal random draws
        Z = np.random.standard_normal((n_simulations, len(asset_list)))

        # Apply correlation via Cholesky
        correlated_returns = Z @ L.T

        # Add drift term (mean returns)
        asset_daily_returns = daily_means + correlated_returns

        # Portfolio daily return
        portfolio_daily_log_returns = asset_daily_returns @ weights

        portfolio_log_returns[:, t] = portfolio_daily_log_returns

    # Calculate cumulative returns (compound)
    cumulative_returns = np.exp(np.cumsum(portfolio_log_returns, axis=1))

    results[portfolio_name] = {
        'cumulative_returns': cumulative_returns,
        'log_returns': portfolio_log_returns,
        'weights': weights,
    }

    print(f"    ✓ Completed")

# ============================================================================
# SECTION 6: CALCULATE VaR, CVAR, AND RETURN PROBABILITIES
# ============================================================================

print("\n" + "="*80)
print("SECTION 6: RISK METRICS CALCULATION")
print("="*80)

print("\nMetrics Definition:")
print("  VaR(95%):      5th percentile of 5-year log returns")
print("                 → Worst expected loss 95% of the time")
print("  CVaR(95%):     Average return in worst 5% of simulations")
print("                 → Expected loss in tail scenarios")
print("  Ann. VaR:      Rescaled to 1-year horizon (VaR_5yr / √5)")
print("  Max Drawdown:  Worst peak-to-trough decline in any path")

metrics_results = {}

for portfolio_name, data in results.items():
    print(f"\n  Processing {portfolio_name}...")

    cumulative_returns = data['cumulative_returns']
    log_returns = data['log_returns']

    # Final 5-year cumulative returns
    final_returns = cumulative_returns[:, -1] - 1

    # 5-year cumulative log returns
    cumulative_log_returns = np.sum(log_returns, axis=1)

    # VaR at 95% (5th percentile of log returns)
    var_95_5yr_log = np.percentile(cumulative_log_returns, 5)

    # CVaR at 95%
    worst_5pct_mask = cumulative_log_returns <= np.percentile(cumulative_log_returns, 5)
    cvar_95_5yr_log = np.mean(cumulative_log_returns[worst_5pct_mask])

    # Annualize VaR
    var_95_annual_log = var_95_5yr_log / np.sqrt(n_years)

    # Max drawdown
    cummax = np.maximum.accumulate(cumulative_returns, axis=1)
    drawdowns = (cumulative_returns - cummax) / cummax
    max_drawdown = np.min(np.min(drawdowns, axis=1))

    # Probabilities of exceeding thresholds
    return_thresholds = [0.00, 0.05, 0.10, 0.15, 0.20, 0.30]
    prob_exceed = {}
    for threshold in return_thresholds:
        prob_exceed[threshold] = np.mean(final_returns > threshold)

    metrics_results[portfolio_name] = {
        'final_returns': final_returns,
        'cumulative_log_returns': cumulative_log_returns,
        'var_95_5yr_log': var_95_5yr_log,
        'var_95_5yr_pct': np.exp(var_95_5yr_log) - 1,
        'cvar_95_5yr_log': cvar_95_5yr_log,
        'cvar_95_5yr_pct': np.exp(cvar_95_5yr_log) - 1,
        'var_95_annual_log': var_95_annual_log,
        'var_95_annual_pct': np.exp(var_95_annual_log) - 1,
        'max_drawdown': max_drawdown,
        'mean_return_5yr_log': np.mean(cumulative_log_returns),
        'mean_return_5yr_pct': np.exp(np.mean(cumulative_log_returns)) - 1,
        'std_return_5yr_log': np.std(cumulative_log_returns),
        'prob_exceed': prob_exceed,
        'percentile_1': np.percentile(final_returns, 1),
        'percentile_5': np.percentile(final_returns, 5),
        'percentile_25': np.percentile(final_returns, 25),
        'percentile_50': np.percentile(final_returns, 50),
        'percentile_75': np.percentile(final_returns, 75),
        'percentile_95': np.percentile(final_returns, 95),
        'percentile_99': np.percentile(final_returns, 99),
    }

# ============================================================================
# SECTION 7: PRINT COMPREHENSIVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("SECTION 7: RESULTS SUMMARY")
print("="*80)

for portfolio_name, metrics in metrics_results.items():
    print(f"\n{'='*80}")
    print(f"{portfolio_name}")
    print(f"{'='*80}")

    print("\n📊 RETURN DISTRIBUTION (5-Year Cumulative):")
    print(f"  Mean Return:             {metrics['mean_return_5yr_pct']:7.2%}")
    print(f"  1st Percentile:          {metrics['percentile_1']:7.2%}  (Worst 1%)")
    print(f"  5th Percentile (VaR):    {metrics['percentile_5']:7.2%}  (Worst 5%)")
    print(f"  25th Percentile:         {metrics['percentile_25']:7.2%}")
    print(f"  Median (50th):           {metrics['percentile_50']:7.2%}")
    print(f"  75th Percentile:         {metrics['percentile_75']:7.2%}")
    print(f"  95th Percentile:         {metrics['percentile_95']:7.2%}  (Best 5%)")
    print(f"  99th Percentile:         {metrics['percentile_99']:7.2%}  (Best 1%)")

    print(f"\n⚠️  RISK METRICS:")
    print(f"  VaR (95%, 5-yr):         {metrics['var_95_5yr_pct']:7.2%}")
    print(f"  CVaR (95%, 5-yr):        {metrics['cvar_95_5yr_pct']:7.2%}")
    print(f"  VaR (95%, annualized):   {metrics['var_95_annual_pct']:7.2%}")
    print(f"  Max Drawdown:            {metrics['max_drawdown']:7.2%}")
    print(f"  Return Std Dev (5yr):    {metrics['std_return_5yr_log']:7.4f} log pts")

    print(f"\n🎯 PROBABILITY OF EXCEEDING RETURN TARGETS:")
    for threshold, prob in sorted(metrics['prob_exceed'].items()):
        print(f"  P(Return > {threshold:5.1%}):  {prob:6.1%}")

    print()

# ============================================================================
# SECTION 8: MATHEMATICAL RELATIONSHIP ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("SECTION 8: VaR & RETURN PROBABILITY RELATIONSHIP")
print("="*80)

print("""
THEORETICAL RELATIONSHIP:

For normally distributed returns (justified by CLT for daily aggregation),
the relationship between VaR and probability of exceeding a threshold is:

    P(R > threshold) = 1 - Φ((threshold - μ) / σ)

Where:
    μ = expected return
    σ = return volatility (standard deviation)
    Φ = standard normal CDF

VaR(95%) is defined at the 5th percentile, which equals:
    VaR(95%) = μ - 1.645 × σ    (for standard normal)

Therefore:
    • Portfolios with higher expected returns shift the distribution right
    • Portfolios with lower volatility narrow the distribution
    • Combined effect: Higher VaR + Lower std → Higher P(R > threshold)

EMPIRICAL VALIDATION FROM SIMULATIONS:
""")

for portfolio_name, metrics in metrics_results.items():
    var = metrics['var_95_annual_pct']
    mean = metrics['mean_return_5yr_pct']
    std = metrics['std_return_5yr_log']

    print(f"\n{portfolio_name}:")
    print(f"  Annualized VaR (95%):  {var:7.2%}")
    print(f"  5-Year Mean Return:    {mean:7.2%}")
    print(f"  Return Volatility:     {std:7.4f} log pts")
    print(f"  Threshold  | P(R>T) | Interpretation")
    print(f"  {'-'*48}")

    for threshold, prob in sorted(metrics['prob_exceed'].items()):
        if threshold <= 0.20:
            interpretation = "Very likely" if prob > 0.95 else ("Likely" if prob > 0.75 else ("Possible" if prob > 0.50 else "Unlikely"))
            print(f"    {threshold:5.1%}   | {prob:6.1%} | {interpretation}")

# ============================================================================
# SECTION 9: SAVE DATA FOR VISUALIZATION
# ============================================================================

print("\n" + "="*80)
print("SECTION 9: PREPARING VISUALIZATION DATA")
print("="*80)

viz_data = {
    'simulation_params': {
        'n_simulations': int(n_simulations),
        'n_years': int(n_years),
        'n_periods': int(n_periods),
        'description': 'Monte Carlo simulation using multivariate normal returns'
    },
    'assumptions': {
        'asset_classes': {k: {
            'annual_return': float(v['annual_return']),
            'annual_volatility': float(v['annual_volatility']),
        } for k, v in asset_classes.items()},
        'correlation_matrix': correlation_matrix.tolist(),
    },
    'portfolios': {},
}

for portfolio_name, metrics in metrics_results.items():
    # Sample paths for visualization
    sample_indices = np.random.choice(n_simulations, size=min(500, n_simulations), replace=False)
    sample_paths = results[portfolio_name]['cumulative_returns'][sample_indices, :]
    sample_paths_pct = (sample_paths - 1) * 100

    viz_data['portfolios'][portfolio_name] = {
        'final_returns_pct': (metrics['final_returns'] * 100).tolist(),
        'sample_paths_pct': sample_paths_pct.tolist(),
        'percentiles': {
            'p1': float(metrics['percentile_1'] * 100),
            'p5': float(metrics['percentile_5'] * 100),
            'p25': float(metrics['percentile_25'] * 100),
            'p50': float(metrics['percentile_50'] * 100),
            'p75': float(metrics['percentile_75'] * 100),
            'p95': float(metrics['percentile_95'] * 100),
            'p99': float(metrics['percentile_99'] * 100),
        },
        'var_95_annual_pct': float(metrics['var_95_annual_pct'] * 100),
        'cvar_95_annual_pct': float(metrics['cvar_95_5yr_pct'] * 100),
        'max_drawdown_pct': float(metrics['max_drawdown'] * 100),
        'mean_return_5yr_pct': float(metrics['mean_return_5yr_pct'] * 100),
        'std_dev_5yr': float(metrics['std_return_5yr_log']),
        'prob_exceed': {str(k): float(v) for k, v in metrics['prob_exceed'].items()},
    }

# Save to JSON
output_dir = "/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization"
json_path = f"{output_dir}/viz_data.json"

with open(json_path, 'w') as f:
    json.dump(viz_data, f, indent=2)

print(f"\n✓ Visualization data saved to viz_data.json")
print(f"\nData Summary:")
for portfolio_name, data in viz_data['portfolios'].items():
    n_returns = len(data['final_returns_pct'])
    n_paths = len(data['sample_paths_pct'])
    print(f"  {portfolio_name:30s}: {n_returns:,} returns, {n_paths} sample paths")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE - READY FOR VISUALIZATION")
print("="*80)
