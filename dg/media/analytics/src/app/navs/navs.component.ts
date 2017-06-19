import { Component, OnInit } from '@angular/core';
import { environment } from '../../environments/environment.loop';

@Component({
  selector: 'app-navs',
  templateUrl: './navs.component.html',
  styleUrls: ['./navs.component.css']
})

export class NavsComponent implements OnInit {
  public isCollapsed:boolean = false;
  navsConfig = environment.navsConfig;
  overall : false;
  recent : false;
  test = false;
  toggleNav = {};

  constructor() {}
  
  ngOnInit() {
    let exceptionNavs = ['active','overall','recent','showDivs']
    Object.keys(this.navsConfig).forEach(navOne => {
      let tempDict = {}
      tempDict['status'] = false;
      tempDict['subNav'] = fillSubNav(this.navsConfig[navOne])
      this.toggleNav[navOne] = tempDict;
    })
     function fillSubNav(subNavs) {
      let navsList = []
      Object.keys(subNavs).forEach(nav => {
        if(!(exceptionNavs.indexOf(nav)>-1)) {
          navsList.push(nav);
        }
      })
      return navsList
    }
    console.log(this.toggleNav)
  }

  showContent(subNav) {
    this.test = true
    //console.log(subNav)
  }  
  toggleNavKeys() {
    return Object.keys(this.toggleNav)
  }

  setNav(selectedItem : string) {
    Object.keys(this.toggleNav).forEach(nav => {
      this.toggleNav[nav].status = false
    });
    this.toggleNav[selectedItem].status = true;
  }
}
