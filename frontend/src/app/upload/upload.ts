import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { UploadService, ReportResponse } from '../core/services/upload';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './upload.html'
})
export class UploadComponent {
  form: FormGroup;
  selectedFile: File | null = null;
  dragOver = false;
  uploadProgress = 0;
  uploading = false;
  uploadedReport: ReportResponse | null = null;
  processingResult: any = null;
  error = '';

  constructor(
    private fb: FormBuilder,
    private uploadService: UploadService,
    private http: HttpClient          // ← added for processing call
  ) {
    this.form = this.fb.group({
      companyName: ['', Validators.required],
      quarter: ['', Validators.required]
    });
  }

  onDragOver(event: DragEvent) { event.preventDefault(); this.dragOver = true; }
  onDragLeave() { this.dragOver = false; }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    const file = event.dataTransfer?.files[0];
    if (file) this.setFile(file);
  }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this.setFile(input.files[0]);
  }

  private setFile(file: File) {
    if (file.type !== 'application/pdf') {
      this.error = 'Only PDF files are accepted';
      return;
    }
    this.selectedFile = file;
    this.error = '';
  }

  onSubmit() {
    if (!this.selectedFile || this.form.invalid) return;
    this.uploading = true;
    this.uploadProgress = 0;
    this.error = '';

    const { companyName, quarter } = this.form.value;

    this.uploadService.uploadReport(this.selectedFile, companyName, quarter).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * event.loaded / event.total);
        }
        if (event.type === HttpEventType.Response) {
          this.uploadedReport = event.body!;
          this.uploading = false;
          this.triggerProcessing(event.body!.id);  // ← auto-trigger pipeline
        }
      },
      error: (err) => {
        this.error = err.error?.detail || 'Upload failed. Please try again.';
        this.uploading = false;
      }
    });
  }

  private triggerProcessing(reportId: string) {
    this.http.post(`${environment.apiUrl}/process/${reportId}`, {}).subscribe({
      next: (result: any) => {
        this.processingResult = result;
      },
      error: () => {
        // processing failed silently — user sees upload success at least
        // we'll add proper error handling in M8
      }
    });
  }

  formatBytes(bytes: number): string {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  }
}