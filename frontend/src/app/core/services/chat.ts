import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ChatSource {
  rank: number;
  score: number;
  section: string;
  page: number;
  chunk_type: string;
  preview: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  question: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  loading?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  ask(question: string, reportId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, {
      question,
      report_id: reportId,
      top_k: 5
    });
  }
}