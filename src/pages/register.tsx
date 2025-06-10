import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import RegisterForm from '@/components/auth/RegisterForm';
import { useAuth } from '@/utils/auth';

export default function Register() {
  const router = useRouter();
  const { user } = useAuth();
  const { redirect } = router.query;

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push((redirect as string) || '/');
    }
  }, [user, router, redirect]);

  const handleRegisterSuccess = () => {
    router.push((redirect as string) || '/');
  };

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center py-12">
      <div className="w-full max-w-md">
        <RegisterForm onSuccess={handleRegisterSuccess} />
      </div>
    </div>
  );
}
