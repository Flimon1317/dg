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
  toggleNav = {};
  navsSecond = [];
  overall : false;
  recent : false;
  
  constructor() {}

  ngOnInit() {
    Object.keys(this.navsConfig).forEach(navOne => {
      let tempDict = {}
      tempDict['status'] = false;
      tempDict['subNav'] = Object.keys(this.navsConfig[navOne])
      this.toggleNav[navOne] = tempDict;
    })
  }

  toggleNavKeys() {
    return Object.keys(this.toggleNav)
  }

  setNav(selectedItem : string) {
    Object.keys(this.toggleNav).forEach(nav => {
      this.toggleNav[nav].status = false
    });
    this.toggleNav[selectedItem].status = true;
    this.navsSecond = this.toggleNav[selectedItem].subNav;
  }
}
