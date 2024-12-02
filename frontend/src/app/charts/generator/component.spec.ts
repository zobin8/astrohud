import { TestBed } from '@angular/core/testing';
import { GeneratorComponent } from './component';

describe('GeneratorComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratorComponent],
    }).compileComponents();
  });

  it('should create the component', () => {
    const fixture = TestBed.createComponent(GeneratorComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });
});
