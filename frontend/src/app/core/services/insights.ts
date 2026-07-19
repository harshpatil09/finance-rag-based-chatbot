import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ReportInsight {
  report_id: string;
  total_revenue: number | null;
  net_income: number | null;
  gross_profit: number | null;
  operating_income: number | null;
  eps_basic: number | null;
  eps_diluted: number | null;
  gross_margin: number | null;
  net_margin: number | null;
  total_assets: number | null;
  total_liabilities: number | null;
  total_equity: number | null;
  operating_cash_flow: number | null;
  extracted_at: string;
}

@Injectable({ providedIn: 'root' })
export class InsightsService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getInsights(reportId: string): Observable<ReportInsight> {
    return this.http.get<ReportInsight>(`${this.apiUrl}/insights/${reportId}`);
  }

  refreshInsights(reportId: string): Observable<ReportInsight> {
    return this.http.post<ReportInsight>(`${this.apiUrl}/insights/${reportId}/refresh`, {});
  }
}