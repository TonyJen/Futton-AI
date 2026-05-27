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
          Pages render <Header /> as their first element.
          This makes the header align perfectly with the sidebar's top bar.
        */}
        <div className="flex-1 overflow-y-auto bg-slate-100">
          {/* 
            Header components are rendered as the first child of pages.
            We use pt-0 so the header aligns flush with the sidebar top.
          */}
          <div className="max-w-[1440px] mx-auto px-8 pt-0 pb-12">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
