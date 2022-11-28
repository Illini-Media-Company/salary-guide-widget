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

  years: string[] = [];
  locationLabels: string[] = [];
  locations = new Map<string, string>();
  
  selectedYear = '';
  selectedLocation = '';

  isLoading = true;
  records: Employee[] = [];
  colleges: string[] = [];
  departments: string[] = [];
  departmentsByCollege = new Map<string, string[]>();

  filterCollege = '';
  filterDepartment = '';
  autocompleteOptions = new Subject<string[]>();
  filteredRecords: Employee[] = [];

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

    this.httpClient.get('assets/contents.txt', {responseType: 'text'}).subscribe(data => {
      this.years = data.split('\n').filter(x => x).sort().reverse();
      this.selectedYear = this.years[0];
      this.updateLocations();
    })
  }

  updateLocations(): void {
    this.isLoading = true;
    this.httpClient.get(`assets/${this.selectedYear}/contents.txt`, {responseType: 'text'}).subscribe(data => {
      const locations = new Map<string, string>();
      const entries = data.split('\n').filter(x => x).sort().reverse();
      for (const entry of entries) {
        const [key, ...value] = entry.split(':');
        const filename = value.join(':');
        locations.set(key, filename);
      }
      this.locationLabels = Array.from(locations.keys());
      this.locations = locations;
      this.selectedLocation = this.locations.keys().next().value;
      this.updateRecords();
    })
  }

  updateRecords(): void {
    this.isLoading = true;
    const filename = this.locations.get(this.selectedLocation);
    this.httpClient.get(`assets/${this.selectedYear}/${filename}`).subscribe(data => {
      this.records = data as Employee[];
      for (const employee of this.records) {
        employee.positions.sort((a, b) => b.positionSalary - a.positionSalary);
      }
      this.filteredRecords = this.records;
      this.filterCollege = '';
      this.filterDepartment = '';
    
      this.paginator.firstPage();
      this.dataSource = new MatTableDataSource(this.records);
      this.dataSource.sort = this.sort;
      this.dataSource.paginator = this.paginator;
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
      const departmentsByCollege = new Map<string, string[]>();
      for (const [college, departments] of departmentMapping) {
        departmentsByCollege.set(college, Array.from(departments).sort());
      }
      this.departmentsByCollege = departmentsByCollege;
      this.autocompleteOptions.next(this.colleges.slice());
      this.isLoading = false;
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

  applyFilter(event: Event) {
    this.paginator.firstPage();
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  private _filterRecords() {
    this.paginator.firstPage();
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
