export const navsConfig = {
  'navs': {
    'Home': {
      // 'active': true,
      'import': {
        'overall': false,
        'recent': false,
      },
      'containers': {
        'container1': {
          'Volume and Famers Cummulative Count': {
            'addDivs': ['cummulativeCount']
          },
        }
      }
    },
    'Analytics': {
      'subNavs': {
        'Aggregators': {
          'active': true,
          'containers': {
            'container1': {
              'Volume': {
                'addDivs': ['aggrvol']
              },
              'Visits': {
                'addDivs': ['aggrvisit']
              }
            },
            'container2': {
              'SPK/CPk': {
                'addDivs': ['aggrspkcpk']
              },
              'Recovered/Total': {
                'addDivs': ['aggrrecoveredtotal']
              }
            },
            'container3': {
              'Farmer Count': {
                'addDivs': ['aggrfarmercount']
              }
            }
          }
        },
        'Mandi': {
          'containers': {
            'container1': {
              'Volume': {
                'addDivs': ['mandivolume']
              },
              'Visits': {
                'addDivs': ['mandivisit']
              }
            },
            'container2': {
              'SPK/CPk': {
                'addDivs': ['mandispkcpk']
              },
              'Recovered/Total': {
                'addDivs': ['mandirecoveredtotal']
              }
            },
            'container3': {
              'Farmer Count': {
                'addDivs': ['mandifarmercount']
              }
            }
          }
        },
        'Crop': {
          'containers': {
            'container1': {
              'Volume': {
                'addDivs': ['cropvolume']
              },
              'Amount': {
                'addDivs': ['cropamount']
              }
            },
            'container2': {
              'Crop Prices': {
                'addDivs': ['cropprices']
              }
            },
            'container3': {
              'Farmer Count': {
                'addDivs': ['cropfarmercount']
              }
            }
          }
        },
      }
    },
    'Time Series': {
      'active': true,
      'DropDownGraph': {
        'container1': {
          'addTab': false,
          'Volume Farmer': {
            'addDivs': ['volFarmerTS', 'spkcpkTS']
          },
        },
      }
    }
  },
}
