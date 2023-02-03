import { Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SampleModalComponent} from 'src/app/modals/sample-modal/sample-modal.component';
import { Scenario} from 'src/app/openapi/model/scenario';
import {ContextService} from 'src/app/service/context.service';
import {ApplicationFormModalComponent} from 'src/app/modals/application-form-modal/application-form-modal.component'
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit  {
  title = 'web';
  scenarios: Array<Scenario> = [];

  constructor(private ctx:ContextService,
            private modalService: NgbModal){
  }



  sampleOpen(){
    this.modalService.open(SampleModalComponent,{centered:true});
  }

  newApplication(){
    this.modalService.open(ApplicationFormModalComponent,{centered:true});
    }

  ngOnInit(): void {
    this.ctx.api.record.recordScenarios().subscribe((result)=>{
      this.scenarios = result;
    });
  }
}
