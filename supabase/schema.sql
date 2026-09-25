-- ==============================================================================
-- Supabase PostgreSQL Schema for AutoForm AI Profiles (CRC Compliant)
-- ==============================================================================
-- Run this in your Supabase SQL Editor:
-- https://app.supabase.com/project/_/sql
-- ==============================================================================

-- 1. Create the `profiles` table linked to Supabase auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Personal & Contact Information
    enrollment_no TEXT,
    full_name TEXT,
    dob TEXT,
    gender TEXT,
    home_location TEXT,
    permanent_address TEXT,
    contact_no TEXT,
    alt_contact_no TEXT,
    personal_email TEXT,
    institutional_email TEXT,
    driving_license_yes_no TEXT,
    
    -- Academic Record
    school_name TEXT,
    category_ug_pg TEXT,
    course TEXT,
    ug_specialization TEXT,
    ug_cgpa TEXT,
    ug_passing_year TEXT,
    pg_specialization TEXT,
    pg_cgpa TEXT,
    pg_passing_year TEXT,
    tenth_percentage TEXT,
    tenth_board TEXT,
    tenth_passing_year TEXT,
    twelfth_percentage TEXT,
    twelfth_board TEXT,
    twelfth_passing_year TEXT,
    
    -- Professional Experience
    internship_organization TEXT,
    internship_topic TEXT,
    extra_certifications TEXT,
    applying_for_role TEXT,
    
    -- Legacy / Social & Dynamic fields
    email TEXT,
    phone TEXT,
    student_id TEXT,
    date_of_birth TEXT,
    university TEXT,
    major TEXT,
    degree TEXT,
    graduation_year TEXT,
    current_year_of_study TEXT,
    gpa TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    resume_url TEXT,
    tech_stack TEXT,
    bio TEXT,
    custom_fields JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Comments for Supabase Dashboard
COMMENT ON TABLE public.profiles IS 'Stores persistent CRC student profile information for automated Google Form filling.';
COMMENT ON COLUMN public.profiles.id IS 'References the auth.users uuid of the authenticated user.';
COMMENT ON COLUMN public.profiles.enrollment_no IS 'University enrollment or roll number.';
COMMENT ON COLUMN public.profiles.custom_fields IS 'Arbitrary key-value mappings for dynamic form question matching.';

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 3. Row Level Security Policies
-- Users can only read, insert, update, or delete their own profile record.

DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can delete own profile" ON public.profiles;
CREATE POLICY "Users can delete own profile"
    ON public.profiles
    FOR DELETE
    USING (auth.uid() = id);

-- 4. Function & Trigger: Automatically set `updated_at` on row modification
CREATE OR REPLACE FUNCTION public.handle_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_profiles_updated ON public.profiles;
CREATE TRIGGER on_profiles_updated
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_profile_updated_at();

-- 5. Function & Trigger: Automatically insert profile row upon user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    user_full_name TEXT;
BEGIN
    user_full_name := COALESCE(
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'name',
        ''
    );

    INSERT INTO public.profiles (
        id,
        email,
        personal_email,
        full_name,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,
        NEW.email,
        NEW.email,
        user_full_name,
        timezone('utc'::text, now()),
        timezone('utc'::text, now())
    )
    ON CONFLICT (id) DO UPDATE
    SET
        email = EXCLUDED.email,
        personal_email = CASE WHEN public.profiles.personal_email IS NULL OR public.profiles.personal_email = '' THEN EXCLUDED.personal_email ELSE public.profiles.personal_email END,
        full_name = CASE WHEN public.profiles.full_name IS NULL OR public.profiles.full_name = '' THEN EXCLUDED.full_name ELSE public.profiles.full_name END,
        updated_at = timezone('utc'::text, now());

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger the function every time a user is created in auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
