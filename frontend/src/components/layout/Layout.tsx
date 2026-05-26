import React from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden">
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* The header is rendered inside each page for flexibility */}
        <div className="flex-1 overflow-y-auto bg-slate-100">
          <div className="max-w-[1440px] mx-auto px-8 pt-8 pb-12">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
