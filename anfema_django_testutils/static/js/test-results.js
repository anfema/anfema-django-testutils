$(document).ready(function(){

    function updateTestCaseContainerVisibility() {
        $('.testcase').each(function() {

            var $container = $(this);
            var currentResultFilter = $("#selection-result-filter").val();
            var $matchingTestRunResults = $container.find(".testrun[result='" + currentResultFilter + "']");

            if (currentResultFilter === "all") {
                $container.show();
            }

            else if ($matchingTestRunResults.length === 0) {
                $container.hide();
            } else {
                $container.show();
            }
        });
    }

    $(document).on('click', '.btn-testrun-details', function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        var $this = $(this);
        $this.closest("tr").next('tr').toggle();
        $this.text(function(i, text){
            return text === 'Hide' ? 'View' : 'Hide';
        });
    });

    $(document).on('click', '.btn-testcase-details', function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        var $this = $(this);
        var $container = $this.closest(".testcase");
        $container.find("tbody").toggle();
        $this.text(function(i, text){
            return text === 'Hide' ? '⋯' : 'Hide';
        });
    });

    $(document).on('change', '#selection-result-filter', function() {
        var selectedValue = $(this).val();

        $('.testrun').each(function() {
            var row = $(this);
            var rowResult = row.attr("result");

            if (selectedValue === "all" || selectedValue === rowResult) {
                row.show();
            } else {
                row.hide();
                row.next('tr').hide();  // also hide outcome
                row.find('.btn-testrun-details').text('View');
            }
        });

        updateTestCaseContainerVisibility();
    });

});
