import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Expense, LinkCode, MonthSummary } from './models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private readonly http: HttpClient) {}

  listExpenses(year?: number, month?: number): Observable<Expense[]> {
    let params = new HttpParams();
    if (year != null) params = params.set('year', year);
    if (month != null) params = params.set('month', month);
    return this.http.get<Expense[]>(`${environment.apiUrl}/api/expenses`, { params });
  }

  createExpense(body: {
    amount: number | string;
    category: string;
    note?: string | null;
    spent_at?: string | null;
  }): Observable<Expense> {
    return this.http.post<Expense>(`${environment.apiUrl}/api/expenses`, body);
  }

  deleteExpense(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/api/expenses/${id}`);
  }

  monthSummary(year?: number, month?: number): Observable<MonthSummary> {
    let params = new HttpParams();
    if (year != null) params = params.set('year', year);
    if (month != null) params = params.set('month', month);
    return this.http.get<MonthSummary>(`${environment.apiUrl}/api/expenses/summary/month`, { params });
  }

  createLinkCode(): Observable<LinkCode> {
    return this.http.post<LinkCode>(`${environment.apiUrl}/api/link-codes`, {});
  }
}
