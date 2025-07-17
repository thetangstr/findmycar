import { useEffect, useLayoutEffect } from 'react';

/**
 * useIsomorphicLayoutEffect ensures we don't run useLayoutEffect on the server
 * to avoid React warnings during SSR. It falls back to useEffect when
 * window is undefined.
 */
export const useIsomorphicLayoutEffect =
  typeof window !== 'undefined' ? useLayoutEffect : useEffect;
