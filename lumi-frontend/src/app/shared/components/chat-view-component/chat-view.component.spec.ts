// import { ComponentFixture, TestBed } from '@angular/core/testing';
// import { ChatViewComponent} from './chat-view.component';

// describe('ChatViewComponent', () => {
//   let component: ChatViewComponent;
//   let fixture: ComponentFixture<ChatViewComponent>;

//   beforeEach(async () => {
//     await TestBed.configureTestingModule({
//       imports: [ChatViewComponent],
//     }).compileComponents();

//     fixture = TestBed.createComponent(ChatViewComponent);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//   });

//   it('should create', () => {
//     expect(component).toBeTruthy();
//   });
// });
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatViewComponent } from './chat-view.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { LumiService } from '../../../core/services/lumi.service';

describe('ChatViewComponent', () => {
  let component: ChatViewComponent;
  let fixture: ComponentFixture<ChatViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ChatViewComponent,
        HttpClientTestingModule
      ],
      providers: [
        LumiService
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatViewComponent);
    component = fixture.componentInstance;

    // ✅ REQUIRED because of @Input
    component.meetingId = 'test-meeting';

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});