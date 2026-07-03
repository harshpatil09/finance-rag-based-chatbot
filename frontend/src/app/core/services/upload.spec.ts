import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UploadService } from './upload';
import { environment } from '../../../environments/environment';

describe('UploadService', () => {
  let service: UploadService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],  // fake HttpClient — no real requests
      providers: [UploadService]
    });
    service = TestBed.inject(UploadService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();  // fails the test if any unexpected HTTP calls were made
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should POST to the correct upload URL', () => {
    const file = new File(['%PDF'], 'test.pdf', { type: 'application/pdf' });

    service.uploadReport(file, 'Apple', 'Q3 2024').subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/upload`);
    expect(req.request.method).toBe('POST');
    req.flush({ id: '1', status: 'uploaded' });
  });
});