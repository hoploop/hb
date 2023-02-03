import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {TranslateModule} from '@ngx-translate/core';
import { ApplicationsCardComponent } from './applications-card/applications-card.component';
import {ModalsModule} from 'src/app/modals/modals.module';


@NgModule({
  declarations: [
    ApplicationsCardComponent
  ],
  imports: [
    CommonModule,
    TranslateModule,
    ModalsModule
  ],
  exports:[
    ApplicationsCardComponent
    ]
})
export class CardsModule { }
