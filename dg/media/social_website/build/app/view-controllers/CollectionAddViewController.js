define(["require","framework/controllers/Controller","framework/ViewRenderer","jquery","libs/external/select2","app/libs/PracticeMappingDataFeed","app/libs/CollectionVideoDropDownDataFeed","app/libs/CollectionsAddDataFeed","text!app/views/practice-mapping.html","text!app/views/collection-add-video-dropdown.html","text!app/views/collection-add-video-carousel.html"],function(e){var t=e("framework/controllers/Controller"),n=e("framework/ViewRenderer"),r=e("jquery"),i=e("libs/external/select2"),s=e("app/libs/PracticeMappingDataFeed"),o=e("app/libs/CollectionVideoDropDownDataFeed"),u=e("app/libs/CollectionsAddDataFeed"),a=e("text!app/views/practice-mapping.html"),f=e("text!app/views/collection-add-video-dropdown.html"),l=e("text!app/views/collection-add-video-carousel.html"),c=t.extend({constructor:function(e){return this.base(e),this.getPracticeMapping(),this.initSelect2(),this},_initReferences:function(e){this.base();var t=this._references;t.dataFeed=new s,t.videodataFeed=new o,t.addDataFeed=new u,t.$collectionAddWrapper=e,t.$collectionUid=e.find(".js-uid").data("collectionuid"),t.$metaInformationContainer=e.find(".js-meta-dropdown"),t.$videoContainer=e.find(".js-video-container"),t.$videoDropDownContainer=e.find(".js-collection-video-dropdown-container"),t.$practiceMappingContainer=e.find(".js-collection-mapping-container"),t.$saveButton=e.find(".collection-save-button"),t.$collectionTitle=e.find(".js-collection-title"),t.$dropDown=e.find(".js-video-criteria"),t.$partnerList=e.find(".js-partnerlist"),t.$stateList=e.find(".js-statelist"),t.$langList=e.find(".js-langlist")},_initEvents:function(){this.base();var e=this._boundFunctions,t=this._references;e.onDataProcessed=this._onDataProcessed.bind(this),t.dataFeed.on("dataProcessed",e.onDataProcessed),e.onVideoDataProcessed=this._onVideoDataProcessed.bind(this),t.videodataFeed.on("dataProcessed",e.onVideoDataProcessed),e.onSaveCollectionClick=this._onSaveCollectionClick.bind(this),t.$saveButton.on("click",e.onSaveCollectionClick),this._boundFunctions.onDropDownChosen=this._onDropDownChosen.bind(this),t.$dropDown.on("change",this._boundFunctions.onDropDownChosen),this.selectVideoSelectionCriteria()},selectVideoSelectionCriteria:function(){var e=this._references;e.$collectionUid&&(e.$partnerList.val(e.$metaInformationContainer.data("collectionpartner")).change(),e.$stateList.val(e.$metaInformationContainer.data("collectionstate")).change(),e.$langList.val(e.$metaInformationContainer.data("collectionlanguage")).change())},selectCollectionMapping:function(){var e=this._references;e.$collectionUid&&e.$practiceMappingContainer.data("category").trim()&&(e.$catList.val(e.$practiceMappingContainer.data("category").trim()).change(),e.$subCatList.val(e.$practiceMappingContainer.data("subcategory").trim()).change(),e.$topicList.val(e.$practiceMappingContainer.data("topic").trim()).change(),e.$subTopicList.val(e.$practiceMappingContainer.data("subtopic").trim()),e.$subjectList.val(e.$practiceMappingContainer.data("subject").trim()))},getPracticeMapping:function(){var e=this._references.dataFeed.getPracticeMapping();if(e==0)return!1;this._references.mapping=e,this._renderPracticeMapping(e),this.selectCollectionMapping(),this.initSelect2()},getCollectionVideoDropDown:function(){var e=this._references,t=e.videodataFeed.getCollectionVideoDropDown();if(t==0)return!1;e.videoArray=t,this._renderVideoCollectionDropDown(t);if(e.$collectionUid){var n=e.$videoDropDownContainer.data("videos"),r;for(r in n)console.log(n[r]),e.$vidList.val(n[r]).change()}},_onDataProcessed:function(){this.getPracticeMapping()},_onVideoDataProcessed:function(){this.getCollectionVideoDropDown()},afterCollectionAdd:function(){var e=this._references,t="/discover/"+e.$partnerList.find("option:selected").text()+"/"+e.$stateList.val()+"/"+e.$langList.val()+"/"+e.$collectionTitle.val();window.location.assign(t)},_onSaveCollectionClick:function(e){e.preventDefault();var t=this._references,n=t.$videoContainer.sortable("toArray");if(n.length<2){t.$videoContainer.notify("Collection Should Have Atleast 2 Videos",{position:"bottom"});return}t.$collectionUid&&(t.addDataFeed.addInputParam("uid",!1,t.$collectionUid),t.addDataFeed.setInputParam("uid",t.$collectionUid,!0)),t.addDataFeed.addInputParam("title",!1,t.$collectionTitle.val()),t.addDataFeed.addInputParam("partner",!1,t.$partnerList.val()),t.addDataFeed.addInputParam("language",!1,t.$langList.val()),t.addDataFeed.addInputParam("state",!1,t.$stateList.val()),t.addDataFeed.addInputParam("videos",!1,n),t.addDataFeed.addInputParam("category",!1,t.$catList.val()),t.addDataFeed.addInputParam("subcategory",!1,t.$subCatList.val()),t.addDataFeed.addInputParam("topic",!1,t.$topicList.val()),t.addDataFeed.addInputParam("subtopic",!1,t.$subTopicList.val()),t.addDataFeed.addInputParam("subject",!1,t.$subjectList.val()),t.addDataFeed.setInputParam("title",t.$collectionTitle.val(),!0),t.addDataFeed.setInputParam("partner",t.$partnerList.val(),!0),t.addDataFeed.setInputParam("language",t.$langList.val(),!0),t.addDataFeed.setInputParam("state",t.$stateList.val(),!0),t.addDataFeed.setInputParam("videos",n,!0),t.addDataFeed.setInputParam("category",t.$catList.val(),!0),t.addDataFeed.setInputParam("subcategory",t.$subCatList.val(),!0),t.addDataFeed.setInputParam("topic",t.$topicList.val(),!0),t.addDataFeed.setInputParam("subtopic",t.$subTopicList.val(),!0),t.addDataFeed.setInputParam("subject",t.$subjectList.val(),!0),t.$collectionUid?t.addDataFeed._fetch(null,this.afterCollectionAdd.bind(this),"PUT"):t.addDataFeed._fetch(null,this.afterCollectionAdd.bind(this),"POST")},_renderPracticeMapping:function(e){var t=this._references,i=[],s;for(s in e)i.push(s);var o={category:i.sort()},u=n.render(a,o);this._references.$practiceMappingContainer.html(u),this._references.category=i.sort(),t.$catList=r(".js-catlist"),t.$subCatList=r(".js-subcatlist"),t.$topicList=r(".js-topiclist"),t.$subTopicList=r(".js-subtopiclist"),t.$subjectList=r(".js-subjectlist"),this._boundFunctions.onCategoryChosen=this._onCategoryChosen.bind(this),t.$catList.on("change",this._boundFunctions.onCategoryChosen),this._boundFunctions.onsubCategoryChosen=this._onsubCategoryChosen.bind(this),t.$subCatList.on("change",this._boundFunctions.onsubCategoryChosen),this._boundFunctions.onTopicChosen=this._onTopicChosen.bind(this),t.$topicList.on("change",this._boundFunctions.onTopicChosen)},_renderVideoCollectionDropDown:function(e){var t=this._references,i={video:e},s=n.render(f,i);t.$videoDropDownContainer.html(s),t.$vidList=r(".js-vidlist"),this._boundFunctions.onVideoChosen=this._onVideoChosen.bind(this),t.$vidList.on("change",this._boundFunctions.onVideoChosen),this.initSelect2()},initSelect2:function(){var e=this._references;try{$(".chosen-select").select2({no_results_text:"No results match",width:"90%"})}catch(t){$("select.chosen-select").select2({no_results_text:"No results match",width:"90%"})}},_onDropDownChosen:function(){var e=this._references;e.$partnerList.val()!=""&&e.$stateList.val()!=""&&e.$langList.val()!=""&&(e.videodataFeed.addInputParam("limit",!1,0),e.videodataFeed.setInputParam("limit",0,!1),e.videodataFeed.addInputParam("state",!1,e.$stateList.val()),e.videodataFeed.setInputParam("state",e.$stateList.val(),!1),e.videodataFeed.addInputParam("partner",!1,e.$partnerList.val()),e.videodataFeed.setInputParam("partner",e.$partnerList.val(),!1),e.videodataFeed.addInputParam("language",!1,e.$langList.val()),e.videodataFeed.setInputParam("language",e.$langList.val(),!1),this.getCollectionVideoDropDown())},_onCategoryChosen:function(){var e=this._references,t=e.$catList.val(),n=this._references.mapping;e.$subCatList.find("option:not(:first)").remove(),e.$topicList.find("option:not(:first)").remove(),e.$subTopicList.find("option:not(:first)").remove(),e.$subjectList.find("option:not(:first)").remove();var r=n[t],i;for(i in r)i!="subject"&&e.$subCatList.append(new Option(i,i));var s=n[t].subject.sort(),o;for(o in s)e.$subjectList.append(new Option(s[o],s[o]));this.initSelect2()},_onsubCategoryChosen:function(){var e=this._references,t=e.$catList.val(),n=e.$subCatList.val(),r=e.mapping;e.$topicList.find("option:not(:first)").remove(),e.$subTopicList.find("option:not(:first)").remove();var i=[],s;for(s in r[t][n])i.push(s),e.$topicList.append(new Option(s,s));this.initSelect2()},_onTopicChosen:function(){var e=this._references,t=e.$catList.val(),n=e.$subCatList.val(),r=e.$topicList.val(),i=e.mapping,s=i[t][n][r];s=s.sort(),e.$subTopicList.find("option:not(:first)").remove();var o;for(o in s)e.$subTopicList.append(new Option(s[o],s[o]));this.initSelect2()},_onVideoChosen:function(){var e=this._references,t=e.$vidList.val(),r=this._references.videoArray,i,s;for(var o=0;o<r.length;o++)r[o].uid==t&&(s=r[o].title,i=r[o].thumbnailURL16by9);var u={title:s,uid:t,thumbnailURL:i};n.renderAppend(e.$videoContainer,l,u);var a=this;$(".sortable li .video-remove").click(function(){e.$vidList.append(new Option($(this).parent().attr("data-title"),$(this).parent().attr("id").trim())),$(this).parent().remove(),a.initSelect2()}),e.$vidList.find("option[value="+t+"]").remove(),e.$vidList.select2("val","")},setInputParam:function(e,t,n){this._references.dataFeed.setInputParam(e,t,n)},_onInputParamChanged:function(){this.getCollectionDropDown()},destroy:function(){this.base()}});return c});