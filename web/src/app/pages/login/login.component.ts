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
      this.error = this.validationMessage();
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
        this.error = this.formatHttpError(err);
      },
    });
  }

  private validationMessage(): string {
    const email = this.form.controls.email;
    const password = this.form.controls.password;
    if (email.hasError('required')) return 'El email es obligatorio';
    if (email.hasError('email')) return 'Email no válido';
    if (password.hasError('required')) return 'La contraseña es obligatoria';
    if (password.hasError('minlength')) return 'La contraseña debe tener al menos 8 caracteres';
    return 'Revisa el formulario';
  }

  private formatHttpError(err: unknown): string {
    const detail = (err as { error?: { detail?: unknown } })?.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === 'string') return item;
          if (item && typeof item === 'object' && 'msg' in item) {
            return String((item as { msg: string }).msg);
          }
          return JSON.stringify(item);
        })
        .join(' · ');
    }
    if (detail != null) return String(detail);
    return 'No se pudo autenticar. ¿Está la API en :8000?';
  }
}
