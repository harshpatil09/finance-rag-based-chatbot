import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  // Default redirect
  { path: '', redirectTo: 'home', pathMatch: 'full' },

  // Auth routes (public)
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

  // Protected routes
  {
    path: 'home',
    loadComponent: () =>
      import('./dashboard/dashboard').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'upload',
    loadComponent: () =>
      import('./upload/upload').then(m => m.UploadComponent),
    canActivate: [authGuard]
  },
  {
    path: 'dashboard/:reportId',
    loadComponent: () =>
      import('./dashboard/report-dashboard/report-dashboard')
        .then(m => m.ReportDashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'chat/:reportId',
    loadComponent: () =>
      import('./chat/chat').then(m => m.ChatComponent),
    canActivate: [authGuard]
  },

  // Fallback
  { path: '**', redirectTo: 'login' }
];