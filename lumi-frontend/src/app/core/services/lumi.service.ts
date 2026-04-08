import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { MeetingDetails, MeetingSummary } from '../../shared/models/meeting.model';

@Injectable({
  providedIn: 'root'
})
export class LumiService {
  // Use the local URL where your FastAPI server is running
  private readonly API_URL = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  loadMeeting(meetingId: string, transcript: string) {
  return this.http.post(
    `${this.API_URL}/load-meeting/${meetingId}`,
    {
      transcript: transcript
    }
  );
}


  /**
   * Fetches the full current state of the meeting, including transcript and history.
   */
  getMeetingState(meetingId: string): Observable<MeetingDetails> {
    return this.http.get<MeetingDetails>(`${this.API_URL}/meeting/${meetingId}`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Triggers the AI to generate a structured summary from the transcript.
   */
  getSummary(meetingId: string): Observable<{ summary: MeetingSummary }> {
    return this.http.post<{ summary: MeetingSummary }>(
      `${this.API_URL}/summarize/${meetingId}`, 
      {}
    ).pipe(catchError(this.handleError));
  }

  /**
   * Sends a specific question to the AI agent.
   */
  askQuestion(meetingId: string, question: string): Observable<{ answer: string }> {
    return this.http.post<{ answer: string }>(`${this.API_URL}/ask/${meetingId}`, {
      transcript: "", // Backend handles transcript fetching from Graph API
      question: question
    }).pipe(catchError(this.handleError));
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
    {}
  );
}
syncSelectedItems(meetingId: string, items: any[]) {
  return this.http.post(
    `${this.API_URL}/sync-selected/${meetingId}`,
    items
  );
}

}