import { Component, OnInit } from '@angular/core';
import { ContextService } from 'src/app/service/context.service';

@Component({
  selector: 'app-sample-modal',
  templateUrl: './sample-modal.component.html',
  styleUrls: ['./sample-modal.component.scss']
})
export class SampleModalComponent implements OnInit {

  constructor(private ctx: ContextService){
  }

  ngOnInit(): void {
  }

  close(){
    this.ctx.modal.close();
  }
}
