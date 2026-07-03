import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () =>
      import('./auth/login/login').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./auth/register/register').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./dashboard/dashboard').then(m => m.DashboardComponent),
    canActivate: [authGuard]   // protected — guard runs before this route activates
  },
  {
    path: 'upload',
    loadComponent: () =>
      import('./upload/upload').then(m => m.UploadComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'login' }
];