import { Component, ChangeDetectionStrategy } from '@angular/core';
import { EmailClassifierChatComponent } from './components/email-classifier-chat/email-classifier-chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [EmailClassifierChatComponent],
  template: `<app-email-classifier-chat />`,
  styles: [`
    :host {
      display: block;
      height: 100vh;
      width: 100%;
      overflow: hidden;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class App { }
