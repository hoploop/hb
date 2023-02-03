import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApplicationFormModalComponent } from './application-form-modal.component';

describe('ApplicationFormModalComponent', () => {
  let component: ApplicationFormModalComponent;
  let fixture: ComponentFixture<ApplicationFormModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ApplicationFormModalComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ApplicationFormModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
