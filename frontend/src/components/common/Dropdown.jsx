import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDown } from 'lucide-react';

const Dropdown = ({ 
  label, 
  items, 
  align = 'right',
  buttonClassName = '',
  menuClassName = '' 
}) => {
  const alignments = {
    left: 'left-0',
    right: 'right-0',
  };

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <Menu.Button 
          className={`inline-flex justify-center items-center w-full rounded-lg border border-secondary-300 dark:border-secondary-600 bg-white dark:bg-secondary-800 px-4 py-2 text-sm font-medium text-secondary-700 dark:text-secondary-300 hover:bg-secondary-50 dark:hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 ${buttonClassName}`}
        >
          {label}
          <ChevronDown className="ml-2 -mr-1 h-4 w-4" aria-hidden="true" />
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items 
          className={`absolute ${alignments[align]} z-10 mt-2 w-56 origin-top-right rounded-lg bg-white dark:bg-secondary-800 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none ${menuClassName}`}
        >
          <div className="py-1">
            {items.map((item, idx) => (
              <Menu.Item key={idx}>
                {({ active }) => (
                  item.divider ? (
                    <div className="border-t border-secondary-200 dark:border-secondary-700 my-1" />
                  ) : (
                    <button
                      onClick={item.onClick}
                      disabled={item.disabled}
                      className={`${
                        active ? 'bg-secondary-100 dark:bg-secondary-700' : ''
                      } ${
                        item.disabled ? 'opacity-50 cursor-not-allowed' : ''
                      } group flex w-full items-center px-4 py-2 text-sm text-secondary-700 dark:text-secondary-300`}
                    >
                      {item.icon && (
                        <item.icon className="mr-3 h-4 w-4" aria-hidden="true" />
                      )}
                      {item.label}
                    </button>
                  )
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
};

export default Dropdown;