import { Component, OnInit, Input, EventEmitter , Output} from '@angular/core';
import {ContextService} from 'src/app/service/context.service';
import {Application} from 'src/app/openapi/model/application';
import { BehaviorSubject } from 'rxjs';
@Component({
  selector: 'app-application-form',
  templateUrl: './application-form.component.html',
  styleUrls: ['./application-form.component.scss']
})
export class ApplicationFormComponent implements OnInit {
  @Input() disabled = new BehaviorSubject<boolean>(false);
  @Input() application: Application = {name:'',description:''};
  @Output() applicationChange = new EventEmitter<Application>();


  constructor(private ctx: ContextService) { }

  ngOnInit(): void {
  }


}
