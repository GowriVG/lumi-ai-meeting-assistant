import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import {
  MeetingDetails,
  MeetingSummary,
} from '../../shared/models/meeting.model';

@Injectable({
  providedIn: 'root',
})
export class LumiService {
  // Use environment variables in a real enterprise setup
  private readonly API_URL = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  /**
   * Initializes the meeting session in the backend.
   * Called when the Teams App is opened in a meeting.
   */
  loadMeeting(meetingId: string, transcript: string): Observable<any> {
    return this.http.post(`${this.API_URL}/load-meeting/${meetingId}`, {
      transcript: transcript,
    });
  }

  /**
   * Triggers AI summarization.
   * Uses shareReplay to avoid redundant calls if multiple components subscribe.
   */
  getSummary(meetingId: string): Observable<{ summary: MeetingSummary }> {
    return this.http
      .post<{
        summary: MeetingSummary;
      }>(`${this.API_URL}/summarize/${meetingId}`, {})
      .pipe(shareReplay(1));
  }

  /**
   * Conversational AI interface.
   * Sends the user's question to the backend.
   */
  askLumi(meetingId: string, question: string): Observable<{ answer: string }> {
    const payload = {
      transcript: '', // Backend handles transcript fetching via Graph API
      question: question,
    };
    return this.http.post<{ answer: string }>(
      `${this.API_URL}/ask/${meetingId}`,
      payload,
    );
  }

  /**
   * Fetches the full current state of the meeting (transcript + current summary).
   */
  getMeetingState(meetingId: string): Observable<MeetingDetails> {
    return this.http.get<MeetingDetails>(
      `${this.API_URL}/meeting/${meetingId}`,
    );
  }
}

//where to add this code snippet in the app.component.ts file?
// You would typically add the code snippet that interacts with the `LumiService` inside the `ngOnInit` method of your `AppComponent`. This is because you want to load the meeting state as soon as the component initializes, which is when the Microsoft Teams context is available.
// import * as microsoftTeams from '@microsoft/teams-js';

// // Inside your ngOnInit
// microsoftTeams.app.getContext().then((context) => {
//   const meetingId = context.meeting?.id;
//   if (meetingId) {
//     this.lumiService.getMeetingState(meetingId).subscribe({
//       next: (data) => this.processMeetingData(data),
//       error: (err) => this.handleError(err) // Caught by your ErrorInterceptor
//     });
//   }
// });
