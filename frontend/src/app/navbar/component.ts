import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'shared-navbar',
  standalone: true,
  imports: [
    RouterOutlet,
    NgbModule,
  ],
  templateUrl: './component.html',
  styleUrl: './component.scss'
})
export class NavbarComponent {
  title = 'navbar';

  constructor() {

  }
}
