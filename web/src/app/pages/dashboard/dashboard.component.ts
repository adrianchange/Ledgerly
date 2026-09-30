import { CurrencyPipe, DatePipe, NgFor, NgIf } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { CATEGORIES, CATEGORY_LABELS, Expense, MonthSummary } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [ReactiveFormsModule, NgFor, NgIf, CurrencyPipe, DatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ApiService);
  readonly auth = inject(AuthService);

  readonly categories = CATEGORIES;
  readonly labels = CATEGORY_LABELS;
  readonly expenses = signal<Expense[]>([]);
  readonly summary = signal<MonthSummary | null>(null);
  readonly linkCode = signal<string | null>(null);
  readonly error = signal('');
  readonly maxCategory = computed(() => {
    const rows = this.summary()?.by_category ?? [];
    return Math.max(1, ...rows.map((r) => Number(r.total)));
  });

  form = this.fb.nonNullable.group({
    amount: [null as number | null, [Validators.required, Validators.min(0.01)]],
    category: ['food' as string, Validators.required],
    note: [''],
    spent_at: [new Date().toISOString().slice(0, 10), Validators.required],
  });

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.error.set('');
    this.api.listExpenses().subscribe({
      next: (rows) => this.expenses.set(rows),
      error: () => this.error.set('No se pudieron cargar los gastos'),
    });
    this.api.monthSummary().subscribe({
      next: (s) => this.summary.set(s),
      error: () => undefined,
    });
  }

  add(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    this.api
      .createExpense({
        amount: v.amount!,
        category: v.category,
        note: v.note || null,
        spent_at: v.spent_at,
      })
      .subscribe({
        next: () => {
          this.form.patchValue({ amount: null, note: '' });
          this.reload();
        },
        error: (err) => this.error.set(err?.error?.detail || 'No se pudo guardar'),
      });
  }

  remove(id: number): void {
    this.api.deleteExpense(id).subscribe({
      next: () => this.reload(),
      error: () => this.error.set('No se pudo borrar'),
    });
  }

  linkTelegram(): void {
    this.api.createLinkCode().subscribe({
      next: (res) => this.linkCode.set(res.code),
      error: () => this.error.set('No se pudo generar el código'),
    });
  }

  barWidth(total: string): string {
    return `${Math.round((Number(total) / this.maxCategory()) * 100)}%`;
  }
}
