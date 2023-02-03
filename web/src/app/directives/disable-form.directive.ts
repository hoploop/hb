import { Directive } from '@angular/core';

@Component({
  selector: '[appSisableForm]',
  styles: [`
    fieldset {
      display: block;
      margin: unset;
      padding: unset;
      border: unset;
    }
  `],
  template: `
    <fieldset [disabled]="disableForm">
      <ng-content></ng-content>
    </fieldset>
  `
})
export class DisableFormComponent {
  @Input('disableForm') disableForm: boolean;
  constructor() {}
  }
}
