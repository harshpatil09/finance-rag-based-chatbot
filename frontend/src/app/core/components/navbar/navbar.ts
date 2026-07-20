import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink],
  template: `
    <nav class="navbar">
      <a routerLink="/home" class="navbar-brand">
        <div class="brand-icon">F</div>
        <div class="brand-name">FinSight <span>AI</span></div>
      </a>
      <div class="navbar-spacer"></div>
      <div class="navbar-actions">
        <a routerLink="/upload" class="btn btn-primary btn-sm">+ Upload report</a>
        <button class="btn btn-secondary btn-sm" (click)="logout()">Sign out</button>
      </div>
    </nav>
  `
})
export class NavbarComponent {
  constructor(private authService: AuthService) {}
  logout() { this.authService.logout(); }
}