//  -*- coding:utf8 -*-
//  treegrid_pager.js
//  基于jeasyui.treegrid.js，参照etree.js编写
//  一些功能性函数，用在树形网格展开的地方

//  20240528: 第一次写jeasyui插件成功！！就是一个如何操作js全局命名空间的问题。

(function ($) {
    //var editingId = undefined;  //  同时只能编辑一条记录，临时存放在本变量中
    $.fn.treegrid.methods = $.extend({}, $.fn.treegrid.methods, {
        pageFilter: function (data) {
            //  为树形数据增加一个翻页控件，通过在装入数据时进行判断后，增加一个div实现。
            //  先使用自定义函数的方式实现和测试，然后参照easyui，写进$.fn名字空间以方便引用
            //  使用方式：在tree/etree的load中，指定：loadFilter=$.fn.etree.methods.pageFilter。
            if (data.total) {    // 如果返回的是select形式，表明需要翻页
                parentNode = $(this).tree('find', data.rows[0].parentid);
                if (parentNode) {
                    parentNode.total = data.total;
                    parentNode.pagesize = data.pagesize;
                } else {    // 是顶层目录，如果记录数超过一页数量,显示翻页插件
                    tree = this;
                    $('#pp0').remove();
                    $('<div id="pp0"></div>').insertBefore($(this));
                    $('#pp0').css({ visibility: "visible" }).pagination({
                        // 根目录的翻页控件需要在页面中提前放置一个"pp0"
                        total: data.total, pageSize: data.pagesize, pageNumber: data.pagenumber
                        , layout: ['prev', 'links', 'next'], displayMsg: ''
                        , onSelectPage: function (pageNumber, pageSize) {
                            opts = $(tree).tree('options');
                            opts['queryParams']['page'] = pageNumber;
                            $(tree).tree('reload');
                            opts['queryParams']['page'] = undefined;
                        }
                    });
                }
                return data.rows;
            } else {
                return data;
            }
        }
        , pageSelect: function (node) {
            //  当tree中展开下级数据时，增加显示翻页控件。
            //  使用方式：在tree/etree的load中，指定：onExpand=$.fn.etree.methods.pageSelect。同时在其onExpand中，调用select。
            if ('children' in node && 'total' in node && node.total > node.children.length) {
                $('#pp').remove();
                tree = this;
                pp = $('<span id="pp" style="position:relative;top:-6px;right:0px;float:right;display:inline-block"></span>').appendTo(node.target);
                pp.pagination({
                    layout: ['prev', 'links', 'next'], displayMsg: '', total: node.total
                    , pageSize: node.pagesize, pageNumber: node.pageNumber
                    , onSelectPage: function (pageNumber, pageSize) {
                        opts = $(tree).tree('options');
                        opts['queryParams']['page'] = pageNumber;
                        $(tree).tree('reload', node.target);
                        opts['queryParams']['page'] = undefined;
                        node.pageNumber = pageNumber;
                    }
                });
            }
        }
        , edit: function (dg) { // 编辑选中节点
            var row = dg.treegrid('getSelected');
            console.log('row:', row);
            if (row==null) {
                console.log('请选选中记录，或者直接在上面双击');
                return;
            }
            if(row.id==editingId) {  // 正在编辑
                console.log('正在编辑不用双击', row.id, editingId);
                return;
            } 
            //如果当前有一笔记录正处在编辑状态，先提交或者取消之
            if(editingId) { // 已经有一行正处于编辑状态，先选中并提交之
                nid = row.id;   // 保存新点击或双击的记录ID
                dg.treegrid('select', editingId);
                dg.treegrid('update');
                dg.treegrid('select', nid);
            }
            dg.treegrid('beginEdit', row.id);
            editingId = row.id;
            //  在进入编辑状态后，禁止翻页控件。退出编辑或保存后，恢复翻页。
            // dg.treegrid('getPager').hide();
        }
        , cancel: function (dg) { // 取消编辑，主要是为了设置editingId
            if (editingId != undefined) {
                dg.treegrid('cancelEdit', editingId);
                editingId = undefined;
            }
            // dg.treegrid('getPager').show();
        }
        ,update: function(dg) {
            if (editingId==undefined) {
                return; // 没有选中记录在编辑状态，直接退出，可弹出提示。
            }
            var old_node = dg.treegrid('getSelected');
            var {...old_node} = old_node;   // 此种方式可以达到浅层复制。
            console.log('old_node:', old_node);
            dg.treegrid('endEdit', editingId);  //坑！在结束修改后，即使以前取得的node，其内容也会变为编辑结束后的内容。需要进行复制。
            editingId = undefined;
            var opts = dg.treegrid('options');
            var node = dg.treegrid('getSelected');
            if (node) {
                /*  这些信息不能在这儿删除，否则会影响页面显示，只能在后台删
                delete node._parentId;  // 下级展开的节点，会多出这一个字段，删之
                delete node.children;   // 删除下级信息
                */
                var {...new_node} = node;
                delete new_node._parentId;
                delete new_node.children;
                delete new_node.state;
                delete new_node.parentid;
                console.log('node:', node);
                console.log('old_node:', old_node);
                //node.haha = 'error';
                $.ajax({
                    url: opts.updateUrl,
                    type: "post",
                    dataType: "json",
                    data: new_node,
                    success: function(data) {
                        console.log('data return:', data);
                        dg.datagrid('updateRow', {index:new_node.id, row:data})
                    }
                }).error(function(jqXHR) {  // 出错时回滚数据？
                    console.log('error:', jqXHR);
                    //dg.treegrid('update', {row:old_node});  //这句为什么不能正常执行，搞不懂。
                    //dg.treegrid('update', {id:node.id, row:old_node});  //这句为什么不能正常执行，搞不懂。
                    //dg.treegrid('reload');    // 目前只有全表刷新可用，但将会回到未打开所有折叠的状态。
                    //dg.treegrid('reload', node.id);
                    //dg.treegrid('reload', node.id, old_node);
                    //dg.treegrid('reload', old_node);
                    dg.datagrid('updateRow',{index:node.id, row:old_node});   //这句可以正常回滚
                    //return false;
                });
                // dg.treegrid('getPager').show();
            }
        }
    });
})(jQuery);
