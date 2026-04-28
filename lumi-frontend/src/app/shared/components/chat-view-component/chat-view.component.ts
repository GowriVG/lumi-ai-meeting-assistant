import {
  Component,
  Input,
  OnInit,
  ElementRef,
  ViewChild,
  AfterViewChecked,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LumiService } from '../../../core/services/lumi.service';
import { ChatMessage } from '../../models/meeting.model';

@Component({
  selector: 'app-chat-view',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-view.component.html',
  styleUrls: ['./chat-view.component.css'],
})
export class ChatViewComponent implements OnInit, AfterViewChecked {
  @Input() meetingId!: string;
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  messages: ChatMessage[] = [];
  userInput: string = '';
  isTyping: boolean = false;
  pendingActionItems: any[] = [];
  shouldScroll: boolean = false;
  isOnline: boolean = false;

  constructor(private lumiService: LumiService) {}

  ngOnInit(): void {
    console.log('Using meeting:', this.meetingId);
    if (!this.meetingId) {
      this.showError('Meeting context not available.');
      return;
    }

    this.lumiService.getMeetingState(this.meetingId).subscribe({
      next: (res: any) => {
        console.log('Meeting data:', res.data);
        if (
          !res.data.transcript ||
          res.data.transcript === 'No transcript available yet.'
        ) {
          this.showError('Meeting transcript is currently unavailable.');
          return;
        }
        // If valid meeting
        this.isOnline = true;
        this.initializeMessages(res.data);

        // Valid meeting
        this.initializeMessages(res.data);
      },

      error: (err) => {
        console.error('Meeting not found:', err);
        this.isOnline = false;
        this.showError('⚠️ Meeting not found. Transcript not loaded.');
      },
    });
  }
  
  canCreateSelectedItems(): boolean {
    return this.pendingActionItems.some(
      (item: any) => item.selected && !item.created,
    );
  }

  showError(message: string) {
    this.messages = [
      {
        id: Date.now().toString(),
        role: 'assistant',
        content: message,
        timestamp: new Date(),
      },
    ];
  }
  initializeMessages(data: any) {
    this.messages = (data.qa_history || []).filter(
      (msg: any) => msg.content && msg.content.trim() !== '',
    );

    if (this.messages.length === 0) {
      this.messages.push({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Ask me anything about your meeting.',
        timestamp: new Date(),
      });
    }
  }
  loadMessages() {
    this.lumiService.getMeetingState(this.meetingId).subscribe({
      next: (res: any) => {
        this.messages = res.data.qa_history || [];
      },
      error: (err) => {
        console.error('Meeting load error:', err);
        this.messages = [];
      },
    });
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  sendMessage() {
    if (!this.userInput.trim() || this.isTyping) return;

    const originalQuestion = this.userInput;
    const question = originalQuestion.trim().toLowerCase();

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: originalQuestion,
      timestamp: new Date(),
    };

    this.messages.push(userMsg);
    this.userInput = '';
    this.isTyping = true;
    this.shouldScroll = true;

    this.lumiService.detectIntent(originalQuestion).subscribe({
      next: (res: any) => {
        //const intent = res.data.intent;
        let intent = res.data.intent;

        // Greeting
        if (intent === 'greeting') {
          this.messages.push({
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Hello. How can I assist you with your meeting?',
            timestamp: new Date(),
          });

          this.shouldScroll = true;
          this.isTyping = false;
          return;
        }

        if (
          originalQuestion.includes('who') ||
          originalQuestion.includes('what') ||
          originalQuestion.includes('when') ||
          originalQuestion.includes('did')
        ) {
          intent = 'qa';
        }
        // Summary
        if (intent === 'summary') {
          this.lumiService.getSummary(this.meetingId).subscribe({
            next: (res: any) => {
              const summary = res.data || {
                key_points: [],
                decisions: [],
                action_items: [],
              };

              const formatted = this.formatSummary(summary);

              this.messages.push({
                id: Date.now().toString(),
                role: 'assistant',
                content: formatted,
                timestamp: new Date(),
              });
              this.messages.push({
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content:
                  'I found action items. Would you like me to create them in Azure DevOps?',
                timestamp: new Date(),
              });

              this.shouldScroll = true;
              this.isTyping = false;
            },
            error: (err) => {
              console.error(err);
              this.isTyping = false;
            },
          });

          return;
        }

        // Work Items
        if (intent === 'work_items') {
          this.lumiService.getSummary(this.meetingId).subscribe({
            next: (res: any) => {
              let items: any = res.data.action_items || [];

              this.pendingActionItems = items.map((item: any) => ({
                ...item,
                selected: false,
              }));

              this.messages.push({
                id: Date.now().toString(),
                role: 'assistant',
                content: '',
                type: 'work-items',
                data: items,
                timestamp: new Date(),
              });

              this.shouldScroll = true;
              this.isTyping = false;
            },
            error: (err) => {
              console.error(err);
              this.isTyping = false;
            },
          });

          return;
        }

        // Default Q&A
        this.lumiService
          .askQuestion(this.meetingId, originalQuestion)
          .subscribe({
            next: (res: any) => {
              const answer =
                typeof res.data === 'string'
                  ? res.data
                  : res.data.answer || 'No response available.';

              this.messages.push({
                id: Date.now().toString(),
                role: 'assistant',
                content: answer,
                timestamp: new Date(),
              });

              this.shouldScroll = true;
              this.isTyping = false;
            },
            error: (err) => {
              console.error(err);
              this.isTyping = false;
            },
          });
      },

      error: (err) => {
        console.error('Intent detection failed:', err);
        this.isTyping = false;
      },
    });
  }

  handleEnter(event: Event) {
    const keyboardEvent = event as KeyboardEvent;

    if (!keyboardEvent.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  // Format ADO preview
  formatActionItems(items: any[]): string {
    if (!items.length) {
      return `<div class="empty-state">No work items identified.</div>`;
    }

    let html = `<div class="work-items">`;

    items.forEach((item) => {
      html += `
      <div class="work-item">
        <div class="header">
          <span class="title">${item.title}</span>
          <span class="badge">${item.type}</span>
        </div>

        ${item.priority ? `<div class="priority">Priority: ${item.priority}</div>` : ''}

        <div class="desc">${item.description}</div>
      </div>
    `;
    });

    html += `
    <div class="footer-note">
      Type "proceed" to create work items in Azure DevOps.
    </div>
  </div>`;

    return html;
  }

  formatSummary(summary: any): string {
    if (
      !summary.key_points?.length &&
      !summary.decisions?.length &&
      !summary.action_items?.length
    ) {
      return `<div class="empty-state">No summary available for this meeting.</div>`;
    }

    let html = `<div class="summary">`;

    if (summary.insights?.length) {
      html += `<h4>Insights</h4><ul>`;

      summary.insights.forEach((i: string) => {
        html += `<li>${i}</li>`;
      });

      html += `</ul>`;
    }

    if (summary.key_points?.length) {
      html += `<h4>Key Points</h4><ul>`;
      summary.key_points.forEach((p: string) => {
        html += `<li>${p}</li>`;
      });
      html += `</ul>`;
    }

    if (summary.decisions?.length) {
      html += `<h4>Decisions</h4><ul>`;
      summary.decisions.forEach((d: string) => {
        html += `<li>${d}</li>`;
      });
      html += `</ul>`;
    }

    if (summary.action_items?.length) {
      html += `<h4>Action Items</h4><ul>`;
      summary.action_items.forEach((a: any) => {
        html += `<li><strong>${a.title}</strong> (${a.type})</li>`;
      });
      html += `</ul>`;
    }

    html += `</div>`;

    return html;
  }

  createSelectedItems() {
    const selectedItems = this.pendingActionItems.filter((i) => i.selected);

    if (!selectedItems.length) {
      this.messages.push({
        id: Date.now().toString(),
        role: 'assistant',
        content: '⚠️ Please select at least one work item.',
        timestamp: new Date(),
      });
      this.shouldScroll = true;
      return;
    }

    this.isTyping = true;

    this.lumiService
      .syncSelectedItems(this.meetingId, selectedItems)
      .subscribe({
        next: () => {
          this.messages.push({
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Selected work items created in Azure DevOps',
            timestamp: new Date(),
          });

          this.pendingActionItems.forEach((item) => {
            if (item.selected) {
              item.created = true;
            }
          });
          this.isTyping = false;
        },
        error: (err) => {
          console.error(err);
          this.isTyping = false;
        },
      });
  }

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTop =
        this.scrollContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }
}
