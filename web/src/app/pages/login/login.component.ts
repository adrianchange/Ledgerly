import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  mode: 'login' | 'register' = 'login';
  error = '';
  loading = false;

  form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  toggle(): void {
    this.mode = this.mode === 'login' ? 'register' : 'login';
    this.error = '';
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.error = '';
    const { email, password } = this.form.getRawValue();
    const req$ = this.mode === 'login' ? this.auth.login(email, password) : this.auth.register(email, password);
    req$.subscribe({
      next: () => {
        this.loading = false;
        void this.router.navigateByUrl('/');
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'No se pudo autenticar';
      },
    });
  }
}
