import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'generator',
  standalone: true,
  imports: [
    RouterOutlet,
    NgbModule,
  ],
  templateUrl: './component.html',
  styleUrl: './component.scss'
})
export class GeneratorComponent {
  title = 'generator';

  constructor() {

  }
}
