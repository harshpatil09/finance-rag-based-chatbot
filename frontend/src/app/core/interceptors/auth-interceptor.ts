import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth';

// Functional interceptor (Angular 17+ style — no class needed)
export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  // If we have a token, clone the request and add the Authorization header.
  // We CLONE because HttpRequest objects are immutable — you cannot modify them,
  // only create a new one with the changes you want.
  if (token) {
    const authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(authReq);
  }

  // No token — pass the request through unchanged (e.g. login/register calls)
  return next(req);
};