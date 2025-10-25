const Card = ({ 
  children, 
  header, 
  footer, 
  className = '',
  headerClassName = '',
  bodyClassName = '',
  footerClassName = '',
}) => {
  return (
    <div className={`bg-white dark:bg-secondary-800 rounded-lg shadow ${className}`}>
      {header && (
        <div className={`px-6 py-4 border-b border-secondary-200 dark:border-secondary-700 ${headerClassName}`}>
          {typeof header === 'string' ? (
            <h3 className="text-lg font-semibold text-secondary-900 dark:text-secondary-100">
              {header}
            </h3>
          ) : (
            header
          )}
        </div>
      )}
      
      <div className={`px-6 py-4 ${bodyClassName}`}>
        {children}
      </div>
      
      {footer && (
        <div className={`px-6 py-4 border-t border-secondary-200 dark:border-secondary-700 bg-secondary-50 dark:bg-secondary-900 rounded-b-lg ${footerClassName}`}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;