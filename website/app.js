/**
 * Victory Points Frontend Application
 * Handles loading and displaying fantasy football standings data
 */

class VictoryPointsApp {
    constructor() {
        this.seasonData = null;
        this.weekData = {};
        this.availableWeeks = [];
        this.config = null;
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        await this.loadConfig();
        await this.loadData();
        this.setupLeagueLinks();
    }
    
    setupEventListeners() {
        const weekSelect = document.getElementById('weekSelect');
        weekSelect.addEventListener('change', (e) => {
            this.displaySelectedView(e.target.value);
        });
    }
    
    async loadConfig() {
        try {
            const response = await fetch('./data/website_config.json');
            if (response.ok) {
                this.config = await response.json();
                console.log('Loaded website configuration:', this.config);
            } else {
                console.log('No website configuration found, using defaults');
                this.config = {
                    league: { id: '', url: '', rules_url: '' },
                    features: { show_league_link: false, show_rules_link: false }
                };
            }
        } catch (error) {
            console.log('Failed to load website configuration, using defaults:', error);
            this.config = {
                league: { id: '', url: '', rules_url: '' },
                features: { show_league_link: false, show_rules_link: false }
            };
        }
    }
    
    setupLeagueLinks() {
        const leagueLinksContainer = document.getElementById('leagueLinks');
        const leagueLink = document.getElementById('leagueLink');
        const rulesLink = document.getElementById('rulesLink');
        
        if (!this.config) return;
        
        let hasVisibleLinks = false;
        
        // Setup league link
        if (this.config.features.show_league_link && this.config.league.url) {
            leagueLink.href = this.config.league.url;
            leagueLink.style.display = 'inline-block';
            hasVisibleLinks = true;
        } else {
            leagueLink.style.display = 'none';
        }
        
        // Setup rules link
        if (this.config.features.show_rules_link && this.config.league.rules_url) {
            rulesLink.href = this.config.league.rules_url;
            rulesLink.style.display = 'inline-block';
            hasVisibleLinks = true;
        } else {
            rulesLink.style.display = 'none';
        }
        
        // Show/hide the entire links container
        if (hasVisibleLinks) {
            leagueLinksContainer.style.display = 'block';
        } else {
            leagueLinksContainer.style.display = 'none';
        }
    }

    async loadData() {
        try {
            await this.loadSeasonStandings();
            await this.loadAvailableWeeks();
            this.displaySelectedView('season');
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError('Failed to load fantasy football data. Please try again later.');
        }
    }
    
    async loadSeasonStandings() {
        try {
            const response = await fetch('./data/season_standings.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.seasonData = await response.json();
        } catch (error) {
            console.error('Failed to load season standings:', error);
            // Create empty season data if file doesn't exist
            this.seasonData = {
                standings: [],
                season_summary: {},
                weeks_included: 0,
                last_updated: new Date().toISOString()
            };
        }
    }
    
    async loadAvailableWeeks() {
        // Try to load week files to determine what's available
        this.availableWeeks = [];
        
        // Try weeks 1-18 (typical NFL season length)
        for (let week = 1; week <= 18; week++) {
            try {
                const response = await fetch(`./data/week_${week.toString().padStart(2, '0')}_results.json`);
                if (response.ok) {
                    const weekData = await response.json();
                    this.weekData[week] = weekData;
                    this.availableWeeks.push(week);
                }
            } catch (error) {
                // Week file doesn't exist, skip
                continue;
            }
        }
        
        this.populateWeekSelector();
    }
    
    populateWeekSelector() {
        const weekSelect = document.getElementById('weekSelect');
        
        // Clear existing options except season
        const seasonOption = weekSelect.querySelector('option[value="season"]');
        weekSelect.innerHTML = '';
        weekSelect.appendChild(seasonOption);
        
        // Add week options
        this.availableWeeks.forEach(week => {
            const option = document.createElement('option');
            option.value = week;
            option.textContent = `Week ${week}`;
            weekSelect.appendChild(option);
        });
    }
    
    displaySelectedView(selection) {
        const seasonContainer = document.getElementById('seasonStandings');
        const weekContainer = document.getElementById('weekResults');
        const seasonSummary = document.getElementById('seasonSummary');
        
        if (selection === 'season') {
            seasonContainer.style.display = 'block';
            weekContainer.style.display = 'none';
            seasonSummary.style.display = 'block';
            this.displaySeasonStandings();
        } else {
            seasonContainer.style.display = 'none';
            weekContainer.style.display = 'block';
            seasonSummary.style.display = 'none';
            this.displayWeekResults(parseInt(selection));
        }
        
        this.updateLastUpdated();
    }
    
    displaySeasonStandings() {
        const tbody = document.getElementById('seasonStandingsBody');
        
        if (!this.seasonData || !this.seasonData.standings || this.seasonData.standings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No season data available yet.</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        
        this.seasonData.standings.forEach((team, index) => {
            const row = this.createSeasonStandingsRow(team, index + 1);
            tbody.appendChild(row);
        });
        
        this.displaySeasonSummary();
    }
    
    createSeasonStandingsRow(team, rank) {
        const row = document.createElement('tr');
        
        const rankCell = document.createElement('td');
        rankCell.innerHTML = this.formatRank(rank);
        row.appendChild(rankCell);
        
        const teamCell = document.createElement('td');
        teamCell.textContent = team.team_name;
        teamCell.style.fontWeight = '600';
        row.appendChild(teamCell);
        
        const totalRecordCell = document.createElement('td');
        totalRecordCell.innerHTML = `<span class="record record-total">${team.total_wins}-${team.total_losses}</span>`;
        row.appendChild(totalRecordCell);
        
        const h2hRecordCell = document.createElement('td');
        const h2hRecord = team.total_h2h_ties > 0 
            ? `${team.total_h2h_wins}-${team.total_h2h_losses}-${team.total_h2h_ties}`
            : `${team.total_h2h_wins}-${team.total_h2h_losses}`;
        h2hRecordCell.innerHTML = `<span class="record record-h2h">${h2hRecord}</span>`;
        row.appendChild(h2hRecordCell);
        
        const perfRecordCell = document.createElement('td');
        perfRecordCell.innerHTML = `<span class="record record-perf">${team.total_performance_wins}-${team.total_performance_losses}</span>`;
        row.appendChild(perfRecordCell);
        
        const totalPointsCell = document.createElement('td');
        totalPointsCell.textContent = team.total_points.toFixed(1);
        row.appendChild(totalPointsCell);
        
        const avgPointsCell = document.createElement('td');
        avgPointsCell.textContent = team.average_score.toFixed(1);
        row.appendChild(avgPointsCell);
        
        return row;
    }
    
    displayWeekResults(week) {
        const weekData = this.weekData[week];
        const tbody = document.getElementById('weekResultsBody');
        const title = document.getElementById('weekResultsTitle');
        
        title.textContent = `Week ${week} Results`;
        
        if (!weekData || !weekData.team_results) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No data available for this week.</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        
        weekData.team_results.forEach((team, index) => {
            const row = this.createWeekResultsRow(team, index + 1);
            tbody.appendChild(row);
        });
        
        this.displayWeekSummary(weekData);
    }
    
    createWeekResultsRow(team, rank) {
        const row = document.createElement('tr');
        
        const rankCell = document.createElement('td');
        rankCell.innerHTML = this.formatRank(rank);
        row.appendChild(rankCell);
        
        const teamCell = document.createElement('td');
        teamCell.textContent = team.team_name;
        teamCell.style.fontWeight = '600';
        row.appendChild(teamCell);
        
        const scoreCell = document.createElement('td');
        scoreCell.textContent = team.week_score.toFixed(1);
        scoreCell.style.fontWeight = '600';
        row.appendChild(scoreCell);
        
        const h2hCell = document.createElement('td');
        h2hCell.innerHTML = `<span class="result-badge result-${team.h2h_result.toLowerCase()}">${team.h2h_result}</span>`;
        row.appendChild(h2hCell);
        
        const perfCell = document.createElement('td');
        perfCell.innerHTML = `<span class="result-badge result-${team.performance_result.toLowerCase()}">${team.performance_result}</span>`;
        row.appendChild(perfCell);
        
        const weekRecordCell = document.createElement('td');
        weekRecordCell.innerHTML = `<span class="record record-total">${team.total_wins}-${team.total_losses}</span>`;
        row.appendChild(weekRecordCell);
        
        return row;
    }
    
    displayWeekSummary(weekData) {
        const summaryContainer = document.getElementById('weekSummary');
        const summary = weekData.week_summary;
        
        if (!summary) {
            summaryContainer.style.display = 'none';
            return;
        }
        
        summaryContainer.style.display = 'block';
        summaryContainer.innerHTML = `
            <h4>Week ${weekData.week} Summary</h4>
            <div class="summary-grid">
                <div class="summary-stat">
                    <span class="value">${summary.highest_score.toFixed(1)}</span>
                    <span class="label">Highest Score</span>
                </div>
                <div class="summary-stat">
                    <span class="value">${summary.lowest_score.toFixed(1)}</span>
                    <span class="label">Lowest Score</span>
                </div>
                <div class="summary-stat">
                    <span class="value">${summary.average_score.toFixed(1)}</span>
                    <span class="label">Average Score</span>
                </div>
                <div class="summary-stat">
                    <span class="value">${summary.perfect_weeks}</span>
                    <span class="label">Perfect (2-0)</span>
                </div>
                <div class="summary-stat">
                    <span class="value">${summary.winless_weeks}</span>
                    <span class="label">Winless (0-2)</span>
                </div>
            </div>
        `;
    }
    
    displaySeasonSummary() {
        const summaryContainer = document.getElementById('seasonSummary');
        const statsContainer = document.getElementById('summaryStats');
        const summary = this.seasonData.season_summary;
        
        if (!summary || !this.seasonData.standings.length) {
            summaryContainer.style.display = 'none';
            return;
        }
        
        summaryContainer.style.display = 'block';
        
        statsContainer.innerHTML = `
            <div class="summary-card">
                <span class="stat-value">${summary.leader || 'N/A'}</span>
                <span class="stat-label">Current Leader</span>
            </div>
            <div class="summary-card">
                <span class="stat-value">${summary.leader_wins || 0}</span>
                <span class="stat-label">Leader Wins</span>
            </div>
            <div class="summary-card">
                <span class="stat-value">${summary.most_points || 'N/A'}</span>
                <span class="stat-label">Most Points</span>
            </div>
            <div class="summary-card">
                <span class="stat-value">${(summary.highest_total_points || 0).toFixed(1)}</span>
                <span class="stat-label">Highest Total</span>
            </div>
        `;
    }
    
    formatRank(rank) {
        if (rank === 1) return `<span class="rank-1">${rank}</span>`;
        if (rank === 2) return `<span class="rank-2">${rank}</span>`;
        if (rank === 3) return `<span class="rank-3">${rank}</span>`;
        return rank;
    }
    
    updateLastUpdated() {
        const lastUpdatedElement = document.getElementById('lastUpdated');
        
        let lastUpdate = null;
        
        if (this.seasonData && this.seasonData.last_updated) {
            lastUpdate = new Date(this.seasonData.last_updated);
        }
        
        if (lastUpdate) {
            const formatOptions = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            lastUpdatedElement.textContent = `Last updated: ${lastUpdate.toLocaleDateString('en-US', formatOptions)}`;
        } else {
            lastUpdatedElement.textContent = 'No data available';
        }
    }
    
    showError(message) {
        const tbody = document.getElementById('seasonStandingsBody');
        tbody.innerHTML = `<tr><td colspan="7" class="loading" style="color: #f56565;">${message}</td></tr>`;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VictoryPointsApp();
});

// Add some utility functions for development/testing
window.VictoryPointsApp = VictoryPointsApp;
