import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ size = 'md', fullScreen = false, text = 'Loading...' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center">
      <Loader2 className={`${sizes[size]} animate-spin text-primary-600 dark:text-primary-400`} />
      {text && (
        <p className="mt-3 text-sm text-secondary-600 dark:text-secondary-400">
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-secondary-900/80 z-50">
        {spinner}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center p-8">
      {spinner}
    </div>
  );
};

export default LoadingSpinner;