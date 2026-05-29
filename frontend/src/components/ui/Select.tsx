import React from 'react';
import { cn } from '@/lib/utils';

type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement>;

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => (
    <select ref={ref} className={cn('select', className)} {...props}>
      {children}
    </select>
  )
);
Select.displayName = 'Select';
