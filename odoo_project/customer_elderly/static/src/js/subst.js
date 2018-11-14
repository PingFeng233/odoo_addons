odoo.define('demo1.alert', function (require) {
    "use strict";
    //var core = require('web.core');
    // var Context = require('web.Context');
    var core = require('web.core');
    // var dataManager = require('web.data_manager');
    // var Dialog = require('web.Dialog');
    // var Domain = require('web.Domain');
    // var FormController = require('web.FormController');
    // var FormRenderer = require('web.FormRenderer');
    // var FormView = require('web.FormView');
    // var viewRegistry = require('web.view_registry');
    // var ajax = require('web.ajax');

    var _t = core._t;
    var QWeb = core.qweb;

    var Sidebar = require('web.Sidebar');
    var ListController = require('web.ListController');
    var field_utils = require('web.field_utils');
    var Dialog = require('web.Dialog');
    var ListView = require('web.ListView');


    // // Mixins that enable the 'Import' feature
    // var ImportViewMixin = {
    //     /**
    //      * @override
    //      */
    //     init: function (viewInfo, params) {
    //        // var importEnabled = 'import_enabled' in params ? params.import_enabled : true;
    //         // if true, the 'Import' button will be visible
    //         //this.controllerParams.importEnabled = importEnabled;
    //     },
    // };

    // ListView.include({
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         ImportViewMixin.init.apply(this, arguments);
    //     },
    // });


    Sidebar.include({
        _redraw: function() {
            var self = this;
            //console.log(this);
            this._super.apply(this, arguments);
            
            //remove first dprint button
            if(this['env']['model']=="account.payment"){
                this.$('.btn-group li a').off();
                this.$('.btn-group').eq(0).hide();
            }
            if(this['env']['model']=="sale.subscription"){
                //  this.$('.btn-group li a').off();
                //  this.$('.btn-group').eq(0).hide();
                // this.$('.o_list_tender_button_create').click(this.proxy('tree_view_action'));
            }
        },
        tree_view_action: function() {     
            alert("");
        }

    });
    var aaa =null;

    function ArrayOutput(data){
        return aaa._rpc({
            context_id:1,
            method:"recurring_invoice",
            model:"sale.subscription",
            args:[[data['res_id']]]
        });
    }

    ListController.include({
        init: function(parent, model, renderer, params){
            this._super.apply(this, arguments);
            this.parent = parent;
            this.res_model = model;
            this.renderer = renderer;
            this.params = params;
            //this.client_download_type = params.initialState.context.client_download_type;
        },
        renderButtons: function ($node) {

            this._super.apply(this, arguments);
            var models = this.modelName;
            console.log("models",this);
            if(models==='sale.subscription'){
                if (!this.noLeaf && this.hasButtons) {
                    this.$buttons.on('click', '.o_list_tender_button_create', this._getPageData.bind(this));
                }
            }
        },
        _getPageData: function(){
            var self = this;
            aaa = this;
            var headers = this.renderer.columns.map(function(v){return v.attrs.name});
            var selectionItems =this.renderer.selection;
            var listItems =this.renderer.state.data;

            console.log(selectionItems);
            console.log(listItems);
            var selectedIDs =[];

            selectedIDs = selectionItems.map(function(idd){
                var targetItem = [];
                listItems.map(function(item){
                    if(item.id==idd){
                        console.log(item);
                        targetItem = item;
                    }
                })
                return targetItem;
            })
            if(selectedIDs.length>1){
                Dialog.confirm(
                    self,
                    _t("產生"+selectedIDs.length+"份 客戶發票?"), {
                        confirm_callback: function () {
                            selectedIDs.map(function(idd){
                                ArrayOutput(idd);
                            });
                        },
                    }
                );
            }else if(selectedIDs.length==1){
                Dialog.confirm(
                    self,
                    _t("產生客戶發票?"), {
                        confirm_callback: function () {
                            selectedIDs.map(function(idd){
                                ArrayOutput(idd);
                            });
                        },
                    }
                );
            }else{
                Dialog.confirm(
                    self,
                    _t("沒有選擇項目")
                );
            }

        }
    })
})