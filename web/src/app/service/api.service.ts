import { Injectable } from '@angular/core';
import { RecordService } from 'src/app/openapi/api/record.service';
import { LearnService } from 'src/app/openapi/api/learn.service';
import { CommonService } from 'src/app/openapi/api/common.service';
@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(public record: RecordService,
              public common: CommonService,
              public learn: LearnService) { }
}
