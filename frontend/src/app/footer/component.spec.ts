import { TestBed } from '@angular/core/testing';
import { FooterComponent } from './component';

describe('FooterComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FooterComponent],
    }).compileComponents();
  });

  it('should create the footer', () => {
    const fixture = TestBed.createComponent(FooterComponent);
    const footer = fixture.componentInstance;
    expect(footer).toBeTruthy();
  });
});
