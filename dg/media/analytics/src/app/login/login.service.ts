import { Injectable } from '@angular/core';
import { Http, Response, Request, Headers, RequestOptions, URLSearchParams } from '@angular/http';
import { Observable } from 'rxjs/Observable';
// import { Observer } from 'rxjs/Observer';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/observable/throw';
import { environment } from '../../environments/environment.loop';

@Injectable()
export class LoginService {
  // _baseUrl = environment.url + "login";
  _baseUrl = "http://localhost:8000/loop/" + "login/";

  constructor(private http: Http) { }

  login(body: Object): Observable<any> {
    let params: URLSearchParams = new URLSearchParams();
    for (let key in body) {
      params.set(key.toString(), body[key]);
    }
    let headers = new Headers({ 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' });
    let options = new RequestOptions({ headers: headers });
    return this.http.post(this._baseUrl, params, options)
      .map(response => response.json())
      .catch(this.handleError);
  }
  private handleError(error: any): Observable<any> {
    return Observable.throw(error.json().error || 'Server Error. Please try again');
  }

}
