import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'   // singleton, available app-wide, no module import needed
})
export class HealthService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  checkHealth(): Observable<{ status: string; message: string }> {
    return this.http.get<{ status: string; message: string }>(`${this.apiUrl}/health`);
  }
}