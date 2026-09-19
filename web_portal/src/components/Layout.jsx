import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Toast from './Toast';

const Layout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface font-body-md text-on-surface antialiased flex flex-col">
      <Sidebar
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      <div className="lg:pl-72 flex flex-col min-h-screen">
        <Header onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />

        <main className="relative pt-16 flex-1 w-full px-4 sm:px-6 lg:px-8 py-6 max-w-[1440px] mx-auto">
          <Outlet />
        </main>
      </div>

      <Toast />
    </div>
  );
};

export default Layout;
