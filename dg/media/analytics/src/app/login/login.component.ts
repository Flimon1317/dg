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
  invalidCredentials: boolean = false;
  errorMessage: string = "";
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

  initiate_login(event): void {
    event.target.innerHTML = "Please Wait...";
    event.target.disabled = true;
    this.loginService.login(this.userDetail).subscribe(val => {
      localStorage.setItem('ApiKey', JSON.stringify(val.key));
      localStorage.setItem('UserName', JSON.stringify(val.user_name));
      localStorage.setItem('FullName', JSON.stringify(val.full_name));
      localStorage.setItem('PhoneNumber', JSON.stringify(val.phone_number));
      this.hideChildModal();
      this.username = JSON.stringify(val.full_name);
    },
      err => {
        event.target.innerHTML = "Login";
        event.target.disabled = false;
        this.invalidCredentials = true;
        this.errorMessage = err;
      });
  }

  logout(): void {
    localStorage.clear();
    this.username = "";
  }
}
