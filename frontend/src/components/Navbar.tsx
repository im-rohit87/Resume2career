import React, { useState } from 'react';
import {
  FileText,
  Briefcase,
  PlayCircle,
  ShieldCheck,
  Calendar,
  History,
  LayoutDashboard,
  Shield,
  LogOut,
  User as UserIcon,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  currentUser: User | null;
  currentPage: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  currentPage,
  onNavigate,
  onLogout,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'resumes', label: 'Resumes', icon: FileText },
    { id: 'matching', label: 'Job Match', icon: Briefcase },
    { id: 'interview-setup', label: 'Mock Interview', icon: PlayCircle },
    { id: 'evidence', label: 'Evidence Checker', icon: ShieldCheck },
    { id: 'learning-plan', label: 'Learning Plan', icon: Calendar },
    { id: 'history', label: 'History', icon: History },
  ];

  if (currentUser?.role === 'admin') {
    navItems.push({ id: 'admin', label: 'Admin Hub', icon: Shield });
  }

  const handleNavClick = (pageId: string) => {
    onNavigate(pageId);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div
            onClick={() => handleNavClick('dashboard')}
            className="flex items-center gap-3 cursor-pointer group select-none"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 p-0.5 shadow-lg shadow-indigo-500/25">
              <div className="w-full h-full bg-gray-50 rounded-[10px] flex items-center justify-center group-hover:bg-transparent transition-colors">
                <Sparkles className="w-4 h-4 text-indigo-400 group-hover:text-gray-900 transition-colors" />
              </div>
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-gray-900 flex items-center gap-1.5">
                Resume2Interview <span className="text-xs px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">AI</span>
              </span>
              <p className="text-[10px] text-gray-500 font-medium hidden sm:block">Adaptive Mock Interview & Analysis</p>
            </div>
          </div>

          {/* Desktop Nav */}
          {currentUser && (
            <nav className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                        : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          )}

          {/* User Controls */}
          <div className="hidden sm:flex items-center gap-3">
            {currentUser ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 pl-3 border-l border-gray-200">
                  <div className="w-7 h-7 rounded-full bg-gray-100 border border-gray-300 flex items-center justify-center text-xs font-bold text-indigo-400 uppercase">
                    {currentUser.username[0]}
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-gray-800 leading-none">{currentUser.full_name}</p>
                    <p className="text-[10px] text-gray-400 leading-tight">
                      {currentUser.role === 'admin' ? (
                        <span className="text-amber-400 font-bold">Admin</span>
                      ) : (
                        'Candidate'
                      )}
                    </p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  title="Logout"
                  className="p-1.5 rounded-lg text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => onNavigate('auth')}
                className="px-4 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-sm shadow-indigo-600/30 transition-all"
              >
                Sign In
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden flex items-center gap-2">
            {currentUser && (
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-white focus:outline-none"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && currentUser && (
        <div className="lg:hidden border-b border-gray-200 bg-white/95 px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm font-medium ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
          <div className="pt-3 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <UserIcon className="w-4 h-4 text-gray-500" />
              <span className="text-xs text-gray-700">{currentUser.full_name}</span>
            </div>
            <button
              onClick={onLogout}
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1"
            >
              <LogOut className="w-3.5 h-3.5" /> Logout
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
