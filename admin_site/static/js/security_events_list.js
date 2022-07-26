$(function(){
    var SecurityEventList = function(container_elem, template_container_id) {
        this.elem = $(container_elem)
        this.searchUrl = window.security_event_search_url
        this.updateUrl = window.security_events_update_url
        this.statusSelectors = []
        BibOS.addTemplate('securityevent-entry', template_container_id)
    }
    $.extend(SecurityEventList.prototype, {
        init: function() {
            var securityeventlist = this
            $('#securityeventlist-status-selectors input:checkbox').on("change", function() {
                securityeventlist.search()
            })
            $('#securityeventlist-level-selectors input:checkbox').on("change", function() {
                securityeventlist.search()
            })
            securityeventlist.search()

            $('#all_events_toggle').on("change", function() {
                all_events_checked = this.checked
                $("#securityevent-list input:checkbox").each(function() {
                    this.checked = all_events_checked
                })
            })

            $('#handle_events_save_button').on("click", function() {
                securityeventlist.handle_events()

                var modal_element = document.getElementById('handle_events_modal')
                var handle_security_events_modal = bootstrap.Modal.getInstance(modal_element)
                handle_security_events_modal.hide()
            })

        },

        appendEntries: function(dataList) {
            var container = this.elem
            $.each(dataList.results, function() {
                var log_info_button = '<button ' +
                        'class="btn btn-secondary loginfobutton p-0" ' +
                        'data-bs-title="Log-info" ' +
                        'data-bs-toggle="popover" ' +
                        'data-bs-content="' + '<span class=severity-high>' + this.problem_name + '</span>' + '<br>' + this.summary + '"' +
                        'data-bs-html=true ' +
                        'data-bs-placement=left ' +
                        'data-bs-trigger="click" ' +
                        'data-bs-animation="true" ' +
                        'data-pk="' + this.pk + '"' +
                    '><span class="material-icons fs-3">info</span></button>'
                var item = $(BibOS.expandTemplate(
                    'securityevent-entry',
                    $.extend(this, {
                        "log_info_button": log_info_button
                    })
                ))
                item.attr('event-id', this.pk)
                item.appendTo(container)
            })
            BibOS.setupSecurityEventLogInfoButtons(container)
        },

        replaceEntries: function(dataList) {
            this.elem.find('tr').remove()
            this.appendEntries(dataList)
        },

        selectFilter: function(field, elem, val) {
            var e = $(elem)
            if(e.hasClass('selected')) {
                e.removeClass('selected')
                val = ''
            } else {
                e.parent().find('li').removeClass('selected')
                e.addClass('selected')
            }
            $('#securityeventlist-filterform input[name=' + field + ']').val(val)
            this.search()
        },

        selectPC: function(elem, val) {
            this.selectFilter('pc', elem, val)
        },

        orderby: function(order) {
            var input = $('#securityeventlist-filterform input[name=orderby]')
            input.val(BibOS.getOrderBy(input.val(), order))
            this.search()
        },
        setUpPaginationCount: function(data) {
            $("div#pagination-count").text(calcPaginationRange(data, 20))
        },
        setUpPaginationLinks: function(data) {
            var pagination = $("ul.pagination")
            pagination.empty()
            var eventsearch = this

            var previous_item = $('<li class="page-item disabled"><a class="page-link"><span class="material-icons">navigate_before</span> Forrige</a></li>')
            if (data.has_previous) {
                previous_item.removeClass("disabled")
                previous_item.find('a').on("click", function() {
                    var input = $('#securityeventlist-filterform input[name=page]')
                    input.val(data.previous_page_number)
                    eventsearch.search()
                })
            }
            previous_item.appendTo(pagination)

            data.page_numbers.forEach(function(page) {
                if (data.page == page) {
                    item = $('<li class="page-item active"><a class="page-link">' + page + '</a></li>')
                }
                else {
                    item = $('<li class="page-item"><a class="page-link">' + page + '</a></li>')
                }
                item.find('a').on("click", function() {
                    var input = $('#securityeventlist-filterform input[name=page]')
                    input.val(page)
                    eventsearch.search()
                })
                item.appendTo(pagination)
            })

            var next_item = $('<li class="page-item disabled"><a class="page-link">Næste <span class="material-icons">navigate_next</span></a></li>')
            if (data.has_next) {
                next_item.removeClass("disabled")
                next_item.find('a').on("click", function() {
                    var input = $('#securityeventlist-filterform input[name=page]')
                    input.val(data.next_page_number)
                    eventsearch.search()
                })
            }
            next_item.appendTo(pagination)
        },
        search: function() {
            var js = this
            js.searchConditions = $('#securityeventlist-filterform').serialize()

            $.ajax({
                type: "GET",
                url: js.searchUrl,
                data: js.searchConditions,
                success: function(data) {
                    js.replaceEntries(data)
                    js.setUpPaginationCount(data)
                    js.setUpPaginationLinks(data)
                },
                error: function(err) {
                    console.log(err)
                },
                dataType: "json"
            })
        },
        handle_events: function() {
            var js = this
            event_ids = []
            $("#securityevent-list input:checkbox:checked").each(function() {
                event_ids.push($(this).parents("tr").attr('event-id'))
            })
            status = $("[name='status']").find(":selected").val()
            note = $("[name='note']").text()
            assigned_user = $("[name='assigned_user']").find(":selected").val()

            $.post({
                type: "POST",
                url: js.updateUrl,
                data: $.param({'ids': event_ids, 'status': status, 'note':note, 'assigned_user':assigned_user}, true),
                success: function() {
                    js.search()
                }
            })
        },
        reset: function() {
            $('#securityeventlist-filterform')[0].reset()
            $('#securityeventlist-filterform li.selected').removeClass('selected')
            $('#jobsearch-filterform input[name=pc]').val('')
            $('#jobsearch-filterform input[name=page]').val('1')
            this.search()
        }
    })
    BibOS.SecurityEventList = new SecurityEventList('#securityevent-list', '#securityeventitem-template')
    $(function() { BibOS.SecurityEventList.init() })
})
