import { Component } from '@angular/core';
import { AuthService } from '../core/services/auth';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.html'
})
export class DashboardComponent {
  constructor(private authService: AuthService) {}
  logout() { this.authService.logout(); }
}