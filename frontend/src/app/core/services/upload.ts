import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ReportResponse {
  id: string;
  filename: string;
  file_size: number;
  company_name: string;
  quarter: string;
  status: string;
  uploaded_at: string;
}

@Injectable({ providedIn: 'root' })
export class UploadService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  uploadReport(
    file: File,
    companyName: string,
    quarter: string
  ): Observable<HttpEvent<ReportResponse>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', companyName);
    formData.append('quarter', quarter);

    // HttpRequest (vs http.post) gives us progress events —
    // essential for the progress bar. reportProgress: true
    // makes Angular emit upload percentage events as the file uploads.
    const req = new HttpRequest('POST', `${this.apiUrl}/upload`, formData, {
      reportProgress: true
    });

    return this.http.request<ReportResponse>(req);
  }
}