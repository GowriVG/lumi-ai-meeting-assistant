import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  MeetingDetails,
  MeetingSummary,
} from '../../shared/models/meeting.model';

@Injectable({
  providedIn: 'root',
})
export class LumiService {
  // Use the local URL where your FastAPI server is running
  private readonly API_URL = 'http://127.0.0.1:8000';
  //private readonly API_URL = 'https://lumiapi01.azurewebsites.net';
  private readonly API_KEY = 'lumi-secret';
  private readonly headers = new HttpHeaders({
    'Content-Type': 'application/json',
    'x-api-key': this.API_KEY,
  });
  constructor(private http: HttpClient) {}

  loadMeeting(meetingId: string, transcript: string) {
    return this.http.post(
      `${this.API_URL}/load-meeting/${meetingId}`,
      { transcript: transcript },
      { headers: this.headers },
    );
  }

  getMeetingState(meetingId: string): Observable<MeetingDetails> {
    return this.http
      .get<MeetingDetails>(`${this.API_URL}/meeting/${meetingId}`, {
        headers: this.headers,
      })
      .pipe(catchError(this.handleError));
  }

  /**
   * Triggers the AI to generate a structured summary from the transcript.
   */
  getSummary(
    meetingId: string,
  ): Observable<{ status: string; data: MeetingSummary }> {
    return this.http
      .post<{
        status: string;
        data: MeetingSummary;
      }>(`${this.API_URL}/summarize/${meetingId}`, {}, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Sends a specific question to the AI agent.
   */
  askQuestion(
    meetingId: string,
    question: string,
  ): Observable<{ answer: string }> {
    return this.http
      .post<{ answer: string }>(
        `${this.API_URL}/ask/${meetingId}`,
        {
          transcript: '',
          question: question,
        },
        {
          headers: this.headers,
        },
      )
      .pipe(catchError(this.handleError));
  }

  /**
   * Centralized error handler for API communication.
   */
  private handleError(error: any) {
    // This will be caught by your global error interceptor
    console.error('LUMI API Error:', error);
    return throwError(() => new Error(error.error?.message || 'Server error'));
  }

  syncToDevOps(meetingId: string): Observable<any> {
    return this.http.post(
      `${this.API_URL}/sync-to-ado/${meetingId}`,
      {},
      { headers: this.headers },
    );
  }
  syncSelectedItems(meetingId: string, items: any[]) {
    return this.http.post(`${this.API_URL}/sync-selected/${meetingId}`, items, {
      headers: this.headers,
    });
  }
  detectIntent(message: string): Observable<any> {
    return this.http.post<any>(
      `${this.API_URL}/detect-intent`,
      { question: message },
      { headers: this.headers },
    );
  }
}
