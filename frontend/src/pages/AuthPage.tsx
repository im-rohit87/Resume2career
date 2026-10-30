import { ArrowRight, Eye, EyeOff, Loader2, Lock, Mail, Sparkles, User } from 'lucide-react';
import React, { useState } from 'react';
import { api } from '../services/api';
import { User as UserType } from '../types';

interface AuthPageProps {
  onLogin: (user: UserType) => void;
}

type Tab = 'login' | 'register';

function Spinner() {
  return <Loader2 className="w-4 h-4 animate-spin" />;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onLogin }) => {
  const [tab, setTab] = useState<Tab>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Login fields
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register fields
  const [regEmail, setRegEmail] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regFullName, setRegFullName] = useState('');

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validateEmail = (email: string) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const validateLoginForm = () => {
    const errs: Record<string, string> = {};
    if (!loginEmail.trim()) errs.login_email = 'Email or username is required';
    if (!loginPassword) errs.login_password = 'Password is required';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const validateRegisterForm = () => {
    const errs: Record<string, string> = {};
    if (!regFullName.trim()) errs.full_name = 'Full name is required';
    if (!regEmail.trim()) errs.email = 'Email is required';
    else if (!validateEmail(regEmail)) errs.email = 'Enter a valid email address';
    if (!regUsername.trim()) errs.username = 'Username is required';
    else if (regUsername.length < 3) errs.username = 'Username must be at least 3 characters';
    if (!regPassword) errs.password = 'Password is required';
    else if (regPassword.length < 6) errs.password = 'Password must be at least 6 characters';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateLoginForm()) return;
    setLoading(true);
    setError('');
    try {
      const result = await api.login({ username_or_email: loginEmail, password: loginPassword });
      onLogin(result.user);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateRegisterForm()) return;
    setLoading(true);
    setError('');
    try {
      const result = await api.register({
        email: regEmail,
        username: regUsername,
        password: regPassword,
        full_name: regFullName,
      });
      onLogin(result.user);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const switchTab = (t: Tab) => {
    setTab(t);
    setError('');
    setFieldErrors({});
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 p-0.5 shadow-xl shadow-indigo-500/30 mb-4">
            <div className="w-full h-full bg-gray-50 rounded-[14px] flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-indigo-400" />
            </div>
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Resume2Interview <span className="text-xs px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 align-middle">AI</span></h1>
          <p className="text-gray-500 text-sm mt-1">Adaptive Mock Interview & Analysis Platform</p>
        </div>

        {/* Card */}
        <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-xl shadow-gray-200">
          {/* Tabs */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-6 gap-1">
            {(['login', 'register'] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => switchTab(t)}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                  tab === t
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-800'
                }`}
              >
                {t === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-4 px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm">
              {error}
            </div>
          )}

          {/* Login Form */}
          {tab === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4" noValidate>
              <div>
                <label htmlFor="login-email" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Email or Username
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="login-email"
                    type="text"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="you@gmail.com"
                    className={`w-full pl-9 pr-4 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.login_email ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                </div>
                {fieldErrors.login_email && <p className="mt-1 text-xs text-rose-400">{fieldErrors.login_email}</p>}
              </div>

              <div>
                <label htmlFor="login-password" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="password"
                    className={`w-full pl-9 pr-10 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.login_password ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {fieldErrors.login_password && <p className="mt-1 text-xs text-rose-400">{fieldErrors.login_password}</p>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-indigo-600/20"
              >
                {loading ? <Spinner /> : <ArrowRight className="w-4 h-4" />}
                {loading ? 'Signing in…' : 'Sign In'}
              </button>
            </form>
          )}

          {/* Register Form */}
          {tab === 'register' && (
            <form onSubmit={handleRegister} className="space-y-4" noValidate>
              <div>
                <label htmlFor="reg-fullname" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="reg-fullname"
                    type="text"
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    placeholder="Enter your Name"
                    className={`w-full pl-9 pr-4 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.full_name ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                </div>
                {fieldErrors.full_name && <p className="mt-1 text-xs text-rose-400">{fieldErrors.full_name}</p>}
              </div>

              <div>
                <label htmlFor="reg-email" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="reg-email"
                    type="email"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="you@gmail.com"
                    className={`w-full pl-9 pr-4 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.email ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                </div>
                {fieldErrors.email && <p className="mt-1 text-xs text-rose-400">{fieldErrors.email}</p>}
              </div>

              <div>
                <label htmlFor="reg-username" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Username <span className="text-gray-400 font-normal">(min 3 chars)</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="reg-username"
                    type="text"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    placeholder="UserName"
                    className={`w-full pl-9 pr-4 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.username ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                </div>
                {fieldErrors.username && <p className="mt-1 text-xs text-rose-400">{fieldErrors.username}</p>}
              </div>

              <div>
                <label htmlFor="reg-password" className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Password <span className="text-gray-400 font-normal">(min 6 chars)</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="reg-password"
                    type={showPassword ? 'text' : 'password'}
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Password"
                    className={`w-full pl-9 pr-10 py-2.5 bg-white border rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
                      fieldErrors.password ? 'border-rose-500' : 'border-gray-300'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {fieldErrors.password && <p className="mt-1 text-xs text-rose-400">{fieldErrors.password}</p>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-indigo-600/20"
              >
                {loading ? <Spinner /> : <Sparkles className="w-4 h-4" />}
                {loading ? 'Creating account…' : 'Create Account'}
              </button>
            </form>
          )}

          <p className="mt-6 text-center text-xs text-gray-400">
            By continuing, you agree to our terms of service and privacy policy.
          </p>
        </div>
      </div>
    </div>
  );
};
