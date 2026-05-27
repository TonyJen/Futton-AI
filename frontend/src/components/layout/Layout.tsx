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
        {/* 
          Pages render <Header /> as their first element (flush with sidebar header).
          All pages then apply consistent mt-8 on their first content block for breathing room.
        */}
        <div className="flex-1 overflow-y-auto bg-slate-100">
          <div className="max-w-[1440px] mx-auto px-8 pt-0 pb-16">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
