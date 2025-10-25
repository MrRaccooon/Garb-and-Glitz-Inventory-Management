import React from 'react';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ForecastChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-gray-500">
        No forecast data available
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border rounded shadow-lg">
          <p className="font-semibold mb-2">{formatDate(payload[0].payload.date)}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value?.toFixed(2) || 'N/A'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={300} minHeight={300}>
      <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fontSize: 12 }}
          stroke="#6b7280"
        />
        <YAxis
          label={{ value: 'Quantity', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
          tick={{ fontSize: 12 }}
          stroke="#6b7280"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '14px' }}
          iconType="line"
        />
        
        <Area
          type="monotone"
          dataKey="upper"
          stroke="none"
          fill="#bfdbfe"
          fillOpacity={0.3}
          name="Upper Bound"
        />
        <Area
          type="monotone"
          dataKey="lower"
          stroke="none"
          fill="#bfdbfe"
          fillOpacity={0.3}
          name="Lower Bound"
        />
        
        <Line
          type="monotone"
          dataKey="actual"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 3 }}
          name="Actual Sales"
          connectNulls
        />
        <Line
          type="monotone"
          dataKey="forecast"
          stroke="#22c55e"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={{ r: 3 }}
          name="Forecast"
          connectNulls
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default ForecastChart;