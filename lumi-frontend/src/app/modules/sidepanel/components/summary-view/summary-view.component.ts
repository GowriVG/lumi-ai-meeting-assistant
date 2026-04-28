import { Component, Input, Output, EventEmitter } from '@angular/core'; // Added Output here
import { CommonModule } from '@angular/common';
import { MeetingSummary } from '../../../../shared/models/meeting.model';

@Component({
  selector: 'app-summary-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './summary-view.component.html',
  styleUrls: ['./summary-view.component.css'],
})
export class SummaryViewComponent {
  // Use the MeetingSummary interface for enterprise-grade type safety
  @Input() summary: MeetingSummary | null = null;
  @Input() meetingId!: string;
  @Output() generate = new EventEmitter<void>();

  onGenerateSummary() {
    this.generate.emit();
  }
}
