import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/utils/auth';

export default function Login() {
  const router = useRouter();
  const { user } = useAuth();
  const { redirect } = router.query;

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push((redirect as string) || '/');
    }
  }, [user, router, redirect]);

  const handleLoginSuccess = () => {
    router.push((redirect as string) || '/');
  };

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center py-12">
      <div className="w-full max-w-md">
        <LoginForm onSuccess={handleLoginSuccess} />
      </div>
    </div>
  );
}
