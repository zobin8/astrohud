import { TestBed } from '@angular/core/testing';
import { NavbarComponent } from './component';

describe('NavbarComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavbarComponent],
    }).compileComponents();
  });

  it('should create the navbar', () => {
    const fixture = TestBed.createComponent(NavbarComponent);
    const navbar = fixture.componentInstance;
    expect(navbar).toBeTruthy();
  });
});
