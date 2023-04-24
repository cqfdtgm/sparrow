function rf1() //一次性删除左边表格选中的记录, 成功的话刷新左右两个表格.
{
    ids = $('#dg1').datagrid('getSelections');
    //alert(ids);
    if (ids.length>0) {
	var delid = [];
	for (i in ids) {
	    delid.push(ids[i].id); } 
	//alert (delid);
	// 以array为参数提交的表单, 变量名会变为变量后面加方括号字样, 比如"id[]"
	$.getJSON('Destroy', {id:delid}, function(json, status, jqr) {
	    if (status="success") {
		$('#dg1').edatagrid('reload');
		$('#dg2').edatagrid('reload');
	    }
	});
    $('#dg1').datagrid('clearSelections');
    }
}
function rf2() //一次性删除右边选中的多个表格, 成功的话刷新左右两个表格
{
    ids = $('#dg2').datagrid('getSelections');
    if (ids.length>0) {
	//$('#dg2').datatgrid('clearChecked');
	var addid = [];
	for (i in ids) {
	   addid.push(ids[i].id); }
	//alert(addid);
	$.getJSON('Save', {id:addid}, function(json, status, jqr) {
	    if (status="success") {
		$('#dg1').edatagrid('reload');
		$('#dg2').edatagrid('reload');
	    }
	});
    $('#dg2').datagrid('clearSelections');
    }
}

