
import { Component, OnInit, AfterViewInit, AfterViewChecked, Inject } from '@angular/core';
import { DOCUMENT } from '@angular/platform-browser';
import { environment } from '../../environments/environment.loop';
import { GraphsService } from './navs.service';
import { SharedService } from '../shared.service';
import { global_filter } from '../app.component';
import { GlobalFilterSharedService } from '../global-filter/global-filter-shared.service';
import { DropDownItem } from './dropdown.model';

@Component({
  selector: 'app-navs',
  templateUrl: './navs.component.html',
  styleUrls: ['./navs.component.css']
})

export class NavsComponent implements OnInit,
  AfterViewChecked {
  //used for collapse button
  public isCollapsed: boolean = false;
  public showOverall: boolean = true;
  public showFilters: boolean = true;
  navClicked: boolean = false;
  public selectedNav: string = '';

  //read config files from environment created for each app
  navsConfig = environment.navsConfig;
  chartsConfig = environment.chartsConfig;
  generalConfig = environment.generalConfig;

  //initialize modules as false and toggle based on user configuration
  overall: false;
  recent: false;

  //keep track of nav switches and respective subnavs
  toggleNav = {};
  //dict with key as end nav and its corresponding containers
  containers = {};
  //dict with key and its corresponding filter graphs to show drop down for graphs
  filterGraphs = {};
  //list of charts in DOM
  charts = [];
  containerCharts = [];
  //Display drop down type graphs
  // showDropDownGraphs: boolean = false;
  filters = { 'params': {} };

  test = '';
  constructor(private graphService: GraphsService, private _sharedService: SharedService,
    private _globalfiltersharedService: GlobalFilterSharedService, @Inject(DOCUMENT) private document: any) {
    this._sharedService.argsList$.subscribe(filters => {
      if (filters) {
        Object.assign(filters.params, global_filter);
      } else {
        filters = {};
        filters['params'] = global_filter;
      }
      this.filters = filters;
      Object.keys(this.containers).forEach(container => {
        this.containers[container].applyFilter = false;
      });
      this.getGraphsData(filters);
      this.containers[this.selectedNav].applyFilter = true;
    });
    this._globalfiltersharedService.argsList$.subscribe(filters => {
      this.filters.params = global_filter;

      Object.keys(this.containers).forEach(container => {
        this.containers[container].applyFilter = false;
      });
      this.getGraphsData(this.filters);
      this.containers[this.selectedNav].applyFilter = true;
    });
    /*setInterval(() => {
      this.charts.forEach(chart => {
        chart.nativeChart.reflow();
      });
    }, 0);*/
  }

  ngOnInit(): void {
    Object.keys(this.chartsConfig).forEach(chart => {
      this.charts.push({
        name: chart,
        options: this.chartsConfig[chart],
        // nativeChart will be assigned with saveInstance
        nativeChart: null
      });
    })
    this.renderNavs();
    //this.renderCharts();
  }

  ngAfterViewChecked() {
    if (this.navClicked) {
      this.navClicked = false;
      Object.assign(this.filters.params, global_filter);
      this.getGraphsData(this.filters);
      this.containers[this.selectedNav].applyFilter = true;
    }
  }

  // renderCharts(): void {
  //   Object.keys(this.chartsConfig).forEach(chart => {
  //     this.charts.push({
  //       name: chart,
  //       options: this.chartsConfig[chart],
  //       // nativeChart will be assigned with saveInstance
  //       nativeChart: null
  //     });
  //   })
  // }
  //render navs and subnavs and create respective containers based on selected nav
  renderNavs(): void {
    Object.keys(this.navsConfig.navs).forEach(nav => {
      let tempDict = {};
      tempDict['status'] = false;
      //check if subNavs exists and create respective container with default view flag as false
      if (this.navsConfig.navs[nav].subNavs != undefined) {
        tempDict['subNavs'] = this.getDictKeys(this.navsConfig.navs[nav].subNavs);
        Object.keys(this.navsConfig.navs[nav].subNavs).forEach(subNav => {
          let container = this.navsConfig.navs[nav].subNavs[subNav];
          if (this.navsConfig.navs[nav].subNavs[subNav].containers != undefined) {
            this.setContainer(subNav, container);
          }
          else if (this.navsConfig.navs[nav].subNavs[subNav].DropDownGraph != undefined) {
            this.setFilterContainer(subNav, container);
          }
        });
      }
      else if (this.navsConfig.navs[nav].containers != undefined) {
        let container = this.navsConfig.navs[nav];
        this.setContainer(nav, container);
      }
      else if (this.navsConfig.navs[nav].DropDownGraph != undefined) {
        let container = this.navsConfig.navs[nav];
        this.setFilterContainer(nav, container);
      }
      else if (this.navsConfig.navs[nav].href != undefined) {
        tempDict['href'] = this.navsConfig.navs[nav].href;
      }
      this.toggleNav[nav] = tempDict;

      //check for active link on nav bar and set status as true
      if (this.navsConfig.navs[nav].hasOwnProperty('active')) {
        this.toggleNav[nav].status = true;
        this.showContent(nav);
      }
    });
    console.log(this.test);
  }

  addChartsToDict(containers) {
    let charts = [];
    Object.keys(containers).forEach(container => {
      Object.keys(containers[container]).forEach(tab => {
        if (containers[container][tab].hasOwnProperty('addDivs')) {
          containers[container][tab]['addDivs'].forEach(chart => {
            charts.push({ name: chart, chart: this.chartsConfig[chart] });
          });
        }
      });
    });
    return charts;
  }

  //set container view based on clicked nav link
  setContainer(nav, container): void {
    this.containers[nav] = container;
    this.containers[nav]['charts'] = this.addChartsToDict(container.containers);
    this.containers[nav]['displayContent'] = false;
    this.containers[nav]['applyFilter'] = true;
  }

  //set container for navs with interdependent filter and graph
  setFilterContainer(nav, container): void {
    this.filterGraphs[nav] = container;
    this.filterGraphs[nav]['charts'] = this.addChartsToDict(container.DropDownGraph);
    this.filterGraphs[nav]['displayContent'] = false;
    this.filterGraphs[nav]['applyFilter'] = true;
  }

  //access underlying chart
  saveInstance(chartInstance, chart) {
    chart.nativeChart = chartInstance;
  }

  //get data for graphs from service
  getGraphsData(filters): void {
    this.containerCharts.forEach(chart => {
      if (chart.nativeChart && (chart.nativeChart.series.length == 0 || (!this.containers[this.selectedNav].applyFilter))) {
        chart.nativeChart.showLoading();
        filters.params['chartType'] = chart.chart.type;
        filters.params['chartName'] = chart.name;
        this.graphService.getData(filters).subscribe(dataList => {
          if (dataList['chartType'] != undefined && dataList['chartType'] === 'StockChart') {
            this.parseDataForStockChart(chart, dataList);
          }
          else {
            Object.keys(dataList).forEach(key => {
              //Find already displayed chart to enter data
              if (key === chart.name) {
                chart.nativeChart.hideLoading();
                this.clearSeriesFromGraph(chart);
                dataList[key]['outerData']['series'].forEach(entry => {
                  chart.nativeChart.addSeries(entry);
                  chart.chart.series.push(entry);
                });
                if (chart.chart.chart.drillDown) {
                  dataList[key]['innerData'].forEach(drilldownEntry => {
                    chart.chart.drilldown.series.push(drilldownEntry);
                  });
                }
              }
              else {
                this.clearSeriesFromGraph(chart);
                chart.nativeChart.showLoading(dataList['error']);
              }
            });
          }
        });
      }
    });
  }

  private parseDataForStockChart(chart, dataList): void {
    this.clearSeriesFromGraph(chart);
    let data;
    if (chart.chart.chart.dropdown) {
      this.fillMenuItemForDropDown(chart, dataList);
      data = dataList.data["1"];
    } else {
      data = dataList.data;
    }
    // console.log(data);
    // console.log(dataList.chartName);
    // console.log(chart);
    Object.keys(data).forEach(series => {
      chart.nativeChart.hideLoading();
      chart.nativeChart.addSeries(data[series]);
      chart.chart.series[series] = data[series];
    });
  }

  private fillMenuItemForDropDown(chart, dataList): any {
    Object.keys(dataList.data).forEach(series => {
      let dropDownItem = new DropDownItem();
      dropDownItem.text = dataList.data[series][0]['name'];
      dropDownItem.data = dataList.data[series][0]['data'];
      dropDownItem.onclick = function() {
        this.series[0].update({ data: dropDownItem.data, name: dropDownItem.text });
        this.exportSVGElements[0].attr({ text: dropDownItem.text });
      };
      chart.chart.exporting.buttons.toggle.menuItems.push(dropDownItem);
    });
  }

  //Empty exting data and then fill in updated data
  private clearSeriesFromGraph(chart): void {
    let size = chart.nativeChart.series.length;
    //TODO: Patch applied for stcockchart as it creates 1 additional series for naigator.
    if (chart.chart.type && chart.chart.type === 'StockChart') {
      size = chart.nativeChart.series.length - 1;
    }
    if (chart.nativeChart.series.length > 0) {
      for (var i = size - 1; i >= 0; i--) {
        chart.nativeChart.series[i].remove();
      }
    }
    chart.chart.series = [];
  }

  //function to return list of keys from a dictionary
  getDictKeys(dict) {
    return Object.keys(dict);
  }

  ifDictionary(obj): boolean {
    if (typeof obj !== 'boolean')
      return true;
    else return false;
  }

  //reset values in a dict, used for navigation and setting containers
  private resetDict(dict, flag, value): void {
    Object.keys(dict).forEach(key => {
      dict[key][flag] = value;
    });
  }

  //set status as true for clicked nav item and rest as false
  setNav(selectedItem: string): void {
    this.resetDict(this.toggleNav, 'status', false);
    this.toggleNav[selectedItem].status = true;
    //set show content for navs with subNavs
    if (this.toggleNav[selectedItem].hasOwnProperty('subNavs')) {
      this.toggleNav[selectedItem].subNavs.forEach(subNav => {
        if (this.navsConfig.navs[selectedItem].subNavs[subNav].hasOwnProperty('active')) {
          this.showContent(subNav);
        }
      });
    }
    else if (this.toggleNav[selectedItem].hasOwnProperty('href')) {
      window.open(this.toggleNav[selectedItem].href, "_blank");
    }
    else {
      this.showContent(selectedItem);
    }
  }

  //render charts to container
  private renderContainerCharts(container): void {
    container.displayContent = true;
    /*    container.charts.forEach(chart => {
          this.charts.push({
            options: chart,
            // nativeChart will be assigned with saveInstance
            nativeChart: null
          });
        });*/
    container.charts.forEach(containerChart => {
      this.charts.forEach(chart => {
        if (chart.name === containerChart.name) {
          this.containerCharts.push(containerChart);
        }
      });
    });
  }

  //display respective containers based on clicked nav
  showContent(selectedNav: string): void {
    this.selectedNav = selectedNav;
    this.navClicked = true;
    if (selectedNav == 'Home') {
      this.showOverall = true;
      this.showFilters = false;
    } else {
      this.showOverall = false;
      this.showFilters = true;
    }
    this.resetDict(this.containers, 'displayContent', false);
    this.resetDict(this.filterGraphs, 'displayContent', false);
    this.containerCharts = [];
    if (this.containers[selectedNav] != undefined) {
      this.renderContainerCharts(this.containers[selectedNav]);
    }
    else if (this.filterGraphs[selectedNav] != undefined) {
      this.renderContainerCharts(this.filterGraphs[selectedNav]);
    }
  }
}
