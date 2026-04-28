import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class MeetingContextService {
  private meetingId: string = '';

  setMeetingId(id: string) {
    this.meetingId = id;
  }

  getMeetingId(): string {
    return this.meetingId;
  }
}