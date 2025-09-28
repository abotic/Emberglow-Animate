import React from 'react';
import { LoaderCircle } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  loading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export function Button({ 
  children, 
  variant = 'primary', 
  loading = false, 
  icon,
  fullWidth = false,
  className = '',
  disabled,
  ...props 
}: ButtonProps) {
  const baseStyles = 'flex items-center justify-center py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300';
  
  const variantStyles = {
    primary: disabled || loading
      ? 'bg-gray-600 cursor-not-allowed'
      : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5',
    secondary: 'bg-gray-700 hover:bg-gray-600',
  };

  const widthStyle = fullWidth ? 'w-full' : '';

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${widthStyle} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <LoaderCircle className="animate-spin h-5 w-5 mr-3" />
          {children}
        </>
      ) : (
        <>
          {icon && <span className="mr-3">{icon}</span>}
          {children}
        </>
      )}
    </button>
  );
}