import { NavLink } from 'react-router-dom';
import { Home, Package, ShoppingCart, Archive, TrendingUp, BarChart } from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: Home },
  { name: 'Products', path: '/products', icon: Package },
  { name: 'Sales', path: '/sales', icon: ShoppingCart },
  { name: 'Inventory', path: '/inventory', icon: Archive },
  { name: 'Forecasting', path: '/forecast', icon: TrendingUp },
  { name: 'Analytics', path: '/analytics', icon: BarChart },
];

function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white dark:bg-secondary-800 border-r border-secondary-200 dark:border-secondary-700 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-6 py-5 border-b border-secondary-200 dark:border-secondary-700">
            <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              Garb & Glitz
            </h1>
          </div>
          
          <nav className="flex-1 px-3 py-4 space-y-1" aria-label="Sidebar navigation">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'text-secondary-700 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon
                      className={`mr-3 h-5 w-5 ${
                        isActive
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-secondary-500 dark:text-secondary-400'
                      }`}
                    />
                    {item.name}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-secondary-800 transform transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center flex-shrink-0 px-6 py-5 border-b border-secondary-200 dark:border-secondary-700">
            <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              Garb & Glitz
            </h1>
          </div>
          
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Mobile sidebar navigation">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                end={item.path === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'text-secondary-700 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon
                      className={`mr-3 h-5 w-5 ${
                        isActive
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-secondary-500 dark:text-secondary-400'
                      }`}
                    />
                    {item.name}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </>
  );
}

export default Sidebar;