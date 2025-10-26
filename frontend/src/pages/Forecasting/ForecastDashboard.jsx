import React, { useState, useEffect } from 'react';
import { Card } from '@/components/common/card';
import { Button } from '@/components/common/button';
import ForecastChart from '../../components/charts/ForecastChart';
import api from '../../api/client';

const ForecastDashboard = () => {
  const [skus, setSkus] = useState([]);
  const [selectedSku, setSelectedSku] = useState('');
  const [horizon, setHorizon] = useState('4w');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchingSkus, setFetchingSkus] = useState(true);

  useEffect(() => {
    fetchSkus();
  }, []);

  const fetchSkus = async () => {
    setFetchingSkus(true);
    try {
      const response = await api.get('/api/v1/inventory');
      const activeSkus = response.data
        .filter(item => item.active !== false)
        .map(item => ({ sku: item.sku, name: item.name }));
      setSkus(activeSkus);
      
      if (activeSkus.length > 0) {
        setSelectedSku(activeSkus[0].sku);
      }
    } catch (error) {
      alert('Failed to fetch SKUs: ' + (error.response?.data?.message || error.message));
    } finally {
      setFetchingSkus(false);
    }
  };

  const getForecast = async () => {
    if (!selectedSku) {
      alert('Please select a SKU');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get('/api/v1/forecast', {
        params: {
          sku: selectedSku,
          horizon: horizon
        }
      });
      setForecastData(response.data);
    } catch (error) {
      alert('Failed to fetch forecast: ' + (error.response?.data?.message || error.message));
      setForecastData(null);
    } finally {
      setLoading(false);
    }
  };

  const calculateMetrics = () => {
    if (!forecastData || !forecastData.forecast) return null;

    const forecastValues = forecastData.forecast.map(d => d.forecast).filter(v => v != null);
    const avgDailyDemand = forecastValues.reduce((a, b) => a + b, 0) / forecastValues.length;
    const peakDemand = Math.max(...forecastValues);
    const recommendedReorder = Math.ceil(avgDailyDemand * 7 * 1.5);

    return {
      avgDailyDemand: avgDailyDemand.toFixed(2),
      peakDemand: peakDemand.toFixed(2),
      recommendedReorder
    };
  };

  const metrics = calculateMetrics();
  const selectedProduct = skus.find(s => s.sku === selectedSku);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Demand Forecasting</h1>

      <Card className="p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Forecast Parameters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Select SKU</label>
            {fetchingSkus ? (
              <div className="text-sm text-gray-500">Loading SKUs...</div>
            ) : (
              <select
                value={selectedSku}
                onChange={(e) => setSelectedSku(e.target.value)}
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Choose a product...</option>
                {skus.map(item => (
                  <option key={item.sku} value={item.sku}>
                    {item.name} ({item.sku})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Forecast Horizon</label>
            <div className="flex gap-2">
              {['4w', '8w', '12w'].map(h => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className={`flex-1 px-4 py-2 rounded font-medium transition-colors ${
                    horizon === h
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 hover:bg-gray-300'
                  }`}
                >
                  {h}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-end">
            <Button
              onClick={getForecast}
              disabled={loading || !selectedSku}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {loading ? 'Loading...' : 'Get Forecast'}
            </Button>
          </div>
        </div>
      </Card>

      {forecastData && (
        <>
          <Card className="p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">
              Forecast for {selectedProduct?.name || selectedSku}
            </h2>
            <ForecastChart data={forecastData.forecast} />
          </Card>

          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-6">
                <div className="text-sm text-gray-600 mb-1">Average Daily Demand</div>
                <div className="text-3xl font-bold text-blue-600">{metrics.avgDailyDemand}</div>
                <div className="text-xs text-gray-500 mt-1">units per day</div>
              </Card>

              <Card className="p-6">
                <div className="text-sm text-gray-600 mb-1">Peak Demand</div>
                <div className="text-3xl font-bold text-orange-600">{metrics.peakDemand}</div>
                <div className="text-xs text-gray-500 mt-1">maximum forecasted</div>
              </Card>

              <Card className="p-6">
                <div className="text-sm text-gray-600 mb-1">Recommended Reorder Qty</div>
                <div className="text-3xl font-bold text-green-600">{metrics.recommendedReorder}</div>
                <div className="text-xs text-gray-500 mt-1">units (1.5 weeks supply)</div>
              </Card>
            </div>
          )}
        </>
      )}

      {!forecastData && !loading && (
        <Card className="p-12">
          <div className="text-center text-gray-500">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-lg">Select a product and click "Get Forecast" to view demand predictions</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ForecastDashboard;