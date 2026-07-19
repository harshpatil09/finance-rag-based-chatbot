import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ChatService, ChatMessage } from '../core/services/chat';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './chat.html'
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messageContainer') messageContainer!: ElementRef;

  reportId = '';
  question = '';
  messages: ChatMessage[] = [];
  loading = false;

  constructor(
    private route: ActivatedRoute,
    private chatService: ChatService,
    private cdr: ChangeDetectorRef    // ← add this
  ) {}

  ngOnInit() {
    this.reportId = this.route.snapshot.paramMap.get('reportId') || '';
    this.messages.push({
      role: 'assistant',
      content: 'Hello! I\'ve analyzed this financial report. Ask me anything about revenue, profits, margins, cash flow, or any other financial metrics.'
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  sendMessage() {
    if (!this.question.trim() || this.loading) return;

    const userQuestion = this.question.trim();
    this.question = '';

    this.messages.push({ role: 'user', content: userQuestion });
    this.messages.push({ role: 'assistant', content: '', loading: true });
    this.loading = true;
    this.cdr.detectChanges();    // ← force loading dots to appear

    this.chatService.ask(userQuestion, this.reportId).subscribe({
      next: (response) => {
        const loadingIndex = this.messages.map(m => m.loading).lastIndexOf(true);
        if (loadingIndex !== -1) {
          this.messages[loadingIndex] = {
            role: 'assistant',
            content: response.answer,
            sources: response.sources,
            loading: false
          };
        }
        this.loading = false;
        this.cdr.detectChanges();    // ← 
      },
      error: () => {
        const loadingIndex = this.messages.map(m => m.loading).lastIndexOf(true);
        if (loadingIndex !== -1) {
          this.messages[loadingIndex] = {
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            loading: false
          };
        }
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  private scrollToBottom() {
    try {
      this.messageContainer.nativeElement.scrollTop =
        this.messageContainer.nativeElement.scrollHeight;
    } catch {}
  }
}