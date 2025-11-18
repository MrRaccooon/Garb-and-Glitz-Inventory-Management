import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, User, Bell, Search, AlertTriangle } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import api from '../../api/client';

function Navbar() {
  const location = useLocation();
  const [showNotifications, setShowNotifications] = useState(false);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const notificationRef = useRef(null);

  // Fetch low stock items
  useEffect(() => {
    fetchLowStockItems();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchLowStockItems = async () => {
    try {
      setLoading(true);
      const response = await api.get('/inventory/low-stock');
      setLowStockItems(response.data || []);
    } catch (error) {
      console.error('Failed to fetch low stock items:', error);
      setLowStockItems([]);
    } finally {
      setLoading(false);
    }
  };

  const getBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [{ name: 'Home', path: '/' }];
    
    let currentPath = '';
    paths.forEach((path) => {
      currentPath += `/${path}`;
      const name = path.charAt(0).toUpperCase() + path.slice(1);
      breadcrumbs.push({ name, path: currentPath });
    });
    
    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <nav className="sticky top-0 z-20 bg-white dark:bg-secondary-800 shadow">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Breadcrumb */}
          <div className="flex items-center space-x-4">
            <div className="hidden lg:block">
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                Garb & Glitz
              </h1>
            </div>
            
            {/* Breadcrumb */}
            <nav className="hidden md:flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
              {breadcrumbs.map((crumb, idx) => (
                <div key={crumb.path} className="flex items-center">
                  {idx > 0 && (
                    <ChevronRight className="h-4 w-4 text-secondary-400 mx-2" />
                  )}
                  <Link
                    to={crumb.path}
                    className={`${
                      idx === breadcrumbs.length - 1
                        ? 'text-secondary-900 dark:text-secondary-100 font-medium'
                        : 'text-secondary-500 dark:text-secondary-400 hover:text-secondary-700 dark:hover:text-secondary-300'
                    }`}
                  >
                    {crumb.name}
                  </Link>
                </div>
              ))}
            </nav>
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-3">
            <button
              className="p-2 rounded-lg text-secondary-600 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700"
              aria-label="Search"
            >
              <Search className="h-5 w-5" />
            </button>

            {/* Logout Button */}
            <button
              onClick={() => {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
              }}
              className="px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              aria-label="Logout"
            >
              Logout
            </button>
            
            <div className="relative" ref={notificationRef}>
              <button
                className="p-2 rounded-lg text-secondary-600 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700 relative"
                aria-label="Notifications"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <Bell className="h-5 w-5" />
                {lowStockItems.length > 0 && (
                  <span className="absolute top-1 right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold">
                    {lowStockItems.length}
                  </span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-secondary-800 rounded-lg shadow-lg border border-secondary-200 dark:border-secondary-700 max-h-96 overflow-y-auto z-50">
                  <div className="p-4 border-b border-secondary-200 dark:border-secondary-700">
                    <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                      Notifications
                    </h3>
                  </div>

                  {loading ? (
                    <div className="p-4 text-center text-secondary-500">Loading...</div>
                  ) : lowStockItems.length === 0 ? (
                    <div className="p-4 text-center text-secondary-500">
                      No notifications
                    </div>
                  ) : (
                    <div className="divide-y divide-secondary-200 dark:divide-secondary-700">
                      {lowStockItems.map((item) => (
                        <Link
                          key={item.sku}
                          to="/inventory"
                          className="block p-4 hover:bg-secondary-50 dark:hover:bg-secondary-700 transition-colors"
                          onClick={() => setShowNotifications(false)}
                        >
                          <div className="flex items-start space-x-3">
                            <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100 truncate">
                                Low Stock Alert
                              </p>
                              <p className="text-sm text-secondary-600 dark:text-secondary-400">
                                {item.name}
                              </p>
                              <p className="text-xs text-secondary-500 dark:text-secondary-500 mt-1">
                                Current: {item.balance_qty || 0} | Reorder Point: {item.reorder_point}
                              </p>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}

                  {lowStockItems.length > 0 && (
                    <div className="p-3 border-t border-secondary-200 dark:border-secondary-700">
                      <Link
                        to="/inventory"
                        className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                        onClick={() => setShowNotifications(false)}
                      >
                        View all in Inventory →
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <button
              className="flex items-center space-x-2 p-2 rounded-lg text-secondary-600 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700"
              aria-label="User menu"
            >
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;