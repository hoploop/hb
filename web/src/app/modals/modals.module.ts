import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SampleModalComponent } from './sample-modal/sample-modal.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ServiceModule } from 'src/app/service/service.module';
import { ApplicationFormModalComponent } from './application-form-modal/application-form-modal.component';
import { FormsModule } from 'src/app/forms/forms.module';
import {TranslateModule} from '@ngx-translate/core';


@NgModule({
  declarations: [
    SampleModalComponent,
    ApplicationFormModalComponent
  ],
  imports: [
    CommonModule,
    NgbModule,
     TranslateModule,
    ServiceModule,
    FormsModule
  ],
  exports: [
    ApplicationFormModalComponent,
    SampleModalComponent
  ]
})
export class ModalsModule { }
