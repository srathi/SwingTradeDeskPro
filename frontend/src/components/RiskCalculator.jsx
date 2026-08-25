import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Calculator, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  DollarSign, 
  Percent, 
  Target,
  Sparkles
} from 'lucide-react';
import { calculateRisk } from '../services/api';

export default function RiskCalculator({ prefillSetup = null }) {
  const [capital, setCapital] = useState(500000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [entryPrice, setEntryPrice] = useState(1300);
  const [stopLoss, setStopLoss] = useState(1260);
  const [customTarget, setCustomTarget] = useState(1380);
  const [maxAllocationPct, setMaxAllocationPct] = useState(25.0);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (prefillSetup) {
      if (prefillSetup.close) setEntryPrice(prefillSetup.close);
      if (prefillSetup.stop_loss) setStopLoss(prefillSetup.stop_loss);
      if (prefillSetup.target_1) setCustomTarget(prefillSetup.target_1);
    }
  }, [prefillSetup]);

  useEffect(() => {
    handleCalculate();
  }, [capital, riskPct, entryPrice, stopLoss, customTarget, maxAllocationPct]);

  const handleCalculate = async () => {
    if (entryPrice <= 0 || stopLoss <= 0 || capital <= 0) return;
    setLoading(true);
    try {
      const res = await calculateRisk({
        capital: Number(capital),
        risk_pct: Number(riskPct),
        entry_price: Number(entryPrice),
        stop_loss: Number(stopLoss),
        target_price: customTarget ? Number(customTarget) : null,
        max_portfolio_allocation_pct: Number(maxAllocationPct)
      });
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-900 via-[#131b2e] to-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl">
        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold uppercase tracking-wider border border-amber-500/20 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" /> Capital Preservation
          </span>
        </div>
        <h1 className="text-xl font-bold text-white mt-1.5">Institutional Position & Risk Sizer</h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Eliminates guesswork by computing mathematically exact share quantities to ensure you never risk more than your predefined portfolio risk budget.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Input Controls */}
        <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2 border-b border-gray-800 pb-3">
            <Calculator className="w-4 h-4 text-cyan-400" />
            <span>Trade & Portfolio Inputs</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-gray-400 block mb-1">Total Account Capital (₹)</label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(e.target.value)}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-gray-400 mb-1">
                <span>Risk Per Trade:</span>
                <span className="font-mono text-cyan-400 font-bold">{riskPct}% (₹{((capital * riskPct) / 100).toLocaleString()})</span>
              </div>
              <input
                type="range"
                min="0.25"
                max="3.0"
                step="0.25"
                value={riskPct}
                onChange={(e) => setRiskPct(e.target.value)}
                className="w-full accent-cyan-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div>
                <label className="text-gray-400 block mb-1">Entry Price (₹)</label>
                <input
                  type="number"
                  step="0.05"
                  value={entryPrice}
                  onChange={(e) => setEntryPrice(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Stop Loss Price (₹)</label>
                <input
                  type="number"
                  step="0.05"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-red-400 font-mono focus:outline-none focus:border-red-500"
                />
              </div>
            </div>

            <div>
              <label className="text-gray-400 block mb-1">Custom Target Price (₹) [Optional]</label>
              <input
                type="number"
                step="0.05"
                value={customTarget}
                onChange={(e) => setCustomTarget(e.target.value)}
                placeholder="Defaults to 1:2 R:R"
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-emerald-400 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-gray-400 mb-1">
                <span>Max Single Stock Exposure:</span>
                <span className="font-mono text-cyan-400 font-bold">{maxAllocationPct}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                step="5"
                value={maxAllocationPct}
                onChange={(e) => setMaxAllocationPct(e.target.value)}
                className="w-full accent-cyan-500"
              />
            </div>
          </div>

        </div>

        {/* Calculated Results Card */}
        <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2 border-b border-gray-800 pb-3">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Recommended Execution Sizing</span>
            </h2>

            {result && !result.error ? (
              <div className="space-y-4 pt-3">
                
                {/* Highlight Share Quantity */}
                <div className="bg-gradient-to-tr from-cyan-950/40 to-gray-950 p-4 rounded-xl border border-cyan-500/30 text-center">
                  <span className="text-xs uppercase font-bold text-gray-400 tracking-wider">Recommended Order Quantity</span>
                  <div className="text-3xl font-black text-white font-mono my-1">
                    {result.shares} <span className="text-sm text-cyan-400 font-medium">Shares</span>
                  </div>
                  <span className="text-xs text-gray-400 font-mono">
                    Total Outlay: ₹{result.capital_required.toLocaleString()} ({result.portfolio_allocation_pct}% of capital)
                  </span>
                </div>

                {/* Sizing Breakdown Table */}
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400 font-sans">Risk / Share</span>
                    <span className="text-red-400 font-semibold">₹{result.risk_per_share}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400 font-sans">Total Monetary Risk</span>
                    <span className="text-red-400 font-bold">₹{result.total_risk_amount.toLocaleString()} ({result.total_risk_pct}%)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400 font-sans">Risk-to-Reward (R:R)</span>
                    <span className="text-emerald-400 font-bold">{result.risk_reward_ratio}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400 font-sans">Profit at Target 1 (2R - ₹{result.target_1_2R})</span>
                    <span className="text-emerald-400 font-bold">+₹{result.potential_profit_target_1.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400 font-sans">Profit at Target 2 (3R - ₹{result.target_2_3R})</span>
                    <span className="text-emerald-300 font-bold">+₹{result.potential_profit_target_2.toLocaleString()}</span>
                  </div>
                </div>

                {/* Allocation Warnings */}
                {result.warnings && result.warnings.length > 0 && (
                  <div className="p-3 bg-amber-950/40 border border-amber-800/80 rounded-xl text-amber-300 text-xs flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-400" />
                    <span>{result.warnings[0]}</span>
                  </div>
                )}

              </div>
            ) : (
              <div className="p-8 text-center text-xs text-gray-500">
                {result?.error || "Enter valid price parameters to compute sizing."}
              </div>
            )}
          </div>

          <div className="text-[11px] text-gray-500 bg-gray-950 p-3 rounded-xl border border-gray-800/80">
            <strong className="text-gray-400">Golden Rule:</strong> Never risk more than 1% to 2% of total account equity on any single swing trade setup.
          </div>

        </div>

      </div>

    </div>
  );
}
