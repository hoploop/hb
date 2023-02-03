import { Component, OnInit } from '@angular/core';
import { ContextService } from 'src/app/service/context.service';
import {Application} from 'src/app/openapi/model/application';
import { BehaviorSubject } from 'rxjs';
import {ApplicationFormModalComponent} from 'src/app/modals/application-form-modal/application-form-modal.component'
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-applications-card',
  templateUrl: './applications-card.component.html',
  styleUrls: ['./applications-card.component.scss']
})
export class ApplicationsCardComponent implements OnInit {
  loading =new BehaviorSubject<boolean>(false);
  applications?: Array<Application> = [];
  total?: number = 0;

  constructor(private ctx: ContextService,private modalService: NgbModal) { }
  ngOnInit(): void {
    this.load();
  }

  load(){
    this.loading.next(true);
    this.ctx.api.common.commonApplicationList().subscribe((result)=>{
      this.applications = result.applications;
      this.total = result.total;
      this.loading.next(false);

    },(err)=>{
    this.loading.next(false);
    });
  }

  newApplication(){
    this.modalService.open(ApplicationFormModalComponent,{centered:true});
    }

}
