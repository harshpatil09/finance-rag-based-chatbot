import { Component } from '@angular/core';
import { AuthService } from '../core/services/auth';
import { RouterLink } from '@angular/router';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports : [RouterLink],
  templateUrl: './dashboard.html'
})
export class DashboardComponent {
  constructor(private authService: AuthService) {}
  logout() { this.authService.logout(); }
}