import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { WarehouseConfig } from 'src/app/models/warehouse.models';

@Injectable({
  providedIn: 'root'
})
export class WarehouseService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  createWarehouse(config: WarehouseConfig): Observable<any> {
    return this.http.post(`${this.apiUrl}/warehouse/create`, config)
      .pipe(
        catchError(this.handleError)
      );
  }

  validateConfig(config: WarehouseConfig): Observable<any> {
    return this.http.post(`${this.apiUrl}/warehouse/validate`, config)
      .pipe(
        catchError(this.handleError)
      );
  }

  getWarehouse(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/warehouse/${id}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  deleteWarehouse(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/warehouse/${id}/delete`)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.error?.detail) {
        // Handle Pydantic validation errors (array of errors)
        if (Array.isArray(error.error.detail)) {
          const details = error.error.detail.map((err: any) => {
            if (typeof err === 'object' && err.loc && err.msg) {
              return `${err.loc.join('.')}: ${err.msg}`;
            }
            return String(err);
          }).join('; ');
          errorMessage = details || 'Validation error occurred';
        } else {
          errorMessage = String(error.error.detail);
        }
      } else if (error.error?.message) {
        errorMessage = error.error.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
    }
    console.error('Warehouse API Error:', errorMessage);
    return throwError(() => ({
      message: errorMessage,
      status: error.status,
      originalError: error
    }));
  }
}