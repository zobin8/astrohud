import { Component } from '@angular/core';
import { NavbarComponent } from './navbar/component';
import { FooterComponent } from './footer/component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    NavbarComponent,
    FooterComponent,
    NgbModule,
    RouterOutlet,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'Astrohud Frontend';

  constructor() {

  }
}
