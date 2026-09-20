import React from 'react';
import { cn } from '../../lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-sm active:bg-blue-700',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700',
    outline: 'border border-border text-slate-300 hover:bg-surfaceHover hover:text-white',
    ghost: 'text-slate-400 hover:text-white hover:bg-surfaceHover',
  };

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-1.5 rounded-lg',
    md: 'text-sm px-3.5 py-2 rounded-lg',
    lg: 'text-base px-5 py-2.5 rounded-xl',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : null}
      {children}
    </button>
  );
}
