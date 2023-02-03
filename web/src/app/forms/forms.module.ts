import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApplicationFormComponent } from './application-form/application-form.component';
import {FormsModule as NgFormsModule} from '@angular/forms'
import {TranslateModule} from '@ngx-translate/core';


@NgModule({
  declarations: [
    ApplicationFormComponent
  ],
  imports: [
    CommonModule,
    NgFormsModule,
    TranslateModule
  ],
  exports: [
    ApplicationFormComponent
  ]
})
export class FormsModule { }
