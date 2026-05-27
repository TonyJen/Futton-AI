import React from 'react';
import { Search, Bell, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { Input } from '../ui/Input';

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, actions }: HeaderProps) {
  const today = format(new Date(), 'EEEE, MMMM dd, yyyy');

  return (
    <div className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-8 flex-shrink-0">
      <div>
        <h1 className="text-2xl font-semibold tracking-tighter text-slate-900 break-words">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 -mt-0.5 break-words">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-5">
        {/* Global Search */}
        <div className="relative w-72 hidden md:block">
          <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search items, orders, agents..." 
            className="pl-10 bg-slate-50 border-slate-200 focus:bg-white" 
          />
        </div>

        {/* Date */}
        <div className="hidden lg:flex items-center gap-2 text-sm text-slate-600 px-4 py-1.5 bg-slate-100 rounded-lg">
          <Calendar className="h-4 w-4" />
          <span className="font-medium">{today}</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
        </button>

        {/* Custom actions (per page) */}
        {actions}
      </div>
    </div>
  );
}
