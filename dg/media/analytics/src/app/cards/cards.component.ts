import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CardsService } from './cards.service';
import { SharedService } from '../shared.service';
import { environment } from '../../environments/environment.training';

@Component({
  selector: 'app-cards',
  templateUrl: './cards.component.html',
  styleUrls: ['./cards.component.css']
})

export class CardsComponent implements OnInit {

    cardsOverall = [];
    cardsRecent = [];
    
    constructor(private cardsService: CardsService, private sharedService: SharedService) {
        this.sharedService.argsList$.subscribe(data => {
        this.getData(data);
      });
    }
    cardsConfigs = environment.cardsConfig;
    ngOnInit(): void {
        Object.keys(this.cardsConfigs).forEach(key => {
            if(this.cardsConfigs[key].overall.show){
                this.cardsOverall.push({
                    'id': key,
                    'text':this.cardsConfigs[key].text,
                    'value':'...'
                });
            }
            if(this.cardsConfigs[key].recent.show){
                this.cardsRecent.push({
                    'id':key,
                    'text':this.cardsConfigs[key].text,
                    'value':'...'
                });
            }
        })
        let options = {
            webUrl: environment.url+"getData",
            params: {
                apply_filter: false,
                'cardName': '',
            }
        }
        this.getData(options);
    }

    public getData(options): any {
        Object.keys(this.cardsConfigs).forEach(key => {
            options.params.cardName = key;
            this.cardsService.getApiData(options)
                .subscribe(dataList => {
                    dataList['data'].forEach( cardData => {
                        if(cardData.placeHolder == "overall") {
                            this.cardsOverall.forEach(card => {
                                if(card.text == cardData.tagName) {
                                    card['value'] = cardData.value
                                }
                            });
                        }
                        if(cardData.placeHolder == "recent") {
                            this.cardsRecent.forEach(card => {
                                if(card.text == cardData.tagName) {
                                    card['value'] = cardData.value
                                }
                            });
                        }
                    });
            });
        });
    }
}
