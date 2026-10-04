import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, Loader2 } from 'lucide-react';

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f4f4f2] text-neutral-900 font-sans">
        <div className="relative flex flex-col items-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-neutral-900 text-white flex items-center justify-center shadow-sm">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div className="flex items-center space-x-2 text-neutral-500 text-xs font-medium tracking-wide">
            <Loader2 className="w-4 h-4 animate-spin text-neutral-800" />
            <span>Verifying session...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};
