import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, User, Bell, Search } from 'lucide-react';

function Navbar() {
  const location = useLocation();
  
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
            
            <button
              className="p-2 rounded-lg text-secondary-600 dark:text-secondary-300 hover:bg-secondary-100 dark:hover:bg-secondary-700 relative"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
            </button>
            
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