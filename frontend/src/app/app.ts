import { Component, OnInit } from '@angular/core';
import { HealthService } from './core/services/health';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `<h1>Backend says: {{ backendStatus }}</h1>`
})
export class AppComponent implements OnInit {
  backendStatus = 'checking...';

  constructor(private healthService: HealthService) {}

  ngOnInit() {
    this.healthService.checkHealth().subscribe({
      next: (res) => this.backendStatus = res.message,
      error: () => this.backendStatus = 'Could not reach backend ✗'
    });
  }
}