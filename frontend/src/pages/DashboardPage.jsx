import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase, isSupabaseConfigured } from '../lib/supabaseClient';
import { 
  Sparkles, 
  User, 
  Link as LinkIcon, 
  Copy, 
  Check, 
  ExternalLink, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  RotateCcw, 
  Zap, 
  Mail, 
  Phone, 
  GraduationCap, 
  Layers,
  ArrowRight,
  RefreshCw,
  LogOut,
  Database,
  ChevronDown,
  ChevronUp,
  Briefcase,
  BookOpen,
  Car,
  MapPin,
  Building2,
  Calendar,
  Award,
  FileBadge
} from 'lucide-react';

import {
  GENDER_OPTIONS,
  DRIVING_LICENSE_OPTIONS,
  CATEGORY_UG_PG_OPTIONS,
  SCHOOL_NAME_OPTIONS,
  APPLYING_FOR_ROLE_OPTIONS
} from '../constants/crcOptions';

const INITIAL_PROFILE = {
  // 1. Personal & Contact
  enrollment_no: '',
  full_name: '',
  dob: '',
  gender: 'Male',
  home_location: '',
  permanent_address: '',
  contact_no: '',
  alt_contact_no: '',
  personal_email: '',
  institutional_email: '',
  driving_license_yes_no: 'Yes',

  // 2. Academic Record
  school_name: 'School of Computer Science & Engineering',
  category_ug_pg: 'UG',
  course: 'B.Tech',
  ug_specialization: 'Computer Science & Engineering',
  ug_cgpa: '',
  ug_passing_year: '2026',
  pg_specialization: '',
  pg_cgpa: '',
  pg_passing_year: '',
  tenth_percentage: '',
  tenth_board: 'CBSE',
  tenth_passing_year: '2020',
  twelfth_percentage: '',
  twelfth_board: 'CBSE',
  twelfth_passing_year: '2022',

  // 3. Professional Experience
  internship_organization: '',
  internship_topic: '',
  extra_certifications: '',
  applying_for_role: 'Software Development Engineer (SDE)',
};

const SAMPLE_CRC_PROFILE = {
  // 1. Personal & Contact
  enrollment_no: '2021BCSE042',
  full_name: 'Alex Mercer',
  dob: '2003-04-12',
  gender: 'Male',
  home_location: 'Noida, Uttar Pradesh',
  permanent_address: 'Flat 402, Lotus Boulevard, Sector 100, Noida, UP - 201304',
  contact_no: '+91 9876543210',
  alt_contact_no: '+91 9876543211',
  personal_email: 'alex.mercer.dev@gmail.com',
  institutional_email: 'alex.mercer@university.edu.in',
  driving_license_yes_no: 'Yes',

  // 2. Academic Record
  school_name: 'School of Computer Science & Engineering',
  category_ug_pg: 'UG',
  course: 'B.Tech',
  ug_specialization: 'Computer Science & Engineering',
  ug_cgpa: '8.92',
  ug_passing_year: '2026',
  pg_specialization: '',
  pg_cgpa: '',
  pg_passing_year: '',
  tenth_percentage: '94.2%',
  tenth_board: 'CBSE',
  tenth_passing_year: '2020',
  twelfth_percentage: '91.8%',
  twelfth_board: 'CBSE',
  twelfth_passing_year: '2022',

  // 3. Professional Experience
  internship_organization: 'Amazon Web Services (AWS)',
  internship_topic: 'Distributed Cloud Microservices & Scalable Telemetry Infrastructure',
  extra_certifications: 'AWS Certified Solutions Architect, Oracle Certified Java Associate, Coursera Deep Learning Specialization',
  applying_for_role: 'Software Development Engineer (SDE)',
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function DashboardPage() {
  const { user, session, signOut } = useAuth();

  // Profile state
  const [profile, setProfile] = useState(INITIAL_PROFILE);
  const [isFetchingProfile, setIsFetchingProfile] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [profileError, setProfileError] = useState(null);

  // Collapsible section toggle states
  const [openSections, setOpenSections] = useState({
    personal: true,
    academic: true,
    professional: true,
  });

  const toggleSection = (sectionKey) => {
    setOpenSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const toggleAllSections = (expand) => {
    setOpenSections({
      personal: expand,
      academic: expand,
      professional: expand,
    });
  };

  // Link Generator state
  const [formUrl, setFormUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Backend connection status
  const [backendOnline, setBackendOnline] = useState(null);

  // Check backend server health
  const checkBackendHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
      if (res.ok) {
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }
    } catch {
      setBackendOnline(false);
    }
  };

  // 1. Fetch CRC Profile from Supabase on mount
  useEffect(() => {
    let isMounted = true;

    const fetchUserProfile = async () => {
      if (!user) {
        setIsFetchingProfile(false);
        return;
      }

      setIsFetchingProfile(true);
      setProfileError(null);

      try {
        if (isSupabaseConfigured) {
          const { data, error: sbError } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', user.id)
            .maybeSingle();

          if (sbError) {
            console.warn('[Supabase] Profile fetch error:', sbError.message);
          }

          if (data && isMounted) {
            setProfile({
              // Personal & Contact
              enrollment_no: data.enrollment_no || '',
              full_name: data.full_name || user.user_metadata?.full_name || '',
              dob: data.dob || data.date_of_birth || '',
              gender: data.gender || 'Male',
              home_location: data.home_location || data.city || '',
              permanent_address: data.permanent_address || data.address || '',
              contact_no: data.contact_no || data.phone || '',
              alt_contact_no: data.alt_contact_no || '',
              personal_email: data.personal_email || data.email || user.email || '',
              institutional_email: data.institutional_email || '',
              driving_license_yes_no: data.driving_license_yes_no || 'Yes',

              // Academic Record
              school_name: data.school_name || data.university || 'School of Computer Science & Engineering',
              category_ug_pg: data.category_ug_pg || 'UG',
              course: data.course || data.degree || 'B.Tech',
              ug_specialization: data.ug_specialization || data.major || 'Computer Science & Engineering',
              ug_cgpa: data.ug_cgpa || data.gpa || '',
              ug_passing_year: data.ug_passing_year || data.graduation_year || '2026',
              pg_specialization: data.pg_specialization || '',
              pg_cgpa: data.pg_cgpa || '',
              pg_passing_year: data.pg_passing_year || '',
              tenth_percentage: data.tenth_percentage || '',
              tenth_board: data.tenth_board || 'CBSE',
              tenth_passing_year: data.tenth_passing_year || '2020',
              twelfth_percentage: data.twelfth_percentage || '',
              twelfth_board: data.twelfth_board || 'CBSE',
              twelfth_passing_year: data.twelfth_passing_year || '2022',

              // Professional Experience
              internship_organization: data.internship_organization || '',
              internship_topic: data.internship_topic || '',
              extra_certifications: data.extra_certifications || data.tech_stack || '',
              applying_for_role: data.applying_for_role || 'Software Development Engineer (SDE)',
            });
          } else if (isMounted) {
            // First time user setup
            setProfile(prev => ({
              ...prev,
              personal_email: user.email || '',
              full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
            }));
          }
        } else {
          // Local storage fallback
          const localSaved = localStorage.getItem(`crc_profile_${user.id}`);
          if (localSaved && isMounted) {
            setProfile(JSON.parse(localSaved));
          } else if (isMounted) {
            setProfile(prev => ({
              ...prev,
              personal_email: user.email || '',
              full_name: user.user_metadata?.full_name || '',
            }));
          }
        }
      } catch (err) {
        console.error('Failed to load user profile:', err);
        if (isMounted) {
          setProfileError('Failed to load profile from database.');
        }
      } finally {
        if (isMounted) setIsFetchingProfile(false);
      }
    };

    fetchUserProfile();
    checkBackendHealth();

    return () => {
      isMounted = false;
    };
  }, [user]);

  // Profile field change handler
  const handleProfileChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
    setIsSaved(false);
  };

  // 2. Save CRC profile to Supabase PostgreSQL Database
  const handleSaveProfile = async (e) => {
    e?.preventDefault();
    if (!user) return;

    setIsSavingProfile(true);
    setProfileError(null);

    try {
      if (isSupabaseConfigured) {
        const payload = {
          id: user.id,
          ...profile,
          // Legacy bridges for compatibility
          email: profile.personal_email || user.email,
          phone: profile.contact_no,
          student_id: profile.enrollment_no,
          date_of_birth: profile.dob,
          university: profile.school_name,
          major: profile.ug_specialization,
          degree: profile.course,
          graduation_year: profile.ug_passing_year,
          gpa: profile.ug_cgpa,
          address: profile.permanent_address,
          tech_stack: profile.extra_certifications,
          updated_at: new Date().toISOString(),
        };

        const { error: upsertError } = await supabase
          .from('profiles')
          .upsert(payload, { onConflict: 'id' });

        if (upsertError) {
          throw upsertError;
        }
      } else {
        localStorage.setItem(`crc_profile_${user.id}`, JSON.stringify(profile));
      }

      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      console.error('Error saving profile:', err);
      setProfileError(err.message || 'Failed to persist profile in Supabase database.');
    } finally {
      setIsSavingProfile(false);
    }
  };

  // Load sample CRC profile
  const handleLoadSample = () => {
    setProfile({
      ...SAMPLE_CRC_PROFILE,
      personal_email: user?.email || SAMPLE_CRC_PROFILE.personal_email,
    });
    setIsSaved(false);
  };

  // Clear profile inputs
  const handleClearProfile = () => {
    setProfile({
      ...INITIAL_PROFILE,
      personal_email: user?.email || '',
    });
    setIsSaved(false);
  };

  // 3. Generate Link Handler with Supabase JWT Bearer token
  const handleGenerateLink = async (e) => {
    e?.preventDefault();
    if (!formUrl.trim()) {
      setError('Please provide a valid Google Form URL.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = session?.access_token;
      
      const headers = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/generate-link`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          form_url: formUrl.trim(),
          student: {
            ...profile,
            // Fallbacks for API schema
            email: profile.personal_email || undefined,
            phone: profile.contact_no || undefined,
            student_id: profile.enrollment_no || undefined,
            date_of_birth: profile.dob || undefined,
            university: profile.school_name || undefined,
            major: profile.ug_specialization || undefined,
            degree: profile.course || undefined,
            graduation_year: profile.ug_passing_year || undefined,
            gpa: profile.ug_cgpa || undefined,
            address: profile.permanent_address || undefined,
            tech_stack: profile.extra_certifications || undefined,
          },
          auto_match: true,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required: Your session token is invalid or expired. Please sign in again.');
        }
        throw new Error(data.detail || 'Failed to process Google Form.');
      }

      setResult(data);
    } catch (err) {
      console.error('Generate Link Error:', err);
      setError(err.message || 'An error occurred while communicating with the backend.');
    } finally {
      setLoading(false);
    }
  };

  // Copy pre-filled URL to clipboard
  const handleCopy = async () => {
    if (result?.prefilled_url) {
      try {
        await navigator.clipboard.writeText(result.prefilled_url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      } catch (err) {
        console.error('Failed to copy', err);
      }
    }
  };

  const userDisplayName = profile.full_name || user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
  const userInitials = (userDisplayName || 'U')
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);

  // Field counter helper for sections
  const countFilled = (keys) => keys.filter(k => profile[k] && String(profile[k]).trim() !== '').length;

  const personalKeys = ['enrollment_no', 'full_name', 'dob', 'gender', 'home_location', 'permanent_address', 'contact_no', 'alt_contact_no', 'personal_email', 'institutional_email', 'driving_license_yes_no'];
  const academicKeys = ['school_name', 'category_ug_pg', 'course', 'ug_specialization', 'ug_cgpa', 'ug_passing_year', 'tenth_percentage', 'tenth_board', 'tenth_passing_year', 'twelfth_percentage', 'twelfth_board', 'twelfth_passing_year'];
  const professionalKeys = ['internship_organization', 'internship_topic', 'extra_certifications', 'applying_for_role'];

  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-100">
      {/* Top Navigation Bar */}
      <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Subtitle */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 p-0.5 shadow-lg shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                  AutoForm AI
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                  CRC Edition
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Automated CRC Placement & Google Forms Prefiller</p>
            </div>
          </div>

          {/* Right Controls: Backend Status & User Account / Signout */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            {/* Backend Status indicator */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-white/10 text-xs">
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : backendOnline === false ? 'bg-rose-500' : 'bg-amber-400'}`} />
              <span className="text-slate-400 font-medium hidden md:inline">Backend API:</span>
              <span className={backendOnline ? 'text-emerald-400 font-medium' : 'text-slate-400'}>
                {backendOnline ? 'Connected' : backendOnline === false ? 'Offline' : 'Checking...'}
              </span>
            </div>

            {/* User Profile Badge & Signout */}
            <div className="flex items-center space-x-2 pl-2 border-l border-white/10">
              <div className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-slate-900/80 border border-white/10">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm">
                  {userInitials}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-semibold text-white leading-tight truncate max-w-[120px]">{userDisplayName}</p>
                  <p className="text-[10px] text-slate-400 leading-tight truncate max-w-[120px]">{user?.email}</p>
                </div>
              </div>

              <button
                type="button"
                onClick={signOut}
                title="Sign out of your account"
                className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition-all cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10">
        {/* Intro banner */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Corporate Resource Center (CRC) Autofill
            </h1>
            <p className="text-sm sm:text-base text-slate-400 mt-1 max-w-3xl">
              Manage your verified CRC student profile across Personal, Academic, and Professional records. Paste any campus drive or Google Form link for instant pre-filled generation.
            </p>
          </div>

          <div className="flex items-center space-x-2 self-start md:self-auto">
            <span className="inline-flex items-center space-x-1.5 text-xs font-medium px-3 py-1.5 rounded-xl bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              <span>Supabase Cloud DB</span>
            </span>
          </div>
        </div>

        {/* 2-Column Side-by-Side Cards Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* ================================================================= */}
          {/* CARD 1: MASTER CRC PROFILE (7 Cols on large screens)              */}
          {/* ================================================================= */}
          <section className="lg:col-span-7 rounded-2xl glass-panel p-5 sm:p-6 relative overflow-hidden border border-white/10">
            {/* Ambient card glow */}
            <div className="absolute top-0 right-0 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

            {/* Header with Quick Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-white/10 mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Master CRC Profile</h2>
                  <p className="text-xs text-slate-400">
                    {isFetchingProfile ? 'Loading from cloud...' : 'Persisted in Supabase PostgreSQL'}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => toggleAllSections(true)}
                  className="text-[11px] text-slate-300 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer"
                  title="Expand all 3 sections"
                >
                  Expand All
                </button>
                <button
                  type="button"
                  onClick={() => toggleAllSections(false)}
                  className="text-[11px] text-slate-300 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer"
                  title="Collapse all 3 sections"
                >
                  Collapse All
                </button>
                <button
                  type="button"
                  onClick={handleLoadSample}
                  className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors px-2.5 py-1 rounded bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 cursor-pointer"
                  title="Populate realistic CRC sample values"
                >
                  Load Sample
                </button>
                <button
                  type="button"
                  onClick={handleClearProfile}
                  className="text-xs text-slate-400 hover:text-slate-300 transition-colors p-1.5 rounded hover:bg-white/5 cursor-pointer"
                  title="Clear all fields"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Profile Error Alert */}
            {profileError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{profileError}</span>
              </div>
            )}

            <form onSubmit={handleSaveProfile} className="space-y-5">
              
              {/* ============================================================= */}
              {/* SECTION 1: PERSONAL INFORMATION                               */}
              {/* ============================================================= */}
              <div className="rounded-xl border border-indigo-500/20 bg-slate-900/40 overflow-hidden transition-all">
                <button
                  type="button"
                  onClick={() => toggleSection('personal')}
                  className="w-full px-4 py-3.5 flex items-center justify-between bg-indigo-500/5 hover:bg-indigo-500/10 border-b border-indigo-500/10 text-left transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-2.5">
                    <User className="w-4 h-4 text-indigo-400" />
                    <span className="font-bold text-sm text-white">1. Personal Information & Contact</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {countFilled(personalKeys)} / {personalKeys.length} Filled
                    </span>
                  </div>
                  <div className="text-slate-400">
                    {openSections.personal ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>

                {openSections.personal && (
                  <div className="p-4 space-y-4 animate-in fade-in duration-200">
                    {/* Enrollment No & Full Name */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Enrollment / Roll No <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. 2021BCSE042"
                          value={profile.enrollment_no}
                          onChange={(e) => handleProfileChange('enrollment_no', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500 font-mono"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Full Name <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Alex Mercer"
                          value={profile.full_name}
                          onChange={(e) => handleProfileChange('full_name', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>
                    </div>

                    {/* DOB & Gender */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          <span>Date of Birth (DOB)</span>
                        </label>
                        <input
                          type="date"
                          placeholder="YYYY-MM-DD"
                          value={profile.dob}
                          onChange={(e) => handleProfileChange('dob', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Gender <span className="text-rose-400">*</span>
                        </label>
                        <select
                          value={profile.gender}
                          onChange={(e) => handleProfileChange('gender', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white bg-slate-900 border border-white/10 cursor-pointer"
                        >
                          {GENDER_OPTIONS.map((opt) => (
                            <option key={opt} value={opt} className="bg-slate-900 text-white">
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Home Location & Driving License */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>Home Location / City</span>
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. Noida, Uttar Pradesh"
                          value={profile.home_location}
                          onChange={(e) => handleProfileChange('home_location', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Car className="w-3.5 h-3.5 text-slate-400" />
                          <span>Driving License Availability</span>
                        </label>
                        <select
                          value={profile.driving_license_yes_no}
                          onChange={(e) => handleProfileChange('driving_license_yes_no', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white bg-slate-900 border border-white/10 cursor-pointer"
                        >
                          {DRIVING_LICENSE_OPTIONS.map((opt) => (
                            <option key={opt} value={opt} className="bg-slate-900 text-white">
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Permanent Address */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                        Permanent Residential Address
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Flat 402, Lotus Boulevard, Sector 100, Noida, UP - 201304"
                        value={profile.permanent_address}
                        onChange={(e) => handleProfileChange('permanent_address', e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                      />
                    </div>

                    {/* Contact Numbers */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Phone className="w-3.5 h-3.5 text-slate-400" />
                          <span>Primary Contact No <span className="text-rose-400">*</span></span>
                        </label>
                        <input
                          type="tel"
                          required
                          placeholder="e.g. +91 9876543210"
                          value={profile.contact_no}
                          onChange={(e) => handleProfileChange('contact_no', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Phone className="w-3.5 h-3.5 text-slate-400" />
                          <span>Alternate Contact No</span>
                        </label>
                        <input
                          type="tel"
                          placeholder="e.g. +91 9876543211"
                          value={profile.alt_contact_no}
                          onChange={(e) => handleProfileChange('alt_contact_no', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>
                    </div>

                    {/* Personal & Institutional Emails */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Mail className="w-3.5 h-3.5 text-slate-400" />
                          <span>Personal Email <span className="text-rose-400">*</span></span>
                        </label>
                        <input
                          type="email"
                          required
                          placeholder="e.g. alex.mercer.dev@gmail.com"
                          value={profile.personal_email}
                          onChange={(e) => handleProfileChange('personal_email', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>Institutional Email</span>
                        </label>
                        <input
                          type="email"
                          placeholder="e.g. alex.mercer@university.edu.in"
                          value={profile.institutional_email}
                          onChange={(e) => handleProfileChange('institutional_email', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* ============================================================= */}
              {/* SECTION 2: ACADEMIC RECORD                                    */}
              {/* ============================================================= */}
              <div className="rounded-xl border border-cyan-500/20 bg-slate-900/40 overflow-hidden transition-all">
                <button
                  type="button"
                  onClick={() => toggleSection('academic')}
                  className="w-full px-4 py-3.5 flex items-center justify-between bg-cyan-500/5 hover:bg-cyan-500/10 border-b border-cyan-500/10 text-left transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-2.5">
                    <GraduationCap className="w-4 h-4 text-cyan-400" />
                    <span className="font-bold text-sm text-white">2. Academic Record</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      {countFilled(academicKeys)} / {academicKeys.length} Filled
                    </span>
                  </div>
                  <div className="text-slate-400">
                    {openSections.academic ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>

                {openSections.academic && (
                  <div className="p-4 space-y-4 animate-in fade-in duration-200">
                    {/* School Name & Category (UG/PG) */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                          <Building2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>School / Faculty Name <span className="text-rose-400">*</span></span>
                        </label>
                        <select
                          value={profile.school_name}
                          onChange={(e) => handleProfileChange('school_name', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-xs text-white bg-slate-900 border border-white/10 cursor-pointer"
                        >
                          {SCHOOL_NAME_OPTIONS.map((opt) => (
                            <option key={opt} value={opt} className="bg-slate-900 text-white">
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Category (UG / PG) <span className="text-rose-400">*</span>
                        </label>
                        <select
                          value={profile.category_ug_pg}
                          onChange={(e) => handleProfileChange('category_ug_pg', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white bg-slate-900 border border-white/10 cursor-pointer"
                        >
                          {CATEGORY_UG_PG_OPTIONS.map((opt) => (
                            <option key={opt} value={opt} className="bg-slate-900 text-white">
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Course & UG Specialization */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Course / Program <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. B.Tech"
                          value={profile.course}
                          onChange={(e) => handleProfileChange('course', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          UG Specialization / Branch <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Computer Science & Engineering"
                          value={profile.ug_specialization}
                          onChange={(e) => handleProfileChange('ug_specialization', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>
                    </div>

                    {/* UG CGPA & Passing Year */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          UG CGPA / Current GPA <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. 8.92"
                          value={profile.ug_cgpa}
                          onChange={(e) => handleProfileChange('ug_cgpa', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          UG Passing Year <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. 2026"
                          value={profile.ug_passing_year}
                          onChange={(e) => handleProfileChange('ug_passing_year', e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500 font-mono"
                        />
                      </div>
                    </div>

                    {/* Postgraduate Details (Optional) */}
                    <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-3">
                      <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Postgraduate Record (Optional - for PG Candidates)</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">PG Specialization</label>
                          <input
                            type="text"
                            placeholder="e.g. Cloud Computing"
                            value={profile.pg_specialization}
                            onChange={(e) => handleProfileChange('pg_specialization', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">PG CGPA</label>
                          <input
                            type="text"
                            placeholder="e.g. 9.10"
                            value={profile.pg_cgpa}
                            onChange={(e) => handleProfileChange('pg_cgpa', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">PG Passing Year</label>
                          <input
                            type="text"
                            placeholder="e.g. 2028"
                            value={profile.pg_passing_year}
                            onChange={(e) => handleProfileChange('pg_passing_year', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600 font-mono"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Class 10th Record */}
                    <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-3">
                      <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                        <Award className="w-3.5 h-3.5 text-amber-400" />
                        <span>Class 10th / Secondary School Record</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">10th Percentage / CGPA</label>
                          <input
                            type="text"
                            placeholder="e.g. 94.2%"
                            value={profile.tenth_percentage}
                            onChange={(e) => handleProfileChange('tenth_percentage', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">10th Board</label>
                          <input
                            type="text"
                            placeholder="e.g. CBSE / ICSE / State"
                            value={profile.tenth_board}
                            onChange={(e) => handleProfileChange('tenth_board', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">10th Passing Year</label>
                          <input
                            type="text"
                            placeholder="e.g. 2020"
                            value={profile.tenth_passing_year}
                            onChange={(e) => handleProfileChange('tenth_passing_year', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600 font-mono"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Class 12th / Diploma Record */}
                    <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-3">
                      <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                        <Award className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Class 12th / Intermediate / Diploma Record</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">12th Percentage / CGPA</label>
                          <input
                            type="text"
                            placeholder="e.g. 91.8%"
                            value={profile.twelfth_percentage}
                            onChange={(e) => handleProfileChange('twelfth_percentage', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">12th Board</label>
                          <input
                            type="text"
                            placeholder="e.g. CBSE / ISC / State"
                            value={profile.twelfth_board}
                            onChange={(e) => handleProfileChange('twelfth_board', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">12th Passing Year</label>
                          <input
                            type="text"
                            placeholder="e.g. 2022"
                            value={profile.twelfth_passing_year}
                            onChange={(e) => handleProfileChange('twelfth_passing_year', e.target.value)}
                            className="w-full px-3 py-2 rounded-lg glass-input text-xs text-white placeholder-slate-600 font-mono"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* ============================================================= */}
              {/* SECTION 3: PROFESSIONAL EXPERIENCE & TARGET ROLE              */}
              {/* ============================================================= */}
              <div className="rounded-xl border border-purple-500/20 bg-slate-900/40 overflow-hidden transition-all">
                <button
                  type="button"
                  onClick={() => toggleSection('professional')}
                  className="w-full px-4 py-3.5 flex items-center justify-between bg-purple-500/5 hover:bg-purple-500/10 border-b border-purple-500/10 text-left transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-2.5">
                    <Briefcase className="w-4 h-4 text-purple-400" />
                    <span className="font-bold text-sm text-white">3. Professional Experience & Preferences</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      {countFilled(professionalKeys)} / {professionalKeys.length} Filled
                    </span>
                  </div>
                  <div className="text-slate-400">
                    {openSections.professional ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>

                {openSections.professional && (
                  <div className="p-4 space-y-4 animate-in fade-in duration-200">
                    {/* Target Applying For Role */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                        <Briefcase className="w-3.5 h-3.5 text-purple-400" />
                        <span>Target Role Applying For <span className="text-rose-400">*</span></span>
                      </label>
                      <select
                        value={profile.applying_for_role}
                        onChange={(e) => handleProfileChange('applying_for_role', e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white bg-slate-900 border border-white/10 cursor-pointer"
                      >
                        {APPLYING_FOR_ROLE_OPTIONS.map((opt) => (
                          <option key={opt} value={opt} className="bg-slate-900 text-white">
                            {opt}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Internship Organization */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                        <Building2 className="w-3.5 h-3.5 text-slate-400" />
                        <span>Internship Organization / Company Name</span>
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Amazon Web Services (AWS) / Microsoft"
                        value={profile.internship_organization}
                        onChange={(e) => handleProfileChange('internship_organization', e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl glass-input text-sm text-white placeholder-slate-500"
                      />
                    </div>

                    {/* Internship Topic */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                        <FileBadge className="w-3.5 h-3.5 text-slate-400" />
                        <span>Internship Project Topic / Domain</span>
                      </label>
                      <textarea
                        rows={2}
                        placeholder="e.g. Distributed Cloud Microservices & Scalable Telemetry Infrastructure"
                        value={profile.internship_topic}
                        onChange={(e) => handleProfileChange('internship_topic', e.target.value)}
                        className="w-full p-3 rounded-xl glass-input text-sm text-white placeholder-slate-500 resize-none font-sans"
                      />
                    </div>

                    {/* Extra Certifications */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                        <Award className="w-3.5 h-3.5 text-slate-400" />
                        <span>Extra Technical Certifications & Skills</span>
                      </label>
                      <textarea
                        rows={2}
                        placeholder="e.g. AWS Certified Solutions Architect, Oracle Java Associate, Coursera Deep Learning"
                        value={profile.extra_certifications}
                        onChange={(e) => handleProfileChange('extra_certifications', e.target.value)}
                        className="w-full p-3 rounded-xl glass-input text-sm text-white placeholder-slate-500 resize-none font-sans"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Save Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSavingProfile}
                  className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg cursor-pointer ${
                    isSaved
                      ? 'bg-emerald-600 text-white shadow-emerald-600/20 ring-2 ring-emerald-400'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/25 active:scale-[0.99]'
                  }`}
                >
                  {isSavingProfile ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Saving CRC Profile to Supabase...</span>
                    </>
                  ) : isSaved ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-white animate-bounce" />
                      <span>CRC Profile Synchronized to Supabase Database!</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>Save Master CRC Profile</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>

          {/* ================================================================= */}
          {/* CARD 2: THE MAGIC LINK GENERATOR (5 Cols on large screens)        */}
          {/* ================================================================= */}
          <section className="lg:col-span-5 rounded-2xl glass-panel p-5 sm:p-6 relative overflow-hidden border border-white/10 flex flex-col sticky top-24">
            {/* Ambient Purple Glow */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

            <div className="pb-5 border-b border-white/10 mb-6 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">The Magic Link Generator</h2>
                  <p className="text-xs text-slate-400">Auto-injects CRC profile into Google Form entries</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleGenerateLink} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Paste Google Form URL Here
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <LinkIcon className="w-4 h-4 text-purple-400" />
                  </div>
                  <input
                    type="url"
                    required
                    placeholder="https://docs.google.com/forms/d/e/.../viewform"
                    value={formUrl}
                    onChange={(e) => setFormUrl(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl glass-input text-xs sm:text-sm text-white placeholder-slate-500 font-mono focus:border-purple-500 focus:ring-purple-500/20"
                  />
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 flex items-center space-x-1">
                  <span>Supports both</span>
                  <code className="text-slate-300 bg-white/5 px-1 py-0.5 rounded text-[10px]">docs.google.com/forms</code>
                  <span>and</span>
                  <code className="text-slate-300 bg-white/5 px-1 py-0.5 rounded text-[10px]">forms.gle</code>
                </p>
              </div>

              {/* Large Prominent Generate Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-5 rounded-xl font-bold text-sm sm:text-base text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:via-indigo-400 hover:to-purple-500 transition-all duration-200 shadow-lg shadow-indigo-500/25 flex items-center justify-center space-x-2.5 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed group cursor-pointer"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Matching CRC Fields & Generating...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5 text-amber-300 fill-amber-300 group-hover:scale-110 transition-transform" />
                    <span>Generate Magic Link</span>
                    <ArrowRight className="w-4 h-4 text-indigo-200 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            {/* Error Message Display */}
            {error && (
              <div className="mt-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start space-x-2.5 animate-in fade-in slide-in-from-top-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="text-xs text-rose-200">
                  <p className="font-semibold text-rose-300">Generation Failed</p>
                  <p className="mt-0.5">{error}</p>
                </div>
              </div>
            )}

            {/* Success Result Container */}
            {result && (
              <div className="mt-5 space-y-4 animate-in fade-in slide-in-from-top-3 duration-300">
                <div className="p-4 rounded-2xl bg-gradient-to-b from-indigo-950/40 to-slate-900/60 border border-indigo-500/30 shadow-xl">
                  <div className="flex items-center justify-between mb-2.5">
                    <div className="flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                        Magic Link Ready
                      </span>
                    </div>
                    {result.form_title && (
                      <span className="text-[11px] text-slate-300 font-medium px-2 py-0.5 bg-white/5 border border-white/10 rounded-full max-w-[180px] truncate">
                        {result.form_title}
                      </span>
                    )}
                  </div>

                  {/* Pre-filled URL Display Box */}
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Pre-Filled Google Form URL
                  </label>
                  
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 p-2.5 rounded-xl bg-slate-950/90 border border-white/10 font-mono text-[11px] text-indigo-300 break-all select-all max-h-20 overflow-y-auto">
                      <a 
                        href={result.prefilled_url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="hover:underline flex items-center space-x-1 text-indigo-300 hover:text-indigo-200"
                      >
                        <span>{result.prefilled_url}</span>
                      </a>
                    </div>

                    {/* Copy to Clipboard Icon Button */}
                    <button
                      type="button"
                      onClick={handleCopy}
                      title="Copy to Clipboard"
                      className={`p-2.5 rounded-xl border transition-all duration-150 flex items-center justify-center shrink-0 cursor-pointer ${
                        copied
                          ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400 ring-2 ring-emerald-500/30'
                          : 'bg-white/5 hover:bg-white/10 border-white/10 text-slate-200 hover:text-white active:scale-95'
                      }`}
                    >
                      {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Actions Row */}
                  <div className="mt-3.5 flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-white/10">
                    <div className="text-[11px] text-slate-400">
                      Matched <strong className="text-white">{result.total_matched}</strong> of <strong className="text-white">{result.total_questions_found}</strong> form entries
                    </div>

                    <a
                      href={result.prefilled_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-indigo-500 text-white hover:bg-indigo-400 transition-colors shadow-sm"
                    >
                      <span>Open Pre-filled Form</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>

                {/* Matched Fields Breakdown Drawer */}
                {result.matched_fields && result.matched_fields.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-slate-900/50 border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                        <Layers className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Autofill Mapping Breakdown</span>
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {result.matched_fields.length} parameters injected
                      </span>
                    </div>

                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1 text-xs">
                      {result.matched_fields.map((field, idx) => (
                        <div 
                          key={idx} 
                          className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-white/5"
                        >
                          <div className="truncate mr-2">
                            <span className="text-slate-400 font-mono text-[10px]">entry.{field.entry_id}</span>
                            <span className="text-slate-300 ml-2 font-medium text-xs">"{field.question_title}"</span>
                          </div>
                          <div className="shrink-0 font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 max-w-[130px] truncate text-[11px]">
                            {field.value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-6 text-center text-xs text-slate-400 mt-auto">
        <p>AutoForm AI (CRC Edition) • Automated Google Form Prefiller Service • Powered by Supabase & FastAPI</p>
      </footer>
    </div>
  );
}
