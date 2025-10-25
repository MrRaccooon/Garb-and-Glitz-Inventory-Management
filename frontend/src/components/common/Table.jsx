import { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

const Table = ({ columns, data, onRowClick, sortable = true }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const handleSort = (key) => {
    if (!sortable) return;
    
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig.key) return 0;
    
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];
    
    if (aValue < bValue) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-secondary-200 dark:divide-secondary-700">
        <thead className="bg-secondary-50 dark:bg-secondary-900">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={`px-6 py-3 text-left text-xs font-medium text-secondary-700 dark:text-secondary-300 uppercase tracking-wider ${
                  sortable && column.sortable !== false ? 'cursor-pointer select-none' : ''
                }`}
                onClick={() => column.sortable !== false && handleSort(column.key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.label}</span>
                  {sortable && column.sortable !== false && (
                    <span className="flex flex-col">
                      <ChevronUp
                        className={`h-3 w-3 -mb-1 ${
                          sortConfig.key === column.key && sortConfig.direction === 'asc'
                            ? 'text-primary-600 dark:text-primary-400'
                            : 'text-secondary-400'
                        }`}
                      />
                      <ChevronDown
                        className={`h-3 w-3 ${
                          sortConfig.key === column.key && sortConfig.direction === 'desc'
                            ? 'text-primary-600 dark:text-primary-400'
                            : 'text-secondary-400'
                        }`}
                      />
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-secondary-800 divide-y divide-secondary-200 dark:divide-secondary-700">
          {sortedData.map((row, idx) => (
            <tr
              key={row.id || idx}
              className={`${
                onRowClick
                  ? 'cursor-pointer hover:bg-secondary-50 dark:hover:bg-secondary-700'
                  : ''
              }`}
              onClick={() => onRowClick && onRowClick(row)}
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900 dark:text-secondary-100"
                >
                  {column.render ? column.render(row[column.key], row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {sortedData.length === 0 && (
        <div className="text-center py-12 text-secondary-500 dark:text-secondary-400">
          No data available
        </div>
      )}
    </div>
  );
};

export default Table;