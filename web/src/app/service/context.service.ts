import { Injectable } from '@angular/core';
import { ApiService} from 'src/app/service/api.service';
import { ModalService} from 'src/app/service/modal.service';
@Injectable({
  providedIn: 'root'
})
export class ContextService {

  constructor(public modal: ModalService,
              public api: ApiService) { }
}
