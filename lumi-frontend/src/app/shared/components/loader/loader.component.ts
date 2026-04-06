import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loader',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './loader.component.html',
  styleUrls: ['./loader.component.css']
})
export class LoaderComponent {
  /**
   * Allows you to pass custom messages like "LUMI is summarizing..." 
   * or "Analyzing transcript..."
   */
  @Input() message: string = 'Loading...';
}