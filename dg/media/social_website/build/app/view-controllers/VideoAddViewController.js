define(["require","framework/controllers/Controller","framework/ViewRenderer","jquery","libs/external/select2","libs/external/jquery-ui","libs/external/resumable","app/libs/PracticeMappingDataFeed","app/libs/CollectionVideoDropDownDataFeed","text!app/views/practice-mapping.html","text!app/views/collection-add-video-dropdown.html"],function(e){var t=e("framework/controllers/Controller"),n=e("framework/ViewRenderer"),r=e("jquery"),i=e("libs/external/select2"),s=e("libs/external/jquery-ui");e("libs/external/resumable");var o=e("app/libs/PracticeMappingDataFeed"),u=e("app/libs/CollectionVideoDropDownDataFeed"),a=e("text!app/views/practice-mapping.html"),f=e("text!app/views/collection-add-video-dropdown.html"),l="/social/api/postvideo/",c=t.extend({constructor:function(e){return this.base(e),this.getPracticeMapping(),this.initSelect2(),this},_initReferences:function(e){this.base();var t=this._references;t.$videoAddWrapper=e,t.$videoAddContainer=e.find(".js-video-add-container"),t.$practiceMappingContainer=e.find(".js-collection-mapping-container"),t.$videoDropDownContainer=e.find(".js-collection-video-dropdown-container"),t.$dropDown=e.find(".js-video-criteria"),t.$partnerList=e.find(".js-partnerlist"),t.$stateList=e.find(".js-statelist"),t.$langList=e.find(".js-langlist"),t.$titleField=e.find(".js-video-title"),t.$descField=e.find(".js-video-desc"),t.dataFeed=new o,t.videodataFeed=new u("api/videodropdown/"),t.resumable=new Resumable({target:l,simultaneousUploads:4,query:{upload_token:"my_token"}}),t.$saveButton=r(".js-save-video-btn"),t.resumable.assignBrowse(document.getElementById("addButton")),t.resumable.assignDrop(document.getElementById("video-dropzone"))},_initEvents:function(){this.base();var e=this._boundFunctions,t=this._references;e.onDataProcessed=this._onDataProcessed.bind(this),t.dataFeed.on("dataProcessed",e.onDataProcessed),e.onVideoDataProcessed=this._onVideoDataProcessed.bind(this),t.videodataFeed.on("dataProcessed",e.onVideoDataProcessed),e.onSaveVideoClick=this._onSaveVideoClick.bind(this),t.$saveButton.on("click",e.onSaveVideoClick),e.onFileAdded=this._onFileAdded.bind(this),t.resumable.on("fileAdded",e.onFileAdded),e.fileProgress=this._fileProgress.bind(this),t.resumable.on("fileProgress",e.fileProgress),e.onFileSuccess=this._onFileSuccess.bind(this),t.resumable.on("fileSuccess",e.onFileSuccess),this._boundFunctions.onDropDownChosen=this._onDropDownChosen.bind(this),t.$dropDown.on("change",this._boundFunctions.onDropDownChosen)},_dropdownChosen:function(){$(".chosen-select").chosen({no_results_text:"No results match",width:"90%"})},selectCollectionMapping:function(){var e=this._references;e.$collectionUid&&e.$practiceMappingContainer.data("category").trim()&&(e.$catList.val(e.$practiceMappingContainer.data("category").trim()).change(),e.$subCatList.val(e.$practiceMappingContainer.data("subcategory").trim()).change(),e.$topicList.val(e.$practiceMappingContainer.data("topic").trim()).change(),e.$subTopicList.val(e.$practiceMappingContainer.data("subtopic").trim()),e.$subjectList.val(e.$practiceMappingContainer.data("subject").trim()))},getPracticeMapping:function(){var e=this._references.dataFeed.getPracticeMapping();if(e==0)return!1;this._references.mapping=e,this._renderPracticeMapping(e),this.selectCollectionMapping(),this.initSelect2()},_onDataProcessed:function(){this.getPracticeMapping()},_onVideoDataProcessed:function(){this.getCollectionVideoDropDown()},_renderVideoFormItems:function(e){n.renderAppend(this._references.$videoAddContainer,videoFormTemplate,e)},_renderPracticeMapping:function(e){var t=this._references,i=[],s;for(s in e)i.push(s);var o={category:i.sort()},u=n.render(a,o);this._references.$practiceMappingContainer.html(u),this._references.category=i.sort(),t.$catList=r(".js-catlist"),t.$subCatList=r(".js-subcatlist"),t.$topicList=r(".js-topiclist"),t.$subTopicList=r(".js-subtopiclist"),t.$subjectList=r(".js-subjectlist"),this._boundFunctions.onCategoryChosen=this._onCategoryChosen.bind(this),t.$catList.on("change",this._boundFunctions.onCategoryChosen),this._boundFunctions.onsubCategoryChosen=this._onsubCategoryChosen.bind(this),t.$subCatList.on("change",this._boundFunctions.onsubCategoryChosen),this._boundFunctions.onTopicChosen=this._onTopicChosen.bind(this),t.$topicList.on("change",this._boundFunctions.onTopicChosen)},_renderVideoCollectionDropDown:function(e){var t=this._references,i={video:e},s=n.render(f,i);t.$videoDropDownContainer.html(s),t.$vidList=r(".js-vidlist"),this._boundFunctions.onVideoChosen=this._onVideoChosen.bind(this),t.$vidList.on("change",this._boundFunctions.onVideoChosen),this.initSelect2()},initSelect2:function(){var e=this._references;try{$(".chosen-select").select2({no_results_text:"No results match",width:"90%"})}catch(t){$("select.chosen-select").select2({no_results_text:"No results match",width:"90%"})}},_onDropDownChosen:function(){var e=this._references;e.$partnerList.val()!=""&&e.$stateList.val()!=""&&e.$langList.val()!=""&&(e.videodataFeed.addInputParam("limit",!1,0),e.videodataFeed.setInputParam("limit",0,!1),e.videodataFeed.addInputParam("state",!1,e.$stateList.val()),e.videodataFeed.setInputParam("state",e.$stateList.val(),!1),e.videodataFeed.addInputParam("partner",!1,e.$partnerList.val()),e.videodataFeed.setInputParam("partner",e.$partnerList.val(),!1),e.videodataFeed.addInputParam("language",!1,e.$langList.val()),e.videodataFeed.setInputParam("language",e.$langList.val(),!1),this.getCollectionVideoDropDown())},_onCategoryChosen:function(){var e=this._references,t=e.$catList.val(),n=this._references.mapping;e.$subCatList.find("option:not(:first)").remove(),e.$topicList.find("option:not(:first)").remove(),e.$subTopicList.find("option:not(:first)").remove(),e.$subjectList.find("option:not(:first)").remove();var r=n[t],i;for(i in r)i!="subject"&&e.$subCatList.append(new Option(i,i));var s=n[t].subject.sort(),o;for(o in s)e.$subjectList.append(new Option(s[o],s[o]));this.initSelect2()},_onsubCategoryChosen:function(){var e=this._references,t=e.$catList.val(),n=e.$subCatList.val(),r=e.mapping;e.$topicList.find("option:not(:first)").remove(),e.$subTopicList.find("option:not(:first)").remove();var i=[],s;for(s in r[t][n])i.push(s),e.$topicList.append(new Option(s,s));this.initSelect2()},_onTopicChosen:function(){var e=this._references,t=e.$catList.val(),n=e.$subCatList.val(),r=e.$topicList.val(),i=e.mapping,s=i[t][n][r];s=s.sort(),e.$subTopicList.find("option:not(:first)").remove();var o;for(o in s)e.$subTopicList.append(new Option(s[o],s[o]));this.initSelect2()},_onFileAdded:function(e){$("#video-innerwrapper").hide(),document.getElementById("fileInfo").innerHTML=e.fileName,$("#progressbar").show(),$("#video-btns").show();var t=this._references;$("#v-pause").click(function(){$("#v-pause").html()=="Pause"?(t.resumable.pause(),$("#v-pause").html("Resume")):$("#v-pause").html()=="Resume"&&(t.resumable.upload(),$("#v-pause").html("Pause"))}),$("#v-cancel").click(function(){var n=confirm("Are you sure you want to cancel upload?");n==1&&(t.resumable.removeFile(e),$("#progressbar-inner").css({width:"0"}),$("#progress-percent").text("Upload cancelled"))}),this._references.file=e,this._onUploadVideoClick()},_fileProgress:function(e){var t=Math.floor(e.progress()*100)*3;$("#progressbar-inner").css({width:t}),$("#progress-percent").text(t/3+"%")},_onFileSuccess:function(e,t){alert(t),$.post(l,{fileidentifier:e.uniqueIdentifier,combine:1}).done(function(e){alert(e),$("#progressbar").hide(),$("#video-btns").hide()})},_onSaveVideoClick:function(e){e.preventDefault();try{var t=this._references,n=t.$titleField.val(),i=t.$descField.val(),s=t.$stateList.val(),o=t.$partnerList.val(),u=t.$langList.val(),a=t.$vidList.val(),f=t.$catList.val(),c=t.$subCatList.val(),h=t.$topicList.val(),p=t.$subTopicList.val(),d=t.$subjectList.val();try{a!=""?$.post(l,{fileidentifier:t.file.uniqueIdentifier,save:1,title:n,desc:i,video_id:a,category:f.trim(),sub_category:c.trim(),topic:h.trim(),sub_topic:p.trim(),subject:d.trim()}).done(function(e){alert("file associated data saved")}):r(".js-partner-label").notify("No Video is Chosen",{position:"left"})}catch(v){$("html, body").animate({scrollTop:0},"slow"),r("#video-innerwrapper").notify("No video file selected for upload",{position:"top-center"})}}catch(v){$("html, body").animate({scrollTop:0},"slow"),r(".js-partner-label").notify("Combination of Partner, State and Language not choosen",{position:"left"})}},_onUploadVideoClick:function(e){var t=this._references;$.post(l,{fileidentifier:this._references.file.uniqueIdentifier,filename:this._references.file.fileName,num_chunks:this._references.file.chunks.length,make_entry:1}).done(function(e){e==1?(alert("File with this name already uploaded"),$("#progress-percent").text("100%"),$("#progressbar").hide(),$("#video-btns").hide()):t.resumable.upload()})},getCollectionVideoDropDown:function(){var e=this._references,t=e.videodataFeed.getCollectionVideoDropDown();if(t==0)return!1;e.videoArray=t,this._renderVideoCollectionDropDown(t),e.$partnerList.prop("disabled",!0),e.$stateList.prop("disabled",!0),e.$langList.prop("disabled",!0)},_onVideoChosen:function(){var e=this._references,t=e.$vidList.val(),n=this._references.videoArray,r,i,s;for(var o=0;o<n.length;o++)n[o].uid==t&&(r=n[o].title,i=n[o].desc,s=n[o].practice);e.$titleField.val(r),e.$descField.val(i),e.$titleField.prop("disabled",!1),e.$descField.prop("disabled",!1),e.$catList.val(""),e.$subCatList.find("option:not(:first)").remove(),e.$topicList.find("option:not(:first)").remove(),e.$subTopicList.find("option:not(:first)").remove(),e.$subjectList.find("option:not(:first)").remove(),this.initSelect2(),s!="Null"&&(e.$catList.val(s.category).change(),e.$subCatList.val(s.subcategory).change(),e.$topicList.val(s.topic).change(),e.$subTopicList.val(s.subtopic).change(),e.$subjectList.val(s.subject).change())},setInputParam:function(e,t,n){this._references.dataFeed.setInputParam(e,t,n)},_onInputParamChanged:function(){this.getFeaturedCollection()},destroy:function(){this.base()}});return c});