
window.onload = date;

//####################################Form Ready#######################################

  jQuery(document).ready(function ($) {

    $('#partnerId').chosen({});
    $('#countryId').chosen({});
    $('#stateId').chosen({});
    $('#districtId').chosen({});$('#blockId').chosen({});
    $('#villageId').chosen({});
    $('#videoId').chosen({});
    $('#blocknumber_video').chosen();
    $('#villagenumber_video').chosen();
    $('#list_video').chosen();
    $('#resetId').click(function () {

        $('#partnerId').val('').trigger("chosen:updated");
        $('#countryId').val('').trigger("chosen:updated");
        $('#stateId').find('option').remove().end().val('').prop('disabled', true).trigger("chosen:updated");
        $('#districtId').find('option').remove().end().val('').prop('disabled', true).trigger("chosen:updated");
        $('#blockId').find('option').remove().end().val('').prop('disabled', true).trigger("chosen:updated");
        $('#villageId').find('option').remove().end().val('').prop('disabled', true).trigger("chosen:updated");
        $('#videoId').find('option').remove().end().val('').prop('disabled', true).trigger("chosen:updated");
        $("#formId").each(function () {
            this.reset();
        });

    });
    $('#formId').keypress(function (event) {

        if (event.keyCode === 10 || event.keyCode === 13)
            event.preventDefault();

    });
    $("#partnerId").bind("change", function () {
        $('#videoId').prop('disabled', false);
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");
    });
    $("#countryID").bind("change", function () {
        $("#partnerId").find('option').remove();
        $('#stateId').prop('disabled', false);
        $('#stateId').find('option').remove();
        $("#districtId").find('option').remove();
        $("#blockId").find('option').remove();
        $("#villageId").find('option').remove();
        $("#partnerId").val('').trigger('chosen:updated');
        $("#stateId").val('').trigger("chosen:updated");
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");
        $("#districtId").prop('disabled',true);
        $("#districtId").val('').trigger("chosen:updated");
        $("#blockId").prop('disabled',true);
        $("#blockId").val('').trigger("chosen:updated");
        $("#villageId").prop('disabled',true);
        $("#villageId").val('').trigger("chosen:updated");
    });
    $("#stateId").bind("change", function () {
        $("#partnerId").find('option').remove();
        $("#districtId").prop('disabled', false);
        $("#districtId").find('option').remove();
        $("#blockId").find('option').remove();
        $("#villageId").find('option').remove();
        $("#partnerId").val('').trigger('chosen:updated');
        $("#districtId").val('').trigger("chosen:updated");
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");
        $("#blockId").prop('disabled',true);
        $("#villageId").prop('disabled',true);
        $("#blockId").val('').trigger("chosen:updated");
        $("#villageId").val('').trigger("chosen:updated");
    });
    $("#districtId").bind("change", function () {
        $("#blockId").prop('disabled', false);
        $("#blockId").find('option').remove();
        $("#villageId").find('option').remove();
        $("#partnerId").find('option').remove();
        $("#partnerId").val('').trigger('chosen:updated');
        $("#blockId").val('').trigger("chosen:updated");
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");
        $("#villageId").prop('disabled',true);
        $("#villageId").val('').trigger("chosen:updated");

    });
    $("#blockId").bind("change", function () {
        $("#villageId").prop('disabled', false);
        $("#villageId").find('option').remove();
        $("#partnerId").find('option').remove();
        $("#partnerId").val('').trigger('chosen:updated');
        $("#villageId").val('').trigger("chosen:updated");
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");

    });
    $('villageId').bind("change",function () {
        $('#videoId').find('option').remove();
        $("#videoId").val('').trigger("chosen:updated");
    });
    $("#partnerId").next().bind("click",function(){
        populate_partner('partner');
        $("#partnerId").trigger("chosen:updated");
    });
    $("#stateId").next().bind("click", function () {
        populate('state', $("#countryId").val());
        $("#stateId").trigger("chosen:updated");
    });
    $("#districtId").next().bind("click", function () {
        populate("district", $("#stateId").val());
        $("#districtId").trigger("chosen:updated");
    });
    $("#blockId").next().bind("click", function () {
        populate("block", $("#districtId").val());
        $("#blockId").trigger("chosen:updated");
    });
    $("#villageId").next().bind("click", function () {
        populate("village", $("#blockId").val());
        $("#villageId").trigger("chosen:updated");
    });
    $("#videoId").next().bind("click", function () {
        populate_video("video");
        $("#videoId").trigger("chosen:updated");
    });
});
//###############################Populate the dropdowns for filter######################################

function populate(src, prevValue) {
    if (!(jQuery("#" + src + "Id" + " option ").length != 0))
 //   for (var values in prevValue) {
        $.get("/raw_data_analytics/dropdown_" + src + "/", {selected: prevValue})
            .done(function (data) {
                data_json = JSON.parse(data);
                for (var jsonData in data_json) {
                    if (jQuery("#" + src + "Id" + " option[value='" + data_json[jsonData] + "']").length == 0)
                        $("#" + src + "Id").append('<option value="' + data_json[jsonData] + '">' + data_json[jsonData] + '</option>');
                }
            });
 //   }
}
function populate_video(src){
  if (!(jQuery("#" + src + "Id" + " option ").length != 0))
  //for (var values in prevValue) {
      $.get("/raw_data_analytics/dropdown_video/", {"country[]":$("#countryId").val(),"partner[]":$("#partnerId").val(),"state[]":$("#stateId").val(),"district[]":$("#districtId").val(),"block[]":$("#blockId").val(),"village[]":$("#villageId").val()})
          .done(function (data) {
              data_json = JSON.parse(data);
              for (var jsonData in data_json) {
                  if (jQuery("#" + src + "Id" + " option[value='" + data_json[jsonData][0] + "']").length == 0)
                      $("#" + src + "Id").append('<option value="' + data_json[jsonData][0] + '">' + data_json[jsonData][0]+' ( '+data_json[jsonData][1]+' )' +'</option>');
              }
          });
  //}
}

function populate_partner(src){
    if(!(jQuery("#partnerId option").length!=0))
        $.get("/raw_data_analytics/dropdown_partner",{"country[]":$("#countryId").val(),"state[]":$("#stateId").val(),"district[]":$("#districtId").val(),"block[]":$("#blockId").val(),"village[]":$("#villageId").val()})
            .done(function(data){
                data_json =JSON.parse(data);
                for(var jsonData in data_json){
                    if (jQuery("#" + src + "Id" + " option[value='" + data_json[jsonData][0] + "']").length == 0)
                        $("#" + src + "Id").append('<option value="' + data_json[jsonData][0] + '">' + data_json[jsonData][0] + '</option>');
                }
            });
}
//##################################################################################################################

function list_display() {
    if ((list.checked) && (video.checked)) {

        if(villagenum.checked){
            $('#villagenum').removeAttr('checked');
        }
        if(blocknum.checked){
            $('#blocknum').removeAttr('checked');
        }
        listoptions.style.visibility = "visible";        
        villagenumberoptions.style.visibility="hidden";
        blocknumberoptions.style.visibility="hidden";
    }
    else
        listoptions.style.visibility = "hidden";
}
function village_number_dropdown(){
    if((villagenum.checked) && (video.checked)){
        if(list.checked){
            $('#list').removeAttr('checked');
        }
        if(blocknum.checked){
            $('#blocknum').removeAttr('checked');
        }
        villagenumberoptions.style.visibility="visible";
        listoptions.style.visibility="hidden";
        blocknumberoptions.style.visibility="hidden";
    }
    else
        villagenumberoptions.style.visibility="hidden";
}
function block_number_dropdown(){
    if((blocknum.checked) && (video.checked)){
        if(villagenum.checked){
            $('#villagenum').removeAttr('checked');
        }
        if(list.checked){
            $('#list').removeAttr('checked');
        }
        blocknumberoptions.style.visibility="visible";        
        listoptions.style.visibility="hidden";
        villagenumberoptions.style.visibility="hidden";
    }
    else
        blocknumberoptions.style.visibility="hidden";        

    
}
//validation check
function validation_check() {
    var error = 0;
    var checked_partitions = [partner, country, state, district, block, village]
    var checked_partitions_restrict = [animator, group, people, video];
    var checked_values = [screening, adoption, animator_no, attendance, video_screened_no, video_produced_no,blocknum,villagenum]
    var count_partition_restrict = 0;
    count_partition = 0;
    var count_values = 0;
    var i;

    for (i = 0; i < checked_partitions.length; i++) {

        if (checked_partitions[i].checked) {
            count_partition++;
        }
    }
    for (i = 0; i < checked_values.length; i++) {
        if (checked_values[i].checked) {
            count_values++;
        }
    }

    if ((count_partition == 0) && (count_values == 0) && (count_partition_restrict == 0) && (!list.checked)) {
        alert("Please select some fields !!");
        event.preventDefault();
    }

    else if ((count_partition != 0) && (count_values == 0) && (!list.checked)) {
        alert("Please select atleast one value field!!");
        event.preventDefault();
    }


    if (list.checked) {
        for (i = 0; i < checked_partitions_restrict.length; i++) {
            if (checked_partitions_restrict[i].checked) {
                count_partition_restrict++;
            }
        }
        if (count_partition_restrict > 1) {
            alert("Along with list please select either Animator/Group/Registered Viewers/Video from Partitions");
            error = 1;
            event.preventDefault();
        }

        else if ((count_partition_restrict == 0) && (count_partition == 0)) {
            alert("Select atleast one option from partition fields!!!");
            error = 1;
            event.preventDefault();

        }
    }
    //alert(list_video.selectedIndex);
    if (((animator.checked) && (animator_no.checked)) ||
        ((people.checked) && (animator_no.checked)) ||
        ((people.checked) && (attendance.checked)) ||
        ((group.checked) && (animator_no.checked)) ||
        ((video.checked) && (animator_no.checked)) ||
        ((video.checked) && (video_screened_no.checked)) ||
        ((video.checked) && (video_produced_no.checked))
        ||((village.checked)&&(villagenum.checked))||
        ((block.checked)&&(blocknum.checked))) {
        alert("Invalid combination of 'Value' and 'Partition' fields!! Please check");
        error = 1;
        event.preventDefault();
    }

    if((video.checked) && (blocknum.checked) && (blocknumber_video.selectedIndex == 0)){
        alert("Please select number of villages for screening  or number of villages for adoption from dropdown!!!");
        error = 1;
        event.preventDefault();
    }

    if ((video.checked) && (list.checked) && (list_video.selectedIndex == 0)) {
        alert("Please select list of videos produced or list of videos produced from dropdown!!!");
        error = 1;
        event.preventDefault();

    }

    if (list.checked) {
        if (count_values > 0) {
            alert("No other value fields can be selected along with list!!");
            error = 1;
            event.preventDefault();
        }
    }
    newfrom_date = new Date($('#from_date').val())
    newto_date  = new Date($('#to_date').val());
    span =new Date(newto_date-newfrom_date);
    days = span/1000/60/60/24;
    if(isNaN( newfrom_date.getTime() ) ){
        alert("Please Fill 'From Date'");
        error = 1;
        event.preventDefault();
    }
    else if (isNaN( newto_date.getTime() ) ){
        alert("Please Fill 'To Date'");
        error = 1;
        event.preventDefault();
    }
    else if(!(days>=0)){
        alert("'From Date' cannot be greater than 'To Date'");
            error = 1;
            event.preventDefault();
    }
    
}
//#######################################onload-date################################################
function date() {
    date = new Date();
    document.getElementById('to_date').valueAsDate = date;
    date.setMonth(date.getMonth() - 1);
    document.getElementById('from_date').valueAsDate = date;
   
}