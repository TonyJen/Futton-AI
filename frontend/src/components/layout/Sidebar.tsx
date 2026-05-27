import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Package, Boxes, Factory, Users, Bot, TrendingUp, Settings
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/items', label: 'Items & BOM', icon: Package },
  { to: '/inventory', label: 'Inventory', icon: Boxes },
  { to: '/production', label: 'Production', icon: Factory },
  { to: '/sales', label: 'Sales', icon: TrendingUp },
  { to: '/agents', label: 'AI Agents Hub', icon: Bot },
];

export function Sidebar() {
  return (
    <div className="w-72 border-r border-slate-200 bg-white flex flex-col h-full">
      {/* Logo / Brand */}
      <div className="h-16 px-6 flex items-center border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-xl tracking-[-1.5px]">F</span>
          </div>
          <div>
            <div className="font-semibold tracking-tight text-xl text-slate-900">Funton AI</div>
            <div className="text-[10px] text-slate-500 -mt-1 font-medium">MANUFACTURING ERP</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="px-3 mb-2 text-xs font-semibold tracking-widest text-slate-400">OPERATIONS</div>
        <nav className="space-y-0.5">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn('nav-link', isActive && 'active')
              }
            >
              <item.icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-3 mt-8 mb-2 text-xs font-semibold tracking-widest text-slate-400">SYSTEM</div>
        <nav className="space-y-0.5">
          <a href="#" className="nav-link text-slate-600">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </a>
        </nav>
      </div>

      {/* User / Footer */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/70">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-slate-300 flex-shrink-0 overflow-hidden">
            <img src="https://i.pravatar.cc/32?img=47" alt="User" className="w-full h-full object-cover" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-800 truncate">Elena Rodriguez</div>
            <div className="text-xs text-slate-500 truncate">Plant Operations Director</div>
          </div>
        </div>
      </div>
    </div>
  );
}
