import { Component, OnInit , Input} from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import {ContextService} from 'src/app/service/context.service';
@Component({
  selector: 'app-image',
  templateUrl: './image.component.html',
  styleUrls: ['./image.component.scss']
})
export class ImageComponent implements OnInit {
  @Input() scenario: string | undefined = '60cbec7b-4aa1-4a1d-89e9-8b8cab34f85d';
  @Input() frame: number | undefined = 1;
  imagePath: any | undefined = undefined;
  base64Image: string | undefined = undefined;

  constructor(private ctx: ContextService,
          private _sanitizer: DomSanitizer) { }

  ngOnInit(): void {
    if (this.scenario != undefined && this.frame != undefined){
      this.ctx.api.learn.learnOcr(this.scenario,this.frame).subscribe((result)=>{
       this.imagePath = this._sanitizer.bypassSecurityTrustResourceUrl('data:image/png;base64,'+ result);
       });
   }
  }

}
