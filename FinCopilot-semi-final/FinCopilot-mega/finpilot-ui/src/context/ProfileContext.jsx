import { createContext, useContext, useState, useEffect } from 'react';

const STORAGE_KEY = 'finpilot_profile';

const defaults = {
  income_monthly: 15000,
  monthly_expenses: 9000,
  savings: 20000,
};

const ProfileContext = createContext({ profile: defaults, setProfile: () => {} });

export function useProfile() {
  return useContext(ProfileContext);
}

export function ProfileProvider({ children }) {
  const [profile, setProfileState] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const setProfile = (p) => {
    const merged = { ...defaults, ...p };
    setProfileState(merged);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
  };

  // Build the full profile object with derived fields for API compatibility
  const fullProfile = profile
    ? {
        ...profile,
        existing_debt_monthly_EMI: 0,
        requested_loan_amount: 50000,
        proposed_EMI: 2500,
        expected_skill_earning_uplift_pct: 20,
        emergency_fund_amount: profile.savings || 10000,
        course_length_months: 6,
        goals: [{ name: 'Savings', required_amount: 100000, target_date: '2027-06' }],
      }
    : null;

  return (
    <ProfileContext.Provider value={{ profile: fullProfile, setProfile, hasProfile: !!profile }}>
      {children}
    </ProfileContext.Provider>
  );
}
