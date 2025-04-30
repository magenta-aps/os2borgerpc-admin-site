let currentPage = 1;
let defaultFilters = [];
// State object to track selected filters and sorting order
const state = {
    selectedBatch: "", selectedPc: "", selectedGroup: "", orderBy: "",
};

// Function to update the job table content based on current filters and page
const updateJobTable = async (page = 1) => {
    currentPage = page;
    try {
        const data = await fetchJobData(page);
        renderJobTable(data.results);
        updatePagination(data);
    } catch (error) {
        const errMsg = `Error fetching job data: ${error.message || error}`;
        console.error(errMsg);
        alert(errMsg);  // Display error if data fetch fails
    }
};

// Fetch job data based on the current page and filter settings
const fetchJobData = (page) => fetch(`${JOBS_SEARCH_URL}?page=${page}&${getQueryString()}`)
    .then(response => response.json());

// Render job rows dynamically in the table body
const renderJobTable = (jobs) => {
    const tableBody = document.getElementById('jobTableBody');
    tableBody.innerHTML = jobs.map(createJobRow).join('');  // Create HTML rows for each job
};

// Create a single job row for the table
const createJobRow = (job) => `
    <tr class="align-middle">
        <td><strong><a href="${job.script_url}">${job.script_name}</a>${job.batch_name ? `<a> (${job.batch_name})</a>` : ""}</strong></td>
        <td>${job.user ? `<a href="${job.user_url}">${job.user}</a>` : ""}</td>
        <td>${job.created}</td>
        <td>${job.started}</td>
        <td>${job.finished}</td>
        <td><span class="badge bg-${job.label}">${job.status}</span></td>
        <td><strong><a href="${job.pc_url}">${job.pc_name}</a></strong></td>
        <td>
            <a type="button" onclick="getPopoverHtml(${job.pk})">
                <span class="material-symbols-outlined fs-3">info</span>
            </a>
        </td>
    </tr>`;

/* TODO: Rewrite the template so the generic copy_button from custom.js is be used instead */
function joblog_copy() {
  let btn = document.getElementById("clipboard-button")
  let log = document.getElementById("job-log").innerText

  navigator.clipboard.writeText(log)

  btn.getElementsByClassName("copy-btn-text-orig")[0].classList.add('d-none')
  btn.lastElementChild.classList.remove('d-none')
}

function closeAllPopovers() {
    document.querySelectorAll(".popover").forEach(pop=>bootstrap.Popover.getInstance(pop).hide())
}

// Function to handle displaying popover for job details
function getPopoverHtml(jobPk) {
    closeAllPopovers()
    const triggerElement = document.querySelector(`a[onclick="getPopoverHtml(${jobPk})"]`);

    fetch(`${JOBS_BASE_URL}${jobPk}/info/`)  // Fetch popover content
        .then(response => response.text())
        .then(data => {
            const popover = new bootstrap.Popover(triggerElement, {
                title: gettext("Job info"), content: data, html: true, placement: 'right', trigger: 'manual'
            });

            popover.show();  // Show the popover

            // Hide popover when clicking outside
            document.addEventListener('click', function handleClickOutside(e) {
                const popoverElement = document.querySelector('.popover');

                if (!triggerElement.contains(e.target) && !popoverElement.contains(e.target)) {
                    popover.hide();
                    document.removeEventListener('click', handleClickOutside);
                }
            });
            Array.from(document.getElementsByClassName('clipboard-btn')).forEach(btn=>btn.addEventListener('click', joblog_copy))
        })
        .catch(error => {
            console.error('Error:', error);  // Log error if popover fetch fails
        });
}

// Update pagination controls based on the current page and total pages
const updatePagination = (data) => {
    const paginationContainer = document.getElementById("job-pagination");
    const paginationInfo = document.getElementById("pagination-info");

    // Build pagination buttons dynamically
    paginationContainer.innerHTML = `
        ${data.has_previous ? `<li class="page-item"><a class="page-link" onclick="updateJobTable(1)"><span class="material-symbols-outlined">first_page</span> ${gettext("First")}</a></li>` : ''}
        ${data.has_previous ? `<li class="page-item"><a class="page-link" onclick="updateJobTable(${currentPage - 1})"><span class="material-symbols-outlined">navigate_before</span> ${gettext("Previous")}</a></li>` : ''}
        ${data.page_numbers.map(pageNum => `
            <li class="page-item ${pageNum === currentPage ? 'selected' : ''}">
                <a class="page-link" onclick="updateJobTable(${pageNum})">${pageNum}</a>
            </li>`).join('')}
        ${data.has_next ? `<li class="page-item"><a class="page-link" onclick="updateJobTable(${currentPage + 1})">${gettext("Next")} <span class="material-symbols-outlined">navigate_next</span></a></li>` : ''}
        ${data.has_next ? `<li class="page-item"><a class="page-link" onclick="updateJobTable(${data.num_pages})">${gettext("Last")}<span class="material-symbols-outlined ms-1">last_page</span></a></li>` : ''}
    `;

    paginationInfo.innerText = calcPaginationRange(data, 20);  // Display page info
};

// Function to reset all filters (status, batch, computer, group)
const resetFilters = () => {
    Object.assign(state, {
        selectedPc: "", selectedBatch: "", selectedGroup: "", orderBy: ""  // Clear all selected filters
    });

    // Reset the status checkboxes to default state (checked for first four)
    for (const filter of defaultFilters) {
        document.getElementById(filter.id).checked = filter.checked;
    }

    // Update UI: deactivate all filter buttons
    document.querySelectorAll(`#jobsearchnav button`).forEach(btn => btn.classList.remove('active'));

    updateJobTable(1);  // Refresh the job table
};

// Function to handle filtering by batch, computer, or group
const selectFilter = (type, pk, targetDiv) => {
    const button = document.getElementById(`${type}-${pk}`);
    const isActive = button.classList.contains("active");  // Check if the filter is active
    const stateKey = `selected${type.charAt(0).toUpperCase() + type.slice(1)}`;

    state[stateKey] = isActive ? "" : pk;  // Update state based on selected filter

    // Update UI: deactivate all buttons, activate the selected one
    document.querySelectorAll(`#${targetDiv} button`).forEach(btn => btn.classList.remove('active'));
    if (!isActive) button.classList.add("active");

    updateJobTable(1);  // Refresh the job table with the new filter
};

// Function to set the sorting field (column) and direction (ascending/descending)
const orderBy = (query) => {
    const sortArrow = document.getElementById(`${query}-sort-arrow`);
    const orderDirection = state.orderBy === query ? `-${query}` : query;  // Toggle sort direction

    state.orderBy = orderDirection;  // Update sorting field in state

    // Reset all sort arrows and update the current one
    document.querySelectorAll('#job-table-head i').forEach(iTag => {
        iTag.innerHTML = "unfold_more";  // Reset all arrows
    });
    sortArrow.innerHTML = orderDirection.startsWith('-') ? "arrow_downward" : "arrow_upward";  // Set the current arrow

    updateJobTable(1);  // Refresh the job table with the new sort order
};

// Function to build the query string based on the selected filters (status, batch, pc, group, and orderBy)
const getQueryString = () => `${Array.from(document.querySelectorAll('input[name="status"]:checked'))
    .map(cb => `status=${encodeURIComponent(cb.value)}`)  // Encode checked status values
    .join('&')}&batch=${state.selectedBatch}&pc=${state.selectedPc}&group=${state.selectedGroup}&orderby=${state.orderBy}`;

// Initialize the job table on page load
addEventListener("DOMContentLoaded", (event) => {
    defaultFilters = Array.from(document.querySelectorAll('input[name="status"]'))
        .map(filter => ({
            id: filter.id, checked: filter.checked
        }));
    updateJobTable(currentPage);
});
