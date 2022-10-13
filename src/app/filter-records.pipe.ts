import { Pipe, PipeTransform } from '@angular/core';

import { Record } from './record';

@Pipe({name: 'filterRecords'})
export class FilterRecordsPipe implements PipeTransform {
  transform(records: Record[], name: string): Record[] {
    return records.filter(record => record.name.toLowerCase().includes(name.toLowerCase()));
  }
}
