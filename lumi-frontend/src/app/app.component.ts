import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { RouterOutlet } from '@angular/router'; 
import * as microsoftTeams from '@microsoft/teams-js';
import { LoaderComponent } from './shared/components/loader/loader.component';

@Component({
  selector: 'app-root',
  standalone: true, // This marks it as a Standalone Component
  imports: [
    CommonModule, 
    RouterOutlet, 
    LoaderComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'LUMI-Frontend';
  isTeamsInitialized = false;
  meetingId: string = '';

  async ngOnInit() {
  if (window.self !== window.top) {
    try {
      await microsoftTeams.app.initialize();

      const context = await microsoftTeams.app.getContext();

      console.log("Teams Context:", context);

      // Get meeting ID
      this.meetingId = context.meeting?.id || context.channel?.id || "default-meeting";

      console.log("Meeting ID from Teams:", this.meetingId);

      this.isTeamsInitialized = true;

      microsoftTeams.app.notifySuccess();

      microsoftTeams.app.registerOnThemeChangeHandler((theme) => {
        this.applyTheme(theme);
      });

    } catch (error) {
      console.error('Teams init failed', error);
      this.isTeamsInitialized = true;
    }
  } else {
    console.log('Running outside Teams (local mode)');
    
    // fallback for local testing
    this.meetingId = "local-test-meeting";
    this.isTeamsInitialized = true;
  }
}

  private applyTheme(theme: string) {
    document.body.className = `theme-${theme}`;
  }
}