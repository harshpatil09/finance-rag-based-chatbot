import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportDashboard } from './report-dashboard';

describe('ReportDashboard', () => {
  let component: ReportDashboard;
  let fixture: ComponentFixture<ReportDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(ReportDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
