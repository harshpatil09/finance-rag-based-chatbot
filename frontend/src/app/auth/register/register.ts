import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.html'
})
export class RegisterComponent {
  form: FormGroup;
  loading = false;
  error = '';
  success = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  get email() { return this.form.get('email'); }
  get password() { return this.form.get('password'); }

  onSubmit(): void {
    if (this.form.invalid) return;

    this.loading = true;
    this.error = '';

    this.authService.register(this.form.value).subscribe({
      next: () => {
        // After register, auto-login so user lands directly on dashboard
        this.authService.login(this.form.value).subscribe({
          next: () => this.router.navigate(['/dashboard']),
          error: () => this.router.navigate(['/login'])
        });
      },
      error: (err) => {
        this.error = err.error?.detail || 'Registration failed. Please try again.';
        this.loading = false;
      }
    });
  }
}