import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { of } from 'rxjs';
import { HttpEventType } from '@angular/common/http';
import { UploadComponent } from './upload';
import { UploadService } from '../core/services/upload';

// Mock the service — never call real HTTP in unit tests
const mockUploadService = {
  uploadReport: jasmine.createSpy('uploadReport').and.returnValue(
    of({ type: HttpEventType.Response, body: {
      id: '1', filename: 'test.pdf', file_size: 1024,
      company_name: 'Apple', quarter: 'Q3 2024',
      status: 'uploaded', uploaded_at: new Date().toISOString()
    }})
  )
};

describe('UploadComponent', () => {
  let component: UploadComponent;
  let fixture: ComponentFixture<UploadComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UploadComponent, ReactiveFormsModule],
      providers: [
        { provide: UploadService, useValue: mockUploadService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should disable submit when no file selected', () => {
    const btn = fixture.nativeElement.querySelector('button[type="submit"]');
    expect(btn.disabled).toBeTrue();
  });

  it('should reject non-PDF files', () => {
    const fakeFile = new File(['content'], 'report.txt', { type: 'text/plain' });
    component['setFile'](fakeFile);  // calling private method directly in tests is fine
    expect(component.error).toBe('Only PDF files are accepted');
    expect(component.selectedFile).toBeNull();
  });

  it('should accept PDF files', () => {
    const fakeFile = new File(['%PDF'], 'report.pdf', { type: 'application/pdf' });
    component['setFile'](fakeFile);
    expect(component.selectedFile).toBeTruthy();
    expect(component.error).toBe('');
  });

  it('should show success card after upload', () => {
    const fakeFile = new File(['%PDF'], 'report.pdf', { type: 'application/pdf' });
    component['setFile'](fakeFile);
    component.form.setValue({ companyName: 'Apple', quarter: 'Q3 2024' });
    component.onSubmit();
    fixture.detectChanges();

    const successCard = fixture.nativeElement.querySelector('.success-card');
    expect(successCard).toBeTruthy();
  });
});