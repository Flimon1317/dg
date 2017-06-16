import { Component, OnInit, ViewChild } from '@angular/core';
import { ModalDirective } from 'ngx-bootstrap/modal';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  @ViewChild('childModal') public childModal: ModalDirective;
  userDetail = { username: "", password: "" }
  // username: string = "";
  // password: string = "";
  ngOnInit() {
  }

  public showChildModal(): void {
    this.childModal.show();
  }

  public hideChildModal(): void {
    this.childModal.hide();
  }

  initiate_login(): void {
    localStorage.setItem('Username', JSON.stringify(this.userDetail.username));
    console.log(this.userDetail.username, this.userDetail.password);
    console.log(localStorage.getItem('Username'));
  }
}
