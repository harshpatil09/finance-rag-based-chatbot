import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticatedSync()) {
    return true; // allow navigation to the protected route
  }

  // Not logged in — redirect to login, block the navigation
  router.navigate(['/login']);
  return false;
};