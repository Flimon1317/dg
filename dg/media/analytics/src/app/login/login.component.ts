import { Component, OnInit, ViewChild } from '@angular/core';
import { ModalDirective } from 'ngx-bootstrap/modal';
import { LoginService } from './login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  @ViewChild('childModal') public childModal: ModalDirective;
  userDetail = { username: "", password: "" }
  username: string = "";
  constructor(private loginService: LoginService) { }

  ngOnInit() {
    this.username = localStorage.getItem('FullName');
  }

  public showChildModal(): void {
    this.childModal.show();
  }

  public hideChildModal(): void {
    this.childModal.hide();
  }

  initiate_login(): void {
    this.loginService.login(this.userDetail).subscribe(val => {
      localStorage.setItem('ApiKey', JSON.stringify(val.key));
      localStorage.setItem('UserName', JSON.stringify(val.user_name));
      localStorage.setItem('FullName', JSON.stringify(val.full_name));
      localStorage.setItem('PhoneNumber', JSON.stringify(val.phone_number));
      this.hideChildModal();
      this.username = JSON.stringify(val.full_name);
    });
  }

  logout(): void {
    localStorage.clear();
    this.username = "";
  }
}
