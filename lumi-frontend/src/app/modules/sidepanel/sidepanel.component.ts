import { Component, OnInit } from '@angular/core';
import * as microsoftTeams from '@microsoft/teams-js';
import { CommonModule } from '@angular/common';
import { ChatViewComponent } from '../../shared/components/chat-view-component/chat-view.component';

@Component({
  selector: 'app-sidepanel',
  standalone: true,
  imports: [
    CommonModule,
    ChatViewComponent
  ],
  templateUrl: './sidepanel.component.html',
  styleUrls: ['./sidepanel.component.css']
})
export class SidepanelComponent implements OnInit {

  meetingId: string = '';
  loading = true;

  ngOnInit(): void {
    microsoftTeams.app.initialize()
      .then(() => {
        return microsoftTeams.app.getContext();
      })
      .then((context) => {

        // ✅ Get real meeting ID from Teams
        if (context.meeting?.id) {
          this.meetingId = context.meeting.id;
        }

        this.loading = false;
      })
      .catch(() => {
        // ✅ Local fallback (only for testing)
        this.meetingId = 'test-meeting';
        this.loading = false;
      });
  }
}