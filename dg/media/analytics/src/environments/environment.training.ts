import { chartsConfig } from '../../training/configs/GraphsConfig';
import { tabsConfig } from '../../training/configs/TabsConfig';
import { cardConfig } from '../../training/configs/CardsConfig';

export const environment = {
  production: true,
  url: 'http://localhost:8000/training/',
  chartsConfig: chartsConfig,
  tabsConfig : tabsConfig,
  cardsConfig : cardConfig
};