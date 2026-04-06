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
import { LoaderComponent } from '../loader/loader.component';

@Component({
  selector: 'app-chat-view',
  standalone: true,
  imports: [CommonModule, FormsModule, LoaderComponent],
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

  constructor(private lumiService: LumiService) {}

  ngOnInit(): void {
    console.log('Using meeting:', this.meetingId);
    // 🔥 Ensure meeting exists first
    this.lumiService.getMeetingState(this.meetingId).subscribe({
      next: (data) => {
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
      },
      error: (err) => {
        console.error('Meeting not found:', err);

        this.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: '⚠️ Meeting not found. Please load a transcript first.',
          timestamp: new Date(),
        });
      },
    });
  }

  loadMessages() {
    this.lumiService.getMeetingState(this.meetingId).subscribe({
      next: (data) => {
        this.messages = data.qa_history || [];
      },
      error: (err) => {
        console.error('Meeting load error:', err);
        this.messages = [];
      },
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  sendMessage() {
    if (!this.userInput.trim() || this.isTyping) return;

    const originalQuestion = this.userInput;
    const question = originalQuestion.trim().toLowerCase();

    // ✅ Push user message
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: originalQuestion,
      timestamp: new Date(),
    };

    this.messages.push(userMsg);
    this.userInput = '';
    this.isTyping = true;

    const greetings = ['hi', 'hello', 'hey'];

    if (greetings.includes(question)) {
      this.messages.push({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Hello. How can I assist you with your meeting?',
        timestamp: new Date(),
      });

      this.isTyping = false;
      return;
    }

    // 🔥 CASE 1: CREATE REQUEST
    if (
      question.includes('create work item') ||
      question.includes('create user story') ||
      question.includes('generate work item')
    ) {
      this.lumiService.getSummary(this.meetingId).subscribe({
        next: (res) => {
          let items: any = res.summary.action_items || [];

          this.pendingActionItems = items;

          const formatted = this.formatActionItems(items);

          this.messages.push({
            id: Date.now().toString(),
            role: 'assistant',
            content: '',
            type: 'work-items', // 🔥 important
            data: items, // 🔥 structured data
            timestamp: new Date(),
          });

          this.isTyping = false;
        },
        error: (err) => {
          console.error(err);
          this.isTyping = false;
        },
      });

      return;
    }

    // CASE 2: PROCEED
    if (question === 'proceed') {
      if (!this.pendingActionItems.length) {
        this.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content:
            '⚠️ No action items to create. Ask me to generate them first.',
          timestamp: new Date(),
        });
        this.isTyping = false;
        return;
      }

      this.lumiService.syncToDevOps(this.meetingId).subscribe({
        next: () => {
          this.messages.push({
            id: Date.now().toString(),
            role: 'assistant',
            content: '✅ Work items successfully created in Azure DevOps',
            timestamp: new Date(),
          });

          this.pendingActionItems = [];
          this.isTyping = false;
        },
        error: (err) => {
          console.error(err);
          this.isTyping = false;
        },
      });

      return;
    }
    console.log('Meeting ID:', this.meetingId);
    // 🔥 CASE: SUMMARY REQUEST
    if (question.includes('summary') || question.includes('summarize')) {
      this.lumiService.getSummary(this.meetingId).subscribe({
        next: (res) => {
          console.log('SUMMARY RESPONSE:', res);

          const summary = res.summary || {
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

          this.isTyping = false;
        },
        error: (err) => {
          console.error(err);
          this.isTyping = false;
        },
      });

      return;
    }

    // 🔥 DEFAULT CHAT
    this.lumiService.askQuestion(this.meetingId, originalQuestion).subscribe({
      next: (res: any) => {
        const answer =
          typeof res.answer === 'string'
            ? res.answer
            : res.answer?.answer || JSON.stringify(res.answer);

        this.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: answer,
          timestamp: new Date(),
        });

        this.isTyping = false;
      },
      error: (err) => {
        console.error(err);
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

  // ✅ Format ADO preview
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

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTop =
        this.scrollContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }
}
