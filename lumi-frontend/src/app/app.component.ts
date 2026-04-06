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

  async ngOnInit() {
  // ✅ Detect if running inside Teams
  if (window.self !== window.top) {
    try {
      await microsoftTeams.app.initialize();
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
    // ✅ Local dev mode
    console.log('Running outside Teams (local mode)');
    this.isTeamsInitialized = true;
  }
}

  private applyTheme(theme: string) {
    document.body.className = `theme-${theme}`;
  }
}