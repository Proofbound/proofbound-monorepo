import { useState, useEffect } from 'react';
import { User } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session }, error }) => {
      // Check if there's an auth error (expired/invalid tokens)
      if (error) {
        // Silently clear any invalid session data
        supabase.auth.signOut();
        setUser(null);
        // Don't log 401 errors as they're expected when tokens expire
        if (!error.message.includes('refresh_token') && !error.message.includes('401')) {
          console.error('Auth session error:', error);
        }
      } else {
        setUser(session?.user ?? null);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null);
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { data, error };
  };

  const signUp = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: undefined, // Disable email confirmation
      },
    });
    return { data, error };
  };

  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      // Clear user state immediately regardless of API response
      setUser(null);
      // Don't treat 403/401 errors as failures for signout - user is logged out either way
      if (error && !error.message.includes('403') && !error.message.includes('401')) {
        console.warn('Signout warning:', error);
        return { error };
      }
      return { error: null };
    } catch (err) {
      // Force local signout even if API call fails
      setUser(null);
      console.warn('Signout failed, cleared local session:', err);
      return { error: null };
    }
  };

  return {
    user,
    loading,
    signIn,
    signUp,
    signOut,
  };
}