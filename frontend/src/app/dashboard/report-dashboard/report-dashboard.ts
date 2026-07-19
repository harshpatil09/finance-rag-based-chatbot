import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { NgApexchartsModule } from 'ng-apexcharts';
import { InsightsService, ReportInsight } from '../../core/services/insights';

@Component({
  selector: 'app-report-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, NgApexchartsModule],
  templateUrl: './report-dashboard.html'
})
export class ReportDashboardComponent implements OnInit {
  reportId = '';
  insight: ReportInsight | null = null;
  loading = true;
  error = '';

  chartOptions: any = { series: [], chart: { type: 'bar', height: 250, toolbar: { show: false } }, plotOptions: { bar: { borderRadius: 6, columnWidth: '45%' } }, colors: ['#185FA5', '#639922'], xaxis: { categories: ['Gross Margin %', 'Net Margin %'] }, yaxis: { labels: { formatter: (v: number) => v + '%' } }, tooltip: { y: { formatter: (v: number) => v.toFixed(2) + '%' } }, dataLabels: { enabled: true, formatter: (v: number) => v.toFixed(1) + '%' } };
  plChartOptions: any = { series: [], chart: { type: 'bar', height: 250, toolbar: { show: false } }, plotOptions: { bar: { borderRadius: 6, horizontal: true } }, colors: ['#185FA5'], xaxis: { labels: { formatter: (v: number) => '$' + (v/1000).toFixed(0) + 'B' } }, dataLabels: { enabled: false }, tooltip: { y: { formatter: (v: number) => '$' + v.toLocaleString() + 'M' } } };

  constructor(
    private route: ActivatedRoute,
    private insightsService: InsightsService,
    private cdr: ChangeDetectorRef    // ← add this
  ) {}

  ngOnInit() {
    this.reportId = this.route.snapshot.paramMap.get('reportId') || '';
    this.loadInsights();
  }

  loadInsights() {
    this.insightsService.getInsights(this.reportId).subscribe({
      next: (data) => {
        this.insight = data;
        this.loading = false;
        this.buildCharts(data);
        this.cdr.detectChanges();    // ← force render
      },
      error: () => {
        this.error = 'Could not load insights. Try refreshing.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  buildCharts(data: ReportInsight) {
    this.chartOptions = {
      ...this.chartOptions,
      series: [{ name: 'Margin', data: [data.gross_margin ?? 0, data.net_margin ?? 0] }]
    };
    this.plChartOptions = {
      ...this.plChartOptions,
      series: [{ name: 'USD (millions)', data: [data.total_revenue ?? 0, data.gross_profit ?? 0, data.operating_income ?? 0, data.net_income ?? 0] }],
      xaxis: { ...this.plChartOptions.xaxis, categories: ['Revenue', 'Gross Profit', 'Operating Income', 'Net Income'] }
    };
    this.cdr.detectChanges();    // ← force charts to render
  }

  formatMillions(val: number | null): string {
    if (val === null) return 'N/A';
    if (val >= 1000) return '$' + (val / 1000).toFixed(2) + 'B';
    return '$' + val.toFixed(0) + 'M';
  }

  refreshInsights() {
    this.loading = true;
    this.insightsService.refreshInsights(this.reportId).subscribe({
      next: (data) => {
        this.insight = data;
        this.loading = false;
        this.buildCharts(data);
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Refresh failed.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}