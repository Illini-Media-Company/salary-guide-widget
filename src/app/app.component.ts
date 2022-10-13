import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PageEvent } from '@angular/material/paginator';

import { Record } from './record';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'salary-guide-widget';
  pageSize = 10;
  pageStart = 0;
  pageEnd = 10;
  records: Record[] = [];
  nameSearch = '';

  defaultYear = "2021";
  defaultDepartment = "All";

  constructor(
    private httpClient: HttpClient
  ) {}

  ngOnInit() {
    this.httpClient.get('assets/records.json').subscribe(data => {
      console.log(data);
      this.records = data as Record[];
    });
  }

  public getPageRange(event: PageEvent): PageEvent {
    this.pageStart = event.pageIndex * this.pageSize;
    this.pageEnd = this.pageStart + this.pageSize;
    return event;
  }
}
