//  -*- coding:utf8 -*-
//  tree_pager.js
//  基于jeasyui.etree.js
//  一些功能性函数，用在树形数据展开的地方

//  20240528: 第一次写jeasyui插件成功！！就是一个如何操作js全局命名空间的问题。

(function ($) {
    $.fn.etree.methods = $.extend({}, $.fn.etree.methods, {
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
                        ,pageList:[data.pagesize,10,20]
                        , layout: ['list', 'sep', 'prev', 'links', 'next', 'last', 'refresh', 'manul']
                        , layout: [ 'list', 'sep', 'links', 'refresh']
                        //, displayMsg: ''
                        , onSelectPage: function (pageNumber, pageSize) {
                            opts = $(tree).tree('options');
                            opts['queryParams']['page'] = pageNumber;
                            $(tree).tree('reload');
                            //opts['queryParams']['page'] = pageNumber; //这句话意识不明了，当时是为什么？
                        }
                    });
                }
                return data.rows;
            } else {
                return data;
            }
        }
        ,pageSelect: function(node) {
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
                        //opts['queryParams']['page'] = undefined;
                        node.pageNumber = pageNumber;
                    }
                });
            }
        }
    });
})(jQuery);
