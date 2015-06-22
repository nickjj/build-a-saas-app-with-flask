var pluralize = require('./pluralize');

class BulkDelete {
    constructor() {
        this.body = $('body');

        this.selectAll = '#select_all';
        this.checkedItems = '.checkbox-item';

        this.colHeader = '.col-header';
        this.selectedRow = 'warning';

        this.updateScope = '#scope';
        this.bulkActions = '#bulk_actions';
    }

    listenForEvents() {
        var self = this;

        this.body.on('change', this.checkedItems, function () {
            var checkedSelector = `${self.checkedItems}:checked`;
            var itemCount = $(checkedSelector).length;
            var pluralizeItem = pluralize('item', itemCount);
            var scopeOptionText = `${itemCount} selected ${pluralizeItem}`;

            if ($(this).is(':checked')) {
                $(this).closest('tr').addClass(self.selectedRow);

                $(self.colHeader).hide();
                $(self.bulkActions).show();
            }
            else {
                $(this).closest('tr').removeClass(self.selectedRow);

                if (itemCount === 0) {
                    $(self.bulkActions).hide();
                    $(self.colHeader).show();
                }
            }

            $(`${self.updateScope} option:first`).text(scopeOptionText)
        });

        this.body.on('change', this.selectAll, function () {
            var checkedStatus = this.checked;

            $(self.checkedItems).each(function () {
                $(this).prop('checked', checkedStatus);
                $(this).trigger('change');
            });
        });
    }
}

module.exports = BulkDelete;
