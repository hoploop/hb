import { AppRoutingModule } from './app-routing.module';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule} from './forms/forms.module';
import { ModalsModule} from './modals/modals.module';
import { CardsModule} from './cards/cards.module';
import { ComponentsModule} from './components/components.module';
import {FormsModule as NgFormsModule} from '@angular/forms';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';
import {
  MissingTranslationHandler,
  MissingTranslationHandlerParams,
  TranslateLoader,
  TranslateModule
} from '@ngx-translate/core';



export class CustomMissingTranslationHandler implements MissingTranslationHandler {
  handle(params: MissingTranslationHandlerParams) {
    return 'MISSING: ' + params.key;
  }
}

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ModalsModule,
    CardsModule,
    ComponentsModule,
    NgFormsModule,
    AppRoutingModule,
    NgbModule,
    TranslateModule.forRoot({
      defaultLanguage: 'en',
      loader: {
        provide: TranslateLoader,
        useFactory: httpTranslateLoader,
        deps: [HttpClient]
      },
     missingTranslationHandler: {provide: MissingTranslationHandler, useClass: CustomMissingTranslationHandler},
    }),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }


// AOT compilation support


export function httpTranslateLoader(http: HttpClient) {
    return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}
