import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import * as microsoftTeams from '@microsoft/teams-js';
import { LoaderComponent } from './shared/components/loader/loader.component';
import { MeetingContextService } from './core/services/meeting-context.service';
import { LumiService } from './core/services/lumi.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, LoaderComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  title = 'LUMI-Frontend';
  isTeamsInitialized = false;
  meetingId: string = '';

  constructor(private meetingContext: MeetingContextService, private lumiService: LumiService) {}

  async ngOnInit() {
  const USE_TEAMS = false;

  if (USE_TEAMS) {
    // 🔷 TEAMS FLOW (future)
    try {
      await microsoftTeams.app.initialize();

      const context = await microsoftTeams.app.getContext();

      console.log('Teams Context:', context);

      if (context.meeting?.id) {
        this.meetingId = context.meeting.id;

        this.meetingContext.setMeetingId(this.meetingId);

        console.log('Meeting ID (Teams):', this.meetingId);
      }

      this.isTeamsInitialized = true;

      microsoftTeams.app.notifySuccess();

      microsoftTeams.app.registerOnThemeChangeHandler((theme) => {
        this.applyTheme(theme);
      });

    } catch (error) {
      console.error('Teams init failed', error);
      this.isTeamsInitialized = true;
    }

  } 
  else {
  this.initializeMeeting();
}
}
createMeetingFromBackend() {
  console.log('Creating meeting from backend...');

  this.lumiService.createMeeting().subscribe({
    next: (res: any) => {
      this.meetingId = res.data.meeting_id;

      console.log('Meeting ID (Backend):', this.meetingId);

      // ✅ STORE IN LOCAL STORAGE (CRITICAL FIX)
      localStorage.setItem('meetingId', this.meetingId);

      this.meetingContext.setMeetingId(this.meetingId);

      this.isTeamsInitialized = true;
    },
    error: (err) => {
      console.error('Failed to create meeting', err);
      this.isTeamsInitialized = true;
    },
  });
}
initializeMeeting() {
  console.log('Initializing meeting...');

  let existingId = localStorage.getItem('meetingId');

  if (existingId) {
    // ✅ REUSE EXISTING MEETING
    this.meetingId = existingId;

    console.log('Reusing Meeting ID:', this.meetingId);

    this.meetingContext.setMeetingId(this.meetingId);
    this.isTeamsInitialized = true;

  } else {
    // ✅ CREATE NEW MEETING
    this.createMeetingFromBackend();
  }
}
  // 🔥 LOCAL SESSION SETUP
  setupLocalSession() {
    console.log('Running in LOCAL MODE');

    this.meetingId = this.generateMeetingId();

    // ✅ store in service
    this.meetingContext.setMeetingId(this.meetingId);

    console.log('Meeting ID (Local):', this.meetingId);

    this.isTeamsInitialized = true;
  }

  // 🔥 PERSISTENT MEETING ID
  generateMeetingId(): string {
    let id = localStorage.getItem('meetingId');

    if (!id) {
      id = 'meeting-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
      localStorage.setItem('meetingId', id);
    }

    return id;
  }

  // 🔥 TEAMS THEME HANDLER
  private applyTheme(theme: string) {
    document.body.className = `theme-${theme}`;
  }
}