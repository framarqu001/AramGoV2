document.addEventListener('DOMContentLoaded', function() {
    // Initialize expansion panels
    initExpansionPanels();
    
    // Initialize tabs
    initTabs();
    
    // Initialize filters
    initFilters();
});

/**
 * Initialize expansion panels
 */
function initExpansionPanels() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const matchCard = this.closest('.match-card');
            const expansionPanel = matchCard.nextElementSibling;
            
            if (expansionPanel.style.display === 'none' || !expansionPanel.style.display) {
                // Close any open panels first
                document.querySelectorAll('.match-expansion-panel').forEach(panel => {
                    if (panel !== expansionPanel && panel.style.display !== 'none') {
                        panel.style.display = 'none';
                        
                        // Reset the button icon
                        const btn = panel.previousElementSibling.querySelector('.match-btn');
                        const svg = btn.querySelector('svg');
                        svg.style.transform = '';
                    }
                });
                
                // Open this panel
                expansionPanel.style.display = 'block';
                
                // Rotate the button icon
                const svg = this.querySelector('svg');
                svg.style.transform = 'rotate(180deg)';
                
                // Initialize charts if they don't exist yet
                initCharts(expansionPanel);
            } else {
                // Close this panel
                expansionPanel.style.display = 'none';
                
                // Reset the button icon
                const svg = this.querySelector('svg');
                svg.style.transform = '';
            }
        });
    });
}

/**
 * Initialize tabs
 */
function initTabs() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('tab-btn')) {
            const tabBtn = event.target;
            const tabName = tabBtn.getAttribute('data-tab');
            const tabPanel = tabBtn.closest('.match-comparison-panel');
            
            // Remove active class from all tabs
            tabPanel.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked tab
            tabBtn.classList.add('active');
            
            // Hide all tab content
            tabPanel.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Show selected tab content
            tabPanel.querySelector(`#${tabName}-tab`).classList.add('active');
            
            // Reinitialize charts for the active tab
            const chartContainer = tabPanel.querySelector(`#${tabName}-tab .chart-container`);
            if (chartContainer) {
                const chartCanvas = chartContainer.querySelector('canvas');
                if (chartCanvas && !chartCanvas.chart) {
                    initChart(chartCanvas, tabName);
                }
            }
        }
    });
}

/**
 * Initialize filters
 */
function initFilters() {
    document.addEventListener('change', function(event) {
        if (event.target.classList.contains('metric-filter') || event.target.classList.contains('sort-filter')) {
            const filter = event.target;
            const tabPanel = filter.closest('.match-comparison-panel');
            const activeTab = tabPanel.querySelector('.tab-content.active');
            const tabName = activeTab.id.replace('-tab', '');
            
            // Update the table based on filter values
            updateTable(tabPanel, tabName);
            
            // Update the chart based on filter values
            updateChart(tabPanel, tabName);
        }
    });
}

/**
 * Initialize charts for a panel
 */
function initCharts(panel) {
    const activeTab = panel.querySelector('.tab-content.active');
    if (activeTab) {
        const tabName = activeTab.id.replace('-tab', '');
        const chartCanvas = activeTab.querySelector('.chart-container canvas');
        
        if (chartCanvas && !chartCanvas.chart) {
            initChart(chartCanvas, tabName);
        }
    }
}

/**
 * Initialize a specific chart
 */
function initChart(canvas, chartType) {
    if (!window.Chart) {
        // Load Chart.js if not already loaded
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = function() {
            createChart(canvas, chartType);
        };
        document.head.appendChild(script);
    } else {
        createChart(canvas, chartType);
    }
}

/**
 * Create a chart based on type
 */
function createChart(canvas, chartType) {
    const panel = canvas.closest('.match-comparison-panel');
    const blueTeamRows = panel.querySelectorAll('.tab-content.active .team-section:first-child .table-row');
    const redTeamRows = panel.querySelectorAll('.tab-content.active .team-section:last-child .table-row');
    
    const labels = [];
    const blueTeamData = [];
    const redTeamData = [];
    
    // Get data from the table
    blueTeamRows.forEach(row => {
        labels.push(row.querySelector('.col:first-child').textContent);
        
        let value;
        switch(chartType) {
            case 'damage':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            case 'gold':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            case 'kda':
                value = parseFloat(row.querySelector('.col:last-child').textContent);
                break;
            case 'cs':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            default:
                value = 0;
        }
        
        blueTeamData.push(value);
    });
    
    redTeamRows.forEach(row => {
        labels.push(row.querySelector('.col:first-child').textContent);
        
        let value;
        switch(chartType) {
            case 'damage':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            case 'gold':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            case 'kda':
                value = parseFloat(row.querySelector('.col:last-child').textContent);
                break;
            case 'cs':
                value = parseFloat(row.querySelector('.col:nth-child(3)').textContent);
                break;
            default:
                value = 0;
        }
        
        redTeamData.push(value);
    });
    
    // Create the chart
    canvas.chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Blue Team',
                    data: blueTeamData,
                    backgroundColor: 'rgba(75, 107, 195, 0.6)',
                    borderColor: 'rgba(75, 107, 195, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Red Team',
                    data: redTeamData,
                    backgroundColor: 'rgba(244, 107, 244, 0.6)',
                    borderColor: 'rgba(244, 107, 244, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Update table based on filters
 */
function updateTable(panel, tabName) {
    const metricFilter = panel.querySelector('.metric-filter').value;
    const sortFilter = panel.querySelector('.sort-filter').value;
    
    // Get all rows
    const blueTeamRows = Array.from(panel.querySelectorAll(`#${tabName}-tab .team-section:first-child .table-row`));
    const redTeamRows = Array.from(panel.querySelectorAll(`#${tabName}-tab .team-section:last-child .table-row`));
    
    // Sort rows based on filters
    const sortIndex = metricFilter === 'per-minute' ? 3 : 2;
    
    const sortFunction = (a, b) => {
        const valueA = parseFloat(a.querySelector(`.col:nth-child(${sortIndex + 1})`).textContent);
        const valueB = parseFloat(b.querySelector(`.col:nth-child(${sortIndex + 1})`).textContent);
        
        return sortFilter === 'highest' ? valueB - valueA : valueA - valueB;
    };
    
    blueTeamRows.sort(sortFunction);
    redTeamRows.sort(sortFunction);
    
    // Update the DOM
    const blueTeamSection = panel.querySelector(`#${tabName}-tab .team-section:first-child`);
    const redTeamSection = panel.querySelector(`#${tabName}-tab .team-section:last-child`);
    
    // Clear existing rows
    blueTeamRows.forEach(row => row.remove());
    redTeamRows.forEach(row => row.remove());
    
    // Add sorted rows
    const blueTeamHeader = blueTeamSection.querySelector('h4');
    blueTeamRows.forEach(row => {
        blueTeamSection.appendChild(row);
    });
    
    const redTeamHeader = redTeamSection.querySelector('h4');
    redTeamRows.forEach(row => {
        redTeamSection.appendChild(row);
    });
}

/**
 * Update chart based on filters
 */
function updateChart(panel, tabName) {
    const chartCanvas = panel.querySelector(`#${tabName}-tab .chart-container canvas`);
    
    if (chartCanvas && chartCanvas.chart) {
        // Get the chart instance
        const chart = chartCanvas.chart;
        
        // Get filter values
        const metricFilter = panel.querySelector('.metric-filter').value;
        const sortFilter = panel.querySelector('.sort-filter').value;
        
        // Get all rows
        const blueTeamRows = Array.from(panel.querySelectorAll(`#${tabName}-tab .team-section:first-child .table-row`));
        const redTeamRows = Array.from(panel.querySelectorAll(`#${tabName}-tab .team-section:last-child .table-row`));
        
        // Get data from the table
        const labels = [];
        const blueTeamData = [];
        const redTeamData = [];
        
        const dataIndex = metricFilter === 'per-minute' ? 3 : 2;
        
        blueTeamRows.forEach(row => {
            labels.push(row.querySelector('.col:first-child').textContent);
            blueTeamData.push(parseFloat(row.querySelector(`.col:nth-child(${dataIndex + 1})`).textContent));
        });
        
        redTeamRows.forEach(row => {
            labels.push(row.querySelector('.col:first-child').textContent);
            redTeamData.push(parseFloat(row.querySelector(`.col:nth-child(${dataIndex + 1})`).textContent));
        });
        
        // Update chart data
        chart.data.labels = labels;
        chart.data.datasets[0].data = blueTeamData;
        chart.data.datasets[1].data = redTeamData;
        
        // Update chart title based on metric
        let chartTitle = '';
        switch(tabName) {
            case 'damage':
                chartTitle = metricFilter === 'per-minute' ? 'Damage Per Minute' : 'Total Damage';
                break;
            case 'gold':
                chartTitle = metricFilter === 'per-minute' ? 'Gold Per Minute' : 'Total Gold';
                break;
            case 'kda':
                chartTitle = 'KDA Ratio';
                break;
            case 'cs':
                chartTitle = metricFilter === 'per-minute' ? 'CS Per Minute' : 'Total CS';
                break;
        }
        
        chart.options.plugins.title = {
            display: true,
            text: chartTitle
        };
        
        // Update the chart
        chart.update();
    }
}