import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';
import { ContextService } from 'src/app/service/context.service';
import {Application} from 'src/app/openapi/model/application';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-application-form-modal',
  templateUrl: './application-form-modal.component.html',
  styleUrls: ['./application-form-modal.component.scss']
})
export class ApplicationFormModalComponent implements OnInit {
  application: Application = {_id:undefined,name:'',description:''};
  loading = new BehaviorSubject<boolean>(false);
  error = new BehaviorSubject<string|undefined>(undefined);
  @Output() saved = new EventEmitter<Application>();
  @Output() updated = new EventEmitter<Application>();
  @Output() deleted = new EventEmitter<Application>();
  @Output() loaded = new EventEmitter<Application>();

  constructor(private ctx: ContextService) { }

  ngOnInit(): void {
    this.load();
  }

  load(){
    if (this.application==undefined) return;
    if (this.application._id == undefined) return;
    this.loading.next(true);
    this.error.next(undefined);
    this.ctx.api.common.commonApplicationLoad(this.application._id).subscribe(
      (result)=>{
        this.loading.next(false);
        this.application = result;
        this.loaded.next(this.application);
      },
      (err)=>{
        this.loading.next(false);
        this.error.next(err.toString());
      });
  }


  save(){
    this.loading.next(true);
    this.error.next(undefined);
    this.ctx.api.common.commonApplicationSave(this.application).subscribe((result)=>{
      this.loading.next(false);
      this.application._id = result;
      this.saved.next(this.application);
      },(err)=>{
        this.loading.next(false);
       this.error.next(err.toString());
    });
  }

  delete(){
    if (this.application == undefined) return;
    if (this.application._id == undefined) return;
    this.ctx.api.common.commonApplicationDelete(this.application._id).subscribe((result)=>{
      this.loading.next(false);
      this.deleted.next(this.application);
      },(err)=>{
        this.loading.next(false);
       this.error.next(err.toString());
    });
  }

  update(){
    this.loading.next(true);
    this.error.next(undefined);
    this.ctx.api.common.commonApplicationUpdate(this.application).subscribe((result)=>{
      this.updated.next(this.application);
      this.loading.next(false);

      },(err)=>{
        this.loading.next(false);
       this.error.next(err.toString());
    });
  }

  close(){
    this.ctx.modal.close();
  }

}
