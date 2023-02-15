# Daily Illini Salary Guide Widget 💸

An [embeddable Angular widget](https://daily-illini.github.io/salary-guide-widget/) for exploring salaries in the UI system. This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version `14.2.5`.

## Setup

First, make sure you have Node.js and the [Angular CLI](https://github.com/angular/angular-cli) installed. Then clone the repository on your local machine.

### Development

Do any substantial development work in a new branch. After you've tested out and committed your changes, create a pull request against the `main` branch, which reflects the [live application](https://daily-illini.github.io/salary-guide-widget/) on the Daily Illini website. Any push to the `main` branch will trigger a workflow that will update the live application.

### Viewing Changes

Run `ng serve` to start a development server, then in a browser tab, navigate to `http://localhost:4200/` to view the widget.

The application will automatically reload if you change any of the source files.

## Widget Structure

### `src/app/`

This directory is where most of the relevant widget code is located. Inside this directory, the two files of interest are `app.component.html` and `app.component.ts`. 

#### `app.component.html`

The HTML file describes the widget table structure and its tabs, or pages. 

The `<mat-tab-group>` tag controls the tab bar at the top of the app, and the `<mat-tab>` tags
correspond to different tab/page views for the widget.

`<div class="search-container">` defines the widget's search controls.

#### `app.component.ts`

The TypeScript (.ts) file describes the underlying logic for the widget and manages the salary guide data.

*add more documentation stuff*

### `src/assets/`

This directory contains the salary guide data per academic year in various JSON files. 

The widget pulls these files and filters the data by using GET requests to fetch the appropriate information. The `contents.txt` text files map the salary data to the widget's class variables. 

You can see the implementation in `app.component.ts` whenever the `httpClient` executes a `get()` request.

## Resources

For comments, questions, and bug requests, please email [webdev@dailyillini.com](mailto:webdev@dailyillini.com)

Check out the [Angular docs](https://angular.io/docs) and the [Angular Material docs](https://material.angular.io/components/categories) for references.
