import Button from './Button';

const EmptyState = ({ 
  icon: Icon, 
  title, 
  description, 
  action, 
  actionLabel,
  className = '' 
}) => {
  return (
    <div className={`text-center py-12 ${className}`}>
      {Icon && (
        <div className="mx-auto h-12 w-12 text-secondary-400 dark:text-secondary-500">
          <Icon className="h-full w-full" />
        </div>
      )}
      <h3 className="mt-4 text-lg font-semibold text-secondary-900 dark:text-secondary-100">
        {title}
      </h3>
      {description && (
        <p className="mt-2 text-sm text-secondary-600 dark:text-secondary-400 max-w-sm mx-auto">
          {description}
        </p>
      )}
      {action && actionLabel && (
        <div className="mt-6">
          <Button onClick={action} variant="primary">
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};

export default EmptyState;