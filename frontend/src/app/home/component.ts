import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'home',
  standalone: true,
  imports: [
    RouterOutlet,
    NgbModule,
  ],
  templateUrl: './component.html',
  styleUrl: './component.scss'
})
export class HomeComponent {
  title = 'home';

  constructor() {

  }
}
