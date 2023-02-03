export * from './common.service';
import { CommonService } from './common.service';
export * from './learn.service';
import { LearnService } from './learn.service';
export * from './record.service';
import { RecordService } from './record.service';
export * from './root.service';
import { RootService } from './root.service';
export const APIS = [CommonService, LearnService, RecordService, RootService];
