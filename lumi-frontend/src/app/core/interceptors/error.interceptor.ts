import { HttpInterceptor, HttpRequest, HttpHandler, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export class ErrorInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        const errorMessage = error.error?.message || 'An unknown error occurred';
        console.error(`LUMI Error [${error.status}]:`, errorMessage);
        // You could trigger a Toast notification here
        return throwError(() => error);
      })
    );
  }
}