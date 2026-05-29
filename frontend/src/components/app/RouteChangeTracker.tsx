import { PropsWithChildren, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

import { reportNavigation } from '@/lib/runtime-monitoring';

export function RouteChangeTracker({ children }: PropsWithChildren) {
  const location = useLocation();

  useEffect(() => {
    reportNavigation(`${location.pathname}${location.search}`);
  }, [location.pathname, location.search]);

  return <>{children}</>;
}
