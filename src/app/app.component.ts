import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl } from '@angular/forms';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { PageEvent } from '@angular/material/paginator';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Subject } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { Employee } from './employee';

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

  records: Employee[] = [];
  colleges: string[] = [];
  departments: string[] = [];
  departmentsByCollege = new Map<string, string[]>();

  filterCollege = '';
  filterDepartment = '';
  autocompleteOptions = new Subject<string[]>();
  filteredRecords: Employee[] = [];

  defaultYear = '2022';
  defaultCampus = 'UIUC';

  nameCtrl = new FormControl('');

  filterCtrl = new FormControl('');
  @ViewChild('filterInput') filterInput: ElementRef<HTMLInputElement>;

  dataSource: MatTableDataSource<Employee>;
  displayedColumns = ['name', 'salary'];
  displayedColumnsWithExpand = [...this.displayedColumns, 'expand'];
  expandedElement: Employee | null;

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    private httpClient: HttpClient
  ) {}

  ngOnInit() {
    this.filterCtrl.valueChanges.pipe(
      startWith(null),
      map((query: string | null) => {
        if (!this.filterDepartment) {
          if (!this.filterCollege) {
            return this._filter(this.colleges, query);
          } else {
            return this._filter(this.departments, query);
          }
        } else {
          return [];
        }
      })
    ).subscribe(this.autocompleteOptions);

    this.httpClient.get('assets/2022.json').subscribe(data => {
      this.records = data as Employee[];
      for (const employee of this.records) {
        employee.positions.sort((a, b) => b.positionSalary - a.positionSalary);
      }
      this.filteredRecords = this.records;
    
      this.dataSource = new MatTableDataSource(this.records);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.dataSource.filterPredicate = (data: Employee, filter: string) => {
        const filterValue = filter.toLowerCase();
        return data.name.toLowerCase().includes(filterValue);
      };

      const departmentMapping = new Map<string, Set<string>>();
      for (const employee of this.records) {
        for (const position of employee.positions) {
          if (!departmentMapping.has(position.college)) {
            departmentMapping.set(position.college, new Set<string>());
          }
          const departments = departmentMapping.get(position.college);
          if (!departments?.has(position.department)) {
            departments?.add(position.department);
          }
        }
      }
      this.colleges = Array.from(departmentMapping.keys()).sort();
      for (const [college, departments] of departmentMapping) {
        this.departmentsByCollege.set(college, Array.from(departments).sort());
      }
      this.autocompleteOptions.next(this.colleges.slice());
    });
  }

  add(event: MatAutocompleteSelectedEvent): void {
    this.filterInput.nativeElement.value = '';
    this.filterCtrl.setValue(null);

    if (!this.filterCollege) {
      this.filterCollege = event.option.viewValue;
      this.departments = this.departmentsByCollege.get(this.filterCollege) ?? [];
      this.autocompleteOptions.next(this.departments.slice());
    } else if (!this.filterDepartment) {
      this.filterDepartment = event.option.viewValue;
      this.autocompleteOptions.next([]);
    }
    this._filterRecords();
  }

  remove(filter: string): void {
    if (filter === this.filterDepartment) {
      this.filterDepartment = '';
      if (this.filterCollege) {
        this.autocompleteOptions.next(this.departments.slice());
      } else {
        this.autocompleteOptions.next(this.colleges.slice());
      }
    } else {
      this.filterCollege = '';
      if (!this.filterDepartment) {
        this.autocompleteOptions.next(this.colleges.slice());
      }
    }
    this._filterRecords();
  }

  getPageRange(event: PageEvent): PageEvent {
    this.pageStart = event.pageIndex * this.pageSize;
    this.pageEnd = this.pageStart + this.pageSize;
    return event;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  private _filterRecords() {
    if (this.filterDepartment) {
      this.filteredRecords = this.filteredRecords.filter(employee =>
        employee.positions.some(position => position.department === this.filterDepartment)
      );
    } else if (this.filterCollege) {
      this.filteredRecords = this.records.filter(employee =>
        employee.positions.some(position => position.college === this.filterCollege)
      );
    } else {
      this.filteredRecords = this.records.slice();
    }
    this.dataSource.data = this.filteredRecords;
  }

  private _filter(items: string[], query: string | null): string[] {
    if (query) {
      const filterValue = query.toLowerCase();
      return items.filter(item => item.toLowerCase().startsWith(filterValue));
    } else {
      return items.slice();
    }
  }
}
