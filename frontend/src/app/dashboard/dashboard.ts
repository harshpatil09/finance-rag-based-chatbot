import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../core/services/auth';
import { NavbarComponent } from '../core/components/navbar/navbar';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, NavbarComponent],
  templateUrl: './dashboard.html'
})
export class DashboardComponent implements OnInit {
  reports: any[] = [];

  constructor(
    private authService: AuthService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.loadReports();
  }

  loadReports() {
    this.http.get<any[]>(`${environment.apiUrl}/reports`).subscribe({
      next: (data) => this.reports = data,
      error: () => this.reports = []
    });
  }

  logout() { this.authService.logout(); }
}